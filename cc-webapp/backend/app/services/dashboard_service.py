from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from .. import models

class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_main_dashboard_stats(self) -> dict:
        """
        Retrieves main dashboard statistics.
        """
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        # Daily Active Users (DAU) - users with any action today
        dau = self.db.query(models.UserAction.user_id).filter(models.UserAction.created_at >= today_start).distinct().count()

        # New Users Today
        new_users = self.db.query(models.User).filter(models.User.created_at >= today_start).count()

        # Total Revenue (sum of all bets) - can be for today or all time
        total_revenue = self.db.query(func.sum(models.Game.bet_amount)).scalar() or 0

        return {
            "daily_active_users": dau,
            "new_users_today": new_users,
            "total_revenue": total_revenue,
        }

    def get_game_dashboard_stats(self) -> dict:
        """
        Retrieves statistics for each game.
        """
        games = ["slot", "roulette", "rps", "gacha"]
        game_stats = {}

        for game_name in games:
            stats = self.db.query(
                func.sum(models.Game.bet_amount).label("total_bet"),
                func.sum(models.Game.payout).label("total_payout")
            ).filter(models.Game.game_type == game_name).first()

            total_bet = stats.total_bet or 0
            total_payout = stats.total_payout or 0
            profit = total_bet - total_payout

            game_stats[game_name] = {
                "total_bet": total_bet,
                "total_payout": total_payout,
                "profit": profit,
                "rtp": (total_payout / total_bet) * 100 if total_bet > 0 else 0
            }

        return game_stats

    def get_social_proof_stats(self) -> dict:
        """
        Retrieves statistics for social proof widgets.
        """
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

        # Total Gacha spins today
        gacha_spins_today = self.db.query(models.UserAction).filter(
            models.UserAction.action_type == "GACHA_PULL",
            models.UserAction.created_at >= today_start
        ).count()

        # Recent big winners (e.g., payout > 100,000)
        recent_big_winners = self.db.query(models.Game, models.User).join(models.User).filter(
            models.Game.payout > 100000
        ).order_by(models.Game.created_at.desc()).limit(5).all()

        winners_data = [
            {"nickname": user.nickname, "payout": game.payout}
            for game, user in recent_big_winners
        ]

        return {
            "gacha_spins_today": gacha_spins_today,
            "recent_big_winners": winners_data
        }
