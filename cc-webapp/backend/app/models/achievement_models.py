from __future__ import annotations

from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import String, Integer, DateTime, Boolean, JSON, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    # condition JSON example: {"type": "CUMULATIVE_BET", "game_type": "SLOT", "threshold": 1000}
    condition: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    reward_coins: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # 기존 reward_gems -> reward_gold 전환
    reward_gold: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    icon: Mapped[Optional[str]] = mapped_column(String(80))
    badge_color: Mapped[Optional[str]] = mapped_column(String(32))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user_achievements: Mapped[list["UserAchievement"]] = relationship("UserAchievement", back_populates="achievement", cascade="all,delete-orphan")

    __table_args__ = (
        Index("ix_achievements_active", "is_active"),
    )


class UserAchievement(Base):
    __tablename__ = "user_achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    achievement_id: Mapped[int] = mapped_column(Integer, ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False)
    unlocked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    progress_value: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_unlocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    achievement: Mapped[Achievement] = relationship("Achievement", back_populates="user_achievements")

    __table_args__ = (
        UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement_user_achievement"),
        Index("ix_user_achievements_unlocked", "is_unlocked"),
    )
