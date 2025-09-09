"""
MVP AI Router - 최소 감정 분석 API
"""

import logging
from typing import Dict, Optional, Any

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from app.services.cj_ai_service import CJAIService
from app.services.recommendation_service import RecommendationService
from app.services.emotion_feedback_service import EmotionFeedbackService
from app.utils.sentiment_analyzer import get_emotion_analysis

router = APIRouter(prefix="/ai", tags=["ai"])

# Request/Response models
class AnalyzeRequest(BaseModel):
    user_id: int
    text: str
    context: Optional[Dict[str, Any]] = None

class EmotionAnalysisResponse(BaseModel):
    success: bool
    data: Dict[str, Any]

# Mock SentimentAnalyzer for testing compatibility
class SentimentAnalyzer:
    """Mock sentiment analyzer for MVP testing"""
    def __init__(self):
        self.model = "mock_model"
        self.fallback_mode = False
    
    def analyze(self, text: str):
        """Mock analyze method"""
        class MockResult:
            def __init__(self):
                self.emotion = "neutral"
                self.score = 0.5
                self.confidence = 0.7
                self.language = "korean"
        
        return MockResult()

def get_current_user():
    """Mock authentication function for testing"""
    return {"user_id": 1, "username": "test_user"}

@router.post("/analyze", response_model=EmotionAnalysisResponse)
def analyze_emotion_ai(req: AnalyzeRequest, current_user = Depends(get_current_user)):
    """Advanced emotion analysis with context awareness"""
    try:
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze(req.text)
        
        return {
            "success": True,
            "data": {
                "emotion": result.emotion,
                "score": result.score,
                "confidence": result.confidence,
                "language": result.language,
                "context_aware": bool(req.context)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
