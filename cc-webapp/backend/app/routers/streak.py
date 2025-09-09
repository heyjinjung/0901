"""Streak API: daily/continuous action streak status and updates"""
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from ..dependencies import get_current_user
from ..models.auth_models import User
from ..models.game_models import UserReward
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from ..utils.redis import (
    update_streak_counter,
    get_streak_counter,
    get_streak_ttl,
    record_attendance_day,
    get_attendance_month,
    get_streak_protection,
    set_streak_protection,
)
from app.utils.redis import get_redis  # 일일 중복 가드용 직접 Redis 접근
from app.utils.streak_utils import calculate_streak_reward

router = APIRouter(prefix="/api/streak", tags=["Streaks"])

DEFAULT_ACTION = "SLOT_SPIN"


class StreakStatus(BaseModel):
    action_type: str
    count: int
    ttl_seconds: Optional[int] = None
    # next_reward 필드 제거 - 간소화된 시스템


class StreakClaimResponse(BaseModel):
    action_type: str
    streak_count: int
    awarded_gold: int
    awarded_xp: int
    new_gold_balance: int
    claimed_at: datetime


@router.get("/status", response_model=StreakStatus)
async def status(
    action_type: str = Query(DEFAULT_ACTION),
    current_user: User = Depends(get_current_user),
):
    cnt = get_streak_counter(str(current_user.id), action_type)
    ttl = get_streak_ttl(str(current_user.id), action_type)
    return StreakStatus(action_type=action_type, count=cnt, ttl_seconds=ttl)


class TickRequest(BaseModel):
    action_type: Optional[str] = None


@router.post("/tick", response_model=StreakStatus)
async def tick(
    body: TickRequest,
    current_user: User = Depends(get_current_user),
):
    action_type = body.action_type or DEFAULT_ACTION

    # ------------------------------
    # 일일 중복 증가 가드 (UTC 기준)
    # 동일 user/action/date 조합에서 하루 1회만 streak 증가.
    # Redis NX 키: user:{id}:streak_daily_lock:{action}:{YYYY-MM-DD}
    # TTL 48h: 자정 교차 시점 여유 확보.
    # Redis 미연결/예외 시엔 기존 동작(증가) 유지 → 가용성 우선.
    # ------------------------------
    allow_increment = True
    today_iso = datetime.utcnow().date().isoformat()
    daily_lock_key = f"user:{current_user.id}:streak_daily_lock:{action_type}:{today_iso}"
    try:
        r = get_redis()
        if r is not None:
            # setnx (nx=True) 실패하면 이미 오늘 증가 처리된 것 → 증가 생략
            if not r.set(daily_lock_key, "1", nx=True, ex=60 * 60 * 48):
                allow_increment = False
    except Exception:
        # Redis 문제는 가드 비활성(증가 허용)
        pass

    if allow_increment:
        cnt = update_streak_counter(str(current_user.id), action_type, increment=True)
    else:
        cnt = get_streak_counter(str(current_user.id), action_type)

    ttl = get_streak_ttl(str(current_user.id), action_type)

    # 출석 기록 (증가 여부와 무관하게 하루 한 번 기록 시도 – SADD idempotent)
    try:
        record_attendance_day(str(current_user.id), action_type, today_iso)
    except Exception:
        pass

    # 실시간 브로드캐스트: 스트릭 카운터 업데이트 (증가된 경우만)
    if allow_increment:
        try:
            from ..routers.realtime import broadcast_streak_update
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(broadcast_streak_update(
                    user_id=current_user.id,
                    action_type=action_type,
                    streak_count=cnt
                ))
        except Exception:
            pass

    return StreakStatus(action_type=action_type, count=cnt, ttl_seconds=ttl)


class ResetRequest(BaseModel):
    action_type: Optional[str] = None


@router.post("/reset")
async def reset(
    body: ResetRequest,
    current_user: User = Depends(get_current_user),
):
    action_type = body.action_type or DEFAULT_ACTION
    # Use update_streak_counter with increment=False to reset
    update_streak_counter(str(current_user.id), action_type, increment=False)
    return {"ok": True}


# /api/streak/next-reward 엔드포인트 제거 - 간소화된 시스템에서는 불필요


# -----------------
# Attendance (출석)
# -----------------
class AttendanceHistory(BaseModel):
    action_type: str
    year: int
    month: int
    days: List[str]


@router.get("/history", response_model=AttendanceHistory)
async def history(
    action_type: str = Query(DEFAULT_ACTION),
    year: int = Query(..., ge=1970, le=2100),
    month: int = Query(..., ge=1, le=12),
    current_user: User = Depends(get_current_user),
):
    days = get_attendance_month(str(current_user.id), action_type, year, month)
    return AttendanceHistory(action_type=action_type, year=year, month=month, days=days)


# ----------------------
# Streak Protection 토글
# ----------------------
class ProtectionStatus(BaseModel):
    action_type: str
    enabled: bool


@router.get("/protection", response_model=ProtectionStatus)
async def protection_status(
    action_type: str = Query(DEFAULT_ACTION),
    current_user: User = Depends(get_current_user),
):
    enabled = get_streak_protection(str(current_user.id), action_type)
    return ProtectionStatus(action_type=action_type, enabled=enabled)


# ----------------------
# Claim (일일 보상 지급)
# ----------------------
class ClaimRequest(BaseModel):
    action_type: Optional[str] = None

from app.services.reward_service import calculate_streak_daily_reward
from app.utils.streak_utils import calculate_streak_reward


# ----------------------
# Preview (보상 미리보기)
# ----------------------
class StreakPreviewResponse(BaseModel):
    action_type: str
    streak_count: int  # 현재 streak (claim 기준)
    claimed_today: bool
    claimable: bool  # 오늘 아직 수령 가능 여부
    today_reward_gold: int
    today_reward_xp: int
    next_day_reward_gold: int
    next_day_reward_xp: int


@router.get("/preview", response_model=StreakPreviewResponse)
async def preview(
    action_type: str = Query(DEFAULT_ACTION),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """현재 streak 및 오늘/내일 보상 금액 미리보기 제공.

    프론트는 이 엔드포인트를 사용해 클라이언트 산식 중복 제거.
    - streak_count: Redis 카운터 (증가 없이 조회)
    - claimed_today: 동일 UTC day idempotency key 존재 여부
    - claimable: streak_count>0 이고 claimed_today False
    - today_reward: streak_count 기반 산식
    - next_day_reward: streak_count+1 기반 산식
    """
    streak_count = get_streak_counter(str(current_user.id), action_type)
    if streak_count < 0:
        streak_count = 0
    # 멱등키 존재 여부 확인
    claim_day = datetime.utcnow().date().isoformat()
    idempotency_key = f"streak:{current_user.id}:{action_type}:{claim_day}"
    existing = (
        db.query(UserReward)
        .filter(UserReward.user_id == current_user.id, UserReward.idempotency_key == idempotency_key)
        .first()
    )
    claimed_today = existing is not None
    
    # 새로운 선형 보상 시스템 사용
    # 프론트와 일관성 유지: preview에서는 raw 0을 사용자에게 보이는 "1일차"로 처리
    # 단, claimable/claimed_today 판정은 기존 로직(실제 streak_count 기반)을 유지
    display_count = streak_count if streak_count > 0 else 1
    reward_info = calculate_streak_reward(display_count)
    today_gold, today_xp = reward_info['gold'], reward_info['xp']

    # next day reward 계산은 실제 다음 증가값(streak_count + 1)을 사용 (기존과 동일)
    next_reward_info = calculate_streak_reward(streak_count + 1)
    next_gold, next_xp = next_reward_info['gold'], next_reward_info['xp']
    
    return StreakPreviewResponse(
        action_type=action_type,
        streak_count=streak_count,
        claimed_today=claimed_today,
        claimable=(streak_count > 0 and not claimed_today),
        today_reward_gold=today_gold,
        today_reward_xp=today_xp,
        next_day_reward_gold=next_gold,
        next_day_reward_xp=next_xp,
    )


@router.post("/claim", response_model=StreakClaimResponse)
async def claim(
    body: Optional[ClaimRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Allow empty body (test clients may omit JSON) and default action_type
    action_type = (body.action_type if body and body.action_type else DEFAULT_ACTION)
    # 진단 로깅: 요청 시작
    try:
        import logging
        logger = logging.getLogger("streak")
        logger.info("[streak.claim] start", extra={"user_id": current_user.id, "action_type": action_type})
    except Exception:
        logger = None
    # 현재 streak 읽기 (증가 없이)
    streak_count = get_streak_counter(str(current_user.id), action_type)
    if streak_count <= 0:
        # 최초 claim 시 자동 seed (tick 1회와 동일 효과) -> 사용자 UX 개선
        try:
            seeded = update_streak_counter(str(current_user.id), action_type, increment=True)
            streak_count = seeded
            if logger:
                logger.info("[streak.claim] auto_seed_applied", extra={"user_id": current_user.id, "action_type": action_type, "seeded": seeded})
        except Exception:
            # Redis/seed 실패 시 이전 로직과 동일하게 400 반환 (fallback)
            if logger:
                logger.info("[streak.claim] auto_seed_failed", extra={"user_id": current_user.id, "action_type": action_type})
            raise HTTPException(status_code=400, detail="No active streak to claim")
        
    # 오늘 이미 보상을 받았는지 확인
    claim_day = datetime.utcnow().date().isoformat()
    # 기존 코드에서 UserReward.created_at 필드를 참조했으나 모델에는 claimed_at 만 존재
    # streak 일일 보상은 claimed_at 기준으로 '오늘' 수령 여부 확인
    existing_today = (
        db.query(UserReward)
        .filter(
            UserReward.user_id == current_user.id,
            UserReward.reward_type == "STREAK_DAILY",
            func.date(UserReward.claimed_at) == func.date(datetime.utcnow())
        )
        .first()
    )
    if existing_today:
        if logger:
            logger.info("[streak.claim] already_claimed_today", extra={"user_id": current_user.id, "reward_id": existing_today.id})
        raise HTTPException(status_code=400, detail="한 회원당 하루에 1번만 연속 보상을 받을 수 있습니다")

    # 멱등키: user_id + action_type + UTC date
    claim_day = datetime.utcnow().date().isoformat()
    idempotency_key = f"streak:{current_user.id}:{action_type}:{claim_day}"

    # Redis/DB 멱등: Redis 플래그(선택적) 우선 확인 (존재 시 DB 조회 생략 가능)
    from app.utils.redis import get_redis
    try:
        r = get_redis()
        redis_flag_key = f"streak_claimed:{current_user.id}:{action_type}:{claim_day}"
        if r.get(redis_flag_key):
            existing = (
                db.query(UserReward)
                .filter(UserReward.user_id == current_user.id, UserReward.idempotency_key == idempotency_key)
                .first()
            )
            if existing:
                return StreakClaimResponse(
                    action_type=action_type,
                    streak_count=streak_count,
                    awarded_gold=existing.gold_amount or 0,
                    awarded_xp=existing.xp_amount or 0,
                    new_gold_balance=current_user.gold_balance,
                    claimed_at=existing.claimed_at,
                )
    except Exception:
        pass

    # 이미 동일 날 보상 지급된 경우 DB user_rewards 조회
    existing = (
        db.query(UserReward)
        .filter(UserReward.user_id == current_user.id, UserReward.idempotency_key == idempotency_key)
        .first()
    )
    if existing:
        return StreakClaimResponse(
            action_type=action_type,
            streak_count=streak_count,
            awarded_gold=existing.gold_amount or 0,
            awarded_xp=existing.xp_amount or 0,
            new_gold_balance=current_user.gold_balance,
            claimed_at=existing.claimed_at,
        )

    # 새로운 선형 보상 시스템으로 보상 계산
    reward_info = calculate_streak_reward(streak_count)
    gold, xp = reward_info['gold'], reward_info['xp']

    # 트랜잭션 처리
    try:
        # current_user 가 ORMapped 객체가 아닐 수 있으므로(테스트 override) 실제 User ORM 객체 재조회
        from app.models.auth_models import User as ORMUser  # 지연 import
        orm_user = db.query(ORMUser).filter(ORMUser.id == current_user.id).first()
        if orm_user:
            orm_user.gold_balance = (getattr(orm_user, 'gold_balance', 0) or 0) + gold
            if hasattr(orm_user, 'experience'):
                try:
                    orm_user.experience = (orm_user.experience or 0) + xp
                except Exception:
                    pass
        # reward row 생성
        reward = UserReward(
            user_id=current_user.id,
            reward_type="STREAK_DAILY",
            gold_amount=gold,
            xp_amount=xp,
            reward_metadata={
                "action_type": action_type,
                "streak_count": streak_count,
                "formula": "C_exp_decay_v1",
                "is_user_action": True,
            },
            idempotency_key=idempotency_key,
            claimed_at=datetime.utcnow(),
        )
        db.add(reward)
        if orm_user:
            db.add(orm_user)
        db.commit()
        db.refresh(reward)
    except IntegrityError:
        db.rollback()
        if logger:
            logger.warning("[streak.claim] integrity_error_retry", extra={"user_id": current_user.id, "idempotency_key": idempotency_key})
        # 재경합 시 재조회 (멱등)
        reward = (
            db.query(UserReward)
            .filter(UserReward.user_id == current_user.id, UserReward.idempotency_key == idempotency_key)
            .first()
        )
        if not reward:
            # IntegrityError 후 재조회 실패 → graceful fallback: 계산값 기반 임시 응답
            if logger:
                logger.warning("[streak.claim] graceful_fallback_ephemeral", extra={
                    "user_id": current_user.id, 
                    "idempotency_key": idempotency_key,
                    "gold": gold,
                    "xp": xp
                })
            return StreakClaimResponse(
                action_type=action_type,
                streak_count=streak_count,
                awarded_gold=gold,
                awarded_xp=xp,
                new_gold_balance=current_user.gold_balance + gold,  # 임시 계산
                claimed_at=datetime.utcnow(),
            )
    except Exception as e:
        db.rollback()
        if logger:
            logger.exception("[streak.claim] unexpected_error", extra={"user_id": current_user.id, "idempotency_key": idempotency_key})
        # 내부 오류 디버깅을 위해 메시지 포함 (테스트 환경)
        raise HTTPException(status_code=500, detail=f"streak claim failed: {type(e).__name__}")

    # Redis 플래그 TTL = 1일 (UTC 자정 교차 허용: 26h 여유)
    try:
        if r:
            r.set(redis_flag_key, "1", ex=60*60*26)
    except Exception:
        pass

    # 실시간 브로드캐스트: 보상 지급 + 프로필 변경
    try:
        from ..routers.realtime import broadcast_reward_granted, broadcast_profile_update
        import asyncio
        
        # 보상 지급 알림
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(broadcast_reward_granted(
                user_id=current_user.id,
                reward_type="streak_daily",
                amount=gold,
                balance_after=current_user.gold_balance
            ))
            
            # 프로필 변경 알림 (골드 + 경험치)
            profile_changes = {"gold_balance": current_user.gold_balance}
            if hasattr(orm_user, 'experience'):
                profile_changes["experience"] = orm_user.experience
            
            loop.create_task(broadcast_profile_update(
                user_id=current_user.id,
                changes=profile_changes
            ))
    except Exception as e:
        # 브로드캐스트 실패해도 메인 기능에 영향 없음
        pass

    if logger:
        try:
            logger.info(
                "[streak.claim] success",
                extra={
                    "user_id": current_user.id,
                    "action_type": action_type,
                    "streak_count": streak_count,
                    "gold": gold,
                    "xp": xp,
                    "new_gold_balance": getattr(current_user, 'gold_balance', None),
                },
            )
        except Exception:
            pass

    return StreakClaimResponse(
        action_type=action_type,
        streak_count=streak_count,
        awarded_gold=gold,
        awarded_xp=xp,
        new_gold_balance=current_user.gold_balance,
        claimed_at=reward.claimed_at,
    )
class ProtectionRequest(BaseModel):
    action_type: Optional[str] = None
    enabled: bool


@router.post("/protection", response_model=ProtectionStatus)
async def set_protection(
    body: ProtectionRequest,
    current_user: User = Depends(get_current_user),
):
    action_type = body.action_type or DEFAULT_ACTION
    set_streak_protection(str(current_user.id), action_type, body.enabled)
    enabled = get_streak_protection(str(current_user.id), action_type)
    return ProtectionStatus(action_type=action_type, enabled=enabled)
