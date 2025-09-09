"""Adult Content Schemas."""

from datetime import datetime
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field


class AdultContentStageBase(BaseModel):
    """Base schema for adult content stage."""
    stage: int
    requirements: Dict[str, Union[int, str]]
    rewards: Dict[str, Union[int, str]]


class AdultContentDetail(BaseModel):
    """Detailed adult content information."""
    id: int
    title: str
    description: str
    content_url: str
    type: str
    unlock_level: int
    prerequisites: List[str]
    name: Optional[str] = None
    stages: List[AdultContentStageBase] = Field(default_factory=list)
    user_current_access_level: Optional[int] = None


class AdultContentGalleryItem(BaseModel):
    """Adult content gallery item."""
    id: int
    name: str
    title: str
    description: str
    thumbnail_url: str
    preview_url: str
    content_type: str
    stage_required: str
    highest_unlocked_stage: Optional[str] = None
    is_unlocked: bool = False


class AdultContentGalleryResponse(BaseModel):
    """Adult content gallery response."""
    items: List[AdultContentGalleryItem]


class ContentStageInfo(BaseModel):
    """Content stage information."""
    stage: int
    stage_to_unlock: Optional[int] = None
    requirements: Dict[str, Union[int, str]]
    rewards: Dict[str, Union[int, str]]


class ContentUnlockRequestNew(BaseModel):
    """Content unlock request."""
    content_id: int
    stage_to_unlock: Optional[Union[int, str]] = None
    user_proof: Optional[Dict] = None


class ContentUnlockResponse(BaseModel):
    """Content unlock response."""
    success: bool
    content_url: Optional[str] = None
    message: str
    status: str
    unlocked_stage: Optional[int] = None
    tokens_spent: Optional[int] = None
    remaining_tokens: Optional[int] = None


class ContentPreviewResponse(BaseModel):
    """Content preview response."""
    id: int
    title: str
    preview_data: Dict
    unlock_requirements: Dict
    preview_url: Optional[str] = None
    current_stage_accessed: Optional[int] = None


class UnlockHistoryItem(BaseModel):
    """Unlock history item."""
    id: int
    content_id: int
    content_name: str
    unlocked_at: str
    stage_required: str


class UnlockHistoryResponse(BaseModel):
    """Unlock history response."""
    history: List[UnlockHistoryItem]


class AccessUpgradeRequest(BaseModel):
    """Access upgrade request."""
    current_level: int
    requested_level: int
    payment_token: str
    target_segment_level: Optional[int] = None
    duration_days: Optional[int] = 30


class AccessUpgradeResponse(BaseModel):
    """Access upgrade response."""
    success: bool
    new_level: int
    message: str
    status: Optional[str] = None
    new_segment_level: Optional[int] = None
    tokens_spent: Optional[int] = None
    valid_until: Optional[datetime] = None
