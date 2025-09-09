from __future__ import annotations
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from ..database import Base

class FollowRelation(Base):
    __tablename__ = "follow_relations"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "target_user_id", name="uq_follow_user_target"),
    )

    user = relationship("User", foreign_keys=[user_id], backref="following")
    target_user = relationship("User", foreign_keys=[target_user_id], backref="followers")
