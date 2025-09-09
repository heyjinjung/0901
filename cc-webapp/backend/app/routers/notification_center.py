"""Notification Center REST API

Provides endpoints for listing notifications and marking them read/unread.
"""
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models.auth_models import User
from .. import models
from ..services.notification_service import NotificationService
from ..utils.redis import RedisManager
from ..core.config import settings

router = APIRouter(prefix="/api/notification", tags=["Notification Center"])


def get_service(db: Session = Depends(get_db)) -> NotificationService:
    return NotificationService(db)


class NotificationItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: Optional[str] = None
    message: str
    notification_type: Optional[str] = "info"
    is_read: bool
    created_at: Optional[str] = None
    read_at: Optional[str] = None


class NotificationListResponse(BaseModel):
    items: List[NotificationItem]
    total: int
    unread: int


# ----------------------
# Settings (minimal v1)
# ----------------------
class NotificationSettings(BaseModel):
    toastEnabled: bool = True
    types: dict = {"reward": True, "event": True, "system": True, "shop": True}
    sound: bool = False
    dnd: dict = {"enabled": False, "start": "22:00", "end": "07:00"}


def _settings_key(user_id: int) -> str:
    return f"user:{user_id}:notification:settings"


@router.get("/list", response_model=NotificationListResponse)
async def list_notifications(
    only_unread: bool = Query(False),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    type: Optional[str] = Query(None, alias="notification_type"),
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_service),
):
    items, total = service.list_notifications(
        user_id=current_user.id,
        limit=limit,
        offset=offset,
        only_unread=only_unread,
        notification_type=type,
    )
    return NotificationListResponse(
        items=[NotificationItem.model_validate(n) for n in items],
        total=total,
        unread=service.unread_count(current_user.id),
    )


class MarkRequest(BaseModel):
    read: bool = True


@router.post("/{notification_id}/read")
async def mark_read(
    notification_id: int,
    body: MarkRequest,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_service),
):
    n = service.mark_as_read(current_user.id, notification_id, read=body.read)
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"ok": True, "is_read": bool(n.is_read)}


@router.post("/read-all")
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_service),
):
    count = service.mark_all_as_read(current_user.id)
    return {"ok": True, "updated": count}


@router.get("/unread-count")
async def unread_count(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_service),
):
    return {"count": service.unread_count(current_user.id)}


@router.get("/settings/auth", response_model=NotificationSettings)
async def get_settings_auth(
    current_user: User = Depends(get_current_user),
):
    rm = RedisManager()
    key = _settings_key(current_user.id)
    data = rm.get_cached_data(key)
    if isinstance(data, dict) and data:
        # Redis에 저장된 구조를 그대로 반환
        try:
            return NotificationSettings(**data)
        except Exception:
            pass
    return NotificationSettings()


@router.put("/settings/auth", response_model=NotificationSettings)
async def put_settings_auth(
    body: NotificationSettings,
    current_user: User = Depends(get_current_user),
):
    rm = RedisManager()
    key = _settings_key(current_user.id)
    rm.cache_user_data(key, body.model_dump(), expire_seconds=7 * 24 * 3600)
    return body


# ----------------------
# Web Push (skeleton)
# ----------------------
class PushSubscription(BaseModel):
    endpoint: str
    p256dh: str
    auth: str


def _push_key(user_id: int) -> str:
    return f"user:{user_id}:push:subs"


@router.post("/push/subscribe")
async def push_subscribe(
    sub: PushSubscription,
    current_user: User = Depends(get_current_user),
):
    rm = RedisManager()
    key = _push_key(current_user.id)
    existing = rm.get_cached_data(key) or {"subs": []}
    subs = existing.get("subs", [])
    # 중복 방지: endpoint 기준
    subs = [s for s in subs if s.get("endpoint") != sub.endpoint]
    subs.append(sub.model_dump())
    rm.cache_user_data(key, {"subs": subs}, expire_seconds=30 * 24 * 3600)
    return {"ok": True, "count": len(subs)}


@router.post("/push/unsubscribe")
async def push_unsubscribe(
    sub: PushSubscription,
    current_user: User = Depends(get_current_user),
):
    rm = RedisManager()
    key = _push_key(current_user.id)
    existing = rm.get_cached_data(key) or {"subs": []}
    subs = [s for s in existing.get("subs", []) if s.get("endpoint") != sub.endpoint]
    rm.cache_user_data(key, {"subs": subs}, expire_seconds=30 * 24 * 3600)
    return {"ok": True, "count": len(subs)}


@router.post("/push/test")
async def push_test(
    current_user: User = Depends(get_current_user),
):
    # 실제 Web Push 발송은 별도 서비스/키(VAPID) 필요. 여기서는 구독 유무 확인만.
    rm = RedisManager()
    key = _push_key(current_user.id)
    existing = rm.get_cached_data(key) or {"subs": []}
    return {"ok": True, "subs": existing.get("subs", [])}


@router.get("/push/vapid-public")
async def get_vapid_public_key():
    # 빈 문자열이면 프론트는 applicationServerKey 없이 구독 시도(환경에 따라 허용될 수 있음)
    return {"publicKey": settings.VAPID_PUBLIC_KEY or ""}


class PushSendRequest(BaseModel):
    user_id: int | None = None  # None이면 현재 사용자에게 발송
    title: str = "알림"
    message: str = ""
    url: str | None = None
    type: str = "info"


@router.post("/push/send")
async def push_send(
    body: PushSendRequest,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_service),
):
    # 간단 보호: admin_only 같은 더 강력한 검증은 RBAC 연동 시 대체
    if not getattr(current_user, "is_admin", False) and getattr(current_user, "role", "").lower() not in ("admin", "superadmin"):
        # 최소 보호: 관리자가 아니면 자기 자신에게만 허용
        target_user_id = body.user_id or current_user.id
        if target_user_id != current_user.id:
            raise HTTPException(status_code=403, detail="forbidden")
    else:
        target_user_id = body.user_id or current_user.id

    payload = {"title": body.title or "알림", "message": body.message or "", "url": body.url, "type": body.type or "info"}
    sent, failed, removed = service.push_to_user_subscriptions(target_user_id, payload)
    return {"ok": True, "sent": sent, "failed": failed, "removed": removed}
