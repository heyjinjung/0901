import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from app.services.rps_service import RPSService
from app.repositories.game_repository import GameRepository
from app.services.token_service import TokenService
from app.models import User

@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)

@pytest.fixture
def mock_game_repo():
    return MagicMock(spec=GameRepository)

@pytest.fixture
def mock_token_service():
    return MagicMock(spec=TokenService)

@pytest.fixture
def standard_user():
    return User(id=1, rank="STANDARD")

@pytest.fixture
def rps_service(mock_game_repo, mock_token_service, mock_db_session):
    return RPSService(repository=mock_game_repo, token_service=mock_token_service, db=mock_db_session)

def test_rps_play_win(rps_service, mock_db_session, mock_token_service, standard_user):
    """Test a winning game of RPS."""
    # Arrange
    mock_db_session.query.return_value.filter.return_value.first.return_value = standard_user
    mock_game_repo.count_daily_actions.return_value = 0
    bet_amount = 5000

    with patch('random.random', return_value=0.1): # Force a win (win rate is 0.39)
        # Act
        result = rps_service.play(user_id=1, user_choice='rock', bet_amount=bet_amount, db=mock_db_session)

    # Assert
    assert result.result == 'win'
    assert result.tokens_change == bet_amount
    mock_token_service.deduct_tokens.assert_called_once_with(1, bet_amount)
    mock_token_service.add_tokens.assert_called_once_with(1, bet_amount * 2)
    mock_game_repo.record_action.assert_called_once()

def test_rps_play_loss(rps_service, mock_db_session, mock_token_service, standard_user):
    """Test a losing game of RPS."""
    # Arrange
    mock_db_session.query.return_value.filter.return_value.first.return_value = standard_user
    mock_game_repo.count_daily_actions.return_value = 0
    bet_amount = 5000
    mock_token_service.add_tokens.reset_mock()

    with patch('random.random', return_value=0.9): # Force a loss
        # Act
        result = rps_service.play(user_id=1, user_choice='rock', bet_amount=bet_amount, db=mock_db_session)

    # Assert
    assert result.result == 'lose'
    assert result.tokens_change == -bet_amount
    mock_token_service.deduct_tokens.assert_called_once_with(1, bet_amount)
    mock_token_service.add_tokens.assert_not_called()

def test_rps_play_daily_limit(rps_service, mock_db_session, standard_user):
    """Test the daily limit for a standard user."""
    # Arrange
    mock_db_session.query.return_value.filter.return_value.first.return_value = standard_user
    rps_service.repo.count_daily_actions.return_value = 3 # At the limit

    # Act & Assert
    with pytest.raises(ValueError, match="Daily RPS play limit (3) exceeded."):
        rps_service.play(user_id=1, user_choice='rock', bet_amount=5000, db=mock_db_session)


@pytest.mark.parametrize("forced,result_field_checker", [
    ("win", lambda r, bet: (r.result == "win" and r.tokens_change == bet)),
    ("draw", lambda r, bet: (r.result == "draw" and r.tokens_change == 0)),
    ("lose", lambda r, bet: (r.result == "lose" and r.tokens_change == -bet)),
])
def test_rps_deterministic_modes(rps_service, mock_db_session, mock_token_service, standard_user, forced, result_field_checker, monkeypatch):
    """CASINO_RPS_DETERMINISTIC=win/draw/lose 강제 결과 모드 검증."""
    monkeypatch.setenv("CASINO_RPS_DETERMINISTIC", forced)
    mock_db_session.query.return_value.filter.return_value.first.return_value = standard_user
    rps_service.repo.count_daily_actions.return_value = 0
    bet_amount = 5000

    result = rps_service.play(user_id=1, user_choice='rock', bet_amount=bet_amount, db=mock_db_session)

    assert result_field_checker(result, bet_amount)
    mock_token_service.deduct_tokens.assert_called_with(1, bet_amount)
