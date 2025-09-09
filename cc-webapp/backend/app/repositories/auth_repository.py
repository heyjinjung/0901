"""
🎰 Casino-Club F2P - Authentication Repository
=============================================
인증 관련 데이터 액세스 레이어

📅 작성일: 2025-08-03
🎯 목적: 인증, 인가, 초대코드 관리
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from datetime import datetime, timedelta
import logging

from ..models.auth_models import User, UserSession, InviteCode
from .base_repository import BaseRepository

from app.repositories.base_repository import BaseRepository
from app import models

logger = logging.getLogger(__name__)


class AuthRepository(BaseRepository[models.User]):
    """인증 도메인 전용 Repository"""

    def __init__(self, db: Session):
        super().__init__(db, models.User)

    # === 로그인/인증 관련 ===
    
    def authenticate_user(self, email: str, password_hash: str) -> Optional[models.User]:
        """사용자 인증"""
        try:
            user = self.db.query(models.User).filter(
                and_(
                    models.User.email == email,
                    models.User.password_hash == password_hash,
                    models.User.is_active == True
                )
            ).first()
            
            if user:
                # 마지막 로그인 시간 업데이트
                user.last_login = datetime.utcnow()
                self.db.commit()
                logger.info(f"User {user.id} authenticated successfully")
            
            return user
        except Exception as e:
            logger.error(f"Error authenticating user {email}: {e}")
            return None

    def verify_password(self, user_id: int, password_hash: str) -> bool:
        """비밀번호 확인"""
        try:
            user = self.db.query(models.User).filter(
                and_(
                    models.User.id == user_id,
                    models.User.password_hash == password_hash
                )
            ).first()
            return user is not None
        except Exception as e:
            logger.error(f"Error verifying password for user_id {user_id}: {e}")
            return False

    def update_password(self, user_id: int, new_password_hash: str) -> bool:
        """비밀번호 업데이트"""
        try:
            user = self.db.query(models.User).filter(models.User.id == user_id).first()
            if user:
                user.password_hash = new_password_hash
                self.db.commit()
                logger.info(f"Password updated for user_id {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating password for user_id {user_id}: {e}")
            self.db.rollback()
            return False

    # === 계정 상태 관리 ===
    
    def activate_user(self, user_id: int) -> bool:
        """사용자 계정 활성화"""
        try:
            user = self.db.query(models.User).filter(models.User.id == user_id).first()
            if user:
                user.is_active = True
                self.db.commit()
                logger.info(f"User {user_id} activated")
                return True
            return False
        except Exception as e:
            logger.error(f"Error activating user_id {user_id}: {e}")
            self.db.rollback()
            return False

    def deactivate_user(self, user_id: int) -> bool:
        """사용자 계정 비활성화"""
        try:
            user = self.db.query(models.User).filter(models.User.id == user_id).first()
            if user:
                user.is_active = False
                self.db.commit()
                logger.info(f"User {user_id} deactivated")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deactivating user_id {user_id}: {e}")
            self.db.rollback()
            return False


class InviteCodeRepository(BaseRepository[InviteCode]):
    """초대 코드 관리 Repository"""

    def __init__(self, db_session: Session):
        super().__init__(InviteCode, db_session)

    def get_by_code(self, code: str) -> Optional[InviteCode]:
        """코드로 초대 코드 조회"""
        try:
            return self.db_session.query(InviteCode).filter(
                InviteCode.code == code
            ).first()
        except Exception as e:
            logger.error(f"Error getting invite code {code}: {e}")
            return None

    def get_valid_invite(self, code: str) -> Optional[InviteCode]:
        """유효한 초대 코드 조회"""
        try:
            return self.db_session.query(InviteCode).filter(
                and_(
                    InviteCode.code == code,
                    InviteCode.is_used == False,
                    or_(InviteCode.expires_at == None, InviteCode.expires_at > datetime.utcnow())
                )
            ).first()
        except Exception as e:
            logger.error(f"Error getting valid invite code {code}: {e}")
            return None

    def create_invite_code(self, code: str, expires_in_days: int = 7, 
                          max_uses: int = 1, creator_id: int = None) -> Optional[InviteCode]:
        """새 초대 코드 생성"""
        try:
            # 중복 코드 확인
            existing = self.get_by_code(code)
            if existing:
                logger.warning(f"Invite code {code} already exists")
                return None

            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
            
            invite_data = {
                "code": code,
                "created_by": creator_id,
                "expires_at": expires_at,
                "max_uses": max_uses,
                "used_count": 0,
                "is_used": False,
                "created_at": datetime.utcnow()
            }
            
            invite = self.create(invite_data)
            if invite:
                logger.info(f"Created invite code {code} (expires: {expires_at})")
            
            return invite
        except Exception as e:
            logger.error(f"Error creating invite code {code}: {e}")
            return None

    def use_invite_code(self, code: str, user_id: int) -> bool:
        """초대 코드 사용 처리"""
        try:
            invite = self.get_valid_invite(code)
            if not invite:
                return False

            invite.used_count += 1
            invite.used_at = datetime.utcnow()
            invite.used_by_user_id = user_id
            
            # 최대 사용 횟수 도달 시 비활성화
            if invite.max_uses is not None and invite.used_count >= invite.max_uses:
                invite.is_used = True
            
            self.db_session.commit()
            logger.info(f"Invite code {code} used by user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error using invite code {code}: {e}")
            self.db_session.rollback()
            return False

    def get_user_invites(self, creator_id: int) -> List[InviteCode]:
        """사용자가 생성한 초대 코드 목록"""
        try:
            return self.db_session.query(InviteCode).filter(
                InviteCode.created_by == creator_id
            ).order_by(desc(InviteCode.created_at)).all()
        except Exception as e:
            logger.error(f"Error getting invites for creator_id {creator_id}: {e}")
            return []

    def get_expired_invites(self) -> List[InviteCode]:
        """만료된 초대 코드 목록"""
        try:
            return self.db_session.query(InviteCode).filter(
                and_(
                    InviteCode.expires_at < datetime.utcnow(),
                    InviteCode.is_used == False
                )
            ).all()
        except Exception as e:
            logger.error(f"Error getting expired invites: {e}")
            return []

    def cleanup_expired_invites(self) -> int:
        """만료된 초대 코드 정리"""
        try:
            expired_count = self.db_session.query(InviteCode).filter(
                and_(
                    InviteCode.expires_at < datetime.utcnow(),
                    InviteCode.is_used == False
                )
            ).update({"is_used": True})
            
            self.db_session.commit()
            logger.info(f"Cleaned up {expired_count} expired invite codes")
            return expired_count
        except Exception as e:
            logger.error(f"Error cleaning up expired invites: {e}")
            self.db_session.rollback()
            return 0

    # === 통계 메서드 ===
    
    def get_invite_stats(self) -> Dict[str, Any]:
        """초대 코드 통계"""
        try:
            total = self.db_session.query(func.count(InviteCode.id)).scalar() or 0
            used = self.db_session.query(func.count(InviteCode.id)).filter(
                InviteCode.is_used == True
            ).scalar() or 0
            expired = self.db_session.query(func.count(InviteCode.id)).filter(
                and_(
                    InviteCode.expires_at < datetime.utcnow(),
                    InviteCode.is_used == False
                )
            ).scalar() or 0
            active = total - used - expired

            return {
                "total_codes": total,
                "used_codes": used,
                "expired_codes": expired,
                "active_codes": active,
                "usage_rate": round((used / total * 100) if total > 0 else 0, 2)
            }
        except Exception as e:
            logger.error(f"Error getting invite stats: {e}")
            return {}


class SessionRepository(BaseRepository[UserSession]):
    """사용자 세션 관리 Repository"""

    def __init__(self, db_session: Session):
        super().__init__(UserSession, db_session)

    def create_session(self, user_id: int, token: str, expires_at: datetime) -> Optional[UserSession]:
        """새 세션 생성"""
        try:
            session_data = {
                "user_id": user_id,
                "token": token,
                "created_at": datetime.utcnow(),
                "expires_at": expires_at,
                "is_active": True
            }
            
            session = self.create(session_data)
            if session:
                logger.info(f"Created session for user_id {user_id}")
            
            return session
        except Exception as e:
            logger.error(f"Error creating session for user_id {user_id}: {e}")
            return None

    def get_by_token(self, token: str) -> Optional[UserSession]:
        """토큰으로 세션 조회"""
        try:
            return self.db_session.query(UserSession).filter(
                and_(
                    UserSession.token == token,
                    UserSession.is_active == True,
                    UserSession.expires_at > datetime.utcnow()
                )
            ).first()
        except Exception as e:
            logger.error(f"Error getting session by token: {e}")
            return None

    def invalidate_session(self, token: str) -> bool:
        """세션 무효화"""
        try:
            session = self.db_session.query(UserSession).filter(
                UserSession.token == token
            ).first()
            
            if session:
                session.is_active = False
                self.db_session.commit()
                logger.info(f"Session invalidated for user_id {session.user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error invalidating session: {e}")
            self.db_session.rollback()
            return False

    def cleanup_expired_sessions(self) -> int:
        """만료된 세션 정리"""
        try:
            expired_count = self.db_session.query(UserSession).filter(
                UserSession.expires_at < datetime.utcnow()
            ).update({"is_active": False})
            
            self.db_session.commit()
            logger.info(f"Cleaned up {expired_count} expired sessions")
            return expired_count
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
            self.db_session.rollback()
            return 0
