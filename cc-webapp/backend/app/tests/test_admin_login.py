import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

ADMIN_SITE_ID = "admin"
ADMIN_PASSWORD = "123456"  # seed_basic_accounts.py sets this
USER_SITE_ID = "user001"
USER_PASSWORD = "123456"


def test_admin_login_success():
    resp = client.post("/api/auth/admin/login", json={"site_id": ADMIN_SITE_ID, "password": ADMIN_PASSWORD})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data.get("access_token")
    assert data.get("user", {}).get("site_id") == ADMIN_SITE_ID
    assert data.get("user", {}).get("is_admin") is True


def test_admin_login_non_admin_rejected():
    # normal user should fail with 401 (invalid admin credentials)
    resp = client.post("/api/auth/admin/login", json={"site_id": USER_SITE_ID, "password": USER_PASSWORD})
    assert resp.status_code == 401
    body = resp.json()
    # Body may be {"detail": ...} per FastAPI for HTTPException
    assert "detail" in body
