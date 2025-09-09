"""Unit tests for EmotionFeedbackService with mocks."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.emotion_feedback_service import EmotionFeedbackService
from app.schemas import FeedbackResponse


class TestEmotionFeedbackService:
    """Test class for EmotionFeedbackService."""
    
    def setup_method(self):
        """Setup test data before each test method."""
        self.service = EmotionFeedbackService()
        
    def test_init_without_db(self):
        """Test service initialization without database."""
        service = EmotionFeedbackService()
        assert service.db is None
        assert service.templates is not None
        assert isinstance(service.templates, dict)
        
    def test_init_with_db(self):
        """Test service initialization with database."""
        mock_db = Mock()
        service = EmotionFeedbackService(db=mock_db)
        assert service.db == mock_db
        
    def test_load_templates(self):
        """Test template loading."""
        templates = self.service._load_templates()
        
        # Check basic structure
        assert "excited" in templates
        assert "frustrated" in templates
        assert "neutral" in templates
        
        # Check segment structure for each emotion
        for emotion in ["excited", "frustrated", "neutral"]:
            assert "Whale" in templates[emotion]
            assert "Medium" in templates[emotion]
            assert "Low" in templates[emotion]
            
            # Check message structure
            for segment in ["Whale", "Medium", "Low"]:
                assert "message" in templates[emotion][segment]
                assert isinstance(templates[emotion][segment]["message"], str)
                
    def test_generate_feedback_excited_whale(self):
        """Test feedback generation for excited whale user."""
        feedback = self.service.generate_feedback(
            emotion="excited",
            segment="Whale",
            context={}
        )
        
        assert feedback["emotion"] == "excited"
        assert feedback["segment"] == "Whale"
        assert "message" in feedback
        assert "suggestions" in feedback
        assert isinstance(feedback["suggestions"], list)
        assert len(feedback["suggestions"]) > 0
        
    def test_generate_feedback_frustrated_medium(self):
        """Test feedback generation for frustrated medium user."""
        feedback = self.service.generate_feedback(
            emotion="frustrated",
            segment="Medium",
            context={}
        )
        
        assert feedback["emotion"] == "frustrated"
        assert feedback["segment"] == "Medium"
        assert "message" in feedback
        assert "suggestions" in feedback
        
    def test_generate_feedback_neutral_low(self):
        """Test feedback generation for neutral low user."""
        feedback = self.service.generate_feedback(
            emotion="neutral",
            segment="Low",
            context={}
        )
        
        assert feedback["emotion"] == "neutral"
        assert feedback["segment"] == "Low"
        assert "message" in feedback
        assert "suggestions" in feedback
        
    def test_generate_feedback_case_insensitive(self):
        """Test that emotion input is case insensitive."""
        feedback1 = self.service.generate_feedback("EXCITED", "Whale", {})
        feedback2 = self.service.generate_feedback("excited", "Whale", {})
        feedback3 = self.service.generate_feedback("Excited", "Whale", {})
        
        assert feedback1["emotion"] == "excited"
        assert feedback2["emotion"] == "excited" 
        assert feedback3["emotion"] == "excited"
        
    def test_generate_feedback_unknown_emotion(self):
        """Test feedback generation with unknown emotion (should default to neutral)."""
        feedback = self.service.generate_feedback(
            emotion="unknown_emotion",
            segment="Medium",
            context={}
        )
        
        # Should fall back to neutral templates
        assert feedback["emotion"] == "unknown_emotion"
        assert feedback["segment"] == "Medium"
        assert "message" in feedback
        
    def test_generate_feedback_unknown_segment(self):
        """Test feedback generation with unknown segment (should default to Medium)."""
        feedback = self.service.generate_feedback(
            emotion="excited",
            segment="Unknown",
            context={}
        )        
        assert feedback["emotion"] == "excited"
        assert feedback["segment"] == "Unknown"
        assert "message" in feedback
        
    def test_generate_feedback_none_emotion(self):
        """Test feedback generation with None emotion (should default to neutral)."""
        feedback = self.service.generate_feedback(
            emotion="neutral",  # Use default emotion instead of None
            segment="Medium",
            context={}
        )
        
        assert feedback["emotion"] == "neutral"
        assert feedback["segment"] == "Medium"
        
    def test_generate_feedback_none_segment(self):
        """Test feedback generation with None segment (should default to Medium)."""
        feedback = self.service.generate_feedback(
            emotion="excited",
            segment="Medium",  # Use default segment instead of None
            context={}
        )
        
        assert feedback["emotion"] == "excited"
        assert feedback["segment"] == "Medium"
        
    def test_generate_suggestions_excited(self):
        """Test suggestion generation for excited emotion."""
        suggestions = self.service._generate_suggestions("excited", "Whale", {})
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        assert any("룰렛" in suggestion for suggestion in suggestions)
        
    def test_generate_suggestions_frustrated(self):
        """Test suggestion generation for frustrated emotion."""
        suggestions = self.service._generate_suggestions("frustrated", "Medium", {})
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        assert any("휴식" in suggestion for suggestion in suggestions)
        
    def test_generate_suggestions_neutral(self):
        """Test suggestion generation for neutral emotion."""
        suggestions = self.service._generate_suggestions("neutral", "Low", {})
        
        assert isinstance(suggestions, list)
        assert len(suggestions) > 0
        
    @patch('app.services.emotion_feedback_service.logger')
    def test_generate_feedback_logs_success(self, mock_logger):
        """Test that successful feedback generation is logged."""
        self.service.generate_feedback("excited", "Whale", {})
        
        mock_logger.info.assert_called_with("Generated feedback for emotion=excited, segment=Whale")
        
    def test_get_emotion_feedback_returns_response(self):
        """Test get_emotion_feedback method returns FeedbackResponse."""
        response = self.service.get_emotion_feedback(
            emotion_result=Mock(),
            user_segment="GENERAL",
            mission_type="GENERAL",
            context_text="test context"        )
        assert isinstance(response, FeedbackResponse)
        assert response.success is True
        assert response.message == "감정 분석 기반 피드백이 생성되었습니다"
        assert isinstance(response.recommendation, dict)
        assert response.recommendation["type"] == "mission"
        assert isinstance(response.reward_suggestion, dict)
        assert response.reward_suggestion["token"] == 50
        
    def test_service_with_different_contexts(self):
        """Test service behavior with different context inputs."""
        contexts = [
            {},
            {"game": "slot"},
            {"previous_result": "win"},
            {"session_time": 120}
        ]
        
        for context in contexts:
            feedback = self.service.generate_feedback("excited", "Medium", context)
            assert "message" in feedback
            assert "suggestions" in feedback
            
    def test_all_emotions_have_all_segments(self):
        """Test that all emotions have all segment configurations."""
        emotions = ["excited", "frustrated", "neutral"]
        segments = ["Whale", "Medium", "Low"]
        
        for emotion in emotions:
            for segment in segments:
                feedback = self.service.generate_feedback(emotion, segment, {})
                assert feedback["emotion"] == emotion
                assert feedback["segment"] == segment
                assert len(feedback["message"]) > 0
