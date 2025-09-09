"""인증 관련 의존성 모듈"""
import logging
import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.orm import Session

from .database import get_db
from .services.auth_service import AuthService
from .models.auth_models import User
from .core.logging import user_id_ctx  # contextvar for structured logging
from jose import jwt

# 로깅 설정
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# 콘솔 로그 핸들러 설정
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """현재 인증된 사용자 정보 반환"""
    try:
        token = credentials.credentials
        token_data = AuthService.verify_token(token, db=db)
        user = db.query(User).filter(User.id == token_data.user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        try:
            user_id_ctx.set(str(user.id))
        except Exception:
            pass
        return user

    except HTTPException as e:
        # 보안 강화를 위해 기본적으로 서명 미검증 폴백을 사용하지 않습니다.
        # 필요 시 개발/테스트 환경에서만 ALLOW_UNVERIFIED_DEP_FALLBACK=1 설정으로 허용하세요.
        allow_unverified = os.getenv("ALLOW_UNVERIFIED_DEP_FALLBACK", "0") == "1"
        if allow_unverified:
            try:
                claims = jwt.get_unverified_claims(credentials.credentials)
                uid = claims.get("user_id")
                if uid is not None:
                    user = db.query(User).filter(User.id == uid).first()
                    if user:
                        try:
                            user_id_ctx.set(str(user.id))
                        except Exception:
                            pass
                        return user
            except Exception:
                pass
        # 폴백 비활성화 또는 실패 시 원래 예외 전파
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}"
        )

async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """현재 인증된 관리자 정보 반환"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

def require_min_rank(required_rank: str):
    """Dependency factory that ensures the current user has at least the required rank.

    Usage:
        @router.get("/vip-only")
        async def vip_only(current_user = Depends(require_min_rank("VIP"))):
            return {"ok": True}
    """
    async def _dep(current_user: User = Depends(get_current_user)) -> User:
        user_rank = getattr(current_user, "user_rank", None) or getattr(current_user, "rank", "STANDARD")
        # Normalize to str
        user_rank_str = str(user_rank)
        if not AuthService.check_rank_access(user_rank_str, required_rank):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient rank: requires {required_rank}"
            )
        return current_user
    return _dep
