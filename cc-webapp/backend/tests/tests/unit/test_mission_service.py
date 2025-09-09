import pytest
pytest.skip("Duplicate mission service test (tests/tests) – skipped", allow_module_level=True)

from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from datetime import datetime

from app.services.mission_service import MissionService
from app.models import Mission, UserMissionProgress, UserReward

@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)

@pytest.fixture
def mission_service(mock_db_session):
    return MissionService(db=mock_db_session)

def test_list_user_missions(mission_service, mock_db_session):
    """Test listing user missions with their progress."""
    # Arrange
    user_id = 1
    mock_missions = [Mission(id=1, title="Test Mission", target_count=10)]
    mock_progress = [UserMissionProgress(mission_id=1, user_id=user_id, current_count=5)]

    # This is a simplification. A real test would mock the query chain.
    def query_side_effect(model):
        if model == Mission:
            return mock_db_session.query.return_value.filter.return_value
        if model == UserMissionProgress:
            return mock_db_session.query.return_value.filter.return_value
        return MagicMock()

    mock_db_session.query.side_effect = query_side_effect
    mock_db_session.query.return_value.filter.return_value.all.side_effect = [mock_missions, mock_progress]

    # Act
    result = mission_service.list_user_missions(user_id=user_id)

    # Assert
    assert len(result) == 1
    assert result[0]["title"] == "Test Mission"
    assert result[0]["current_count"] == 5

def test_claim_reward_success(mission_service, mock_db_session):
    """Test successfully claiming a completed mission reward."""
    # Arrange
    user_id = 1
    mission_id = 1
    mock_progress = UserMissionProgress(is_completed=True, is_claimed=False)
    mock_mission = Mission(id=mission_id, title="Claimable", reward_type="COIN", reward_amount=100)

    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_progress
    mock_db_session.query.return_value.filter_by.return_value.one.return_value = mock_mission

    # Mock the nested RewardService call
    with patch('app.services.mission_service.RewardService') as mock_reward_service_class:
        mock_reward_service_instance = mock_reward_service_class.return_value
        mock_reward_service_instance.distribute_reward.return_value = UserReward(id=99)

        # Act
        result = mission_service.claim_reward(user_id=user_id, mission_id=mission_id)

    # Assert
    assert mock_progress.is_claimed is True
    assert mock_progress.claimed_at is not None
    mock_reward_service_instance.distribute_reward.assert_called_once_with(
        user_id=user_id,
        reward_type="COIN",
        amount=100,
        source_description="Mission Complete: Claimable"
    )
    mock_db_session.commit.assert_called_once()
    assert result.id == 99

def test_claim_reward_not_completed(mission_service, mock_db_session):
    """Test claiming a reward for a mission that is not yet completed."""
    # Arrange
    mock_progress = UserMissionProgress(is_completed=False)
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_progress

    # Act & Assert
    with pytest.raises(ValueError, match="Mission not completed."):
        mission_service.claim_reward(user_id=1, mission_id=1)

def test_claim_reward_already_claimed(mission_service, mock_db_session):
    """Test claiming a reward that has already been claimed."""
    # Arrange
    mock_progress = UserMissionProgress(is_completed=True, is_claimed=True)
    mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_progress

    # Act & Assert
    with pytest.raises(ValueError, match="Reward already claimed."):
        mission_service.claim_reward(user_id=1, mission_id=1)
