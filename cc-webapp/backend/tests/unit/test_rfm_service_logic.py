import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.services.rfm_service import RFMService
from app.models import User, UserAction, Game, UserSegment

@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)

@pytest.fixture
def rfm_service(mock_db_session):
    return RFMService(db=mock_db_session)

def test_update_all_user_segments(rfm_service, mock_db_session):
    """
    Test the full RFM segmentation process for a list of users.
    """
    # Arrange
    # 1. Create mock users
    user1 = User(id=1) # High value user
    user2 = User(id=2) # At-risk user
    user3 = User(id=3) # New user with no data
    mock_users = [user1, user2, user3]

    # 2. Mock the query for all users
    mock_db_session.query.return_value.all.return_value = mock_users

    # 3. Mock the data for the high-value user (user1)
    # This user is recent, frequent, and high-spending
    action_stats_user1 = MagicMock()
    action_stats_user1.last_action_date = datetime.utcnow() - timedelta(days=5)
    action_stats_user1.frequency = 60
    monetary_stats_user1 = MagicMock()
    monetary_stats_user1.monetary_value = 600000

    # 4. Mock the data for the at-risk user (user2)
    # This user has not been active recently
    action_stats_user2 = MagicMock()
    action_stats_user2.last_action_date = datetime.utcnow() - timedelta(days=40)
    action_stats_user2.frequency = 5
    monetary_stats_user2 = MagicMock()
    monetary_stats_user2.monetary_value = 10000

    # 5. Mock the data for the new user (user3) - no actions
    action_stats_user3 = MagicMock()
    action_stats_user3.last_action_date = None
    action_stats_user3.frequency = 0
    monetary_stats_user3 = MagicMock()
    monetary_stats_user3.monetary_value = 0

    # Configure the side effect for the query mock
    def query_side_effect(model):
        if model == User:
            return mock_db_session.query.return_value
        # This part is tricky, we need to return the correct stats for each user
        # A more robust way would be to mock the filter().first() chain
        return MagicMock()

    mock_db_session.query.side_effect = query_side_effect

    # We will mock the filter().first() calls instead to be more specific
    def filter_first_side_effect(*args, **kwargs):
        # Based on the user_id being filtered, return the correct stats
        # This is a simplification; a real test might need more complex mocking
        # to inspect the filter arguments.
        # For this test, we'll assume the loop runs in order and we can pop from a list.
        if mock_db_session.query.call_args[0][0] == UserAction:
            return stats_by_user.pop(0)
        if mock_db_session.query.call_args[0][0] == Game:
            return monetary_by_user.pop(0)
        if mock_db_session.query.call_args[0][0] == UserSegment:
            return None # Assume no segments exist yet
        return MagicMock()

    stats_by_user = [action_stats_user1, action_stats_user2, action_stats_user3]
    monetary_by_user = [monetary_stats_user1, monetary_stats_user2, monetary_stats_user3]

    mock_db_session.query.return_value.filter.return_value.first.side_effect = filter_first_side_effect


    # Act
    rfm_service.update_all_user_segments()

    # Assert
    # Check that commit was called once at the end
    mock_db_session.commit.assert_called_once()

    # Check how many times `db.add` was called (should be 3 for 3 new segments)
    assert mock_db_session.add.call_count == 3

    # Inspect the created UserSegment objects
    added_segments = [call.args[0] for call in mock_db_session.add.call_args_list]

    segment_user1 = next((s for s in added_segments if s.user_id == 1), None)
    segment_user2 = next((s for s in added_segments if s.user_id == 2), None)
    segment_user3 = next((s for s in added_segments if s.user_id == 3), None)

    assert segment_user1 is not None
    assert segment_user1.rfm_group == "Whale"

    assert segment_user2 is not None
    assert segment_user2.rfm_group == "At-Risk"

    assert segment_user3 is not None
    assert segment_user3.rfm_group == "Low-Value"
