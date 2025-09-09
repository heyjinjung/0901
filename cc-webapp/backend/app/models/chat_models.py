"""
💬 Casino-Club F2P - 채팅 시스템 모델
===================================
AI 채팅, 실시간 채팅, 감정 기반 메시징 시스템
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from ..database import Base


class ChatRoom(Base):
    """채팅방"""
    __tablename__ = "chat_rooms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    room_type = Column(String(50), default="public")  # public, private, ai_assistant, support
    description = Column(Text)
    max_participants = Column(Integer, default=100)
    is_active = Column(Boolean, default=True)
    
    # 채팅방 설정
    allow_anonymous = Column(Boolean, default=False)
    auto_moderation = Column(Boolean, default=True)
    ai_assistant_enabled = Column(Boolean, default=True)
    
    # 메타데이터
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계
    creator = relationship("User", foreign_keys=[created_by])
    messages = relationship("ChatMessage", back_populates="room")
    participants = relationship("ChatParticipant", back_populates="room")


class ChatParticipant(Base):
    """채팅방 참가자"""
    __tablename__ = "chat_participants"
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 참가 상태
    role = Column(String(20), default="member")  # admin, moderator, member
    is_active = Column(Boolean, default=True)
    is_muted = Column(Boolean, default=False)
    
    # 활동 기록
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True))
    message_count = Column(Integer, default=0)
    
    # 관계
    room = relationship("ChatRoom", back_populates="participants")
    user = relationship("User")


class ChatMessage(Base):
    """채팅 메시지"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("chat_rooms.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"))
    
    # 메시지 내용
    message_type = Column(String(50), default="text")  # text, image, emoji, system, ai_response
    content = Column(Text, nullable=False)
    formatted_content = Column(JSON)  # HTML, 마크다운 등
    
    # AI/감정 분석
    emotion_detected = Column(String(50))  # joy, sad, angry, neutral, etc.
    sentiment_score = Column(Float)  # -1.0 (부정) ~ 1.0 (긍정)
    ai_generated = Column(Boolean, default=False)
    ai_model_version = Column(String(20))
    
    # 메시지 메타데이터
    reply_to_id = Column(Integer, ForeignKey("chat_messages.id"))
    thread_id = Column(String(100))  # 스레드 관리용
    is_edited = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    
    # 상호작용
    reaction_counts = Column(JSON)  # {"👍": 5, "❤️": 3}
    read_by = Column(JSON)  # 읽은 사용자 목록
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    edited_at = Column(DateTime(timezone=True))
    
    # 관계
    room = relationship("ChatRoom", back_populates="messages")
    sender = relationship("User")
    reply_to = relationship("ChatMessage", remote_side=[id])
    reactions = relationship("MessageReaction", back_populates="message")


class MessageReaction(Base):
    """메시지 반응 (이모지 등)"""
    __tablename__ = "message_reactions"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("chat_messages.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reaction_type = Column(String(50), nullable=False)  # emoji, like, dislike
    reaction_value = Column(String(10))  # 실제 이모지 또는 반응 값
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계
    message = relationship("ChatMessage", back_populates="reactions")
    user = relationship("User")


class AIAssistant(Base):
    """AI 어시스턴트 설정"""
    __tablename__ = "ai_assistants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    assistant_type = Column(String(50), default="general")  # general, game_guide, support
    personality = Column(JSON)  # 성격 설정
    
    # AI 모델 설정
    model_name = Column(String(100))
    model_version = Column(String(20))
    prompt_template = Column(Text)
    response_style = Column(JSON)
    
    # 감정/무드 설정
    default_mood = Column(String(50), default="neutral")
    mood_adaptation = Column(Boolean, default=True)
    emotion_responsiveness = Column(Float, default=0.7)
    
    # 기능 설정
    can_access_user_data = Column(Boolean, default=True)
    can_make_recommendations = Column(Boolean, default=True)
    can_provide_rewards = Column(Boolean, default=False)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계
    conversations = relationship("AIConversation", back_populates="assistant")


class AIConversation(Base):
    """AI 대화 세션"""
    __tablename__ = "ai_conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assistant_id = Column(Integer, ForeignKey("ai_assistants.id"), nullable=False)
    
    # 대화 설정
    conversation_type = Column(String(50), default="general")  # general, support, guidance
    context_data = Column(JSON)  # 대화 컨텍스트
    
    # 대화 상태
    status = Column(String(20), default="active")  # active, paused, ended
    current_mood = Column(String(50), default="neutral")
    user_satisfaction = Column(Float)  # 사용자 만족도
    
    # 통계
    message_count = Column(Integer, default=0)
    duration_minutes = Column(Integer, default=0)
    
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True))
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계
    user = relationship("User")
    assistant = relationship("AIAssistant", back_populates="conversations")
    messages = relationship("AIMessage", back_populates="conversation")


class AIMessage(Base):
    """AI 대화 메시지"""
    __tablename__ = "ai_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("ai_conversations.id"), nullable=False)
    
    # 메시지 내용
    message_type = Column(String(50), default="text")  # text, suggestion, reward, info
    content = Column(Text, nullable=False)
    sender_type = Column(String(20), nullable=False)  # user, ai
    
    # AI 처리 정보
    input_tokens = Column(Integer)
    output_tokens = Column(Integer)
    processing_time = Column(Float)  # 처리 시간(초)
    confidence_score = Column(Float)
    
    # 감정/무드
    detected_emotion = Column(String(50))
    response_mood = Column(String(50))
    personalization_applied = Column(JSON)
    
    # 상호작용
    user_feedback = Column(String(20))  # helpful, not_helpful, irrelevant
    follow_up_needed = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계
    conversation = relationship("AIConversation", back_populates="messages")


class EmotionProfile(Base):
    """사용자 감정 프로필"""
    __tablename__ = "emotion_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # 현재 감정 상태
    current_mood = Column(String(50), default="neutral")
    mood_intensity = Column(Float, default=0.5)  # 0.0 ~ 1.0
    
    # 감정 히스토리
    emotion_history = Column(JSON)  # 최근 감정 변화 기록
    dominant_emotions = Column(JSON)  # 주요 감정들과 빈도
    
    # 패턴 분석
    emotion_triggers = Column(JSON)  # 감정 변화 트리거들
    response_patterns = Column(JSON)  # 감정별 반응 패턴
    
    # 개인화 설정
    preferred_mood_responses = Column(JSON)  # 감정별 선호 응답 스타일
    sensitivity_level = Column(Float, default=0.5)  # 감정 민감도
    
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계
    user = relationship("User")


class ChatModeration(Base):
    """채팅 모더레이션 로그"""
    __tablename__ = "chat_moderations"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("chat_messages.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    moderator_id = Column(Integer, ForeignKey("users.id"))
    
    # 모더레이션 정보
    action_type = Column(String(50), nullable=False)  # warning, mute, ban, delete
    reason = Column(String(200))
    auto_moderation = Column(Boolean, default=False)
    severity_level = Column(Integer, default=1)  # 1-5
    
    # 처리 결과
    action_taken = Column(JSON)  # 실제 취한 조치들
    expires_at = Column(DateTime(timezone=True))  # 제재 만료일
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계
    message = relationship("ChatMessage")
    user = relationship("User", foreign_keys=[user_id])
    moderator = relationship("User", foreign_keys=[moderator_id])
