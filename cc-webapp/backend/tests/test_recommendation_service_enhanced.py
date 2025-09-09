"""
Enhanced tests for RecommendationService following project testing standards
"""

import pytest
from unittest.mock import Mock, patch
from typing import List, Dict, Any

from app.services.recommendation_service import RecommendationService, FinalRecommendation
from app.models import SupportedEmotion


class TestRecommendationService:
    """RecommendationService 단위 테스트"""
    
    def setup_method(self):
        """각 테스트 전 실행되는 설정"""
        self.mock_db = Mock()
        self.service = RecommendationService(db=self.mock_db)
    
    def test_init_service(self):
        """서비스 초기화 테스트"""
        assert self.service.db == self.mock_db
        assert isinstance(self.service.games, list)
        assert len(self.service.games) > 0
    
    def test_get_recommendations_with_emotion(self):
        """감정 기반 추천 테스트"""
        user_id = 1
        emotion = SupportedEmotion.EXCITED
        context = {"session_length": 1800}
        
        result = self.service.get_recommendations(user_id, emotion, context)
        
        assert isinstance(result, list)
        assert len(result) <= 3  # 최대 3개 추천
    
    def test_get_personalized_recommendations_exception_handling(self):
        """개인화 추천 예외 처리 테스트"""
        user_id = 1
        emotion = "invalid"
        
        with patch.object(self.service, '_emotion_based_filtering') as mock_filter:
            mock_filter.side_effect = Exception("Test error")
            
            result = self.service.get_personalized_recommendations(user_id, emotion)
            
            # 예외 발생 시 기본 추천 반환 (서비스 안정성을 위해)
            assert len(result) == 1
            assert result[0]["game_type"] == "slot"
            assert result[0]["name"] == "슬롯머신"
            assert result[0]["confidence"] == 0.5
    
    def test_emotion_based_filtering_positive_emotion(self):
        """긍정적 감정 기반 필터링 테스트"""
        emotion = "excited"
        
        result = self.service._emotion_based_filtering(emotion)
        
        assert isinstance(result, list)
        # 긍정적 감정일 때 전략 게임 추천
        strategy_games = [g for g in result if "strategy" in g["tags"]]
        assert len(strategy_games) > 0
    
    def test_emotion_based_filtering_neutral_emotion(self):
        """중립 감정 기반 필터링 테스트"""
        emotion = "neutral"
        
        result = self.service._emotion_based_filtering(emotion)
        
        assert isinstance(result, list)
        # 중립 감정일 때 모든 게임 반환
        assert len(result) == len(self.service.games)
    
    def test_get_user_preferences(self):
        """사용자 선호도 조회 테스트"""
        user_id = 1
        
        result = self.service._get_user_preferences(user_id)
        
        assert isinstance(result, dict)
        # MVP에서는 더미 데이터 반환
        expected_keys = {"slot", "roulette", "gacha", "blackjack", "dice"}
        assert set(result.keys()) == expected_keys
        
        # 모든 값이 0.0 ~ 1.0 사이여야 함
        for game_type, preference in result.items():
            assert 0.0 <= preference <= 1.0
    
    def test_calculate_recommendation_score_with_preference(self):
        """선호도 기반 추천 점수 계산 테스트"""
        game = {"game_type": "roulette", "name": "룰렛", "tags": ["luck"]}
        user_preferences = {"roulette": 0.7}
        emotion = ""
        
        # 랜덤 요소 제거를 위해 패치
        with patch('app.services.recommendation_service.random.uniform', return_value=0.0):
            score = self.service._calculate_recommendation_score(game, user_preferences, emotion)
            
            assert isinstance(score, float)
            assert 0.0 <= score <= 1.0
            # 기본 점수는 사용자 선호도 기반
            assert score == 0.7
    
    def test_calculate_recommendation_score_boundary_values(self):
        """경계값 추천 점수 계산 테스트"""
        game_min = {"game_type": "unknown", "name": "알 수 없음", "tags": []}
        user_preferences_min = {}
        emotion_none = ""
        
        with patch('app.services.recommendation_service.random.uniform', return_value=0.0):
            score_min = self.service._calculate_recommendation_score(
                game_min, user_preferences_min, emotion_none
            )
            assert score_min >= 0.0
    
    def test_full_recommendation_flow_with_emotion(self):
        """전체 추천 플로우 통합 테스트 (감정 포함)"""
        user_id = 1
        emotion = SupportedEmotion.EXCITED
        context = {"session_length": 1800}
        
        result = self.service.get_recommendations(user_id, emotion, context)
        
        assert isinstance(result, list)
        assert len(result) <= 3  # 최대 3개 추천
        
        # 각 추천은 필수 필드를 가져야 함
        for rec in result:
            assert "game_type" in rec
            assert "name" in rec
            assert "confidence" in rec
            assert isinstance(rec["confidence"], (int, float))
            assert 0.0 <= rec["confidence"] <= 1.0
    
    def test_different_emotions_produce_different_results(self):
        """다른 감정 상태가 다른 추천 결과를 생성하는지 테스트"""
        user_id = 4
        context = {}
        
        # 랜덤성 제거를 위해 시드 고정
        with patch('app.services.recommendation_service.random.uniform', return_value=0.0):
            result_excited = self.service.get_recommendations(
                user_id, SupportedEmotion.EXCITED, context
            )
            result_frustrated = self.service.get_recommendations(
                user_id, SupportedEmotion.FRUSTRATED, context
            )
            
            # 다른 감정은 다른 추천을 생성해야 함
            if len(result_excited) > 0 and len(result_frustrated) > 0:
                # 적어도 신뢰도나 순서가 달라야 함
                excited_confidence = [r["confidence"] for r in result_excited]
                frustrated_confidence = [r["confidence"] for r in result_frustrated]
                
                # 완전히 동일하지 않아야 함
                assert excited_confidence != frustrated_confidence
