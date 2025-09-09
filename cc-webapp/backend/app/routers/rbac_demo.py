"""Minimal RBAC demo endpoints for tests."""
from fastapi import APIRouter, Depends
from app.dependencies import require_min_rank

router = APIRouter(prefix="/api/rbac", tags=["RBAC Demo"])

@router.get("/premium")
async def premium_only(current_user = Depends(require_min_rank("PREMIUM"))):
    return {"ok": True, "required": "PREMIUM"}

@router.get("/vip")
async def vip_only(current_user = Depends(require_min_rank("VIP"))):
    return {"ok": True, "required": "VIP"}
