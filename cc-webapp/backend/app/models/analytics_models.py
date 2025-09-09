"""분석 관련 데이터베이스 모델"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship

from ..database import Base


class SiteVisit(Base):
    """사이트 방문 모델"""
    __tablename__ = "site_visits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class UserAnalytics(Base):
    """사용자 분석 모델"""
    __tablename__ = "user_analytics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_type = Column(String(50), nullable=False)
    event_data = Column(JSON)
    session_id = Column(String(100))
    page_url = Column(String(500))
    referrer = Column(String(500))
    user_agent = Column(Text)
    ip_address = Column(String(45))
    device_type = Column(String(50))
    os_type = Column(String(50))
    browser_type = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    user = relationship("User")


class PageView(Base):
    """페이지 조회 모델"""
    __tablename__ = "page_views"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    session_id = Column(String(100), nullable=False)
    page_url = Column(String(500), nullable=False)
    page_title = Column(String(200))
    referrer = Column(String(500))
    load_time = Column(Float)  # 페이지 로드 시간 (초)
    stay_duration = Column(Integer)  # 체류 시간 (초)
    scroll_depth = Column(Float)  # 스크롤 깊이 (%)
    user_agent = Column(Text)
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    user = relationship("User")


class ConversionEvent(Base):
    """전환 이벤트 모델"""
    __tablename__ = "conversion_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_name = Column(String(100), nullable=False)
    conversion_value = Column(Float, default=0.0)
    currency = Column(String(3), default="USD")
    event_data = Column(JSON)
    campaign_id = Column(String(100))
    source = Column(String(100))
    medium = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    user = relationship("User")




class ABTestParticipant(Base):
    """A/B 테스트 참가자 모델"""
    __tablename__ = "ab_test_participants"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    test_name = Column(String(100), nullable=False)
    variant = Column(String(50), nullable=False)  # A, B, C 등
    assigned_at = Column(DateTime, default=datetime.utcnow)
    converted_at = Column(DateTime)
    conversion_value = Column(Float)
    
    # 관계
    user = relationship("User")


class CustomEvent(Base):
    """커스텀 이벤트 모델"""
    __tablename__ = "custom_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    event_name = Column(String(100), nullable=False)
    properties = Column(JSON)
    session_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    user = relationship("User")
