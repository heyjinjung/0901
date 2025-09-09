"""가챠 라우터 테스트 모듈."""

import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.services.gacha_service import GachaPullResult
from app.routers import gacha as gacha_router

@pytest.fixture
def client():
    from app.main import app
    with TestClient(app) as c:
        yield c

def test_pull_gacha_uses_service(client, monkeypatch):
    """서비스 의존성 주입이 제대로 동작하는지 확인."""

    service_mock = MagicMock()
    service_mock.pull.return_value = GachaPullResult(["Legendary"], -50, 50)
    monkeypatch.setitem(
        client.app.dependency_overrides, gacha_router.get_service, lambda: service_mock
    )

    class DummyDB:
        def query(self, model):
            class Q:
                def filter(self, *args, **kwargs):
                    class F:
                        def first(self):
                            return object()

                    return F()

            return Q()

    monkeypatch.setitem(
        client.app.dependency_overrides, gacha_router.get_db, lambda: DummyDB()
    )

    response = client.post("/api/gacha/pull", json={"user_id": 1})
    assert response.status_code == 200
    assert response.json()["type"] == "Legendary"
    service_mock.pull.assert_called_once()
