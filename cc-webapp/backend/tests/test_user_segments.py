import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.models import UserSegment

@pytest.fixture
def client():
    # FIX: app import moved to module level, TestClient(app) as positional argument only
    with TestClient(app) as c:
        yield c

# Test Case 1: Whale/High-Risk, high streak
@patch('app.routers.user_segments.redis_client')
@patch('app.routers.user_segments.SessionLocal')
def test_recommendation_whale_high_risk_high_streak(MockSessionLocal, mock_redis_client_instance, client):
    mock_db_session = MagicMock()
    mock_user_segment_db_instance = UserSegment(user_id=1, rfm_group="Whale", name="Whale", risk_profile="High-Risk")
    mock_db_session.query(UserSegment).filter().first.return_value = mock_user_segment_db_instance
    MockSessionLocal.return_value.__enter__.return_value = mock_db_session

    if mock_redis_client_instance is not None:
        mock_redis_client_instance.get.return_value = "10"

    response = client.get("/api/user-segments/1/recommendation")

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 1
    assert data["rfm_group"] == "Whale"
    assert data["risk_profile"] == "High-Risk"
    assert data["streak_count"] == 10
    assert data["recommended_reward_probability"] == 0.85
    assert data["recommended_time_window"] == "next 2 hours"

# Test Case 2: Medium/Low-Risk, zero streak
@patch('app.routers.user_segments.redis_client')
@patch('app.routers.user_segments.SessionLocal')
def test_recommendation_medium_low_risk_zero_streak(MockSessionLocal, mock_redis_client_instance, client):
    mock_db_session = MagicMock()
    mock_user_segment_db_instance = UserSegment(user_id=2, rfm_group="Medium", name="Medium", risk_profile="Low-Risk")
    mock_db_session.query(UserSegment).filter().first.return_value = mock_user_segment_db_instance
    MockSessionLocal.return_value.__enter__.return_value = mock_db_session

    if mock_redis_client_instance:
        mock_redis_client_instance.get.return_value = "0"

    response = client.get("/api/user-segments/2/recommendation")
    assert response.status_code == 200
    data = response.json()
    assert data["rfm_group"] == "Medium"
    assert data["risk_profile"] == "Low-Risk"
    assert data["streak_count"] == 0
    assert data["recommended_reward_probability"] == 0.50
    assert data["recommended_time_window"] == "next 6 hours"

# Test Case 3: Low RFM, any risk, no streak in Redis (default to 0)
@patch('app.routers.user_segments.redis_client')
@patch('app.routers.user_segments.SessionLocal')
def test_recommendation_low_rfm_no_streak_in_redis(MockSessionLocal, mock_redis_client_instance, client):
    mock_db_session = MagicMock()
    mock_user_segment_db_instance = UserSegment(user_id=3, rfm_group="Low", name="Low", risk_profile="Medium-Risk")
    mock_db_session.query(UserSegment).filter().first.return_value = mock_user_segment_db_instance
    MockSessionLocal.return_value.__enter__.return_value = mock_db_session

    if mock_redis_client_instance:
        mock_redis_client_instance.get.return_value = None

    response = client.get("/api/user-segments/3/recommendation")
    assert response.status_code == 200
    data = response.json()
    assert data["rfm_group"] == "Low"
    assert data["risk_profile"] == "Medium-Risk"
    assert data["streak_count"] == 0
    assert data["recommended_reward_probability"] == 0.25
    assert data["recommended_time_window"] == "next 24 hours"

# Test Case 4: User segment not found in DB
@patch('app.routers.user_segments.redis_client')
@patch('app.routers.user_segments.SessionLocal')
def test_recommendation_user_segment_not_found(MockSessionLocal, mock_redis_client_instance, client):
    mock_db_session = MagicMock()
    mock_db_session.query(UserSegment).filter().first.return_value = None
    MockSessionLocal.return_value.__enter__.return_value = mock_db_session

    if mock_redis_client_instance:
        mock_redis_client_instance.get.return_value = "5"

    response = client.get("/api/user-segments/999/recommendation")
    assert response.status_code == 404

# Test Case 5: Redis client is None (simulating connection failure at startup)
@patch('app.routers.user_segments.redis_client', None)
@patch('app.routers.user_segments.SessionLocal')
def test_recommendation_redis_client_none(MockSessionLocal, client):
    mock_db_session = MagicMock()
    mock_user_segment_db_instance = UserSegment(user_id=1, rfm_group="Whale", name="Whale", risk_profile="High-Risk")
    mock_db_session.query(UserSegment).filter().first.return_value = mock_user_segment_db_instance
    MockSessionLocal.return_value.__enter__.return_value = mock_db_session

    response = client.get("/api/user-segments/1/recommendation")

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 1
    assert data["rfm_group"] == "Whale"
    assert data["risk_profile"] == "High-Risk"
    assert data["streak_count"] == 0
    assert data["recommended_reward_probability"] == 0.75
    assert data["recommended_time_window"] == "next 2 hours"
