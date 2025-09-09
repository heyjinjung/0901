"""
📢 Casino-Club F2P - 알림 모델
============================
알림 시스템 데이터베이스 모델
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from ..database import Base


class Notification(Base):
    """알림 모델"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), default="info")  # info, warning, success, error
    is_read = Column(Boolean, default=False)
    is_sent = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    read_at = Column(DateTime(timezone=True))
    
    # 관계
    user = relationship("User", back_populates="notifications")


class NotificationCampaign(Base):
    """알림/캠페인 스케줄 모델

    - targeting_type: 'all' | 'segment' | 'user_ids'
    - target_segment: 세그먼트 라벨 (segment 선택 시)
    - user_ids: 콤마로 구분된 대상 유저 ID 목록 (user_ids 선택 시)
    - scheduled_at: 예약 발송 시간 (UTC)
    - status: 'scheduled' | 'sent' | 'cancelled'
    """
    __tablename__ = "notification_campaigns"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    targeting_type = Column(String(20), nullable=False, default="all")
    target_segment = Column(String(50))
    user_ids = Column(Text)
    scheduled_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    sent_at = Column(DateTime(timezone=True))
    status = Column(String(20), nullable=False, default="scheduled")
