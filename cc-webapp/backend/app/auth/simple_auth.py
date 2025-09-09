"""
Consolidated authentication functions for the Casino-Club F2P API.
This module provides simple functions for user authentication.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
import logging

from ..database import get_db
from ..models.auth_models import User
from ..core.config import settings

# 로깅 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 콘솔 로그 핸들러 설정
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# OAuth2 설정
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """현재 인증된 사용자 가져오기"""
    logger.debug(f"[AUTH] Token received (first 10 chars): {token[:10]}...")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # JWT 토큰 디코딩
        payload = jwt.decode(
            token, 
            settings.jwt_secret_key, 
            algorithms=[settings.jwt_algorithm]
        )
        site_id = payload.get("sub")
        user_id = payload.get("user_id")
        
        if site_id is None:
            logger.error("[AUTH] Invalid token: sub field missing")
            raise credentials_exception
            
        logger.debug(f"[AUTH] Token verified for user {site_id}")
    except JWTError as e:
        logger.error(f"[AUTH] Token verification failed: {str(e)}")
        raise credentials_exception
    
    # 데이터베이스에서 사용자 조회
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        logger.error(f"[AUTH] User with ID {user_id} not found")
        raise credentials_exception
        
    logger.debug(f"[AUTH] Successfully authenticated user: {user.nickname}")
    return user

def get_current_user_id(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> int:
    """현재 인증된 사용자의 ID만 가져오기"""
    user = get_current_user(token, db)
    return user.id

def require_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """기본 사용자 권한 확인"""
    return get_current_user(token, db)

def require_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """관리자 권한 확인"""
    user = get_current_user(token, db)
    if not user.is_admin:
        logger.error(f"[AUTH] Admin access denied for user {user.nickname}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    logger.debug(f"[AUTH] Admin access granted for {user.nickname}")
    return user

def require_vip(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """VIP 사용자 권한 확인 - 추가 구현 필요"""
    # VIP 사용자 검증 로직 구현 필요
    user = get_current_user(token, db)
    # TODO: Implement VIP check logic
    return user
