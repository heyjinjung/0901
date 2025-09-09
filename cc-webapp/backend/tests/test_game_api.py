"""
게임 API 통합 테스트 (pytest)
- /api/games/stats/{user_id}
- /api/games/session/{user_id}/current
- /api/games/achievements/{user_id}
- /api/games/leaderboard
- /api/games/profile/{user_id}/stats
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_get_game_stats(client):
    user_id = 1
    response = client.get(f"/api/games/stats/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert data["user_id"] == user_id

def test_get_current_game_session(client):
    user_id = 1
    response = client.get(f"/api/games/session/{user_id}/current")
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert data["user_id"] == user_id

def test_get_user_achievements(client):
    user_id = 1
    response = client.get(f"/api/games/achievements/{user_id}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_leaderboard(client):
    response = client.get("/api/games/leaderboard?game_type=roulette")
    assert response.status_code == 200
    data = response.json()
    assert "game_type" in data
    assert "entries" in data

def test_get_profile_game_stats(client):
    user_id = 1
    response = client.get(f"/api/games/profile/{user_id}/stats")
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert data["user_id"] == user_id
