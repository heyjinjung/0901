from __future__ import annotations

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from datetime import datetime

from ..models.achievement_models import Achievement, UserAchievement
from ..models.history_models import GameHistory
from ..models.notification_models import Notification
from ..realtime.hub import hub
from .achievement_evaluator import AchievementEvaluatorRegistry, EvalContext, EvalResult


class AchievementService:
    """Service layer for achievements evaluation and retrieval."""

    def __init__(self, db: Session):
        self.db = db

    def list_active(self) -> List[Achievement]:
        return self.db.scalars(select(Achievement).where(Achievement.is_active == True)).all()  # noqa: E712

    def user_progress(self, user_id: int) -> List[Dict[str, Any]]:
        ach_map = {a.id: a for a in self.list_active()}
        ua_rows = self.db.scalars(select(UserAchievement).where(UserAchievement.user_id == user_id)).all()
        response = []
        for a in ach_map.values():
            ua = next((r for r in ua_rows if r.achievement_id == a.id), None)
            progress_val = ua.progress_value if ua else 0
            unlocked = bool(ua and ua.is_unlocked)
            threshold = a.condition.get("threshold") if isinstance(a.condition, dict) else None
            response.append({
                "code": a.code,
                "title": a.title,
                "description": a.description,
                "icon": a.icon,
                "badge_color": a.badge_color,
                "reward_coins": a.reward_coins,
                # reward_gold 사용 (legacy gems 제거)
                "reward_gold": 0,
                "progress": progress_val,
                "threshold": threshold,
                "unlocked": unlocked,
            })
        return response

    def evaluate_after_history(self, history: GameHistory) -> List[str]:
        """Evaluate achievements for a new `GameHistory` via strategy registry.

        Returns list of unlocked achievement codes.
        """
        metadata = history.metadata or {}
        if not metadata.get("is_user_action", False):
            return []

        unlocked_codes: List[str] = []
        ctx = EvalContext(db=self.db, history=history)

        for ach in self.list_active():
            cond = ach.condition if isinstance(ach.condition, dict) else {}
            result: Optional[EvalResult] = AchievementEvaluatorRegistry.evaluate(ctx, cond)
            if not result:
                continue

            ua = self.db.scalar(select(UserAchievement).where(UserAchievement.user_id == history.user_id, UserAchievement.achievement_id == ach.id))
            if ua is None:
                ua = UserAchievement(user_id=history.user_id, achievement_id=ach.id, progress_value=result.progress, is_unlocked=False)
                self.db.add(ua)
            else:
                ua.progress_value = result.progress

            if not ua.is_unlocked and result.unlocked:
                ua.is_unlocked = True
                ua.unlocked_at = datetime.utcnow()
                unlocked_codes.append(ach.code)
                notif = Notification(
                    user_id=history.user_id,
                    title=f"Achievement Unlocked: {ach.title}",
                    message=ach.description or ach.code,
                    notification_type="achievement_unlock",
                    related_code=ach.code,
                )
                self.db.add(notif)
                hub.broadcast(history.user_id, {
                    "type": "achievement_unlock",
                    "code": ach.code,
                    "title": ach.title,
                    "reward_coins": ach.reward_coins,
                    "reward_gold": 0,
                })
                try:
                    from ..routers.realtime import broadcast_achievement_progress
                    import asyncio
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        loop.create_task(broadcast_achievement_progress(
                            user_id=history.user_id,
                            achievement_code=ach.code,
                            progress=result.progress,
                            unlocked=True
                        ))
                except Exception:
                    pass
        return unlocked_codes

    # Aggregation helpers moved into achievement_evaluator strategies.
