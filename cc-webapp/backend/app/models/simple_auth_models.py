"""단순화된 인증 관련 데이터베이스 모델"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class User(Base):
    """사용자 모델 - 필수 필드만 포함"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(String(50), unique=True, index=True, nullable=False)  # 사이트 아이디
    nickname = Column(String(50), unique=True, nullable=False)  # 닉네임
    password_hash = Column(String(255), nullable=False)  # 비밀번호
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 필수 관계만 포함
    security_events = relationship("SecurityEvent", back_populates="user", cascade="all, delete-orphan")

class SecurityEvent(Base):
    """보안 이벤트 모델"""
    __tablename__ = "security_events"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    event_type = Column(String(50), nullable=False)  # 로그인, 비밀번호 변경 등
    ip_address = Column(String(45))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 관계
    user = relationship("User", back_populates="security_events")

class InviteCode(Base):
    """초대코드 모델"""
    __tablename__ = "invite_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, index=True, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
