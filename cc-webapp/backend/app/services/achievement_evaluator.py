"""Achievement evaluation engine (strategy-based).

Centralizes achievement progress & unlock logic to avoid scattering conditional
branches across service layers. Each achievement *condition* JSON should at
least contain a `type` field; optional fields are type-specific.

Supported built‑in types:
  - CUMULATIVE_BET: {"type": "CUMULATIVE_BET", "game_type?": str, "threshold": int}
  - TOTAL_WIN_AMOUNT: {"type": "TOTAL_WIN_AMOUNT", "game_type?": str, "threshold": int}
  - WIN_STREAK: {"type": "WIN_STREAK", "game_type?": str, "threshold": int}

To add a new one create a function with signature:
    def evaluator(ctx: EvalContext, cond: Dict[str, Any]) -> EvalResult
and register it via AchievementEvaluatorRegistry.register("TYPE", evaluator)

All database access must go through ctx.db; NO side effects (notifications,
model mutation, broadcasting) happen here—this layer is pure calculation.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Optional, Protocol
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from ..models.history_models import GameHistory


@dataclass
class EvalResult:
    progress: int
    unlocked: bool


@dataclass
class EvalContext:
    db: Session
    history: GameHistory  # triggering history row


class EvaluatorFn(Protocol):  # type: ignore[misc]
    def __call__(self, ctx: EvalContext, cond: Dict[str, Any]) -> EvalResult: ...


class AchievementEvaluatorRegistry:
    _registry: Dict[str, EvaluatorFn] = {}

    @classmethod
    def register(cls, ach_type: str, fn: EvaluatorFn) -> None:
        cls._registry[ach_type.upper()] = fn

    @classmethod
    def evaluate(cls, ctx: EvalContext, cond: Dict[str, Any]) -> Optional[EvalResult]:
        ach_type = cond.get("type")
        if not ach_type:
            return None
        fn = cls._registry.get(ach_type.upper())
        if not fn:
            return None
        return fn(ctx, cond)


# ---------------- Built‑in evaluator implementations ---------------- #

def _cumulative_amount(ctx: EvalContext, cond: Dict[str, Any], action_filter: str) -> EvalResult:
    game_type = cond.get("game_type")
    threshold = int(cond.get("threshold", 0))
    stmt = select(func.sum(GameHistory.delta_coin)).where(
        GameHistory.user_id == ctx.history.user_id,
        GameHistory.action_type == action_filter,
    )
    if game_type:
        if ctx.history.game_type != game_type:
            return EvalResult(progress=0, unlocked=False)
        stmt = stmt.where(GameHistory.game_type == game_type)
    total = ctx.db.execute(stmt).scalar() or 0
    return EvalResult(progress=int(total), unlocked=int(total) >= threshold)


def eval_cumulative_bet(ctx: EvalContext, cond: Dict[str, Any]) -> EvalResult:
    return _cumulative_amount(ctx, cond, action_filter="BET")


def eval_total_win_amount(ctx: EvalContext, cond: Dict[str, Any]) -> EvalResult:
    return _cumulative_amount(ctx, cond, action_filter="WIN")


def eval_win_streak(ctx: EvalContext, cond: Dict[str, Any]) -> EvalResult:
    game_type = cond.get("game_type")
    threshold = int(cond.get("threshold", 0))
    if game_type and ctx.history.game_type != game_type:
        return EvalResult(progress=0, unlocked=False)

    q = (
        select(GameHistory.action_type, GameHistory.game_type)
        .where(GameHistory.user_id == ctx.history.user_id)
        .order_by(GameHistory.created_at.desc())
        .limit(100)
    )
    rows = ctx.db.execute(q).all()
    streak = 0
    for action_type, gtype in rows:
        if action_type != "WIN":
            break
        if game_type and gtype != game_type:
            break
        streak += 1
    return EvalResult(progress=streak, unlocked=streak >= threshold)


AchievementEvaluatorRegistry.register("CUMULATIVE_BET", eval_cumulative_bet)
AchievementEvaluatorRegistry.register("TOTAL_WIN_AMOUNT", eval_total_win_amount)
AchievementEvaluatorRegistry.register("WIN_STREAK", eval_win_streak)

__all__ = [
    "EvalContext",
    "EvalResult",
    "AchievementEvaluatorRegistry",
]
