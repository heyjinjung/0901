from __future__ import annotations
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from decimal import Decimal
from ..models.game_stats_models import UserGameStats
from ..models.history_models import GameHistory
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# --- Constants (unified across update/recalc) ---
GAME_TYPE_CRASH = "crash"
ACTION_BET = "BET"
ACTION_WIN = "WIN"

class GameStatsService:
    """Server-authoritative aggregated user game stats.

    Update path: call update_from_round after a round is *settled* (win or loss determined).
    Supports idempotent increment via passing a unique round identifier (future extension not yet stored).
    """
    def __init__(self, db: Session):
        self.db = db

    def get_or_create(self, user_id: int) -> UserGameStats:
        stats = self.db.get(UserGameStats, user_id)
        if stats:
            return stats
        stats = UserGameStats(user_id=user_id)
        self.db.add(stats)
        # flush to assign defaults now (no commit yet; caller decides)
        self.db.flush()
        return stats

    def update_from_round(self, *, user_id: int, bet_amount: int, win_amount: int, final_multiplier: float) -> UserGameStats:
        """Apply a single crash round result.

        bet_amount: amount wagered (positive integer)
        win_amount: amount returned (0 if loss) (positive int) -> profit = win_amount - bet_amount
        final_multiplier: achieved multiplier (>=1.0). If win, this is the cashout multiplier; if loss, the crash multiplier.
        """
        stats = self.get_or_create(user_id)
        profit = win_amount - bet_amount

        # Highest multiplier update (monotonic non-decreasing)
        if final_multiplier and final_multiplier > 0:
            try:
                if stats.highest_multiplier is None or float(final_multiplier) > float(stats.highest_multiplier):
                    stats.highest_multiplier = Decimal(str(final_multiplier))
                elif float(final_multiplier) < float(stats.highest_multiplier):
                    logger.warning(
                        "highest_multiplier regression observed user=%s final=%s stored=%s",
                        user_id,
                        final_multiplier,
                        stats.highest_multiplier,
                    )
            except Exception:
                logger.warning("highest_multiplier update failed", exc_info=True)

        # Append authoritative history row for recomputation/parity (explicit logging + flush)
        if win_amount > 0:
            delta = int(win_amount - bet_amount)
            if delta <= 0:
                logger.warning(
                    "WIN delta non-positive user=%s bet=%s win=%s -> delta=%s",
                    user_id,
                    bet_amount,
                    win_amount,
                    delta,
                )
            rec = GameHistory(
                user_id=user_id,
                game_type=GAME_TYPE_CRASH,
                action_type=ACTION_WIN,
                delta_coin=delta,
                delta_gem=0,
                result_meta={
                    "bet_amount": int(bet_amount),
                    "win_amount": int(win_amount),
                    "final_multiplier": float(final_multiplier) if final_multiplier is not None else None,
                },
            )
            self.db.add(rec)
            self.db.flush()
            logger.info(
                "GameHistory appended: user=%s type=%s action=%s id=%s delta=%s",
                user_id,
                GAME_TYPE_CRASH,
                ACTION_WIN,
                getattr(rec, 'id', None),
                delta,
            )
        else:
            delta = -int(bet_amount)
            rec = GameHistory(
                user_id=user_id,
                game_type=GAME_TYPE_CRASH,
                action_type=ACTION_BET,
                delta_coin=delta,
                delta_gem=0,
                result_meta={
                    "bet_amount": int(bet_amount),
                    "win_amount": int(win_amount),
                    "final_multiplier": float(final_multiplier) if final_multiplier is not None else None,
                },
            )
            self.db.add(rec)
            self.db.flush()
            logger.info(
                "GameHistory appended: user=%s type=%s action=%s id=%s delta=%s",
                user_id,
                GAME_TYPE_CRASH,
                ACTION_BET,
                getattr(rec, 'id', None),
                delta,
            )

        # Recompute authoritative aggregates from history (crash only)
        agg = (
            self.db.query(
                func.sum(
                    case(((GameHistory.action_type == ACTION_WIN) & (GameHistory.delta_coin > 0), 1), else_=0)
                ).label("win_rows"),
                func.sum(
                    case(((GameHistory.action_type == ACTION_BET) & (GameHistory.delta_coin < 0), 1), else_=0)
                ).label("loss_rows"),
                func.coalesce(func.sum(GameHistory.delta_coin), 0).label("delta_sum"),
            )
            .filter(GameHistory.user_id == user_id, GameHistory.game_type == GAME_TYPE_CRASH)
        ).one()

        wins = int(agg.win_rows or 0)
        losses = int(agg.loss_rows or 0)
        total_bets = wins + losses
        delta_sum = int(agg.delta_sum or 0)

        stats.total_bets = total_bets
        stats.total_wins = wins
        stats.total_losses = losses
        stats.total_profit = Decimal(str(delta_sum))
        stats.updated_at = datetime.utcnow()
        self.db.flush()
        return stats

    def recalculate_user(self, user_id: int) -> Optional[UserGameStats]:
        """Full authoritative recomputation from GameHistory for crash only (MVP).

        Current history logging stores WIN rows with positive delta_coin (net) and BET rows for losses (delta negative + win_amount 0).
        We infer losses = bets - wins. Profit is simply sum(delta_coin) (wins add net positive, bets subtract wager).
        """
        q = (
            self.db.query(
                func.sum(
                    case(((GameHistory.action_type == ACTION_WIN) & (GameHistory.delta_coin > 0), 1), else_=0)
                ).label("win_rows"),
                func.sum(
                    case(((GameHistory.action_type == ACTION_BET) & (GameHistory.delta_coin < 0), 1), else_=0)
                ).label("loss_rows"),
                func.coalesce(func.sum(GameHistory.delta_coin), 0).label("delta_sum"),
            )
            .filter(GameHistory.user_id == user_id, GameHistory.game_type == GAME_TYPE_CRASH)
        )
        row = q.one()
        wins = int(row.win_rows or 0)
        losses = int(row.loss_rows or 0)
        total_bets = wins + losses
        delta_sum = int(row.delta_sum or 0)
        stats = self.get_or_create(user_id)
        stats.total_bets = total_bets
        stats.total_wins = wins
        stats.total_losses = losses
        stats.total_profit = Decimal(str(delta_sum))
        # highest_multiplier cannot be recomputed without multiplier in history -> leave as-is
        stats.updated_at = datetime.utcnow()
        self.db.flush()
        return stats
