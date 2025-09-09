import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from app.services.roulette_service import RouletteService
from app.repositories.game_repository import GameRepository
from app.services.token_service import TokenService

@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)

@pytest.fixture
def mock_game_repo():
    repo = MagicMock(spec=GameRepository)
    repo.count_daily_actions.return_value = 0
    return repo

@pytest.fixture
def mock_token_service():
    ts = MagicMock(spec=TokenService)
    ts.deduct_tokens.return_value = 5000  # Assume success
    return ts

@pytest.fixture
def roulette_service(mock_game_repo, mock_token_service, mock_db_session):
    return RouletteService(repository=mock_game_repo, token_service=mock_token_service, db=mock_db_session)

def test_roulette_spin_success(roulette_service, mock_token_service):
    """
    Test a successful roulette spin.
    """
    # Arrange
    user_id = 1
    bet_amount = 5000

    # Act
    result = roulette_service.spin(user_id=user_id, bet_amount=bet_amount, db=MagicMock())

    # Assert
    assert result.success is True
    assert result.prize is not None
    assert result.daily_spin_count == 1
    mock_token_service.deduct_tokens.assert_called_once_with(user_id, bet_amount)
    if result.prize.id != 'bet_back':
        mock_token_service.add_tokens.assert_called_once_with(user_id, result.prize.value)
        assert result.tokens_change == result.prize.value - bet_amount
    else:
        mock_token_service.add_tokens.assert_called_once_with(user_id, bet_amount)
        assert result.tokens_change == 0


def test_roulette_spin_daily_limit_exceeded(roulette_service, mock_game_repo):
    """
    Test that a user cannot spin if they have reached their daily limit.
    """
    # Arrange
    user_id = 1
    bet_amount = 5000
    mock_game_repo.count_daily_actions.return_value = 10 # At the limit

    # Act & Assert
    with pytest.raises(ValueError, match="일일 룰렛 스핀 횟수(10회)를 초과했습니다."):
        roulette_service.spin(user_id=user_id, bet_amount=bet_amount, db=MagicMock())

def test_roulette_spin_insufficient_funds(roulette_service, mock_token_service):
    """
    Test that a user cannot spin if they have insufficient funds.
    """
    # Arrange
    user_id = 1
    bet_amount = 5000
    mock_token_service.deduct_tokens.return_value = None # Simulate insufficient funds

    # Act & Assert
    with pytest.raises(ValueError, match="토큰이 부족합니다."):
        roulette_service.spin(user_id=user_id, bet_amount=bet_amount, db=MagicMock())

@pytest.mark.parametrize("bet_amount", [4999, 10001])
def test_roulette_spin_invalid_bet_amount(roulette_service, bet_amount):
    """
    Test that a spin with an invalid bet amount is rejected.
    """
    # Arrange
    user_id = 1

    # Act & Assert
    with pytest.raises(ValueError, match="베팅액은 5,000에서 10,000 사이여야 합니다."):
        roulette_service.spin(user_id=user_id, bet_amount=bet_amount, db=MagicMock())
