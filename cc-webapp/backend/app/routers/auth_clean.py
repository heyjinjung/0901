"""Authentication API Router"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from ..database import get_db
from ..schemas.auth import UserCreate, UserLogin, AdminLogin, UserResponse, Token
from ..services.auth_service import AuthService, security
from ..models.auth_models import User, InviteCode
from ..core.config import settings

# Logger setup
logger = logging.getLogger(__name__)

# Auth service instance
auth_service = AuthService()

# OAuth2 schema
oauth2_scheme = HTTPBearer()

# Configuration values
JWT_EXPIRE_MINUTES = settings.jwt_expire_minutes
INITIAL_CYBER_TOKENS = getattr(settings, 'initial_cyber_tokens', 200)

router = APIRouter(tags=["authentication"])

@router.post("/signup", response_model=Token)
async def signup(
    data: UserCreate,
    db = Depends(get_db)
):
    """User registration (5 required fields: site_id, nickname, phone_number, invite_code, password)"""
    try:
        logger.info(f"Registration attempt: site_id={data.site_id}, nickname={data.nickname}")
        
        # Create user through AuthService
        user = auth_service.create_user(db, data)
        
        # Generate token
        access_token = auth_service.create_access_token(
            data={"sub": user.site_id, "user_id": user.id}
        )
        
        # Create user response data
        user_response = UserResponse(
            id=user.id,
            site_id=user.site_id,
            nickname=user.nickname,
            phone_number=user.phone_number,
            cyber_token_balance=user.cyber_token_balance,
            created_at=user.created_at,
            last_login=user.last_login,
            is_admin=user.is_admin,
            is_active=user.is_active
        )
        
        logger.info(f"Registration successful: user_id={user.id}")
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {e}")
        raise HTTPException(status_code=500, detail="Registration processing error occurred")

@router.post("/login", response_model=Token)
async def login(
    form_data: UserLogin,
    db = Depends(get_db)
):
    """User login"""
    try:
        logger.info(f"Login attempt: site_id={form_data.site_id}")
        
        # Authenticate user through AuthService
        user = auth_service.authenticate_user(db, form_data.site_id, form_data.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid site_id or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Generate access token
        access_token = auth_service.create_access_token(
            data={"sub": user.site_id, "user_id": user.id}
        )
        
        # Update last login time
        auth_service.update_last_login(db, user.id)
        
        # Create user response
        user_response = UserResponse(
            id=user.id,
            site_id=user.site_id,
            nickname=user.nickname,
            phone_number=user.phone_number,
            cyber_token_balance=user.cyber_token_balance,
            created_at=user.created_at,
            last_login=datetime.now(),
            is_admin=user.is_admin,
            is_active=user.is_active
        )
        
        logger.info(f"Login successful: user_id={user.id}")
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login processing error occurred")

@router.post("/admin/login", response_model=Token)
async def admin_login(
    form_data: AdminLogin,
    db = Depends(get_db)
):
    """Admin login"""
    try:
        logger.info(f"Admin login attempt: site_id={form_data.site_id}")
        
        # Admin authentication through AuthService
        user = auth_service.authenticate_admin(db, form_data.site_id, form_data.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid admin credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Generate access token
        access_token = auth_service.create_access_token(
            data={"sub": user.site_id, "user_id": user.id, "is_admin": True}
        )
        
        # Update last login time
        auth_service.update_last_login(db, user.id)
        
        # Create user response
        user_response = UserResponse(
            id=user.id,
            site_id=user.site_id,
            nickname=user.nickname,
            phone_number=user.phone_number,
            cyber_token_balance=user.cyber_token_balance,
            created_at=user.created_at,
            last_login=datetime.now(),
            is_admin=user.is_admin,
            is_active=user.is_active
        )
        
        logger.info(f"Admin login successful: user_id={user.id}")
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin login error: {e}")
        raise HTTPException(status_code=500, detail="Admin login processing error occurred")
