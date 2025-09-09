"""
Casino-Club F2P - Auth API Endpoints
=============================================================================
Enhanced authentication API endpoints for user registration, login, and token management
Features:
- Invite code registration
- Username/password login
- Token refresh
- Session management
- Logout functionality
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..database import get_db
from .auth_service import AuthService
from .token_manager import TokenManager
from .auth_responses import (
    TokenResponse, 
    LoginResponse, 
    UserProfileResponse,
    SessionInfoResponse,
    SessionsListResponse,
    AuthErrorResponse
)
from ..models.auth_models import User

# Setup logging
logger = logging.getLogger("auth_api")

# Security scheme
security = HTTPBearer(auto_error=False)

# Router
router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={401: {"model": AuthErrorResponse}}
)


# Helper function to get client IP and user agent
def get_client_info(request: Request):
    ip = request.client.host
    user_agent = request.headers.get("user-agent", "Unknown")
    return ip, user_agent


@router.post("/register", response_model=LoginResponse)
async def register_user(
    request: Request,
    invite_code: str,
    nickname: str,
    db: Session = Depends(get_db)
):
    """
    Register a new user with an invite code
    
    - **invite_code**: Valid invite code (required)
    - **nickname**: Desired nickname (required)
    
    Returns user info and tokens for immediate login
    """
    try:
        # Register user with invite code
        user = AuthService.register_with_invite_code(invite_code, nickname, db)
        
        # Get client info
        ip_address, user_agent = get_client_info(request)
        
        # Create session
        session_id = AuthService.create_user_session(
            user.id, ip_address, user_agent, db
        )
        
        # Generate tokens
        access_token = TokenManager.create_access_token(user.id, session_id)
        refresh_token = TokenManager.create_refresh_token(
            user.id, ip_address, user_agent, db
        )
        
        # Record successful registration/login
        AuthService.record_login_attempt(
            site_id=user.site_id,
            ip_address=ip_address,
            user_agent=user_agent,
            success=True,
            user_id=user.id,
            db=db
        )
        
        # Return user info and tokens
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=3600,  # 1 hour
            user_id=user.id,
            nickname=user.nickname,
            vip_tier=user.vip_tier,
            cyber_tokens=user.cyber_tokens
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="가입 처리 중 오류가 발생했습니다"
        )


@router.post("/login", response_model=LoginResponse)
async def login_user(
    request: Request,
    site_id: str,
    db: Session = Depends(get_db)
):
    """
    Login with site ID (no password required in F2P version)
    
    - **site_id**: User site ID
    
    Returns user info and authentication tokens
    """
    try:
        # Get client info
        ip_address, user_agent = get_client_info(request)
        
        # Check login attempts (brute force protection)
        is_allowed, remaining_attempts = AuthService.check_login_attempts(
            site_id, ip_address, db
        )
        
        if not is_allowed:
            AuthService.record_login_attempt(
                site_id=site_id,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                failure_reason="too_many_attempts",
                db=db
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"로그인 시도 횟수 초과. {remaining_attempts}분 후 다시 시도해주세요"
            )
        
        # Find user by site_id
        user = db.query(User).filter(User.site_id == site_id).first()
        
        if not user:
            AuthService.record_login_attempt(
                site_id=site_id,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                failure_reason="user_not_found",
                db=db
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 사용자입니다"
            )
        
        # Create session
        session_id = AuthService.create_user_session(
            user.id, ip_address, user_agent, db
        )
        
        # Generate tokens
        access_token = TokenManager.create_access_token(user.id, session_id)
        refresh_token = TokenManager.create_refresh_token(
            user.id, ip_address, user_agent, db
        )
        
        # Record successful login
        AuthService.record_login_attempt(
            site_id=site_id,
            ip_address=ip_address,
            user_agent=user_agent,
            success=True,
            user_id=user.id,
            db=db
        )
        
        # Update last login timestamp
        user.last_login = AuthService.get_current_timestamp()
        db.commit()
        
        # Return user info and tokens
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=3600,  # 1 hour
            user_id=user.id,
            nickname=user.nickname,
            vip_tier=user.vip_tier,
            cyber_tokens=user.cyber_tokens
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그인 중 오류가 발생했습니다"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using a valid refresh token
    
    - **refresh_token**: Valid refresh token
    
    Returns new access token and optional new refresh token
    """
    try:
        # Get client info
        ip_address, user_agent = get_client_info(request)
        
        # Verify refresh token
        is_valid, user_id, error_msg = TokenManager.verify_refresh_token(
            refresh_token, ip_address, user_agent, db
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=error_msg or "유효하지 않은 리프레시 토큰입니다"
            )
        
        # Create new session
        session_id = AuthService.create_user_session(
            user_id, ip_address, user_agent, db
        )
        
        # Generate new access token
        new_access_token = TokenManager.create_access_token(user_id, session_id)
        
        # Rotate refresh token (security best practice)
        new_refresh_token = TokenManager.rotate_refresh_token(
            refresh_token, user_id, ip_address, user_agent, db
        )
        
        logger.info(f"Token refreshed for user {user_id}")
        
        # Return new tokens
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            expires_in=3600  # 1 hour
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="토큰 갱신 중 오류가 발생했습니다"
        )


@router.post("/logout")
async def logout(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Logout user by invalidating current session and token
    
    Returns confirmation message
    """
    try:
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="인증 토큰이 필요합니다",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        token = credentials.credentials
        
        # Get user from token
        user = AuthService.get_current_user(token, db)
        
        # Get client info
        ip_address, user_agent = get_client_info(request)
        
        # Get payload to extract session ID
        payload = TokenManager.verify_access_token(token)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰입니다",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        session_id = payload.get("sid")
        
        # End session
        if session_id:
            AuthService.end_session(user.id, session_id, "user_logout", db)
        
        # Blacklist token
        TokenManager.blacklist_token(token, reason="logout")
        
        return {"message": "성공적으로 로그아웃되었습니다"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그아웃 처리 중 오류가 발생했습니다"
        )


@router.get("/profile", response_model=UserProfileResponse)
async def get_user_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get current user profile information
    
    Returns detailed user profile data
    """
    try:
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="인증 토큰이 필요합니다",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        token = credentials.credentials
        
        # Get user from token
        user = AuthService.get_current_user(token, db)
        
        # Return profile data
        return UserProfileResponse(
            user_id=user.id,
            site_id=user.site_id,
            nickname=user.nickname,
            email=user.email,
            vip_tier=user.vip_tier,
            battlepass_level=user.battlepass_level,
            cyber_tokens=user.cyber_tokens,
            created_at=user.created_at.isoformat(),
            last_login=user.last_login.isoformat() if user.last_login else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="프로필 정보 조회 중 오류가 발생했습니다"
        )


@router.get("/sessions", response_model=SessionsListResponse)
async def list_active_sessions(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    List all active sessions for current user
    
    Returns list of active sessions with device info
    """
    try:
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="인증 토큰이 필요합니다",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        token = credentials.credentials
        
        # Get user from token
        user = AuthService.get_current_user(token, db)
        
        # Get current session ID
        payload = TokenManager.verify_access_token(token)
        current_session_id = payload.get("sid") if payload else None
        
        # Get active sessions
        sessions = AuthService.get_active_sessions(user.id, db)
        
        # Format response
        session_list = []
        for session in sessions:
            session_list.append(SessionInfoResponse(
                session_id=session.session_id,
                device_info=session.user_agent,
                ip_address=session.ip_address,
                created_at=session.created_at.isoformat(),
                expires_at=session.expires_at.isoformat(),
                is_current=(session.session_id == current_session_id)
            ))
        
        return SessionsListResponse(
            active_sessions=session_list,
            total_count=len(session_list)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session listing failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="세션 정보 조회 중 오류가 발생했습니다"
        )
