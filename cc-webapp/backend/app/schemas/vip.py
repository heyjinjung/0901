from typing import List, Optional
from pydantic import BaseModel

class VIPExclusiveContentItem(BaseModel):
    id: int
    name: str
    title: str
    description: str
    content_type: str
    thumbnail_url: Optional[str] = None
    tier_required: str

class VIPInfoResponse(BaseModel):
    user_id: int
    vip_tier: str
    tier: str
    benefits: List[str]
    content_access: List[str]
