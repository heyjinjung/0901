import pytest
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session

from app.services.gacha_service import GachaService
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
    user = User(id=1, rank="STANDARD")
    return user

@pytest.fixture
def vip_user():
    user = User(id=2, rank="VIP")
    return user

def test_gacha_pull_success(mock_db_session, mock_game_repo, mock_token_service, standard_user):
    """
    Test a successful gacha pull for a standard user.
    """
    # Arrange
    mock_db_session.query.return_value.filter.return_value.first.return_value = standard_user
    mock_game_repo.count_daily_actions.return_value = 1  # Below the limit of 3
    mock_token_service.deduct_tokens.return_value = 5000
    mock_token_service.get_token_balance.return_value = 100000 - 5000

    gacha_service = GachaService(repository=mock_game_repo, token_service=mock_token_service, db=mock_db_session)

    # Act
    result = gacha_service.pull(user_id=standard_user.id, db=mock_db_session)

    # Assert
    assert result.tokens_change == -5000
    mock_token_service.deduct_tokens.assert_called_once_with(standard_user.id, 5000)
    mock_game_repo.record_action.assert_called_once()
    assert "GACHA_PULL" in mock_game_repo.record_action.call_args[0]

def test_gacha_pull_daily_limit_standard(mock_db_session, mock_game_repo, mock_token_service, standard_user):
    """
    Test that a standard user cannot pull if they have reached their daily limit.
    """
    # Arrange
    mock_db_session.query.return_value.filter.return_value.first.return_value = standard_user
    mock_game_repo.count_daily_actions.return_value = 3 # At the limit

    gacha_service = GachaService(repository=mock_game_repo, token_service=mock_token_service, db=mock_db_session)

    # Act & Assert
    with pytest.raises(ValueError, match="일일 가챠 횟수(3회)를 초과했습니다."):
        gacha_service.pull(user_id=standard_user.id, db=mock_db_session)

def test_gacha_pull_daily_limit_vip(mock_db_session, mock_game_repo, mock_token_service, vip_user):
    """
    Test that a VIP user cannot pull if they have reached their daily limit.
    """
    # Arrange
    mock_db_session.query.return_value.filter.return_value.first.return_value = vip_user
    mock_game_repo.count_daily_actions.return_value = 5 # At the limit

    gacha_service = GachaService(repository=mock_game_repo, token_service=mock_token_service, db=mock_db_session)

    # Act & Assert
    with pytest.raises(ValueError, match="일일 가챠 횟수(5회)를 초과했습니다."):
        gacha_service.pull(user_id=vip_user.id, db=mock_db_session)

def test_gacha_pull_insufficient_funds(mock_db_session, mock_game_repo, mock_token_service, standard_user):
    """
    Test that a user cannot pull if they have insufficient funds.
    """
    # Arrange
    mock_db_session.query.return_value.filter.return_value.first.return_value = standard_user
    mock_game_repo.count_daily_actions.return_value = 0
    mock_token_service.deduct_tokens.return_value = None # Simulate insufficient funds

    gacha_service = GachaService(repository=mock_game_repo, token_service=mock_token_service, db=mock_db_session)

    # Act & Assert
    with pytest.raises(ValueError, match="토큰이 부족합니다."):
        gacha_service.pull(user_id=standard_user.id, db=mock_db_session)
