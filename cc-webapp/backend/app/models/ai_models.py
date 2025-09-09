"""
🤖 Casino-Club F2P - AI 추천 시스템 모델
======================================
개인화 추천 및 AI 기반 콘텐츠 제공 시스템
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from ..database import Base


class RecommendationTemplate(Base):
    """추천 템플릿"""
    __tablename__ = "recommendation_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    template_type = Column(String(50), nullable=False)  # game, reward, mission, content
    target_segment = Column(String(50))  # Whale, High, Medium, At-risk
    trigger_conditions = Column(JSON)  # 추천 트리거 조건
    content_template = Column(JSON)  # 추천 콘텐츠 템플릿
    priority = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계
    recommendations = relationship("UserRecommendation", back_populates="template")


class UserRecommendation(Base):
    """사용자별 개인화 추천"""
    __tablename__ = "user_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    template_id = Column(Integer, ForeignKey("recommendation_templates.id"))
    recommendation_type = Column(String(50), nullable=False)  # game, reward, mission, content
    title = Column(String(200), nullable=False)
    description = Column(Text)
    content_data = Column(JSON)  # 추천 콘텐츠 상세 데이터
    priority_score = Column(Float, default=0.5)
    confidence_score = Column(Float, default=0.5)  # AI 신뢰도
    personalization_factors = Column(JSON)  # 개인화 요소들
    
    # 상태 관리
    status = Column(String(20), default="pending")  # pending, shown, clicked, dismissed, expired
    shown_at = Column(DateTime(timezone=True))
    clicked_at = Column(DateTime(timezone=True))
    dismissed_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
    
    # 메타데이터
    source = Column(String(50), default="ai_engine")  # ai_engine, manual, rule_based
    algorithm_version = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계
    user = relationship("User")
    template = relationship("RecommendationTemplate", back_populates="recommendations")
    interactions = relationship("RecommendationInteraction", back_populates="recommendation")


class RecommendationInteraction(Base):
    """추천 상호작용 기록"""
    __tablename__ = "recommendation_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    recommendation_id = Column(Integer, ForeignKey("user_recommendations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    interaction_type = Column(String(50), nullable=False)  # view, click, dismiss, complete
    interaction_data = Column(JSON)  # 상호작용 상세 데이터
    duration = Column(Integer)  # 상호작용 지속 시간(초)
    result_data = Column(JSON)  # 결과 데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계
    recommendation = relationship("UserRecommendation", back_populates="interactions")
    user = relationship("User")


class UserPreference(Base):
    """사용자 선호도 프로필"""
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # 게임 선호도
    preferred_games = Column(JSON)  # 선호 게임 목록과 점수
    game_difficulty_preference = Column(String(20), default="medium")
    risk_tolerance = Column(Float, default=0.5)  # 0.0 (보수적) ~ 1.0 (위험선호)
    
    # 보상 선호도
    preferred_reward_types = Column(JSON)  # 선호 보상 타입들
    spending_pattern = Column(JSON)  # 지출 패턴 분석
    
    # 시간 패턴
    active_hours = Column(JSON)  # 활동 시간대
    session_duration_preference = Column(Integer)  # 선호 세션 길이
    
    # 콘텐츠 선호도
    content_categories = Column(JSON)  # 선호 콘텐츠 카테고리
    interaction_style = Column(String(50))  # casual, competitive, social
    
    # AI 학습 데이터
    learning_rate = Column(Float, default=0.1)
    last_model_update = Column(DateTime(timezone=True))
    preference_accuracy = Column(Float, default=0.5)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 관계
    user = relationship("User")


class AIModel(Base):
    """AI 모델 메타데이터"""
    __tablename__ = "ai_models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    model_type = Column(String(50), nullable=False)  # recommendation, prediction, classification
    version = Column(String(20), nullable=False)
    description = Column(Text)
    
    # 모델 설정
    algorithm = Column(String(50))  # collaborative_filtering, content_based, hybrid
    hyperparameters = Column(JSON)
    training_data_info = Column(JSON)
    
    # 성능 메트릭
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    
    # 상태
    status = Column(String(20), default="training")  # training, active, deprecated
    is_production = Column(Boolean, default=False)
    
    # 메타데이터
    trained_at = Column(DateTime(timezone=True))
    deployed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계
    predictions = relationship("ModelPrediction", back_populates="model")


class ModelPrediction(Base):
    """모델 예측 결과"""
    __tablename__ = "model_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("ai_models.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    prediction_type = Column(String(50), nullable=False)  # churn, ltv, next_action, preference
    input_features = Column(JSON)  # 입력 특성들
    prediction_result = Column(JSON)  # 예측 결과
    confidence_score = Column(Float)
    
    # 검증 데이터
    actual_result = Column(JSON)  # 실제 결과 (나중에 업데이트)
    is_correct = Column(Boolean)  # 예측 정확도
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    validated_at = Column(DateTime(timezone=True))
    
    # 관계
    model = relationship("AIModel", back_populates="predictions")
    user = relationship("User")


class PersonalizationRule(Base):
    """개인화 규칙"""
    __tablename__ = "personalization_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    rule_type = Column(String(50), nullable=False)  # segment_based, behavior_based, time_based
    conditions = Column(JSON, nullable=False)  # 조건들
    actions = Column(JSON, nullable=False)  # 실행할 액션들
    priority = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    
    # 성능 추적
    execution_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ContentPersonalization(Base):
    """콘텐츠 개인화 설정"""
    __tablename__ = "content_personalizations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_type = Column(String(50), nullable=False)  # game, ui, message, reward
    personalization_data = Column(JSON)  # 개인화 데이터
    effectiveness_score = Column(Float, default=0.5)
    last_applied = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계
    user = relationship("User")
