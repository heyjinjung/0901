"""
개인화된 게임 추천 서비스
"""
from typing import List, Dict, Any, Optional
import logging
import random
from app.models import SupportedEmotion

logger = logging.getLogger(__name__)

class FinalRecommendation:
    """최종 추천 결과를 담는 Pydantic 모델"""

class RecommendationService:
    """
    사용자 특성 및 감정에 기반한 추천 서비스
    SOLID 원칙에 따라 단일 책임 원칙을 준수
    """
    
    def __init__(self, db=None):
        """
        추천 서비스 초기화
        
        Args:
            db: 데이터베이스 연결 (옵션)
        """
        self.db = db
        self.games = self._load_available_games()
        logger.info("Recommendation Service initialized")
    
    def _load_available_games(self) -> List[Dict[str, Any]]:
        """
        사용 가능한 게임 목록 로드
        
        Returns:
            게임 목록
        """
        return [
            {"game_type": "slot", "name": "슬롯머신", "tags": ["casual", "luck"]},
            {"game_type": "roulette", "name": "룰렛", "tags": ["strategy", "luck"]},
            {"game_type": "gacha", "name": "가챠", "tags": ["collection", "luck"]},
            {"game_type": "blackjack", "name": "블랙잭", "tags": ["card", "strategy"]},
            {"game_type": "dice", "name": "주사위", "tags": ["casual", "luck"]}
        ]
    
    def get_recommendations(self, user_id: int, emotion: SupportedEmotion, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        SupportedEmotion을 기반으로 게임 추천
        """
        emotion_str = emotion.value.lower() if emotion else None
        recommendations = self.get_personalized_recommendations(user_id, emotion_str)
        
        # 추가 컨텍스트 기반 필터링 적용
        if context:
            recommendations = self._apply_context_filters(recommendations, context)
        
        return recommendations

    def get_personalized_recommendations(self, user_id: int, emotion: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        사용자별 개인화된 게임 추천
        
        Args:
            user_id: 사용자 ID
            emotion: 현재 감정 상태 (옵션)
        
        Returns:
            추천 게임 목록
        """
        try:
            # 컨텍스트가 없는 경우를 위한 기본 추천 알고리즘
            recommendations = []
            
            # 감정 기반 필터링
            filtered_games = self._emotion_based_filtering(emotion)
            
            # 사용자 기반 필터링
            user_preferences = self._get_user_preferences(user_id)
            
            # 추천 점수 계산 및 정렬
            for game in filtered_games:
                score = self._calculate_recommendation_score(game, user_preferences, emotion)
                recommendations.append({
                    "game_type": game["game_type"],
                    "name": game["name"],
                    "confidence": score
                })
            
            # 점수 순 정렬
            recommendations.sort(key=lambda x: x["confidence"], reverse=True)
            
            # 로그 기록
            logger.info(f"Generated {len(recommendations)} recommendations for user {user_id}")
            return recommendations[:3]  # 상위 3개만 반환
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            # 기본 추천 반환
            return [{"game_type": "slot", "name": "슬롯머신", "confidence": 0.5}]

    def _apply_context_filters(self, recommendations: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """추가 컨텍스트 기반 필터링 적용"""
        if not context:
            return recommendations

        filtered_recommendations = recommendations.copy()
        
        # 최근 승패 반영
        if "recent_wins" in context:
            for rec in filtered_recommendations:
                if rec["game_type"] in ["slot", "roulette"]:
                    rec["confidence"] *= min(1.2, 1 + context["recent_wins"] * 0.1)
        
        # 세션 길이 반영
        if "session_length" in context:
            session_hours = context["session_length"] / 3600
            if session_hours > 2:
                for rec in filtered_recommendations:
                    if rec["game_type"] == "slot":
                        rec["confidence"] *= 0.8  # 장시간 플레이시 슬롯 선호도 감소
        
        # 신규 유저 반영
        if context.get("new_user", False):
            for rec in filtered_recommendations:
                if rec["game_type"] in ["slot", "dice"]:  # 초보자 친화적 게임
                    rec["confidence"] *= 1.2
        
        return filtered_recommendations
    
    def _emotion_based_filtering(self, emotion: Optional[str]) -> List[Dict[str, Any]]:
        """
        감정에 따른 게임 필터링
        
        Args:
            emotion: 감정 상태
        
        Returns:
            필터링된 게임 목록
        """
        if not emotion:
            return self.games
        
        emotion = emotion.lower() if isinstance(emotion, str) else "neutral"
        
        positive_emotions = [SupportedEmotion.EXCITED.value.lower(), SupportedEmotion.JOY.value.lower()]
        negative_emotions = [SupportedEmotion.FRUSTRATED.value.lower(), 
                           SupportedEmotion.ANGER.value.lower(),
                           SupportedEmotion.SADNESS.value.lower()]

        if emotion in positive_emotions:
            # 긍정적 감정일 때는 모험적인 게임 추천
            return [g for g in self.games if "strategy" in g["tags"]]
        elif emotion in negative_emotions:
            # 부정적 감정일 때는 간단하고 보상이 많은 게임 추천
            return [g for g in self.games if "casual" in g["tags"]]
        else:
            return self.games
    
    def _get_user_preferences(self, user_id: int) -> Dict[str, float]:
        """
        사용자 선호도 조회
        
        Args:
            user_id: 사용자 ID
        
        Returns:
            게임별 선호도 점수
        """
        # 실제로는 DB에서 사용자 히스토리를 조회하여 선호도 계산
        # MVP에서는 간단한 더미 데이터 반환
        return {
            "slot": 0.8,
            "roulette": 0.6,
            "gacha": 0.7,
            "blackjack": 0.5,
            "dice": 0.4
        }
    
    def _calculate_recommendation_score(
        self, 
        game: Dict[str, Any], 
        preferences: Dict[str, float],
        emotion: Optional[str]
    ) -> float:
        """
        추천 점수 계산
        
        Args:
            game: 게임 정보
            preferences: 사용자 선호도
            emotion: 현재 감정
        
        Returns:
            추천 점수 (0~1)
        """
        base_score = preferences.get(game["game_type"], 0.5)
        
        # 감정 보정치
        emotion_modifier = 0.0
        if emotion:
            emotion = emotion.lower() if isinstance(emotion, str) else SupportedEmotion.NEUTRAL.value.lower()
            if emotion in [SupportedEmotion.EXCITED.value.lower(), SupportedEmotion.JOY.value.lower()] and "strategy" in game["tags"]:
                emotion_modifier = 0.2
            elif emotion in [e.value.lower() for e in [SupportedEmotion.FRUSTRATED, SupportedEmotion.ANGER, SupportedEmotion.SADNESS]] and "casual" in game["tags"]:
                emotion_modifier = 0.3
        
        # 약간의 랜덤성 추가 (탐색 촉진)
        random_factor = random.uniform(-0.1, 0.1)
        
        final_score = min(1.0, max(0.0, base_score + emotion_modifier + random_factor))
        return round(final_score, 2)
