# cc-webapp/backend/app/routers/unlock.py
from fastapi import APIRouter, Depends, HTTPException, Query

from sqlalchemy import desc # Correct import for desc
from pydantic import BaseModel, ConfigDict
from datetime import datetime
import logging # For logging

from .. import models  # Should import User, UserReward, AdultContent, UserSegment
from ..database import get_db
from ..services.user_service import UserService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/unlock", tags=["Unlock"])

# --- Configuration ---
MAX_UNLOCK_STAGE = 3 # Define this based on your content stages. Consider making it configurable.

# --- Dependencies ---
def get_user_service(db = Depends(get_db)) -> UserService:
    return UserService(db)

# --- Pydantic Models ---
class UnlockResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    stage: int
    name: str # Added name from AdultContent
    description: str | None # Added description
    thumbnail_url: str | None
    media_url: str | None
    # message: str | None = None # Optional: for any accompanying message

# --- Helper Functions ---
def get_segment_level(rfm_group: str | None) -> int:
    """Maps RFM group string to a numerical level."""
    if rfm_group == "Whale":
        return 3
    elif rfm_group == "Medium":
        return 2
    elif rfm_group == "Low":
        return 1
    logger.debug(f"Unknown RFM group '{rfm_group}' received, defaulting to level 0.")
    return 0 # Default for None or Unknown RFM groups

# --- API Endpoint ---
# Canonical path is exactly '/api/unlock' to avoid duplicate '/api/unlock/unlock'
@router.get("", response_model=UnlockResponse)
async def attempt_content_unlock(
    user_id: int = Query(..., description="ID of the user attempting to unlock content"),
    db = Depends(get_db),
    user_service: UserService = Depends(get_user_service)
):
    # 1. Fetch User record with unified error handling
    try:
        user_service.get_user_or_error(user_id)
    except ValueError as e:
        logger.warning(f"Attempt to unlock content for non-existent user_id: {user_id}")
        raise HTTPException(status_code=404, detail=str(e))    # 2. Query for the latest UserReward with reward_type="CONTENT_UNLOCK"
    latest_unlock_reward = db.query(models.UserReward).filter(
        models.UserReward.user_id == user_id,
        models.UserReward.reward_type == "CONTENT_UNLOCK"
    ).order_by(desc(models.UserReward.awarded_at)).first() # Order by awarded_at to get the latest    last_stage_unlocked = 0
    if latest_unlock_reward is not None and getattr(latest_unlock_reward, 'reward_value', None) is not None:
        try:
            # Assuming reward_value stores the stage number as a string
            last_stage_unlocked = int(str(latest_unlock_reward.reward_value))
        except (ValueError, TypeError):
            logger.error(
                f"Could not parse last_stage_unlocked from UserReward.reward_value='{latest_unlock_reward.reward_value}' for user {user_id}. Defaulting to 0."
            )
            # This indicates a data integrity issue or a different storage format than expected.
            last_stage_unlocked = 0 # Default to 0 if parsing fails

    logger.info(f"User {user_id}: Last stage unlocked = {last_stage_unlocked}.")

    # 3. Compute next_stage
    next_stage_to_unlock = last_stage_unlocked + 1
    if next_stage_to_unlock > MAX_UNLOCK_STAGE:
        logger.info(f"User {user_id}: All stages already unlocked (last stage {last_stage_unlocked}, max stage {MAX_UNLOCK_STAGE}).")
        raise HTTPException(status_code=400, detail="All content stages already unlocked or no further stages available.")

    # 4. Fetch AdultContent row for next_stage_to_unlock
    adult_content_item = db.query(models.AdultContent).filter(models.AdultContent.stage == next_stage_to_unlock).first()
    if not adult_content_item:
        logger.error(f"Content for stage {next_stage_to_unlock} not found in adult_content table.")
        raise HTTPException(status_code=404, detail=f"Content for stage {next_stage_to_unlock} not found.")    # 5. Verify user segment meets required_segment_level on AdultContent
    user_segment = db.query(models.UserSegment).filter(models.UserSegment.user_id == user_id).first()

    current_user_segment_level = 0  # Default to lowest if no segment info
    if not user_segment:
        logger.warning(f"User segment data for user_id {user_id} not found. Assuming lowest segment level (0).")
    else:
        current_user_segment_level = get_segment_level(getattr(user_segment, 'rfm_group', None))
        logger.info(f"User {user_id}: Current segment level = {current_user_segment_level} (from RFM group '{getattr(user_segment, 'rfm_group', None)}').")

    required_content_level = getattr(adult_content_item, 'required_segment_level', 0)
    logger.info(f"Content stage {next_stage_to_unlock} requires segment level {required_content_level}.")

    if current_user_segment_level < required_content_level:
        logger.warning(
            f"User {user_id} (segment level {current_user_segment_level}) failed to unlock stage {next_stage_to_unlock} (requires level {required_content_level})."
        )
        raise HTTPException(
            status_code=403,
            detail=(
                f"User current segment level ({current_user_segment_level}) does not meet the required level ({required_content_level}) to unlock content stage {next_stage_to_unlock}"
            )
        )

    # 6. Insert a new UserReward to mark this stage as unlocked
    new_reward = models.UserReward(
        user_id=user_id,
        reward_type="CONTENT_UNLOCK",
        reward_value=str(next_stage_to_unlock), # Store stage as string
        awarded_at=datetime.utcnow(),
        trigger_action_id=None # This unlock is direct
    )
    db.add(new_reward)
    db.commit()
    db.refresh(new_reward)
    # db.refresh(adult_content_item) # Not strictly necessary as we're not changing adult_content_item

    logger.info(f"User {user_id} successfully unlocked content stage {next_stage_to_unlock}.")    # 7. Return response with details of the unlocked content
    return UnlockResponse(
        stage=next_stage_to_unlock,  # Use the variable we already computed
        name=getattr(adult_content_item, 'name', ''),
        description=getattr(adult_content_item, 'description', None),
        thumbnail_url=getattr(adult_content_item, 'thumbnail_url', None),
        media_url=getattr(adult_content_item, 'media_url', None)
    )

# Ensure this router is included in app/main.py:
# from .routers import unlock
# app.include_router(unlock.router, prefix="/api", tags=["unlock"])
