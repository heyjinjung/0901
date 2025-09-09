# cc-webapp/backend/app/routers/user_segments.py
import os
try:
    import redis
except Exception:  # noqa: BLE001
    redis = None
from fastapi import APIRouter, Depends, HTTPException, Path

from pydantic import BaseModel

from .. import models  # Assuming UserSegment model is here
from ..database import SessionLocal  # For DB session
from ..services.user_service import UserService
import logging # For logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Redis Client Configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = None # Initialize as None
try:
    # decode_responses=True is important for getting strings from Redis
    if redis is not None:
        redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
        redis_client.ping()
        logger.info("Successfully connected to Redis.")
except Exception as e:  # noqa: BLE001
    logger.warning(f"Could not connect to Redis: {e}. Recommendation endpoint will use default streak_count (0).")
    redis_client = None # Explicitly set to None on failure


# Dependency to get DB session
def get_db():
    with SessionLocal() as db:
        yield db

def get_user_service(db = Depends(get_db)) -> UserService:
    return UserService(db)

class RecommendationResponse(BaseModel):
    user_id: int
    rfm_group: str | None # Can be None if user has no segment yet and we don't default
    risk_profile: str | None # Can be None
    streak_count: int
    recommended_reward_probability: float
    recommended_time_window: str

@router.get(
    "/user-segments/{user_id}/recommendation",
    response_model=RecommendationResponse,
    tags=["user_segments", "recommendations"] # Added recommendations tag
)
async def get_user_recommendation(
    user_id: int = Path(..., title="The ID of the user to get recommendations for", ge=1),
    db = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
):
    try:
        user_service.get_user_or_error(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    # Fetch existing segment or create a default one via the service layer
    user_segment = user_service.get_or_create_segment(user_id)

    rfm_group = user_segment.rfm_group or "Low"
    risk_profile = user_segment.risk_profile or "Unknown"
    logger.info(
        f"User {user_id}: RFM='{rfm_group}', Risk='{risk_profile}' returned from UserService."
    )


    streak_count = 0
    if redis_client:
        try:
            streak_key = f"user:{user_id}:streak_count"
            streak_val = redis_client.get(streak_key)
            if streak_val is not None:
                streak_count = int(streak_val)
                logger.info(f"User {user_id}: Streak count {streak_count} from Redis.")
            else:
                logger.info(f"Streak count for user {user_id} not found in Redis (key: {streak_key}), defaulting to 0.")
        except Exception as e:
            logger.warning(f"Redis error while fetching streak count for user {user_id} (key: {streak_key}): {e}. Defaulting to 0.")
        except ValueError: # Handle case where streak_val is not a valid int
            logger.warning(f"Invalid streak count value '{streak_val}' in Redis for user {user_id} (key: {streak_key}), defaulting to 0.")
    else:
        logger.warning("Redis client not available. Defaulting streak_count to 0 for user {user_id}.")

    # Recommendation logic (placeholder based on 02_data_personalization_en.md)
    # This should be replaced with the precise logic from the document.
    if rfm_group == "Whale" and risk_profile == "High-Risk": # Note: "High-Risk" might need to be "High" depending on actual values
        recommended_reward_probability = 0.75
        recommended_time_window = "next 2 hours"
    elif rfm_group == "Medium" and risk_profile == "Low-Risk": # Note: "Low-Risk" might need to be "Low"
        recommended_reward_probability = 0.50
        recommended_time_window = "next 6 hours"
    elif rfm_group == "Low":
        recommended_reward_probability = 0.25
        recommended_time_window = "next 24 hours"
    else:  # Default or other combinations
        logger.info(f"User {user_id}: Using default recommendation due to RFM/Risk combo: RFM='{rfm_group}', Risk='{risk_profile}'.")
        recommended_reward_probability = 0.10
        recommended_time_window = "any time"

    # Adjust probability based on streak_count (example: +1% per day of streak, cap at 95%, min 5%)
    probability_boost = streak_count * 0.01
    recommended_reward_probability += probability_boost
    recommended_reward_probability = min(recommended_reward_probability, 0.95) # Cap
    recommended_reward_probability = max(recommended_reward_probability, 0.05) # Floor

    logger.info(f"User {user_id}: Final recommendation - Prob: {recommended_reward_probability:.4f}, Window: '{recommended_time_window}'. (Base prob: {recommended_reward_probability-probability_boost:.2f}, Streak boost: {probability_boost:.2f})")

    return RecommendationResponse(
        user_id=user_id,
        rfm_group=rfm_group,
        risk_profile=risk_profile,
        streak_count=streak_count,
        recommended_reward_probability=round(recommended_reward_probability, 4), # Round to 4 decimal places
        recommended_time_window=recommended_time_window
    )

# Ensure this router is included in app/main.py:
# from .routers import user_segments
# app.include_router(user_segments.router, prefix="/api", tags=["user_segments"])
