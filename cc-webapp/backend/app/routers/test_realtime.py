from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, Optional
from app.core.config import settings
from app.dependencies import get_current_user
from app.models.auth_models import User
from .realtime import (
    broadcast_profile_update,
    broadcast_reward_granted,
    broadcast_purchase_update,
    broadcast_stats_update,
)


router = APIRouter(prefix="/api/test/realtime", tags=["test"], include_in_schema=False)


def _dev_only_guard():
    if settings.ENVIRONMENT not in ("development", "local", "dev", "test"):
        raise HTTPException(status_code=403, detail="development only")


class ProfileUpdateBody(BaseModel):
    changes: Dict[str, Any]


@router.post("/emit/profile_update")
async def emit_profile_update(body: ProfileUpdateBody, current_user: User = Depends(get_current_user)):
    _dev_only_guard()
    await broadcast_profile_update(int(current_user.id), body.changes)
    return {"ok": True}


class RewardGrantedBody(BaseModel):
    reward_type: str
    amount: int
    balance_after: Optional[int] = None


@router.post("/emit/reward_granted")
async def emit_reward_granted(body: RewardGrantedBody, current_user: User = Depends(get_current_user)):
    _dev_only_guard()
    await broadcast_reward_granted(int(current_user.id), body.reward_type, body.amount, body.balance_after or 0)
    return {"ok": True}


class PurchaseUpdateBody(BaseModel):
    status: str
    product_id: Optional[str] = None
    receipt_code: Optional[str] = None
    reason_code: Optional[str] = None
    amount: Optional[int] = None


@router.post("/emit/purchase_update")
async def emit_purchase_update(body: PurchaseUpdateBody, current_user: User = Depends(get_current_user)):
    _dev_only_guard()
    await broadcast_purchase_update(
        int(current_user.id),
        status=body.status,
        product_id=body.product_id,
        receipt_code=body.receipt_code,
        reason_code=body.reason_code,
        amount=body.amount,
    )
    return {"ok": True}


class StatsUpdateBody(BaseModel):
    stats: Dict[str, Any]


@router.post("/emit/stats_update")
async def emit_stats_update(body: StatsUpdateBody, current_user: User = Depends(get_current_user)):
    _dev_only_guard()
    await broadcast_stats_update(int(current_user.id), body.stats)
    return {"ok": True}
