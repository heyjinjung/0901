from __future__ import annotations
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ActionCreate(BaseModel):
    user_id: int
    action_type: str = Field(..., min_length=1, max_length=50)
    context: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None


class ActionBatchCreate(BaseModel):
    actions: List[ActionCreate]


class ActionResponse(BaseModel):
    id: int
    user_id: int
    action_type: str
    action_data: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
