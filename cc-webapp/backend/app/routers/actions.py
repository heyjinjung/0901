import os
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.core.config import settings

try:
    from kafka import KafkaProducer
    _producer = None
    def get_producer():
        global _producer
        if _producer is None and settings.KAFKA_ENABLED:
            _producer = KafkaProducer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS.split(","),
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
        return _producer
except Exception:
    def get_producer(): return None

from .. import models
from ..database import get_db
from ..realtime.hub import hub

router = APIRouter(prefix="/api/actions", tags=["Game Actions"])


class ActionCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    action_type: str = Field(..., examples=["SLOT_SPIN", "GACHA_SPIN", "LOGIN", "REWARD_GRANT"])
    context: Optional[Dict[str, Any]] = None
    client_ts: Optional[str] = None


class ActionLoggedResponse(BaseModel):
    id: int
    user_id: int
    action_type: str
    created_at: datetime


PII_KEYS = {"password", "phone", "phone_number", "email"}


def _scrub_context(ctx: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not ctx:
        return {}
    scrubbed = {}
    for k, v in ctx.items():
        if k.lower() in PII_KEYS:
            continue
        scrubbed[k] = v
    return scrubbed


@router.post("", response_model=ActionLoggedResponse)
async def log_action(action: ActionCreate, db=Depends(get_db)):
    now = datetime.now(timezone.utc)
    payload = {
        "user_id": action.user_id,
        "action_type": action.action_type,
        "client_ts": action.client_ts,
        "context": _scrub_context(action.context),
        "server_ts": now.isoformat().replace("+00:00", "Z"),
    }

    # persist to DB (Text column for action_data)
    db_row = models.UserAction(
        user_id=action.user_id,
        action_type=action.action_type,
        action_data=json.dumps(payload, ensure_ascii=False),
        created_at=now,
    )
    db.add(db_row)
    db.commit()
    db.refresh(db_row)

    # fire-and-forget to Kafka if enabled
    prod = get_producer()
    if prod is not None:
        try:
            prod.send(settings.KAFKA_ACTIONS_TOPIC, payload)
        except Exception as e:
            print(f"Kafka produce failed: {e}")

    # realtime fanout via unified hub (personal)
    try:
        await hub.broadcast({
            "type": "user_action",
            "user_id": action.user_id,
            "data": payload,
        })
    except Exception:
        # 비차단 안전 실패
        pass

    return ActionLoggedResponse(
        id=db_row.id,
        user_id=db_row.user_id,
        action_type=db_row.action_type,
        created_at=db_row.created_at,
    )


class BulkActions(BaseModel):
    items: List[ActionCreate]


@router.post("/bulk", response_model=dict)
async def log_actions_bulk(batch: BulkActions, db=Depends(get_db)):
    now = datetime.now(timezone.utc)
    rows: List[models.UserAction] = []
    prod = get_producer()
    for item in batch.items:
        payload = {
            "user_id": item.user_id,
            "action_type": item.action_type,
            "client_ts": item.client_ts,
            "context": _scrub_context(item.context),
            "server_ts": now.isoformat().replace("+00:00", "Z"),
        }
        rows.append(
            models.UserAction(
                user_id=item.user_id,
                action_type=item.action_type,
                action_data=json.dumps(payload, ensure_ascii=False),
                created_at=now,
            )
        )
        if prod is not None:
            try:
                prod.send(settings.KAFKA_ACTIONS_TOPIC, payload)
            except Exception:
                pass
    if rows:
        db.add_all(rows)
        db.commit()
    # optional Kafka flush is skipped to avoid blocking
    return {"logged": len(rows)}


class ActionItem(BaseModel):
    id: int
    action_type: str
    created_at: datetime
    action_data: Dict[str, Any]


@router.get("/recent/{user_id}", response_model=List[ActionItem])
async def recent_actions(user_id: int, limit: int = 20, db=Depends(get_db)):
    q = (
        db.query(models.UserAction)
        .filter(models.UserAction.user_id == user_id)
        .order_by(models.UserAction.created_at.desc())
        .limit(max(1, min(200, limit)))
        .all()
    )
    out: List[ActionItem] = []
    for r in q:
        try:
            data = json.loads(r.action_data or "{}")
        except Exception:
            data = {}
        out.append(
            ActionItem(id=r.id, action_type=r.action_type, created_at=r.created_at, action_data=data)
        )
    return out

# Ensure this router is included in app/main.py:
# from .routers import actions
# app.include_router(actions.router, prefix="/api", tags=["actions"])
