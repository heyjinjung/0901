from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    event_type = Column(String, nullable=False)  # 'daily', 'weekly', 'special'
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    rewards = Column(JSON)  # {gold: 1000, gems: 10, items: [...]}
    requirements = Column(JSON)  # {min_level: 5, games_played: 10}
    image_url = Column(String)
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    participations = relationship("EventParticipation", back_populates="event")

class EventParticipation(Base):
    __tablename__ = "event_participations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    event_id = Column(Integer, ForeignKey("events.id"), index=True)
    progress = Column(JSON, default={})  # 진행 상황 저장
    completed = Column(Boolean, default=False)
    claimed_rewards = Column(Boolean, default=False)
    joined_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    # 새 메타 필드 (Alembic에서 조건부 추가):
    # progress_version: 클라이언트 레이스 방지를 위한 단조 증가 버전
    # last_progress_at: 마지막 진행 갱신 UTC
    progress_version = Column(Integer, default=0)  # 안전: 컬럼 없으면 Alembic이 추가
    last_progress_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="event_participations")
    event = relationship("Event", back_populates="participations")

class Mission(Base):
    __tablename__ = "missions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    mission_type = Column(String, nullable=False)  # 'daily', 'weekly', 'achievement'
    category = Column(String)  # 'game', 'social', 'collection', 'spending'
    target_value = Column(Integer, nullable=False)  # 목표값
    target_type = Column(String, nullable=False)  # 'play_count', 'win_count', 'spend_gold'
    rewards = Column(JSON)  # {gold: 500, exp: 100}
    requirements = Column(JSON)  # {min_level: 1}
    reset_period = Column(String)  # 'daily', 'weekly', 'never'
    icon = Column(String)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user_missions = relationship("UserMission", back_populates="mission")

class UserMission(Base):
    __tablename__ = "user_missions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    mission_id = Column(Integer, ForeignKey("missions.id"), index=True)
    current_progress = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    claimed = Column(Boolean, default=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    claimed_at = Column(DateTime)
    reset_at = Column(DateTime)  # 리셋 예정 시간
    progress_version = Column(Integer, default=0)
    last_progress_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="missions")
    mission = relationship("Mission", back_populates="user_missions")