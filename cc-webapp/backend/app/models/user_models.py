"""사용자 세분화 및 프로필 관련 추가 모델"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base

class UserSegment(Base):
    """사용자 세그먼트 모델"""
    __tablename__ = "user_segments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    rfm_group = Column(String(50), index=True)  # e.g., Whale, High Engaged, Medium, Low/At-risk
    name = Column(String(50), nullable=True)    # 테스트 코드가 name= 전달; rfm_group 별칭
    ltv_score = Column(Float, default=0.0)
    risk_profile = Column(String(50))  # e.g., High-Risk, Medium-Risk, Low-Risk
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # User 모델과의 관계 설정
    user = relationship("User", back_populates="segment")


class VIPAccessLog(Base):
    """VIP 콘텐츠 접근 로그 모델"""
    __tablename__ = "vip_access_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("adult_contents.id"), nullable=False)
    accessed_at = Column(DateTime, default=datetime.utcnow)
