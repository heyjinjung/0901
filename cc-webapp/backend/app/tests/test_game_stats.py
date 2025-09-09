import pytest
from sqlalchemy.orm import Session
from decimal import Decimal

from app.services.game_stats_service import GameStatsService
from app.models.game_stats_models import UserGameStats
from app.models.history_models import GameHistory

# NOTE: Assuming a pytest fixture `db` (Session) exists elsewhere in test suite.
# If not, this test will need a fixture providing a transactional session.

@pytest.mark.usefixtures("db")
class TestGameStatsService:
    def test_get_or_create_idempotent(self, db: Session):
        svc = GameStatsService(db)
        a = svc.get_or_create(123)
        b = svc.get_or_create(123)
        assert a.user_id == 123
        assert a is b  # same instance within session

    def test_update_from_round_win_and_loss_accumulation(self, db: Session):
        svc = GameStatsService(db)
        # first loss: bet 100, win 0
        svc.update_from_round(user_id=1, bet_amount=100, win_amount=0, final_multiplier=1.25)
        stats = db.get(UserGameStats, 1)
        assert stats.total_bets == 1
        assert stats.total_losses == 1
        assert stats.total_wins == 0
        assert stats.total_profit == Decimal('-100')

        # second win: bet 200, win 400 (profit +200)
        svc.update_from_round(user_id=1, bet_amount=200, win_amount=400, final_multiplier=2.0)
        stats = db.get(UserGameStats, 1)
        assert stats.total_bets == 2
        assert stats.total_losses == 1
        assert stats.total_wins == 1
        # profit: -100 + (400-200)= +100
        assert stats.total_profit == Decimal('100')
        assert float(stats.highest_multiplier) == 2.0

    def test_highest_multiplier_regression_warning(self, db: Session, caplog):
        svc = GameStatsService(db)
        svc.update_from_round(user_id=2, bet_amount=50, win_amount=100, final_multiplier=3.0)
        # lower multiplier should NOT replace
        svc.update_from_round(user_id=2, bet_amount=10, win_amount=0, final_multiplier=1.5)
        stats = db.get(UserGameStats, 2)
        assert float(stats.highest_multiplier) == 3.0
        # we expect a regression warning log (non-fatal)
        found = any('highest_multiplier regression' in r.message for r in caplog.records)
        assert found

    def test_recalculate_user_parity(self, db: Session, monkeypatch):
        """Ensure recalc overwrites counters & keeps highest_multiplier intact."""
        svc = GameStatsService(db)
        # Build some history via incremental updates
        svc.update_from_round(user_id=3, bet_amount=100, win_amount=0, final_multiplier=1.1)  # loss
        svc.update_from_round(user_id=3, bet_amount=100, win_amount=300, final_multiplier=3.0)  # win +200
        svc.update_from_round(user_id=3, bet_amount=50, win_amount=100, final_multiplier=2.0)  # win +50
        before = db.get(UserGameStats, 3)
        assert before.total_bets == 3
        assert before.total_wins == 2
        assert before.total_losses == 1
        assert before.total_profit == Decimal('150')
        assert float(before.highest_multiplier) == 3.0

        # Simulate manual tamper
        before.total_bets = 999
        db.commit()

        # Recalculate -> should restore authoritative counts but leave highest_multiplier
        svc.recalculate_user(3)
        after = db.get(UserGameStats, 3)
        assert after.total_bets != 999
        assert after.total_wins == 2
        assert after.total_losses == 1
        assert after.total_profit == Decimal('150')
        assert float(after.highest_multiplier) == 3.0

    def test_history_visibility_same_session(self, db: Session):
        """update_from_round 직후 동일 세션에서 GameHistory가 조회 가능한지 확인."""
        svc = GameStatsService(db)
        svc.update_from_round(user_id=3, bet_amount=40, win_amount=0, final_multiplier=1.05)
        rows = (
            db.query(GameHistory)
            .filter(GameHistory.user_id == 3, GameHistory.game_type == "crash")
            .all()
        )
        assert any(r.action_type in ("BET", "WIN") for r in rows)
