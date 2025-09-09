"""
💬 Casino-Club F2P - Chat Schemas
================================
채팅 시스템 Pydantic 스키마 정의
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class RoomType(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    AI_ASSISTANT = "ai_assistant"
    SUPPORT = "support"


class MessageType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    EMOJI = "emoji"
    SYSTEM = "system"
    AI_RESPONSE = "ai_response"


class ParticipantRole(str, Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    MEMBER = "member"


class ConversationType(str, Enum):
    GENERAL = "general"
    SUPPORT = "support"
    GUIDANCE = "guidance"


class MoodType(str, Enum):
    JOY = "joy"
    SAD = "sad"
    ANGRY = "angry"
    NEUTRAL = "neutral"
    CALM = "calm"
    LOVE = "love"
    EXCITED = "excited"


class ChatRoomCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    room_type: RoomType = RoomType.PUBLIC
    description: Optional[str] = None
    max_participants: int = Field(default=100, ge=2, le=1000)
    allow_anonymous: bool = False
    auto_moderation: bool = True
    ai_assistant_enabled: bool = True


class ChatRoomResponse(BaseModel):
    id: int
    name: str
    room_type: RoomType
    description: Optional[str] = None
    max_participants: int = 100
    is_active: bool = True
    allow_anonymous: bool = False
    auto_moderation: bool = True
    ai_assistant_enabled: bool = True
    created_at: datetime
    participant_count: Optional[int] = 0
    model_config = ConfigDict(from_attributes=True)


class ChatParticipantResponse(BaseModel):
    id: int
    room_id: int
    user_id: int
    role: ParticipantRole = ParticipantRole.MEMBER
    is_active: bool = True
    is_muted: bool = False
    joined_at: datetime
    last_seen: Optional[datetime] = None
    message_count: int = 0
    model_config = ConfigDict(from_attributes=True)


class ChatMessageCreate(BaseModel):
    room_id: int
    message_type: MessageType = MessageType.TEXT
    content: str = Field(..., min_length=1, max_length=2000)
    reply_to_id: Optional[int] = None
    thread_id: Optional[str] = None


class ChatMessageResponse(BaseModel):
    id: int
    room_id: int
    sender_id: Optional[int] = None
    message_type: MessageType = MessageType.TEXT
    content: str
    formatted_content: Optional[Dict[str, Any]] = None
    emotion_detected: Optional[MoodType] = None
    sentiment_score: Optional[float] = None
    ai_generated: bool = False
    ai_model_version: Optional[str] = None
    reply_to_id: Optional[int] = None
    thread_id: Optional[str] = None
    is_edited: bool = False
    is_deleted: bool = False
    reaction_counts: Optional[Dict[str, int]] = None
    read_by: Optional[List[int]] = None
    created_at: datetime
    edited_at: Optional[datetime] = None
    sender_nickname: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class MessageReactionCreate(BaseModel):
    reaction_type: str = "emoji"
    reaction_value: str = Field(..., min_length=1, max_length=10)


class MessageReactionResponse(BaseModel):
    id: int
    message_id: int
    user_id: int
    reaction_type: str
    reaction_value: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AIAssistantCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    assistant_type: str = "general"
    personality: Optional[Dict[str, Any]] = None
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    prompt_template: Optional[str] = None
    response_style: Optional[Dict[str, Any]] = None
    default_mood: MoodType = MoodType.NEUTRAL
    mood_adaptation: bool = True
    emotion_responsiveness: float = Field(default=0.7, ge=0.0, le=1.0)
    can_access_user_data: bool = True
    can_make_recommendations: bool = True
    can_provide_rewards: bool = False
    # Allow fields starting with "model_" without protected-namespace warnings (Pydantic v2)
    model_config = ConfigDict(protected_namespaces=())


class AIAssistantResponse(BaseModel):
    id: int
    name: str
    assistant_type: str = "general"
    personality: Optional[Dict[str, Any]] = None
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    default_mood: MoodType = MoodType.NEUTRAL
    mood_adaptation: bool = True
    emotion_responsiveness: float = 0.7
    can_access_user_data: bool = True
    can_make_recommendations: bool = True
    can_provide_rewards: bool = False
    is_active: bool = True
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AIConversationCreate(BaseModel):
    assistant_id: int
    conversation_type: ConversationType = ConversationType.GENERAL
    context_data: Optional[Dict[str, Any]] = None


class AIConversationResponse(BaseModel):
    id: int
    user_id: int
    assistant_id: int
    conversation_type: ConversationType = ConversationType.GENERAL
    context_data: Optional[Dict[str, Any]] = None
    status: str = "active"
    current_mood: MoodType = MoodType.NEUTRAL
    user_satisfaction: Optional[float] = None
    message_count: int = 0
    duration_minutes: int = 0
    started_at: datetime
    ended_at: Optional[datetime] = None
    last_activity: datetime
    model_config = ConfigDict(from_attributes=True)


class AIMessageCreate(BaseModel):
    conversation_id: int
    message_type: MessageType = MessageType.TEXT
    content: str = Field(..., min_length=1, max_length=2000)
    sender_type: str = Field(..., pattern="^(user|ai)$")


class AIMessageResponse(BaseModel):
    id: int
    conversation_id: int
    message_type: MessageType = MessageType.TEXT
    content: str
    sender_type: str
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    processing_time: Optional[float] = None
    confidence_score: Optional[float] = None
    detected_emotion: Optional[MoodType] = None
    response_mood: Optional[MoodType] = None
    personalization_applied: Optional[Dict[str, Any]] = None
    user_feedback: Optional[str] = None
    follow_up_needed: bool = False
    created_at: datetime
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class EmotionProfileUpdate(BaseModel):
    current_mood: Optional[MoodType] = None
    mood_intensity: Optional[float] = Field(None, ge=0.0, le=1.0)
    sensitivity_level: Optional[float] = Field(None, ge=0.0, le=1.0)


class EmotionProfileResponse(BaseModel):
    id: int
    user_id: int
    current_mood: MoodType = MoodType.NEUTRAL
    mood_intensity: float = 0.5
    emotion_history: Optional[Dict[str, Any]] = None
    dominant_emotions: Optional[Dict[str, Any]] = None
    emotion_triggers: Optional[Dict[str, Any]] = None
    response_patterns: Optional[Dict[str, Any]] = None
    preferred_mood_responses: Optional[Dict[str, Any]] = None
    sensitivity_level: float = 0.5
    last_updated: datetime
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ChatModerationAction(BaseModel):
    action_type: str = Field(..., pattern="^(warning|mute|ban|delete)$")
    reason: Optional[str] = Field(None, max_length=200)
    severity_level: int = Field(default=1, ge=1, le=5)
    expires_at: Optional[datetime] = None


class ChatModerationResponse(BaseModel):
    id: int
    message_id: Optional[int] = None
    user_id: int
    moderator_id: Optional[int] = None
    action_type: str
    reason: Optional[str] = None
    auto_moderation: bool = False
    severity_level: int = 1
    action_taken: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
