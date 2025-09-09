"""
🤖 Casino-Club F2P - AI Recommendation Schemas
============================================
AI 추천 시스템 Pydantic 스키마 정의
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class RecommendationType(str, Enum):
    GAME = "game"
    REWARD = "reward"
    MISSION = "mission"
    CONTENT = "content"


class RecommendationStatus(str, Enum):
    PENDING = "pending"
    SHOWN = "shown"
    CLICKED = "clicked"
    DISMISSED = "dismissed"
    EXPIRED = "expired"


class InteractionType(str, Enum):
    VIEW = "view"
    CLICK = "click"
    DISMISS = "dismiss"
    COMPLETE = "complete"


class RecommendationTemplateResponse(BaseModel):
    id: int
    name: str
    template_type: RecommendationType
    target_segment: Optional[str] = None
    trigger_conditions: Dict[str, Any] = {}
    content_template: Dict[str, Any] = {}
    priority: int = 1
    is_active: bool = True
    
    model_config = ConfigDict(from_attributes=True)


class UserRecommendationCreate(BaseModel):
    template_id: Optional[int] = None
    recommendation_type: RecommendationType
    title: str
    description: Optional[str] = None
    content_data: Optional[Dict[str, Any]] = None
    priority_score: float = Field(default=0.5, ge=0.0, le=1.0)
    confidence_score: float = Field(default=0.5, ge=0.0, le=1.0)
    personalization_factors: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None


class UserRecommendationResponse(BaseModel):
    id: int
    user_id: int
    recommendation_type: RecommendationType
    title: str
    description: Optional[str] = None
    content_data: Optional[Dict[str, Any]] = None
    priority_score: float = 0.5
    confidence_score: float = 0.5
    personalization_factors: Optional[Dict[str, Any]] = None
    status: RecommendationStatus = RecommendationStatus.PENDING
    shown_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    dismissed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    source: str = "ai_engine"
    algorithm_version: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class RecommendationInteractionCreate(BaseModel):
    interaction_type: InteractionType
    interaction_data: Optional[Dict[str, Any]] = None
    duration: Optional[int] = None
    result_data: Optional[Dict[str, Any]] = None


class RecommendationInteractionResponse(BaseModel):
    id: int
    recommendation_id: int
    user_id: int
    interaction_type: InteractionType
    interaction_data: Optional[Dict[str, Any]] = None
    duration: Optional[int] = None
    result_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserPreferenceUpdate(BaseModel):
    preferred_games: Optional[Dict[str, Any]] = None
    game_difficulty_preference: Optional[str] = None
    risk_tolerance: Optional[float] = Field(None, ge=0.0, le=1.0)
    preferred_reward_types: Optional[Dict[str, Any]] = None
    spending_pattern: Optional[Dict[str, Any]] = None
    active_hours: Optional[Dict[str, Any]] = None
    session_duration_preference: Optional[int] = None
    content_categories: Optional[Dict[str, Any]] = None
    interaction_style: Optional[str] = None


class UserPreferenceResponse(BaseModel):
    id: int
    user_id: int
    preferred_games: Optional[Dict[str, Any]] = None
    game_difficulty_preference: str = "medium"
    risk_tolerance: float = 0.5
    preferred_reward_types: Optional[Dict[str, Any]] = None
    spending_pattern: Optional[Dict[str, Any]] = None
    active_hours: Optional[Dict[str, Any]] = None
    session_duration_preference: Optional[int] = None
    content_categories: Optional[Dict[str, Any]] = None
    interaction_style: Optional[str] = None
    learning_rate: float = 0.1
    last_model_update: Optional[datetime] = None
    preference_accuracy: float = 0.5
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ModelPredictionResponse(BaseModel):
    id: int
    model_id: int
    user_id: int
    prediction_type: str
    input_features: Dict[str, Any] = {}
    prediction_result: Dict[str, Any] = {}
    confidence_score: float = 0.5
    actual_result: Optional[Dict[str, Any]] = None
    is_correct: Optional[bool] = None
    created_at: datetime
    validated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class PersonalizationRequest(BaseModel):
    user_id: int
    content_type: str
    context_data: Optional[Dict[str, Any]] = None
    max_recommendations: int = Field(default=5, ge=1, le=20)


class PersonalizationResponse(BaseModel):
    recommendations: List[UserRecommendationResponse]
    personalization_factors: Dict[str, Any]
    confidence_score: float
    algorithm_version: str
    generated_at: datetime

class RFMScore(BaseModel):
    r_score: int
    f_score: int
    m_score: int
    rfm_group: str

class SupportedLanguage(str, Enum):
    KOREAN = "ko"
    ENGLISH = "en"
    JAPANESE = "ja"
    CHINESE = "zh"

class EmotionResult(BaseModel):
    emotion: str
    score: float
    confidence: float
    language: SupportedLanguage
    fallback_attempted: bool = False
