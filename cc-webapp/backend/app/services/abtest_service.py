

"""AB Test service.

Deterministic variant assignment for feature flags / experiments.

Features:
 - Stable hashing of (user_id, flag_key)
 - Idempotent: existing assignment returned
 - Simple even distribution across provided variants

Planned extensions (documented for future work):
 - Weighted variants
 - Time-bounded experiments (start/end)
 - Exclusion cohorts / holdouts
 - ClickHouse export pipeline
"""
from __future__ import annotations

import hashlib
from typing import Optional
from sqlalchemy.orm import Session

from .. import models


class ABTestService:
    def __init__(self, db: Session):
        self.db = db

    def _stable_hash(self, user_id: int, flag_key: str) -> int:
        raw = f"{user_id}:{flag_key}".encode()
        h = hashlib.sha256(raw).hexdigest()
        return int(h[:8], 16)  # first 32 bits

    def assign(self, user_id: int, test_name: str, variants: list[str] | tuple[str, ...]) -> models.ABTestParticipant:
        existing = self.db.query(models.ABTestParticipant).filter(
            models.ABTestParticipant.user_id == user_id,
            models.ABTestParticipant.test_name == test_name,
        ).one_or_none()
        if existing:
            return existing
        if not variants:
            raise ValueError("variants must be non-empty")
        h_val = self._stable_hash(user_id, test_name)
        variant = variants[h_val % len(variants)]
        row = models.ABTestParticipant(user_id=user_id, test_name=test_name, variant=variant)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def get(self, user_id: int, test_name: str) -> Optional[models.ABTestParticipant]:
        return self.db.query(models.ABTestParticipant).filter(
            models.ABTestParticipant.user_id == user_id,
            models.ABTestParticipant.test_name == test_name,
        ).one_or_none()
