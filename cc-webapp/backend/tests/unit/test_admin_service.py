import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from app.services.admin_service import AdminService
from app.models import User

@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)

@pytest.fixture
def admin_service(mock_db_session):
    return AdminService(db=mock_db_session)

@pytest.fixture
def mock_users():
    return [
        User(id=1, site_id='user1', nickname='TestUser1', phone_number='111'),
        User(id=2, site_id='user2', nickname='TestUser2', phone_number='222'),
        User(id=3, site_id='user3', nickname='SearchMe', phone_number='333'),
    ]

def test_list_users_no_search(admin_service, mock_db_session, mock_users):
    """
    Test listing users without any search query.
    """
    # Arrange
    mock_query = mock_db_session.query.return_value
    mock_query.offset.return_value.limit.return_value.all.return_value = mock_users

    # Act
    result = admin_service.list_users(skip=0, limit=10, search=None)

    # Assert
    assert len(result) == 3
    mock_db_session.query.assert_called_once_with(User)
    assert mock_query.filter.call_count == 0 # No filter should be applied

def test_list_users_with_search(admin_service, mock_db_session, mock_users):
    """
    Test listing users with a search query.
    """
    # Arrange
    mock_query = mock_db_session.query.return_value
    # Simulate the filtering returning one user
    mock_filtered_query = mock_query.filter.return_value
    mock_filtered_query.offset.return_value.limit.return_value.all.return_value = [mock_users[2]] # The 'SearchMe' user

    # Act
    result = admin_service.list_users(skip=0, limit=10, search="SearchMe")

    # Assert
    assert len(result) == 1
    assert result[0].nickname == "SearchMe"
    mock_query.filter.assert_called_once() # Filter should be applied

def test_get_user_details(admin_service, mock_db_session, mock_users):
    """
    Test getting details for a single user.
    """
    # Arrange
    user_id = 2
    mock_user = mock_users[1]
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user

    # Act
    result = admin_service.get_user_details(user_id=user_id)

    # Assert
    assert result is not None
    assert result.id == user_id
    assert result.nickname == "TestUser2"
    mock_db_session.query.assert_called_once_with(User)
    mock_db_session.query.return_value.filter.assert_called_once()
