"""토큰 블랙리스트 모델"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class TokenBlacklist(Base):
    """만료되거나 무효화된 토큰을 저장하는 모델"""
    __tablename__ = "token_blacklist"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(255), unique=True, nullable=False, index=True)
    jti = Column(String(36), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    blacklisted_at = Column(DateTime, default=datetime.utcnow)
    blacklisted_by = Column(Integer, ForeignKey("users.id"))
    reason = Column(String(100))
    
    # 관계 정의
    user = relationship("User", foreign_keys=[blacklisted_by])
