"""Service layer for admin content persistence.

Thin abstraction over SQLAlchemy sessions so routers remain skinny and testable.
"""
from __future__ import annotations

from datetime import datetime
from typing import Sequence, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete

from ..models import (
    AdminEvent,
    MissionTemplate,
    EventMissionLink,
    RewardCatalog,
    RewardAudit,
)


class AdminEventService:
    def __init__(self, db: Session):
        self.db = db

    def list(self) -> Sequence[AdminEvent]:
        return self.db.scalars(select(AdminEvent).order_by(AdminEvent.id.desc())).all()

    def create(self, **data) -> AdminEvent:
        obj = AdminEvent(**data)
        self.db.add(obj)
        self.db.flush()
        return obj

    def get(self, event_id: int) -> Optional[AdminEvent]:
        return self.db.get(AdminEvent, event_id)

    def update(self, event_id: int, **data) -> Optional[AdminEvent]:
        obj = self.get(event_id)
        if not obj:
            return None
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.flush()
        return obj

    def delete(self, event_id: int) -> bool:
        obj = self.get(event_id)
        if not obj:
            return False
        self.db.delete(obj)
        return True


class MissionTemplateService:
    def __init__(self, db: Session):
        self.db = db

    def list(self) -> Sequence[MissionTemplate]:
        return self.db.scalars(select(MissionTemplate).order_by(MissionTemplate.id.desc())).all()

    def create(self, **data) -> MissionTemplate:
        obj = MissionTemplate(**data)
        self.db.add(obj)
        self.db.flush()
        return obj

    def get(self, pk: int) -> Optional[MissionTemplate]:
        return self.db.get(MissionTemplate, pk)

    def update(self, pk: int, **data) -> Optional[MissionTemplate]:
        obj = self.get(pk)
        if not obj:
            return None
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.flush()
        return obj

    def delete(self, pk: int) -> bool:
        obj = self.get(pk)
        if not obj:
            return False
        self.db.delete(obj)
        return True


class RewardCatalogService:
    def __init__(self, db: Session):
        self.db = db

    def list(self) -> Sequence[RewardCatalog]:
        return self.db.scalars(select(RewardCatalog).order_by(RewardCatalog.id.desc())).all()

    def create(self, **data) -> RewardCatalog:
        obj = RewardCatalog(**data)
        self.db.add(obj)
        self.db.flush()
        return obj

    def get(self, pk: int) -> Optional[RewardCatalog]:
        return self.db.get(RewardCatalog, pk)

    def update(self, pk: int, **data) -> Optional[RewardCatalog]:
        obj = self.get(pk)
        if not obj:
            return None
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.flush()
        return obj

    def toggle_active(self, pk: int, active: bool) -> Optional[RewardCatalog]:
        obj = self.get(pk)
        if not obj:
            return None
        obj.active = active
        self.db.flush()
        return obj

    def delete(self, pk: int) -> bool:
        obj = self.get(pk)
        if not obj:
            return False
        self.db.delete(obj)
        return True


class RewardAuditService:
    def __init__(self, db: Session):
        self.db = db

    def record(self, **data) -> RewardAudit:
        obj = RewardAudit(**data)
        self.db.add(obj)
        self.db.flush()
        return obj

    def list(self, user_id: Optional[int] = None, limit: int = 100) -> Sequence[RewardAudit]:
        stmt = select(RewardAudit).order_by(RewardAudit.id.desc()).limit(limit)
        if user_id is not None:
            stmt = stmt.where(RewardAudit.user_id == user_id)
        return self.db.scalars(stmt).all()
