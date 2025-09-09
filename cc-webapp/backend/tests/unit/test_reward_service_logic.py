import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from app.services.reward_service import RewardService
from app.services.token_service import TokenService
from app.models import UserReward

@pytest.fixture
def mock_db_session():
    db = MagicMock(spec=Session)
    # Mock the add, commit, and refresh methods
    db.add.return_value = None
    db.commit.return_value = None
    db.refresh.return_value = None
    return db

@pytest.fixture
def mock_token_service():
    return MagicMock(spec=TokenService)

@pytest.fixture
def reward_service(mock_db_session, mock_token_service):
    return RewardService(db=mock_db_session, token_service=mock_token_service)

def test_distribute_reward_coin(reward_service, mock_db_session, mock_token_service):
    """
    Test distributing a COIN reward.
    """
    # Arrange
    user_id = 1
    reward_type = "COIN"
    amount = 1000
    source = "Test Win"

    # Act
    result = reward_service.distribute_reward(
        user_id=user_id,
        reward_type=reward_type,
        amount=amount,
        source_description=source
    )

    # Assert
    # 1. Check if token service was called
    mock_token_service.add_tokens.assert_called_once_with(user_id, amount)

    # 2. Check if a UserReward object was created and added to the session
    mock_db_session.add.assert_called_once()
    added_object = mock_db_session.add.call_args[0][0]
    assert isinstance(added_object, UserReward)
    assert added_object.user_id == user_id
    assert added_object.reward_type == reward_type
    assert added_object.reward_value == str(amount)
    assert added_object.source_description == source

    # 3. Check if commit was called
    mock_db_session.commit.assert_called_once()

def test_distribute_reward_other_type(reward_service, mock_db_session, mock_token_service):
    """
    Test distributing a non-COIN reward (e.g., an item).
    """
    # Arrange
    user_id = 1
    reward_type = "ITEM"
    amount = 1 # Represents one item
    source = "Test Gacha"

    # Act
    result = reward_service.distribute_reward(
        user_id=user_id,
        reward_type=reward_type,
        amount=amount,
        source_description=source
    )

    # Assert
    # 1. Token service should NOT be called for non-coin rewards
    mock_token_service.add_tokens.assert_not_called()

    # 2. A UserReward record should still be created
    mock_db_session.add.assert_called_once()
    added_object = mock_db_session.add.call_args[0][0]
    assert isinstance(added_object, UserReward)
    assert added_object.reward_type == "ITEM"
    mock_db_session.commit.assert_called_once()
