from fastapi import APIRouter, Depends
from fastapi import HTTPException
from typing import Any, Dict, Optional

from ..dependencies import get_current_user  # 인증 사용자 컨텍스트
from ..models.auth_models import User as AuthUser
from datetime import datetime, timezone, timedelta
from ..utils.redis import (
    get_streak_counter,
    get_streak_ttl,
    get_attendance_month,
)
from ..utils.streak_utils import calc_next_streak_reward

from ..services.dashboard_service import DashboardService
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.game_models import UserReward
from ..database import get_db
from ..services.auth_service import AuthService  # For admin protection (optional future)

router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"],
)

@router.get("/main")
def get_main_dashboard(db = Depends(get_db)):
    """
    Get main dashboard statistics.
    """
    dashboard_service = DashboardService(db)
    return dashboard_service.get_main_dashboard_stats()

@router.get("/games")
def get_games_dashboard(db = Depends(get_db)):
    """
    Get game-specific dashboard statistics.
    """
    dashboard_service = DashboardService(db)
    return dashboard_service.get_game_dashboard_stats()

@router.get("/social-proof")
def get_social_proof(db = Depends(get_db)):
    """
    Get statistics for social proof widgets.
    This endpoint is not protected by admin auth to be publicly available.
    """
    dashboard_service = DashboardService(db)
    return dashboard_service.get_social_proof_stats()


@router.get("", summary="Unified dashboard aggregate")
def get_unified_dashboard(
    db: Session = Depends(get_db),
    current_user: Optional[AuthUser] = Depends(get_current_user),
) -> Dict[str, Any]:
    """통합 대시보드 집계 엔드포인트

    기존 개별 엔드포인트(/dashboard/main, /dashboard/games, /dashboard/social-proof)를 한 번에 호출해
    프론트 초기 로딩 RTT를 줄이고 일관된 스냅샷을 제공한다.

    Response 예시:
    {
      "main": {...},
      "games": {...},
      "social_proof": {...},
      "_meta": {"generated_at": "2025-08-21T12:34:56Z"}
    }
    """
    service = DashboardService(db)
    try:
        main_stats = service.get_main_dashboard_stats()
        game_stats = service.get_game_dashboard_stats()
        social = service.get_social_proof_stats()
    except Exception as e:  # 방어적 처리, 부분 실패 시 500
        raise HTTPException(status_code=500, detail=f"dashboard aggregation failed: {e}")

    payload: Dict[str, Any] = {
        "main": main_stats,
        "games": game_stats,
        "social_proof": social,
        "_meta": {"generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")},
    }

    # 인증 사용자 정보가 있으면 streak / vip 정보를 통합 응답에 추가 (프론트 legacy 호출 제거 위한 준비)
    if current_user:
        try:
            action_type = "DAILY_LOGIN"  # 프론트에서 사용하는 streak 기본 action
            streak_count = get_streak_counter(str(current_user.id), action_type)
            ttl_seconds = get_streak_ttl(str(current_user.id), action_type)
            # 공통 util 사용
            next_reward = calc_next_streak_reward(streak_count + 1)

            # 주간 attendance (현재 UTC 주간)
            today_utc = datetime.utcnow().date()
            year = today_utc.year
            month = today_utc.month
            # 월 전체 attendance 집합에서 이번 주 필터 (streak 프론트는 주간 캘린더 표시)
            month_days = get_attendance_month(str(current_user.id), action_type, year, month)
            # 이번 주 (일~토) 경계 계산
            weekday = today_utc.weekday()  # 월=0
            # Python weekday: Monday=0; 주간 캘린더(일요일 시작) 맞추기 위해 offset 조정
            # 일요일 시작 주: 현재 날짜의 요일 인덱스 (일요일=0) 계산
            # Convert Monday=0..Sunday=6 -> Sunday=0..Saturday=6
            monday_based = weekday
            sunday_based = (monday_based + 1) % 7
            week_start = today_utc - timedelta(days=sunday_based)
            week_dates = [week_start + timedelta(days=i) for i in range(7)]
            week_days_iso = {d.isoformat() for d in week_dates}
            attendance_week = [d for d in month_days if d in week_days_iso]

            payload["streak"] = {
                "count": streak_count,
                "ttl_seconds": ttl_seconds,
                "next_reward": next_reward,
                "attendance_week": sorted(attendance_week),
            }
        except Exception:
            pass

        # VIP 상태: 기존 /api/vip/status 의 최소 필드 (vip_points, claimed_today) - 가용한 경우만
        try:
            vip_points = getattr(current_user, "vip_points", 0) or 0
            today_iso = datetime.utcnow().date().isoformat()
            vip_idem_key = f"vip:{current_user.id}:{today_iso}"
            existing_vip = (
                db.query(UserReward)
                .filter(UserReward.user_id == current_user.id, UserReward.idempotency_key == vip_idem_key)
                .first()
            )
            payload["vip"] = {
                "vip_points": vip_points,
                "claimed_today": existing_vip is not None,
                # (선택) 마지막 claim 시간: 프론트 필요 시 사용
                "last_claim_at": getattr(existing_vip, "claimed_at", None) if existing_vip else None,
            }
        except Exception:
            pass

    # shape 참고 (문서 자동화용):
    # {
    #   main: {...}, games: {...}, social_proof: {...},
    #   streak?: { count, ttl_seconds, next_reward, attendance_week: [YYYY-MM-DD,...] },
    #   vip?: { vip_points, claimed_today, last_claim_at },
    #   _meta: { generated_at }
    # }

    return payload
