"""
사용자 서비스 간소화 버전
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from ..models.auth_models import User

class SimpleUserService:
    """
    간소화된 사용자 서비스
    """
    
    @staticmethod
    def get_user_tokens(db: Session, user_id: int) -> int:
        """사용자 토큰 잔액 조회"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return 0
        return user.cyber_token_balance
    
    @staticmethod
    def update_user_tokens(db: Session, user_id: int, amount: int) -> int:
        """사용자 토큰 잔액 업데이트"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return 0
        
        # 잔액 업데이트
        user.cyber_token_balance += amount
        
        # 마이너스 방지
        if user.cyber_token_balance < 0:
            user.cyber_token_balance = 0
            
        db.commit()
        return user.cyber_token_balance
    
    @staticmethod
    def get_user_profile(db: Session, user_id: int) -> Dict[str, Any]:
        """사용자 프로필 정보 조회"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {}
            
        return {
            "id": user.id,
            "site_id": user.site_id,
            "nickname": user.nickname,
            "cyber_token_balance": user.cyber_token_balance,
            "is_active": user.is_active
        }
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """사용자 조회"""
        return db.query(User).filter(User.id == user_id).first()
