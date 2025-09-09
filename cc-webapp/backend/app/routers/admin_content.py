"""Admin 콘텐츠 관리 라우터 (DB 영속화 버전)

기능:
- 이벤트 CRUD + 활성/비활성 토글
- 미션 템플릿 CRUD (daily|weekly|event)
- 리워드 카탈로그 CRUD + 활성/비활성 토글
- 리워드 감사 로그 조회 (기본 목록)

이전 in-memory 구현을 DB persistence + service layer 로 대체.
"""
from datetime import datetime
from typing import Optional, List, Sequence

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.admin_content_service import (
    AdminEventService,
    MissionTemplateService,
    RewardCatalogService,
    RewardAuditService,
)
from ..models import AdminEvent, MissionTemplate, RewardCatalog, RewardAudit
from ..dependencies import get_current_user
from ..models.auth_models import User

router = APIRouter(prefix="/api/admin/content", tags=["Admin Content"])


# --- 권한 의존성 ---
def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=403, detail="관리자 권한 필요")
    return current_user


# --- 공통 스키마 ---
class EventBase(BaseModel):
    name: str
    start_at: datetime
    end_at: datetime
    reward_scheme: dict = Field(default_factory=dict)


class EventCreate(EventBase):
    pass


class EventUpdate(BaseModel):
    name: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    reward_scheme: Optional[dict] = None
    missions: Optional[List[int]] = None


class EventResponse(EventBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class MissionTemplateBase(BaseModel):
    title: str
    mission_type: str = Field(pattern="^(daily|weekly|event)$")
    target: int = 1
    reward: dict = Field(default_factory=dict)


class MissionTemplateCreate(MissionTemplateBase):
    pass


class MissionTemplateUpdate(BaseModel):
    title: Optional[str] = None
    mission_type: Optional[str] = Field(default=None, pattern="^(daily|weekly|event)$")
    target: Optional[int] = None
    reward: Optional[dict] = None


class MissionTemplateResponse(MissionTemplateBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class RewardCatalogBase(BaseModel):
    code: str
    reward_type: str
    amount: int
    metadata: Optional[dict] = Field(default_factory=dict, alias="meta")


class RewardCatalogCreate(RewardCatalogBase):
    pass


class RewardCatalogUpdate(BaseModel):
    reward_type: Optional[str] = None
    amount: Optional[int] = None
    metadata: Optional[dict] = Field(default=None, alias="meta")


class RewardCatalogItem(RewardCatalogBase):
    id: int
    active: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class RewardAuditItem(BaseModel):
    id: int
    user_id: Optional[int] = None
    reward_type: str
    amount: int
    source: Optional[str] = None
    event_id: Optional[int] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


def _event_service(db: Session) -> AdminEventService:
    return AdminEventService(db)


def _mission_service(db: Session) -> MissionTemplateService:
    return MissionTemplateService(db)


def _reward_catalog_service(db: Session) -> RewardCatalogService:
    return RewardCatalogService(db)


def _reward_audit_service(db: Session) -> RewardAuditService:
    return RewardAuditService(db)


# --- 이벤트 CRUD ---
@router.post("/events", response_model=EventResponse)
def create_event(body: EventCreate, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    svc = _event_service(db)
    obj = svc.create(**body.model_dump())
    return obj


@router.get("/events", response_model=List[EventResponse])
def list_events(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    svc = _event_service(db)
    return list(svc.list())


@router.get("/events/{event_id}", response_model=EventResponse)
def get_event(event_id: int = Path(..., ge=1), _: User = Depends(require_admin), db: Session = Depends(get_db)):
    svc = _event_service(db)
    obj = svc.get(event_id)
    if not obj:
        raise HTTPException(status_code=404, detail="이벤트 없음")
    return obj


@router.put("/events/{event_id}", response_model=EventResponse)
def update_event(event_id: int, body: EventUpdate, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    svc = _event_service(db)
    obj = svc.update(event_id, **body.model_dump(exclude_unset=True))
    if not obj:
        raise HTTPException(status_code=404, detail="이벤트 없음")
    return obj


@router.delete("/events/{event_id}")
def delete_event(event_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    svc = _event_service(db)
    ok = svc.delete(event_id)
    if not ok:
        raise HTTPException(status_code=404, detail="이벤트 없음")
    return {"ok": True}


@router.post("/events/{event_id}/activate")
def activate_event(event_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    svc = _event_service(db)
    obj = svc.update(event_id, is_active=True)
    if not obj:
        raise HTTPException(status_code=404, detail="이벤트 없음")
    return {"ok": True, "is_active": True}


@router.post("/events/{event_id}/deactivate")
def deactivate_event(event_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    svc = _event_service(db)
    obj = svc.update(event_id, is_active=False)
    if not obj:
        raise HTTPException(status_code=404, detail="이벤트 없음")
    return {"ok": True, "is_active": False}


# --- 미션 템플릿 CRUD ---
@router.post("/missions/templates", response_model=MissionTemplateResponse)
def create_mission_template(body: MissionTemplateCreate, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    svc = _mission_service(db)
    obj = svc.create(**body.model_dump())
    return obj


@router.get("/missions/templates", response_model=List[MissionTemplateResponse])
def list_mission_templates(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    svc = _mission_service(db)
    return list(svc.list())


@router.put("/missions/templates/{template_id}", response_model=MissionTemplateResponse)
def update_mission_template(template_id: int, body: MissionTemplateUpdate, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    svc = _mission_service(db)
    obj = svc.update(template_id, **body.model_dump(exclude_unset=True))
    if not obj:
        raise HTTPException(status_code=404, detail="미션 템플릿 없음")
    return obj


@router.delete("/missions/templates/{template_id}")
def delete_mission_template(template_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    svc = _mission_service(db)
    ok = svc.delete(template_id)
    if not ok:
        raise HTTPException(status_code=404, detail="미션 템플릿 없음")
    return {"ok": True}


# --- 리워드 카탈로그 CRUD ---
@router.post("/rewards/catalog", response_model=RewardCatalogItem)
def create_reward_catalog(body: RewardCatalogCreate, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    svc = _reward_catalog_service(db)
    obj = svc.create(**body.model_dump())
    return obj


@router.get("/rewards/catalog", response_model=List[RewardCatalogItem])
def list_reward_catalog(_: User = Depends(require_admin), db: Session = Depends(get_db)):
    svc = _reward_catalog_service(db)
    return list(svc.list())


@router.put("/rewards/catalog/{reward_id}", response_model=RewardCatalogItem)
def update_reward_catalog(reward_id: int, body: RewardCatalogUpdate, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    svc = _reward_catalog_service(db)
    obj = svc.update(reward_id, **body.model_dump(exclude_unset=True))
    if not obj:
        raise HTTPException(status_code=404, detail="리워드 항목 없음")
    return obj


@router.delete("/rewards/catalog/{reward_id}")
def delete_reward_catalog(reward_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    svc = _reward_catalog_service(db)
    ok = svc.delete(reward_id)
    if not ok:
        raise HTTPException(status_code=404, detail="리워드 항목 없음")
    return {"ok": True}


@router.post("/rewards/catalog/{reward_id}/activate")
def activate_reward(reward_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    svc = _reward_catalog_service(db)
    obj = svc.toggle_active(reward_id, True)
    if not obj:
        raise HTTPException(status_code=404, detail="리워드 항목 없음")
    return {"ok": True, "active": True}


@router.post("/rewards/catalog/{reward_id}/deactivate")
def deactivate_reward(reward_id: int, _: User = Depends(require_admin), db: Session = Depends(get_db)):
    svc = _reward_catalog_service(db)
    obj = svc.toggle_active(reward_id, False)
    if not obj:
        raise HTTPException(status_code=404, detail="리워드 항목 없음")
    return {"ok": True, "active": False}


# --- 리워드 감사 조회 (샘플) ---
class RewardAuditResponse(BaseModel):
    items: List[RewardAuditItem]
    total: int
    page: int
    page_size: int


@router.get("/rewards/audit", response_model=RewardAuditResponse)
def reward_audit(
    user_id: Optional[int] = Query(None, ge=1),
    event_id: Optional[int] = Query(None, ge=1),
    source: Optional[str] = Query(None, max_length=100),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    svc = _reward_audit_service(db)
    items = svc.list(user_id=user_id, limit=page_size)
    # simple filter client-side for source/event until dedicated query composition added
    filtered: List[RewardAudit] = []
    for i in items:
        if source and i.source != source:
            continue
        if event_id and i.event_id != event_id:
            continue
        filtered.append(i)
    return RewardAuditResponse(items=filtered, total=len(filtered), page=page, page_size=page_size)

# NOTE: 미션-이벤트 연결(EventMissionLink) 관련 CRUD/배치 API 는 후속 단계에서 추가 가능.
