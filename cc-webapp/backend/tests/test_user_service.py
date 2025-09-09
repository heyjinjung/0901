"""
Casino Club UserService 테스트
커버리지 향상용 기본/엣지/에러 케이스 포함
"""
import pytest
from app.services.user_service import UserService
from unittest.mock import MagicMock

@pytest.fixture
def mock_repo():
    repo = MagicMock()
    repo.get_user.return_value = {"id": 1, "nickname": "tester", "rank": "VIP"}
    repo.create_user.return_value = {"id": 2, "nickname": "newbie", "rank": "STANDARD"}
    return repo

@pytest.fixture
def service(mock_repo):
    return UserService(repository=mock_repo)


def test_get_user_success(service):
    user = service.get_user(1)
    assert user["id"] == 1
    assert user["nickname"] == "tester"
    assert user["rank"] == "VIP"


def test_get_user_none(service, mock_repo):
    mock_repo.get_user.return_value = None
    user = service.get_user(999)
    assert user is None


def test_create_user_success(service):
    user = service.create_user("newbie", "STANDARD", site_id=1)
    assert user["id"] == 2
    assert user["nickname"] == "newbie"
    assert user["rank"] == "STANDARD"


def test_create_user_invalid_rank(service):
    with pytest.raises(ValueError):
        service.create_user("badguy", "UNKNOWN")


def test_update_user_rank(service, mock_repo):
    mock_repo.update_user_rank.return_value = {"id": 1, "nickname": "tester", "rank": "PREMIUM"}
    user = service.update_user_rank(1, "PREMIUM")
    assert user["rank"] == "PREMIUM"


def test_update_user_rank_invalid(service):
    with pytest.raises(ValueError):
        service.update_user_rank(1, "INVALID")


def test_delete_user(service, mock_repo):
    mock_repo.delete_user.return_value = True
    result = service.delete_user(1)
    assert result is True


def test_delete_user_not_found(service, mock_repo):
    mock_repo.delete_user.return_value = False
    result = service.delete_user(999)
    assert result is False
