"""Admin content persistence models (events / mission templates / reward catalog / reward audit).

These are intentionally minimal and separate from legacy Event / Mission models
to avoid coupling with older gameplay/event systems. They power the new
admin_content router replacing the previous in-memory stub.

Revision: added 2025-08-19 (single alembic revision for all four tables)
"""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    JSON,
    ForeignKey,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship

from ..database import Base


class AdminEvent(Base):
    __tablename__ = "admin_events"
    __table_args__ = (
        UniqueConstraint("name", name="uq_admin_events_name"),
        Index("ix_admin_events_active_window", "is_active", "start_at", "end_at"),
    )

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    start_at = Column(DateTime, nullable=False)
    end_at = Column(DateTime, nullable=False)
    reward_scheme = Column(JSON, nullable=False, default=dict)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    mission_links = relationship("EventMissionLink", back_populates="event", cascade="all, delete-orphan")


class MissionTemplate(Base):
    __tablename__ = "mission_templates"
    __table_args__ = (
        Index("ix_mission_templates_active_type", "is_active", "mission_type"),
    )

    id = Column(Integer, primary_key=True)
    title = Column(String(150), nullable=False)
    mission_type = Column(String(20), nullable=False)  # daily|weekly|event
    target = Column(Integer, nullable=False, default=1)
    reward = Column(JSON, nullable=False, default=dict)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    event_links = relationship("EventMissionLink", back_populates="mission", cascade="all, delete-orphan")


class EventMissionLink(Base):
    __tablename__ = "event_mission_links"
    __table_args__ = (
        UniqueConstraint("event_id", "mission_template_id", name="uq_event_mission_pair"),
    )

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey("admin_events.id", ondelete="CASCADE"), nullable=False, index=True)
    mission_template_id = Column(Integer, ForeignKey("mission_templates.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    event = relationship("AdminEvent", back_populates="mission_links")
    mission = relationship("MissionTemplate", back_populates="event_links")


class RewardCatalog(Base):
    __tablename__ = "reward_catalog"
    __table_args__ = (
        UniqueConstraint("code", name="uq_reward_catalog_code"),
        Index("ix_reward_catalog_active_type", "active", "reward_type"),
    )

    id = Column(Integer, primary_key=True)
    code = Column(String(80), nullable=False)
    reward_type = Column(String(50), nullable=False)
    amount = Column(Integer, nullable=False)
    meta = Column("metadata", JSON, nullable=False, default=dict)  # stored as 'metadata' column, attribute 'meta'
    active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class RewardAudit(Base):
    __tablename__ = "reward_audit"
    __table_args__ = (
        Index("ix_reward_audit_user_created", "user_id", "created_at"),
        Index("ix_reward_audit_event_created", "event_id", "created_at"),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True)
    reward_type = Column(String(50), nullable=False)
    amount = Column(Integer, nullable=False)
    source = Column(String(100), nullable=True, index=True)
    event_id = Column(Integer, ForeignKey("admin_events.id", ondelete="SET NULL"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
