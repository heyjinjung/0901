import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.services.dashboard_service import DashboardService
from app.models import User, UserAction, Game

@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)

@pytest.fixture
def dashboard_service(mock_db_session):
    return DashboardService(db=mock_db_session)

def test_get_main_dashboard_stats(dashboard_service, mock_db_session):
    """
    Test the main dashboard statistics aggregation.
    """
    # Arrange
    mock_query = mock_db_session.query.return_value

    # Mock DAU count
    mock_query.filter.return_value.distinct.return_value.count.return_value = 5
    # Mock New Users count
    mock_query.filter.return_value.count.return_value = 2
    # Mock Total Revenue
    mock_query.scalar.return_value = 500000

    # Act
    result = dashboard_service.get_main_dashboard_stats()

    # Assert
    assert result["daily_active_users"] == 5
    assert result["new_users_today"] == 2
    assert result["total_revenue"] == 500000

def test_get_game_dashboard_stats(dashboard_service, mock_db_session):
    """
    Test the game-specific dashboard statistics aggregation.
    """
    # Arrange
    mock_query = mock_db_session.query.return_value

    # Mock stats for 'slot' game
    mock_slot_stats = MagicMock()
    mock_slot_stats.total_bet = 100000
    mock_slot_stats.total_payout = 15000

    # Mock stats for 'roulette' game
    mock_roulette_stats = MagicMock()
    mock_roulette_stats.total_bet = 50000
    mock_roulette_stats.total_payout = 45000

    # The filter().first() chain will be called for each game.
    # We can use side_effect to return different values for each call.
    mock_query.filter.return_value.first.side_effect = [
        mock_slot_stats,
        mock_roulette_stats,
        MagicMock(total_bet=0, total_payout=0), # rps
        MagicMock(total_bet=0, total_payout=0)  # gacha
    ]

    # Act
    result = dashboard_service.get_game_dashboard_stats()

    # Assert
    assert "slot" in result
    assert result["slot"]["total_bet"] == 100000
    assert result["slot"]["profit"] == 85000
    assert result["slot"]["rtp"] == 15.0

    assert "roulette" in result
    assert result["roulette"]["total_bet"] == 50000
    assert result["roulette"]["profit"] == 5000
    assert result["roulette"]["rtp"] == 90.0

    assert "rps" in result
    assert result["rps"]["total_bet"] == 0

def test_get_social_proof_stats(dashboard_service, mock_db_session):
    """
    Test the social proof statistics aggregation.
    """
    # Arrange
    mock_query = mock_db_session.query.return_value

    # Mock gacha spins count
    mock_query.filter.return_value.count.return_value = 123

    # Mock big winners
    mock_winners = [
        (MagicMock(payout=200000), MagicMock(nickname="Winner1")),
        (MagicMock(payout=150000), MagicMock(nickname="Winner2")),
    ]
    mock_query.join.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = mock_winners

    # Act
    result = dashboard_service.get_social_proof_stats()

    # Assert
    assert result["gacha_spins_today"] == 123
    assert len(result["recent_big_winners"]) == 2
    assert result["recent_big_winners"][0]["nickname"] == "Winner1"
    assert result["recent_big_winners"][0]["payout"] == 200000
