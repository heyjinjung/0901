from fastapi.testclient import TestClient
from app.main import app
import pytest


@pytest.mark.ci_core
def test_health_endpoint_basic():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200, r.text
    data = r.json()
    assert isinstance(data, dict)
    # 기존 다양한 형태 지원 -> 이제 표준 HealthResponse 사용
    assert set(["status", "timestamp", "version"]).issubset(data.keys()), data
    # 새 필드 redis_connected 존재 (bool 또는 null)
    assert "redis_connected" in data
    assert data["status"] == "healthy"
