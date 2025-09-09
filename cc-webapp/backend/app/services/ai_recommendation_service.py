"""
🤖 Casino-Club F2P - AI 추천 시스템 서비스
========================================
AI 기반 개인화 추천 및 콘텐츠 제공 서비스
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from ..models.ai_models import (
    RecommendationTemplate, UserRecommendation, RecommendationInteraction,
    UserPreference, AIModel, ModelPrediction, PersonalizationRule,
    ContentPersonalization
)
from ..models.auth_models import User
from ..models.user_models import UserSegment
from ..models.game_models import UserAction, UserReward
from ..schemas.ai_schemas import (
    UserRecommendationCreate, RecommendationInteractionCreate,
    UserPreferenceUpdate, PersonalizationRequest
)
from ..utils.emotion_engine import EmotionEngine

logger = logging.getLogger(__name__)


class AIRecommendationService:
    """AI 추천 시스템 서비스"""
    
    def __init__(self, db: Session, redis=None):
        self.db = db
        self.redis = redis
        self.emotion_engine = EmotionEngine(redis) if redis else None
        
    async def generate_recommendations(
        self, 
        user_id: int, 
        recommendation_type: str = None,
        max_recommendations: int = 5
    ) -> List[UserRecommendation]:
        """사용자를 위한 개인화 추천 생성"""
        try:
            # 사용자 정보 조회
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.error(f"User not found: {user_id}")
                return []
            
            # 사용자 세그먼트 조회
            user_segment = self.db.query(UserSegment).filter(
                UserSegment.user_id == user_id
            ).first()
            
            segment_name = user_segment.segment_name if user_segment else "Medium"
            
            # 사용자 선호도 조회
            user_preference = self.db.query(UserPreference).filter(
                UserPreference.user_id == user_id
            ).first()
            
            # 최근 활동 분석
            recent_actions = self.db.query(UserAction).filter(
                UserAction.user_id == user_id,
                UserAction.action_timestamp >= datetime.utcnow() - timedelta(days=7)
            ).limit(50).all()
            
            # 추천 생성
            recommendations = []
            
            # 1. 게임 추천
            if not recommendation_type or recommendation_type == "game":
                game_recs = await self._generate_game_recommendations(
                    user_id, segment_name, user_preference, recent_actions
                )
                recommendations.extend(game_recs)
            
            # 2. 보상 추천
            if not recommendation_type or recommendation_type == "reward":
                reward_recs = await self._generate_reward_recommendations(
                    user_id, segment_name, user_preference, recent_actions
                )
                recommendations.extend(reward_recs)
            
            # 3. 미션 추천
            if not recommendation_type or recommendation_type == "mission":
                mission_recs = await self._generate_mission_recommendations(
                    user_id, segment_name, user_preference, recent_actions
                )
                recommendations.extend(mission_recs)
            
            # 4. 콘텐츠 추천
            if not recommendation_type or recommendation_type == "content":
                content_recs = await self._generate_content_recommendations(
                    user_id, segment_name, user_preference, recent_actions
                )
                recommendations.extend(content_recs)
            
            # 우선순위별 정렬 및 제한
            recommendations.sort(key=lambda x: x.priority_score, reverse=True)
            recommendations = recommendations[:max_recommendations]
            
            # DB에 저장
            for rec in recommendations:
                self.db.add(rec)
            self.db.commit()
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations: {str(e)}")
            self.db.rollback()
            return []
    
    async def _generate_game_recommendations(
        self, 
        user_id: int, 
        segment: str, 
        preference: UserPreference,
        recent_actions: List[UserAction]
    ) -> List[UserRecommendation]:
        """게임 추천 생성"""
        recommendations = []
        
        # 최근 플레이한 게임 분석
        recent_games = {}
        for action in recent_actions:
            if action.action_type.startswith("GAME_"):
                game_type = action.metadata.get("game_type", "unknown")
                recent_games[game_type] = recent_games.get(game_type, 0) + 1
        
        # 선호 게임 기반 추천
        if preference and preference.preferred_games:
            for game_type, score in preference.preferred_games.items():
                if score > 0.6:  # 높은 선호도
                    rec = UserRecommendation(
                        user_id=user_id,
                        recommendation_type="game",
                        title=f"좋아하는 {game_type} 게임",
                        description=f"선호도가 높은 {game_type} 게임을 즐겨보세요!",
                        content_data={
                            "game_type": game_type,
                            "reason": "user_preference",
                            "preference_score": score
                        },
                        priority_score=0.8 + score * 0.2,
                        confidence_score=0.9,
                        personalization_factors={
                            "segment": segment,
                            "preference_score": score,
                            "recent_activity": recent_games.get(game_type, 0)
                        },
                        source="ai_engine",
                        algorithm_version="v1.0"
                    )
                    recommendations.append(rec)
        
        # 세그먼트 기반 추천
        segment_games = {
            "Whale": ["premium_slots", "high_stakes_poker"],
            "High": ["tournament_games", "competitive_modes"],
            "Medium": ["daily_missions", "casual_slots"],
            "At-risk": ["free_games", "tutorial_modes"]
        }
        
        for game_type in segment_games.get(segment, []):
            rec = UserRecommendation(
                user_id=user_id,
                recommendation_type="game",
                title=f"{segment} 사용자 추천 게임",
                description=f"{game_type} 게임을 시도해보세요!",
                content_data={
                    "game_type": game_type,
                    "reason": "segment_based",
                    "target_segment": segment
                },
                priority_score=0.6,
                confidence_score=0.7,
                personalization_factors={
                    "segment": segment,
                    "recommendation_basis": "segment_targeting"
                },
                source="ai_engine",
                algorithm_version="v1.0"
            )
            recommendations.append(rec)
        
        return recommendations
    
    async def _generate_reward_recommendations(
        self,
        user_id: int,
        segment: str,
        preference: UserPreference,
        recent_actions: List[UserAction]
    ) -> List[UserRecommendation]:
        """보상 추천 생성"""
        recommendations = []
        
        # 최근 보상 활동 분석
        recent_rewards = [
            action for action in recent_actions 
            if action.action_type in ["EARN_CYBER_TOKENS", "CLAIM_REWARD"]
        ]
        
        # 세그먼트별 보상 추천
        if segment == "At-risk" and len(recent_rewards) < 3:
            # 복귀 유도 보상
            rec = UserRecommendation(
                user_id=user_id,
                recommendation_type="reward",
                title="복귀 보상",
                description="오랜만이네요! 특별 복귀 보상을 받아보세요",
                content_data={
                    "reward_type": "comeback_bonus",
                    "tokens": 500,
                    "expires_hours": 24
                },
                priority_score=0.9,
                confidence_score=0.8,
                personalization_factors={
                    "segment": segment,
                    "inactivity_detected": True
                },
                expires_at=datetime.utcnow() + timedelta(hours=24),
                source="ai_engine",
                algorithm_version="v1.0"
            )
            recommendations.append(rec)
        
        elif segment == "Whale":
            # VIP 전용 보상
            rec = UserRecommendation(
                user_id=user_id,
                recommendation_type="reward",
                title="VIP 특별 보상",
                description="프리미엄 사용자만을 위한 특별 보상입니다",
                content_data={
                    "reward_type": "vip_exclusive",
                    "tokens": 2000,
                    "special_items": ["legendary_badge", "premium_avatar"]
                },
                priority_score=0.95,
                confidence_score=0.9,
                personalization_factors={
                    "segment": segment,
                    "vip_status": True
                },
                source="ai_engine",
                algorithm_version="v1.0"
            )
            recommendations.append(rec)
        
        return recommendations
    
    async def _generate_mission_recommendations(
        self,
        user_id: int,
        segment: str,
        preference: UserPreference,
        recent_actions: List[UserAction]
    ) -> List[UserRecommendation]:
        """미션 추천 생성"""
        recommendations = []
        
        # 미션 완료 기록 분석
        mission_actions = [
            action for action in recent_actions 
            if action.action_type == "COMPLETE_MISSION"
        ]
        
        # 개인화된 미션 추천
        if len(mission_actions) > 5:  # 활발한 미션 수행자
            rec = UserRecommendation(
                user_id=user_id,
                recommendation_type="mission",
                title="도전 미션",
                description="더 어려운 미션에 도전해보세요!",
                content_data={
                    "mission_type": "challenge",
                    "difficulty": "hard",
                    "reward_multiplier": 2.0
                },
                priority_score=0.8,
                confidence_score=0.85,
                personalization_factors={
                    "mission_completion_rate": len(mission_actions),
                    "player_type": "mission_enthusiast"
                },
                source="ai_engine",
                algorithm_version="v1.0"
            )
            recommendations.append(rec)
        
        elif len(mission_actions) < 2:  # 미션 초보자
            rec = UserRecommendation(
                user_id=user_id,
                recommendation_type="mission",
                title="입문 미션",
                description="쉬운 미션부터 시작해보세요!",
                content_data={
                    "mission_type": "tutorial",
                    "difficulty": "easy",
                    "guidance": True
                },
                priority_score=0.7,
                confidence_score=0.8,
                personalization_factors={
                    "mission_experience": "beginner",
                    "needs_guidance": True
                },
                source="ai_engine",
                algorithm_version="v1.0"
            )
            recommendations.append(rec)
        
        return recommendations
    
    async def _generate_content_recommendations(
        self,
        user_id: int,
        segment: str,
        preference: UserPreference,
        recent_actions: List[UserAction]
    ) -> List[UserRecommendation]:
        """콘텐츠 추천 생성"""
        recommendations = []
        
        # 감정 기반 콘텐츠 추천
        if self.emotion_engine and self.redis:
            current_mood = await self.emotion_engine.get_user_mood(user_id)
            
            mood_content = {
                "joy": {
                    "title": "축하 이벤트",
                    "description": "기쁜 기분에 어울리는 특별 이벤트!",
                    "content_type": "celebration_event"
                },
                "sad": {
                    "title": "위로 콘텐츠",
                    "description": "기분 전환이 되는 콘텐츠를 준비했어요",
                    "content_type": "comfort_content"
                },
                "neutral": {
                    "title": "일반 콘텐츠",
                    "description": "다양한 콘텐츠를 둘러보세요",
                    "content_type": "general_content"
                }
            }
            
            if current_mood in mood_content:
                content_info = mood_content[current_mood]
                rec = UserRecommendation(
                    user_id=user_id,
                    recommendation_type="content",
                    title=content_info["title"],
                    description=content_info["description"],
                    content_data={
                        "content_type": content_info["content_type"],
                        "mood_based": True,
                        "detected_mood": current_mood
                    },
                    priority_score=0.75,
                    confidence_score=0.7,
                    personalization_factors={
                        "emotion_detection": current_mood,
                        "mood_adaptation": True
                    },
                    source="ai_engine",
                    algorithm_version="v1.0"
                )
                recommendations.append(rec)
        
        return recommendations
    
    async def record_interaction(
        self,
        recommendation_id: int,
        user_id: int,
        interaction_data: RecommendationInteractionCreate
    ) -> RecommendationInteraction:
        """추천 상호작용 기록"""
        try:
            # 추천 존재 확인
            recommendation = self.db.query(UserRecommendation).filter(
                UserRecommendation.id == recommendation_id,
                UserRecommendation.user_id == user_id
            ).first()
            
            if not recommendation:
                raise ValueError("Recommendation not found")
            
            # 상호작용 기록 생성
            interaction = RecommendationInteraction(
                recommendation_id=recommendation_id,
                user_id=user_id,
                interaction_type=interaction_data.interaction_type,
                interaction_data=interaction_data.interaction_data or {},
                duration=interaction_data.duration,
                result_data=interaction_data.result_data or {}
            )
            
            self.db.add(interaction)
            
            # 추천 상태 업데이트
            if interaction_data.interaction_type == "click":
                recommendation.status = "clicked"
                recommendation.clicked_at = datetime.utcnow()
            elif interaction_data.interaction_type == "dismiss":
                recommendation.status = "dismissed"
                recommendation.dismissed_at = datetime.utcnow()
            
            self.db.commit()
            
            # 사용자 선호도 학습
            await self._update_user_preference_from_interaction(
                user_id, recommendation, interaction_data
            )
            
            return interaction
            
        except Exception as e:
            logger.error(f"Failed to record interaction: {str(e)}")
            self.db.rollback()
            raise
    
    async def _update_user_preference_from_interaction(
        self,
        user_id: int,
        recommendation: UserRecommendation,
        interaction: RecommendationInteractionCreate
    ):
        """상호작용을 통한 사용자 선호도 학습"""
        try:
            user_preference = self.db.query(UserPreference).filter(
                UserPreference.user_id == user_id
            ).first()
            
            if not user_preference:
                user_preference = UserPreference(user_id=user_id)
                self.db.add(user_preference)
            
            # 학습률 적용
            learning_rate = user_preference.learning_rate
            
            # 상호작용 타입에 따른 피드백 점수
            feedback_scores = {
                "click": 1.0,
                "complete": 1.5,
                "dismiss": -0.5,
                "view": 0.1
            }
            
            feedback_score = feedback_scores.get(interaction.interaction_type, 0.0)
            
            # 추천 타입별 선호도 업데이트
            if recommendation.recommendation_type == "game":
                game_type = recommendation.content_data.get("game_type")
                if game_type and user_preference.preferred_games:
                    current_score = user_preference.preferred_games.get(game_type, 0.5)
                    new_score = current_score + (feedback_score * learning_rate)
                    new_score = max(0.0, min(1.0, new_score))  # 0-1 범위로 제한
                    
                    preferred_games = user_preference.preferred_games.copy()
                    preferred_games[game_type] = new_score
                    user_preference.preferred_games = preferred_games
            
            user_preference.last_model_update = datetime.utcnow()
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to update user preference: {str(e)}")
    
    async def get_user_preferences(self, user_id: int) -> Optional[UserPreference]:
        """사용자 선호도 조회"""
        return self.db.query(UserPreference).filter(
            UserPreference.user_id == user_id
        ).first()
    
    async def update_user_preferences(
        self,
        user_id: int,
        preference_data: UserPreferenceUpdate
    ) -> UserPreference:
        """사용자 선호도 업데이트"""
        try:
            user_preference = self.db.query(UserPreference).filter(
                UserPreference.user_id == user_id
            ).first()
            
            if not user_preference:
                user_preference = UserPreference(user_id=user_id)
                self.db.add(user_preference)
            
            # 필드별 업데이트
            update_data = preference_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(user_preference, field) and value is not None:
                    setattr(user_preference, field, value)
            
            user_preference.updated_at = datetime.utcnow()
            self.db.commit()
            
            return user_preference
            
        except Exception as e:
            logger.error(f"Failed to update user preferences: {str(e)}")
            self.db.rollback()
            raise
