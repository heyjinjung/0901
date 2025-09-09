"""
테스트 수정을 위한 임시 파일
"""
import os
import pytest
from unittest.mock import Mock, patch
from app.utils.sentiment_analyzer import SentimentAnalyzer
from app.models import SupportedEmotion
from app.schemas.ai_schemas import EmotionResult, SupportedLanguage

class TestSentimentAnalyzer:
    @patch('app.utils.sentiment_analyzer.call_llm_fallback')
    def test_llm_fallback_failure_cascade(self, mock_llm):
        """Test cascading failures in LLM fallback"""
        # Simulate LLM service failures
        mock_llm.side_effect = [
            Exception("OpenAI API rate limit"),
            Exception("Claude API timeout"),
            Exception("Network error")
        ]
        
        # 낮은 신뢰도 결과를 반환하도록 analyze_emotion_basic을 모킹
        low_confidence_result = EmotionResult(
            emotion=SupportedEmotion.NEUTRAL,
            score=0.5, 
            confidence=0.5,  # 임계값 미만의 신뢰도로 설정
            language=SupportedLanguage.ENGLISH
        )
          # 환경 변수 패치하여 LLM 폴백 활성화
        with patch.dict(os.environ, {'LLM_FALLBACK_ENABLED': 'true'}):
            with patch('app.utils.sentiment_analyzer.analyze_emotion_basic', return_value=low_confidence_result):
                with patch('app.utils.sentiment_analyzer.load_local_model') as mock_load:
                    # Create a proper mock EmotionResult with all expected attributes
                    mock_result = EmotionResult(
                    emotion=SupportedEmotion.NEUTRAL,
                    score=0.5,
                    confidence=0.6,
                    language=SupportedLanguage.ENGLISH,
                    fallback_attempted=True
                )
                mock_model = Mock()
                mock_model.predict.return_value = mock_result
                mock_load.return_value = mock_model
                
                analyzer = SentimentAnalyzer()
                # Should fall back to local model result when LLM fails
                result = analyzer.analyze("Ambiguous text")
                
                assert result.emotion == SupportedEmotion.NEUTRAL
                assert result.confidence == 0.6
                # Should have fallback_used flag
                assert result.fallback_attempted == True
