import pytest
from fastapi.testclient import TestClient


def test_streak_status_basic(client: TestClient):
    r = client.get("/api/streak/status?action_type=DAILY_LOGIN")
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["action_type"] == "DAILY_LOGIN"
    assert "count" in data
    assert "ttl_seconds" in data
    assert "next_reward" in data
