from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from typing import List

from ..dependencies import get_db
from .. import models
from ..services.abtest_service import ABTestService

router = APIRouter(prefix="/api/abtest", tags=["abtest"])


class AssignmentRequest(BaseModel):
    test_name: str
    variants: List[str] = ["A", "B"]


class AssignmentResponse(BaseModel):
    user_id: int
    test_name: str
    variant: str

    @classmethod
    def from_model(cls, m: models.ABTestParticipant) -> "AssignmentResponse":
        return cls(user_id=m.user_id, test_name=m.test_name, variant=m.variant)


@router.post("/assign", response_model=AssignmentResponse)
def assign_variant(req: AssignmentRequest, user_id: int = Query(..., description="User ID"), db=Depends(get_db)):
    svc = ABTestService(db)
    row = svc.assign(user_id=user_id, test_name=req.test_name, variants=req.variants)
    return AssignmentResponse.from_model(row)


@router.get("/variant", response_model=AssignmentResponse)
def get_variant(test_name: str, user_id: int = Query(..., description="User ID"), db=Depends(get_db)):
    svc = ABTestService(db)
    row = svc.get(user_id=user_id, test_name=test_name)
    if not row:
        row = svc.assign(user_id=user_id, test_name=test_name, variants=["A", "B"])
    return AssignmentResponse.from_model(row)
