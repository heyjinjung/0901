"""Auth 라우터의 로깅을 검증하는 테스트."""

import logging
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    from app.main import app
    with TestClient(app) as c:
        yield c

def test_login_logging(client, caplog):
    """로그인 성공 시 INFO 로그가 남는지 확인."""
    with caplog.at_level(logging.INFO):
        response = client.post(
            "/api/auth/login",
            json={
                "site_id": "testuser", 
                "password": "password"
            },
        )
        assert response.status_code == 200
        assert "Test login for testuser" in caplog.text
