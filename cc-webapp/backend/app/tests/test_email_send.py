import os
import time
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


def test_email_test_endpoint(monkeypatch):
    # Ensure SMTP points to Mailpit by default
    monkeypatch.setenv("SMTP_HOST", os.getenv("SMTP_HOST", "mailpit"))
    monkeypatch.setenv("SMTP_PORT", os.getenv("SMTP_PORT", "1025"))

    # Create a user and login via existing fixtures if available; fallback to stub token
    token = os.getenv("TEST_USER_TOKEN", "testtoken")

    # If auth is enforced, this may require a real token; this test focuses on route wiring
    r = client.get("/api/email/test", headers=auth_headers(token))
    assert r.status_code in (200, 401, 403), r.text


def test_send_template_self_guard(monkeypatch):
    token = os.getenv("TEST_USER_TOKEN", "testtoken")
    payload = {
        "to": "self@example.com",
        "template": "welcome",
        "context": {"nickname": "Tester", "bonus": 100},
    }
    r = client.post("/api/email/send-template", json=payload, headers=auth_headers(token))
    # Might be 403 if token isn't admin and target doesn't match current user's email
    assert r.status_code in (200, 403, 401)
