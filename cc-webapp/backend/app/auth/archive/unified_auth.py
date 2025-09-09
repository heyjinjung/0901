"""
통합 인증 시스템 (Unified Authentication System)
- 초대코드 기반 간소화된 가입
- JWT 액세스/리프레시 토큰 관리
- 세션 관리 및 보안
- 모든 auth 관련 기능 통합
"""

import hashlib
import secrets
import uuid
import os
import logging
import random
import string
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple

from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer

from ..core.config import get_settings
from ...models.auth_models import User, InviteCode, LoginAttempt, RefreshToken, UserSession, SecurityEvent
from .token_blacklist import get_token_blacklist

logger = logging.getLogger("unified_auth")
settings = get_settings()

# Security 
security = HTTPBearer(auto_error=False)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UnifiedAuth:
    """통합 인증 서비스 클래스"""
    
    def __init__(self):
        # JWT 설정 (환경 변수 또는 기본값)
        self.JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "casino-club-secret-key-2024")
        self.JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
        self.JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
        self.REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))
        self.MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
        self.LOCKOUT_DURATION_MINUTES = int(os.getenv("LOCKOUT_DURATION_MINUTES", "15"))
        
        # 토큰 블랙리스트 초기화
        self.token_blacklist = get_token_blacklist()
    
    # ============================================
    # 1. 초대코드 기반 간소화된 가입/로그인
    # ============================================
    
    def generate_invite_code(self) -> str:
        """6자리 초대코드 생성"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    def create_invite_code(self, db: Session, tier: str = "STANDARD", 
                          adult_content_enabled: bool = False) -> InviteCode:
        """새 초대코드 생성"""
        try:
            code = self.generate_invite_code()
            # 중복 확인
            while db.query(InviteCode).filter(InviteCode.code == code).first():
                code = self.generate_invite_code()
            
            invite = InviteCode(
                code=code,
                tier=tier,
                adult_content_enabled=adult_content_enabled,
                created_at=datetime.utcnow(),
                is_active=True
            )
            db.add(invite)
            db.commit()
            db.refresh(invite)
            
            logger.info(f"Created invite code: {code} with tier: {tier}")
            return invite
            
        except Exception as e:
            logger.error(f"Failed to create invite code: {str(e)}")
            db.rollback()
            raise HTTPException(status_code=500, detail="Failed to create invite code")
    
    def register_with_invite_code(self, invite_code: str, nickname: str, db: Session) -> Dict[str, Any]:
        """초대코드로 즉시 가입 - JWT 토큰 반환"""
        try:
            # 초대코드 검증
            invite = db.query(InviteCode).filter(
                and_(InviteCode.code == invite_code, InviteCode.is_active == True)
            ).first()
            
            if not invite:
                raise HTTPException(status_code=400, detail="Invalid or expired invite code")
            
            # 닉네임 중복 확인
            existing_user = db.query(User).filter(User.nickname == nickname).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="Nickname already exists")
            
            # 사용자 생성
            user = User(
                id=str(uuid.uuid4()),
                nickname=nickname,
                email=f"{nickname.lower()}@casino-club.local",  # 임시 이메일
                vip_tier=invite.tier,
                adult_content_unlocked=invite.adult_content_enabled,
                created_at=datetime.utcnow(),
                points=1000,  # 기본 포인트
                gems=100,     # 기본 젬
                battlepass_level=1,
                battlepass_xp=0,
                total_spent=0.0,
                is_admin=False,
                is_active=True
            )
            
            db.add(user)
            
            # 초대코드 비활성화 (일회용)
            invite.is_active = False
            invite.used_at = datetime.utcnow()
            invite.used_by_user_id = user.id
            
            db.commit()
            db.refresh(user)
            
            # JWT 토큰 생성
            tokens = self.create_tokens(user.id, db)
            
            logger.info(f"User registered successfully: {nickname} with tier: {invite.tier}")
            
            return {
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "nickname": user.nickname,
                    "vip_tier": user.vip_tier,
                    "points": user.points,
                    "gems": user.gems,
                    "adult_content_unlocked": user.adult_content_unlocked
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Registration failed: {str(e)}")
            db.rollback()
            raise HTTPException(status_code=500, detail="Registration failed")
    
    def login_with_nickname(self, nickname: str, db: Session) -> Dict[str, Any]:
        """닉네임으로 로그인 (비밀번호 없음)"""
        try:
            user = db.query(User).filter(
                and_(User.nickname == nickname, User.is_active == True)
            ).first()
            
            if not user:
                # 로그인 시도 기록
                self._log_failed_login_attempt(None, nickname, "USER_NOT_FOUND", db)
                raise HTTPException(status_code=401, detail="User not found")
            
            # 계정 잠금 확인
            if self._is_account_locked(user.id, db):
                raise HTTPException(status_code=423, detail="Account temporarily locked")
            
            # JWT 토큰 생성
            tokens = self.create_tokens(user.id, db)
            
            # 성공 로그인 기록
            self._log_successful_login(user.id, db)
            
            logger.info(f"User logged in successfully: {nickname}")
            
            return {
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "token_type": "bearer",
                "user": {
                    "id": user.id,
                    "nickname": user.nickname,
                    "vip_tier": user.vip_tier,
                    "points": user.points,
                    "gems": user.gems,
                    "adult_content_unlocked": user.adult_content_unlocked,
                    "is_admin": user.is_admin
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Login failed")
    
    # ============================================
    # 2. JWT 토큰 관리
    # ============================================
    
    def create_access_token(self, data: dict) -> str:
        """액세스 토큰 생성"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.JWT_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "access"})
        
        return jwt.encode(to_encode, self.JWT_SECRET_KEY, algorithm=self.JWT_ALGORITHM)
    
    def create_refresh_token(self, user_id: str, db: Session) -> str:
        """리프레시 토큰 생성 및 DB 저장"""
        token_id = str(uuid.uuid4())
        expire = datetime.utcnow() + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode = {
            "user_id": user_id,
            "token_id": token_id,
            "exp": expire,
            "type": "refresh"
        }
        
        token = jwt.encode(to_encode, self.JWT_SECRET_KEY, algorithm=self.JWT_ALGORITHM)
        
        # DB에 리프레시 토큰 저장
        refresh_token = RefreshToken(
            id=token_id,
            user_id=user_id,
            token_hash=hashlib.sha256(token.encode()).hexdigest(),
            expires_at=expire,
            created_at=datetime.utcnow(),
            is_active=True
        )
        
        db.add(refresh_token)
        db.commit()
        
        return token
    
    def create_tokens(self, user_id: str, db: Session) -> Dict[str, str]:
        """액세스 + 리프레시 토큰 쌍 생성"""
        access_token = self.create_access_token({"user_id": user_id})
        refresh_token = self.create_refresh_token(user_id, db)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """토큰 검증 및 페이로드 반환"""
        try:
            # 블랙리스트 확인
            if self.token_blacklist and self.token_blacklist.is_blacklisted(token):
                logger.warning("Attempt to use blacklisted token")
                return None
            
            payload = jwt.decode(token, self.JWT_SECRET_KEY, algorithms=[self.JWT_ALGORITHM])
            return payload
            
        except JWTError as e:
            logger.warning(f"Token verification failed: {str(e)}")
            return None
    
    def refresh_access_token(self, refresh_token: str, db: Session) -> Dict[str, str]:
        """리프레시 토큰으로 새 액세스 토큰 발급"""
        try:
            payload = self.verify_token(refresh_token)
            if not payload or payload.get("type") != "refresh":
                raise HTTPException(status_code=401, detail="Invalid refresh token")
            
            user_id = payload.get("user_id")
            token_id = payload.get("token_id")
            
            # DB에서 리프레시 토큰 확인
            stored_token = db.query(RefreshToken).filter(
                and_(RefreshToken.id == token_id, RefreshToken.is_active == True)
            ).first()
            
            if not stored_token or stored_token.expires_at < datetime.utcnow():
                raise HTTPException(status_code=401, detail="Refresh token expired")
            
            # 새 액세스 토큰 생성
            new_access_token = self.create_access_token({"user_id": user_id})
            
            return {
                "access_token": new_access_token,
                "token_type": "bearer"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            raise HTTPException(status_code=500, detail="Token refresh failed")
    
    def logout(self, access_token: str, refresh_token: Optional[str], db: Session) -> bool:
        """로그아웃 - 토큰 무효화"""
        try:
            # 액세스 토큰 블랙리스트 추가
            access_payload = self.verify_token(access_token)
            if access_payload:
                expire_time = datetime.fromtimestamp(access_payload.get("exp", 0))
                if self.token_blacklist:
                    self.token_blacklist.add_to_blacklist(access_token, expire_time)
            
            # 리프레시 토큰 무효화
            if refresh_token:
                refresh_payload = self.verify_token(refresh_token)
                if refresh_payload and refresh_payload.get("type") == "refresh":
                    token_id = refresh_payload.get("token_id")
                    db.query(RefreshToken).filter(RefreshToken.id == token_id).update({
                        "is_active": False
                    })
                    db.commit()
            
            logger.info("User logged out successfully")
            return True
            
        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            return False
    
    # ============================================
    # 3. 세션 관리 및 보안
    # ============================================
    
    def _log_failed_login_attempt(self, user_id: Optional[str], identifier: str, 
                                 reason: str, db: Session):
        """실패한 로그인 시도 기록"""
        try:
            attempt = LoginAttempt(
                user_id=user_id,
                identifier=identifier,
                success=False,
                failure_reason=reason,
                ip_address="0.0.0.0",  # 실제 구현시 request에서 가져옴
                user_agent="unknown",   # 실제 구현시 request에서 가져옴
                attempted_at=datetime.utcnow()
            )
            db.add(attempt)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to log login attempt: {str(e)}")
    
    def _log_successful_login(self, user_id: str, db: Session):
        """성공한 로그인 기록"""
        try:
            attempt = LoginAttempt(
                user_id=user_id,
                identifier=user_id,
                success=True,
                ip_address="0.0.0.0",  # 실제 구현시 request에서 가져옴
                user_agent="unknown",   # 실제 구현시 request에서 가져옴
                attempted_at=datetime.utcnow()
            )
            db.add(attempt)
            db.commit()
        except Exception as e:
            logger.error(f"Failed to log successful login: {str(e)}")
    
    def _is_account_locked(self, user_id: str, db: Session) -> bool:
        """계정 잠금 상태 확인"""
        try:
            recent_time = datetime.utcnow() - timedelta(minutes=self.LOCKOUT_DURATION_MINUTES)
            
            failed_attempts = db.query(LoginAttempt).filter(
                and_(
                    LoginAttempt.user_id == user_id,
                    LoginAttempt.success == False,
                    LoginAttempt.attempted_at > recent_time
                )
            ).count()
            
            return failed_attempts >= self.MAX_LOGIN_ATTEMPTS
            
        except Exception as e:
            logger.error(f"Failed to check account lock status: {str(e)}")
            return False
    
    def create_user_session(self, user_id: str, access_token: str, db: Session) -> UserSession:
        """사용자 세션 생성"""
        try:
            session = UserSession(
                id=str(uuid.uuid4()),
                user_id=user_id,
                access_token_hash=hashlib.sha256(access_token.encode()).hexdigest(),
                created_at=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                is_active=True,
                ip_address="0.0.0.0",  # 실제 구현시 request에서 가져옴
                user_agent="unknown"   # 실제 구현시 request에서 가져옴
            )
            
            db.add(session)
            db.commit()
            db.refresh(session)
            
            return session
            
        except Exception as e:
            logger.error(f"Failed to create user session: {str(e)}")
            raise
    
    def get_current_user(self, token: str, db: Session) -> Optional[User]:
        """현재 사용자 조회 (토큰 기반)"""
        try:
            payload = self.verify_token(token)
            if not payload or payload.get("type") != "access":
                return None
            
            user_id = payload.get("user_id")
            if not user_id:
                return None
            
            user = db.query(User).filter(
                and_(User.id == user_id, User.is_active == True)
            ).first()
            
            return user
            
        except Exception as e:
            logger.error(f"Failed to get current user: {str(e)}")
            return None

# 싱글톤 인스턴스
unified_auth = UnifiedAuth()

# ============================================
# FastAPI 의존성 함수들
# ============================================

def get_current_user_token(credentials: HTTPBearer = Depends(security)) -> Optional[str]:
    """Authorization 헤더에서 토큰 추출"""
    if credentials:
        return credentials.credentials
    return None

def get_current_user(
    token: str = Depends(get_current_user_token),
    db: Session = Depends(lambda: None)  # 실제 구현시 get_db로 교체
) -> User:
    """현재 로그인한 사용자 조회"""
    if not token:
        raise HTTPException(status_code=401, detail="Access token required")
    
    user = unified_auth.get_current_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return user

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """관리자 권한 필요"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

def require_vip_tier(min_tier: str = "VIP"):
    """VIP 등급 이상 필요"""
    def check_tier(current_user: User = Depends(get_current_user)) -> User:
        tier_levels = {"STANDARD": 1, "PREMIUM": 2, "VIP": 3}
        user_level = tier_levels.get(current_user.vip_tier, 0)
        required_level = tier_levels.get(min_tier, 999)
        
        if user_level < required_level:
            raise HTTPException(
                status_code=403, 
                detail=f"Tier {min_tier} or higher required"
            )
        return current_user
    return check_tier
