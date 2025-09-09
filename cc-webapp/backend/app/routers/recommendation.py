from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, field_validator # Ensure all are imported

from ..emotion_models import EmotionResult, SupportedEmotion, SupportedLanguage
from ..services.recommendation_service import RecommendationService
from app.schemas import FinalRecommendation
from app.auth.simple_auth import get_current_user_id
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/recommend", tags=["Recommendations"])

def get_db_dummy():
    try:
        logger.debug("Dummy DB session created for recommendation router.")
        yield None
    finally: logger.debug("Dummy DB session closed for recommendation router.")

def get_recommendation_service(db: Session = Depends(get_db_dummy)) -> RecommendationService:
    return RecommendationService(db=db)

class PersonalizedRecommendationRequest(BaseModel):
    user_id: int
    current_emotion_data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    limit: int = Field(default=5, gt=0, le=20)
    
    @field_validator('current_emotion_data', mode='before')
    @classmethod
    def parse_emotion_data(cls, v_dict): # Removed values parameter as it's not needed in V2
        if not v_dict: # Handle case where current_emotion_data might be optional or empty
            raise ValueError("current_emotion_data must be provided")
        # This validator is intended to ensure the input dict is valid for EmotionResult instantiation
        # It doesn't return an EmotionResult instance itself, Pydantic does that.
        # Basic checks can be done here if needed, e.g. presence of required keys.
        if not all(k in v_dict for k in ['emotion', 'score', 'confidence', 'language']):
             raise ValueError("current_emotion_data missing required fields (emotion, score, confidence, language)")
        return v_dict


@router.post("/personalized", response_model=List[FinalRecommendation],
             summary="Get Personalized Recommendations")
async def get_personalized_recommendations_endpoint(
    request_data: PersonalizedRecommendationRequest = Body(...),
    db: Optional[Session] = Depends(get_db_dummy) # Allow Optional[Session] for dummy
):
    logger.info(f"Received personalized recommendation request for user {request_data.user_id}")

    try:
        # Convert incoming dict to SupportedLanguage and SupportedEmotion enums
        # Pydantic v2 should handle this conversion automatically if types are correct in EmotionResult
        # Forcing it here based on prompt's note.
        emotion_data_for_model = request_data.current_emotion_data.copy()
        if 'language' in emotion_data_for_model and isinstance(emotion_data_for_model['language'], str):
            emotion_data_for_model['language'] = SupportedLanguage[emotion_data_for_model['language'].upper()]
        if 'emotion' in emotion_data_for_model and isinstance(emotion_data_for_model['emotion'], str):
            emotion_data_for_model['emotion'] = SupportedEmotion[emotion_data_for_model['emotion'].upper()]

        current_emotion = EmotionResult(**emotion_data_for_model)
    except (KeyError, ValueError) as e: # Catch specific errors during enum conversion or model instantiation
        logger.error(f"Router: Error parsing current_emotion_data for user {request_data.user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Invalid current_emotion_data format: {str(e)}")
    except Exception as e: # Catch all other unexpected errors
        logger.error(f"Router: Unexpected error processing emotion data for user {request_data.user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Unexpected error in current_emotion_data: {str(e)}")
    try:
        recommendation_service = RecommendationService(db=db)
        recommendations = recommendation_service.get_personalized_recommendations(
            user_id=request_data.user_id, emotion=None  # Í∞êÏ†ï ?∞Ïù¥?∞Îäî ?îÏ≤≠??current_emotion_dataÎ°??¥Î? Ï≤òÎ¶¨??
        )
    except Exception as e:
        logger.exception(f"Error generating recommendations for user {request_data.user_id}")
        raise HTTPException(status_code=500, detail="Failed to generate recommendations.")

    if not recommendations:
        logger.info(f"No recommendations generated for user {request_data.user_id}.")

    return recommendations


@router.get("/personalized")
async def get_personalized_recommendations_v2(
    user_id: int = Query(..., description="?¨Ïö©??ID"),
    emotion: Optional[str] = Query(None, description="?ÑÏû¨ Í∞êÏ†ï ?ÅÌÉú"),
    current_user_id = Depends(get_current_user_id),
    service: RecommendationService = Depends(get_recommendation_service)
):
    """
    Í∞úÏù∏?îÎêú Í≤åÏûÑ Ï∂îÏ≤ú???úÍ≥µ?©Îãà??
    
    Args:
        user_id: ?¨Ïö©??ID
        emotion: ?ÑÏû¨ Í∞êÏ†ï ?ÅÌÉú (?µÏÖò)
    
    Returns:
        Ï∂îÏ≤ú Í≤åÏûÑ Î™©Î°ù
    """
    try:        # ?ÑÏû¨ ?¨Ïö©??Í∂åÌïú ?ïÏù∏
        if user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this resource")# Ï∂îÏ≤ú ?úÎπÑ???∏Ï∂ú - ?¨Î∞îÎ•?Îß§Í∞úÎ≥Ä???¨Ïö©
        recommendations = service.get_personalized_recommendations(user_id=user_id, emotion=emotion)
        
        return {
            "success": True,
            "data": recommendations
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to get recommendations: {str(e)}"
        }
