from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict
from datetime import datetime

class FeedbackBase(BaseModel):
    user_id: int
    action_type: str
    context: Optional[Dict[str, str]] = None
    
class FeedbackRequest(FeedbackBase):
    pass

class FeedbackResponse(BaseModel):
    success: bool
    message: str
    animation_key: Optional[str] = None
    sound_key: Optional[str] = None
    intensity: Optional[int] = None  # 1-5 scale for emotional intensity
    color_scheme: Optional[str] = None  # For UI color adaptation (e.g., "success", "warning", "danger")
    bonus_tokens: Optional[int] = None  # Any bonus tokens awarded with feedback
    recommendation: Optional[str] = None  # 테스트에서 참조될 수 있는 권장 행동 문자열
    model_config = ConfigDict(from_attributes=True)
    
class FeedbackLog(FeedbackBase):
    id: int
    message: str
    animation_key: Optional[str] = None
    sound_key: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class RecommendationResult(BaseModel):
    user_id: int
    segment: Optional[str] = None
    primary_recommendations: list[str] = []
    secondary_recommendations: list[str] = []
    generated_at: datetime
    strategy_version: str = "v1"
    model_config = ConfigDict(from_attributes=True)