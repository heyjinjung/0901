from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base

class Mission(Base):
    __tablename__ = "missions"
    __table_args__ = {'extend_existing': True}  # 이 줄 추가

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    mission_type = Column(String) # e.g., 'DAILY', 'WEEKLY', 'ACHIEVEMENT'
    target_action = Column(String) # e.g., 'SLOT_SPIN', 'RPS_WIN'
    target_count = Column(Integer, nullable=False)
    reward_type = Column(String, nullable=False)
    reward_amount = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)

class UserMissionProgress(Base):
    __tablename__ = "user_mission_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mission_id = Column(Integer, ForeignKey("missions.id"), nullable=False)
    current_count = Column(Integer, default=0)
    is_completed = Column(Boolean, default=False)
    is_claimed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    claimed_at = Column(DateTime, nullable=True)

    user = relationship("User")
    mission = relationship("Mission")
