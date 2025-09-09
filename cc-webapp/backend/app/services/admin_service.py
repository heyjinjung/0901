from sqlalchemy.orm import Session
from typing import List, Optional

from .. import models

class AdminService:
    def __init__(self, db: Session):
        self.db = db

    def list_users(self, skip: int, limit: int, search: Optional[str]) -> List[models.User]:
        """
        Lists users for the admin panel, with optional search.
        """
        query = self.db.query(models.User)
        if search:
            query = query.filter(
                (models.User.nickname.ilike(f"%{search}%")) |
                (models.User.site_id.ilike(f"%{search}%")) |
                (models.User.phone_number.ilike(f"%{search}%"))
            )
        return query.offset(skip).limit(limit).all()

    def get_user_details(self, user_id: int) -> models.User:
        """
        Gets a specific user by ID.
        """
        user = self.db.query(models.User).filter(models.User.id == user_id).first()
        return user

    def get_user_activities(self, user_id: int, limit: int = 10) -> List[models.UserAction]:
        """
        Gets recent activities for a specific user.
        """
        return self.db.query(models.UserAction).filter(models.UserAction.user_id == user_id).order_by(models.UserAction.created_at.desc()).limit(limit).all()

    def get_user_rewards(self, user_id: int, limit: int = 10) -> List[models.UserReward]:
        """
        Gets recent rewards for a specific user.
        """
        return (
            self.db.query(models.UserReward)
            .filter(models.UserReward.user_id == user_id)
            .order_by(models.UserReward.claimed_at.desc())
            .limit(limit)
            .all()
        )

    def list_all_activities(self, skip: int, limit: int) -> List[models.UserAction]:
        """
        Gets a list of all recent user activities.
        """
        return self.db.query(models.UserAction).order_by(models.UserAction.created_at.desc()).offset(skip).limit(limit).all()

    # === Added: System stats and user admin operations ===
    class _Stats:
        def __init__(self, total_users: int, active_users: int, total_games_played: int, total_tokens_in_circulation: int) -> None:
            self.total_users = total_users
            self.active_users = active_users
            self.total_games_played = total_games_played
            self.total_tokens_in_circulation = total_tokens_in_circulation

    def get_system_stats(self) -> "AdminService._Stats":
        """Aggregate basic system statistics for admin dashboard."""
        total_users = self.db.query(models.User).count()
        active_users = self.db.query(models.User).filter(models.User.is_active == True).count()  # noqa: E712
        total_games_played = self.db.query(models.UserAction).count()
        # cyber_token_balance 는 Python property (실제 컬럼 아님) 이므로 직접 SELECT 하면 SQLAlchemy 에러 발생.
        # 통합 통화: gold_balance 컬럼 합계를 사용.
        try:
            from sqlalchemy import func
            total_tokens_sum = self.db.query(func.coalesce(func.sum(models.User.gold_balance), 0)).scalar() or 0
        except Exception:
            # fallback: 전량 로드 (소규모 테스트 환경 안전)
            balances = self.db.query(models.User.gold_balance).all()
            total_tokens_sum = sum(b[0] or 0 for b in balances)
        return AdminService._Stats(
            total_users=total_users,
            active_users=active_users,
            total_games_played=total_games_played,
            total_tokens_in_circulation=total_tokens_sum,
        )

    # --- 확장 통계 (캐싱은 라우터에서 처리) ---
    def get_system_stats_extended(self) -> dict:
        """확장된 관리자 통계 집계.

        반환 필드:
          - total_users
          - active_users
          - total_games_played
          - total_tokens_in_circulation
          - online_users: 최근 5분 내 active 세션 사용자 수
          - total_revenue: 모든 success 거래 amount 합계
          - today_revenue: 금일 00:00 이후 success 거래 amount 합계
          - pending_actions: pending 상태 거래 수
          - critical_alerts: 최근 10분 내 지정 action 발생 수
        """
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        five_min_ago = now - timedelta(minutes=5)
        ten_min_ago = now - timedelta(minutes=10)
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        # 기본 통계 재사용
        basic = self.get_system_stats()

        # 온라인 사용자 (최근 5분 세션)
        try:
            online_users = self.db.query(models.UserSession.user_id) \
                .filter(models.UserSession.last_used_at > five_min_ago, models.UserSession.is_active == True) \
                .distinct().count()
        except Exception:
            online_users = 0

        # 매출 합계 (ShopTransaction)
        from sqlalchemy import func
        try:
            total_revenue = self.db.query(func.coalesce(func.sum(models.ShopTransaction.amount), 0)) \
                .filter(models.ShopTransaction.status == 'success').scalar() or 0
        except Exception:
            total_revenue = 0
        try:
            today_revenue = self.db.query(func.coalesce(func.sum(models.ShopTransaction.amount), 0)) \
                .filter(models.ShopTransaction.status == 'success', models.ShopTransaction.created_at >= today_start).scalar() or 0
        except Exception:
            today_revenue = 0

        # Pending actions (pending 거래)
        try:
            pending_actions = self.db.query(models.ShopTransaction.id) \
                .filter(models.ShopTransaction.status == 'pending').count()
        except Exception:
            pending_actions = 0

        # Critical alerts (최근 10분 지정 action)
        CRITICAL_ACTIONS = ['LIMITED_STOCK_ZERO', 'FRAUD_BLOCK', 'PAYMENT_FAIL_SPIKE']
        try:
            critical_alerts = self.db.query(models.AdminAuditLog.id) \
                .filter(models.AdminAuditLog.created_at > ten_min_ago, models.AdminAuditLog.action.in_(CRITICAL_ACTIONS)).count()
        except Exception:
            critical_alerts = 0

        return {
            'total_users': basic.total_users,
            'active_users': basic.active_users,
            'total_games_played': basic.total_games_played,
            'total_tokens_in_circulation': basic.total_tokens_in_circulation,
            'online_users': online_users,
            'total_revenue': int(total_revenue),
            'today_revenue': int(today_revenue),
            'pending_actions': pending_actions,
            'critical_alerts': critical_alerts,
            'generated_at': now.isoformat() + 'Z'
        }

    class _BanResult:
        def __init__(self, banned_until=None) -> None:
            self.banned_until = banned_until

    def ban_user(self, user_id: int, reason: str, duration_hours: Optional[int] = None) -> "AdminService._BanResult":
        """Minimal ban implementation: deactivate user; optionally log security event."""
        user = self.db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        user.is_active = False
        # Optional: record as security event
        try:
            evt = models.SecurityEvent(
                user_id=user.id,
                event_type="admin_ban",
                event_data=reason,
                is_suspicious=False,
            )
            self.db.add(evt)
        except Exception:
            # best-effort only
            pass
        self.db.add(user)
        self.db.commit()
        banned_until = None
        if duration_hours and duration_hours > 0:
            from datetime import datetime, timedelta
            banned_until = datetime.utcnow() + timedelta(hours=duration_hours)
        return AdminService._BanResult(banned_until=banned_until)

    def unban_user(self, user_id: int) -> None:
        user = self.db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        user.is_active = True
        self.db.add(user)
        self.db.commit()

    def add_user_tokens(self, user_id: int, amount: int) -> int:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        user = self.db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        user.cyber_token_balance = int((user.cyber_token_balance or 0) + amount)
        self.db.add(user)
        self.db.commit()
        return user.cyber_token_balance
