"""VIP Daily Claim API
Provides daily VIP point claim with idempotency & once-per-day enforcement.
"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..dependencies import get_current_user
from ..models.auth_models import User
from ..models.game_models import UserReward
from ..database import get_db
from ..utils.redis import get_redis_manager

router = APIRouter(prefix="/api/vip", tags=["VIP"])  # add to main app include

# Configurable daily award values (simple constants for now)
VIP_DAILY_POINTS = 50
VIP_DAILY_GOLD = 0  # If later we decide to also grant small gold
VIP_DAILY_XP = 0

class VipClaimResponse(BaseModel):
    awarded_points: int
    new_vip_points: int
    claimed_at: datetime
    idempotent: bool

class VipStatusResponse(BaseModel):
    claimed_today: bool
    vip_points: int
    last_claim_at: datetime | None = None

@router.get("/status", response_model=VipStatusResponse)
async def vip_status(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    today = datetime.utcnow().date().isoformat()
    idempotency_key = f"vip:{current_user.id}:{today}"
    reward = db.query(UserReward).filter(UserReward.user_id == current_user.id, UserReward.idempotency_key == idempotency_key).first()
    claimed = reward is not None
    return VipStatusResponse(
        claimed_today=claimed,
        vip_points=current_user.vip_points or 0,
    last_claim_at=reward.claimed_at if reward else None,
    )

@router.post("/claim", response_model=VipClaimResponse)
async def claim_vip_daily(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    today = datetime.utcnow().date().isoformat()
    idempotency_key = f"vip:{current_user.id}:{today}"
    redis_flag_key = f"vip_claimed:{current_user.id}:{today}"
    r = None
    try:
        # RedisManager는 redis_client 속성을 사용합니다.
        mgr = get_redis_manager()
        r = getattr(mgr, 'redis_client', None)
        if r and r.get(redis_flag_key):
            # Check DB for existing reward
            existing = (
                db.query(UserReward)
                .filter(UserReward.user_id == current_user.id, UserReward.idempotency_key == idempotency_key)
                .first()
            )
            if existing:
                return VipClaimResponse(
                    awarded_points=existing.reward_metadata.get("vip_points", VIP_DAILY_POINTS) if existing.reward_metadata else VIP_DAILY_POINTS,
                    new_vip_points=current_user.vip_points,
                    claimed_at=existing.claimed_at,
                    idempotent=True,
                )
    except Exception:
        pass

    # Query again in DB to be safe
    existing = (
        db.query(UserReward)
        .filter(UserReward.user_id == current_user.id, UserReward.idempotency_key == idempotency_key)
        .first()
    )
    if existing:
        return VipClaimResponse(
            awarded_points=existing.reward_metadata.get("vip_points", VIP_DAILY_POINTS) if existing.reward_metadata else VIP_DAILY_POINTS,
            new_vip_points=current_user.vip_points,
            claimed_at=existing.claimed_at,
            idempotent=True,
        )

    # Award
    try:
        current_user.vip_points = (current_user.vip_points or 0) + VIP_DAILY_POINTS
        reward = UserReward(
            user_id=current_user.id,
            reward_type="VIP_DAILY",
            gold_amount=VIP_DAILY_GOLD,
            xp_amount=VIP_DAILY_XP,
            reward_metadata={"vip_points": VIP_DAILY_POINTS, "source": "VIP_DAILY", "day": today},
            idempotency_key=idempotency_key,
        )
        db.add(reward)
        db.add(current_user)
        db.commit()
        db.refresh(reward)
    except IntegrityError:
        db.rollback()
        reward = (
            db.query(UserReward)
            .filter(UserReward.user_id == current_user.id, UserReward.idempotency_key == idempotency_key)
            .first()
        )
        if not reward:
            raise HTTPException(status_code=500, detail="Failed to finalize VIP claim")
    except Exception:
        db.rollback()
        raise

    try:
        if r:
            r.set(redis_flag_key, "1", ex=60*60*26)
    except Exception:
        pass

    return VipClaimResponse(
        awarded_points=VIP_DAILY_POINTS,
        new_vip_points=current_user.vip_points,
        claimed_at=reward.claimed_at,
        idempotent=False,
    )
