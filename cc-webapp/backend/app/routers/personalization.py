from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime



from app.database import get_db
from app.services.rfm_service import RFMService, RFMScore
from app.services.ltv_service import LTVService
from app.services.personalization_service import PersonalizationService
from app.repositories.game_repository import GameRepository

router = APIRouter(prefix="/personalization", tags=["personalization"])


def get_user_from_token() -> int:
    return 1


class GameRecommendation(BaseModel):
    game_type: str
    recommended_bet: int
    win_probability: float
    expected_return: float
    reason: str


class UserProfile(BaseModel):
    user_id: int
    segment: str
    rfm_scores: Dict[str, int]
    ltv_prediction: Dict[str, float]
    churn_risk: str
    last_activity: datetime | None


@router.get("/recommendations", response_model=List[GameRecommendation])
async def get_recommendations(
    user_id: int = Depends(get_user_from_token),
    db = Depends(get_db),
):
    game_repository = GameRepository()
    rfm_service = RFMService(db, game_repository)
    ltv_service = LTVService(db, game_repository)
    personalization = PersonalizationService(db, game_repository)

    rfm = rfm_service.calculate_rfm(user_id)
    segment = rfm.segment
    ltv = {"prediction": 0.0}  # Placeholder
    recs = [
        GameRecommendation(
            game_type="slot", 
            recommended_bet=100, 
            win_probability=0.5, 
            expected_return=50.0, 
            reason="Based on user segment"
        )
    ]
    return recs


@router.get("/profile", response_model=UserProfile)
async def get_user_profile(
    user_id: int = Depends(get_user_from_token),
    db = Depends(get_db),
):
    game_repository = GameRepository()
    rfm_service = RFMService(db, game_repository)
    ltv_service = LTVService(db, game_repository)
    personalization = PersonalizationService(db, game_repository)

    rfm = rfm_service.calculate_rfm(user_id)
    segment = str(rfm.segment)
    ltv = ltv_service.predict_ltv(user_id)
    
    # Determine churn risk based on RFM score
    rfm_score = float(rfm.rfm_score)
    churn = (
        "High" if rfm_score < 0.3 else
        "Medium" if rfm_score < 0.6 else
        "Low"
    )

    return UserProfile(
        user_id=user_id,
        segment=segment,
        rfm_scores={
            "recency": int(rfm.recency),
            "frequency": int(rfm.frequency),
            "monetary": int(rfm.monetary)
        },
        ltv_prediction=ltv,
        churn_risk=churn,
        last_activity=datetime.now()
    )


@router.post("/feedback")
async def collect_feedback(
    recommendation_id: str,
    feedback_type: str,
    user_id: int = Depends(get_user_from_token),
):
    return {"status": "ok"}
