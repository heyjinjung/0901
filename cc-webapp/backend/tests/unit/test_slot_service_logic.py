import pytest
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session

from app.services.slot_service import SlotService, SlotSpinResult
from app.repositories.game_repository import GameRepository
from app.services.token_service import TokenService

@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)

@pytest.fixture
def mock_game_repo():
    return MagicMock(spec=GameRepository)

@pytest.fixture
def mock_token_service():
    return MagicMock(spec=TokenService)

def test_slot_spin_success_win(mock_db_session, mock_game_repo, mock_token_service):
    """
    Test a successful slot spin that results in a win.
    """
    # Arrange
    user_id = 1
    bet_amount = 5000

    mock_game_repo.count_daily_actions.return_value = 5  # Below the limit
    mock_token_service.deduct_tokens.return_value = bet_amount
    mock_token_service.get_token_balance.return_value = 10000 + (bet_amount * 2) - bet_amount

    # Force a win by mocking random.random
    with pytest.MonkeyPatch.context() as m:
        m.setattr('random.random', lambda: 0.01) # This will be less than win_chance (0.075)
        slot_service = SlotService(repository=mock_game_repo, token_service=mock_token_service, db=mock_db_session)

        # Act
        result = slot_service.spin(user_id=user_id, bet_amount=bet_amount, db=mock_db_session)

    # Assert
    assert result.result == "win"
    assert result.tokens_change == bet_amount  # Payout (2*bet) - Cost (bet) = bet
    mock_token_service.deduct_tokens.assert_called_once_with(user_id, bet_amount)
    mock_token_service.add_tokens.assert_called_once_with(user_id, bet_amount * 2)
    mock_game_repo.record_action.assert_called_once()
    assert result.daily_spin_count == 6

def test_slot_spin_success_loss(mock_db_session, mock_game_repo, mock_token_service):
    """
    Test a successful slot spin that results in a loss.
    """
    # Arrange
    user_id = 1
    bet_amount = 5000

    mock_game_repo.count_daily_actions.return_value = 10
    mock_token_service.deduct_tokens.return_value = bet_amount
    mock_token_service.get_token_balance.return_value = 10000 - bet_amount
    mock_token_service.add_tokens.call_count = 0 # Reset mock

    # Force a loss
    with pytest.MonkeyPatch.context() as m:
        m.setattr('random.random', lambda: 0.9) # This will be more than win_chance (0.075)
        slot_service = SlotService(repository=mock_game_repo, token_service=mock_token_service, db=mock_db_session)

        # Act
        result = slot_service.spin(user_id=user_id, bet_amount=bet_amount, db=mock_db_session)

    # Assert
    assert result.result == "lose"
    assert result.tokens_change == -bet_amount
    mock_token_service.deduct_tokens.assert_called_once_with(user_id, bet_amount)
    mock_token_service.add_tokens.assert_not_called() # No tokens should be added on loss
    mock_game_repo.record_action.assert_called_once()
    assert result.daily_spin_count == 11

def test_slot_spin_daily_limit_exceeded(mock_db_session, mock_game_repo, mock_token_service):
    """
    Test that a user cannot spin if they have reached their daily limit.
    """
    # Arrange
    user_id = 1
    bet_amount = 5000
    mock_game_repo.count_daily_actions.return_value = 30 # At the limit

    slot_service = SlotService(repository=mock_game_repo, token_service=mock_token_service, db=mock_db_session)

    # Act & Assert
    with pytest.raises(ValueError, match="일일 슬롯 스핀 횟수(30회)를 초과했습니다."):
        slot_service.spin(user_id=user_id, bet_amount=bet_amount, db=mock_db_session)

def test_slot_spin_insufficient_funds(mock_db_session, mock_game_repo, mock_token_service):
    """
    Test that a user cannot spin if they have insufficient funds.
    """
    # Arrange
    user_id = 1
    bet_amount = 5000
    mock_game_repo.count_daily_actions.return_value = 15
    mock_token_service.deduct_tokens.return_value = None # Simulate insufficient funds

    slot_service = SlotService(repository=mock_game_repo, token_service=mock_token_service, db=mock_db_session)

    # Act & Assert
    with pytest.raises(ValueError, match="토큰이 부족합니다."):
        slot_service.spin(user_id=user_id, bet_amount=bet_amount, db=mock_db_session)

def test_slot_spin_invalid_bet_amount(mock_db_session, mock_game_repo, mock_token_service):
    """
    Test that a spin with an invalid bet amount is rejected.
    """
    # Arrange
    user_id = 1
    bet_amount = 100 # Invalid bet amount
    slot_service = SlotService(repository=mock_game_repo, token_service=mock_token_service, db=mock_db_session)

    # Act & Assert
    with pytest.raises(ValueError, match="베팅액은 5,000에서 10,000 사이여야 합니다."):
        slot_service.spin(user_id=user_id, bet_amount=bet_amount, db=mock_db_session)
