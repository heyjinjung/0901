from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional

from ..services.recommendation_service import RecommendationService

router = APIRouter(prefix="/recommend", tags=["recommend"])

@router.get("/personalized")
async def get_personalized_recommendations(
    user_id: int = Query(..., description="?�용??ID"),
    emotion: Optional[str] = Query(None, description="?�재 감정 ?�태"),
    segment: Optional[str] = Query(None, description="?�용???�그먼트")
):
    """개인?�된 게임 추천"""
    try:
        service = RecommendationService()
        recommendations = service.get_personalized_recommendations(
            user_id=user_id,
            emotion=emotion,
            segment=segment
        )
        
        return {
            "success": True,
            "data": {
                "recommendations": [
                    {
                        "game_type": rec.game_type,
                        "confidence": rec.confidence,
                        "reason": rec.reason,
                        "metadata": rec.metadata
                    }
                    for rec in recommendations
                ]
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")
