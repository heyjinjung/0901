from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

from ..utils.sentiment_analyzer import EmotionResult, SupportedEmotion, SupportedLanguage
from ..schemas import FeedbackResponse
from ..services.emotion_feedback_service import EmotionFeedbackService 
from ..dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/feedback", tags=["Feedback"])

class EmotionFeedbackRequest(BaseModel):
    emotion_result_data: Dict[str, Any] = Field(..., description="EmotionResult as dict.")
    user_segment: Optional[str] = "GENERAL"
    mission_type: Optional[str] = "GENERAL"
    context_text: Optional[str] = None

def get_emotion_feedback_service():
    try: return EmotionFeedbackService()
    except Exception as e: logger.error(f"Failed to init EmotionFeedbackService: {e}", exc_info=True); return None

@router.post("/emotion_based", response_model=Optional[FeedbackResponse], summary="Get Personalized Emotion-Based Feedback")
async def get_emotion_based_feedback_endpoint(
    request_data: EmotionFeedbackRequest = Body(...),
    feedback_service: Optional[EmotionFeedbackService] = Depends(get_emotion_feedback_service)
):
    logger.info(f"Received feedback request for user_segment: {request_data.user_segment}")
    if not feedback_service:
        raise HTTPException(status_code=503, detail="Feedback service unavailable.")

    try:
        # Convert relevant fields in emotion_result_data to enums before passing to EmotionResult
        raw_emotion_data = request_data.emotion_result_data.copy() # Work on a copy
        if 'language' in raw_emotion_data and isinstance(raw_emotion_data['language'], str):
            raw_emotion_data['language'] = SupportedLanguage[raw_emotion_data['language'].upper()]
        if 'emotion' in raw_emotion_data and isinstance(raw_emotion_data['emotion'], str):
            raw_emotion_data['emotion'] = SupportedEmotion[raw_emotion_data['emotion'].upper()]

        parsed_emotion_result = EmotionResult(**raw_emotion_data)
    except (KeyError, ValueError, TypeError) as e: # Catch specific errors
        logger.error(f"Error parsing emotion_result_data: {e}, input: {request_data.emotion_result_data}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Invalid emotion_result_data: {e}")

    try:
        feedback = feedback_service.get_emotion_feedback(
            emotion_result=parsed_emotion_result, user_segment=request_data.user_segment,
            mission_type=request_data.mission_type, context_text=request_data.context_text
        )
    except Exception as e:
        logger.exception("Error generating emotion feedback in router.")
        raise HTTPException(status_code=500, detail="Failed to generate feedback.")

    if not feedback: logger.warning("No feedback generated for context.")
    return feedback

@router.post("/generate")
async def generate_feedback(
    request: Dict[str, Any],
    current_user = Depends(get_current_user),
    service: EmotionFeedbackService = Depends(get_emotion_feedback_service)
):
    """
    Generate emotion-based feedback for user
    
    Args:
        request: Feedback request data
            - user_id: User ID
            - emotion: Emotion state
            - segment: User segment
            - context: Additional context information
    
    Returns:
        Feedback response object
    """
    try:
        user_id = request.get("user_id")
        emotion = request.get("emotion")
        segment = request.get("segment", "Medium")
        context = request.get("context", {})
        
        # Validate required fields
        if not user_id or not emotion:
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Check current user authorization
        if user_id != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Not authorized to access this resource")
        
        # Generate feedback
        feedback = service.generate_feedback(emotion, segment, context)
        
        return {
            "success": True,
            "data": feedback
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to generate feedback: {str(e)}"
        }
