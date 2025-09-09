import time
from datetime import datetime, timedelta

from app.models import InviteCode
from app.database import SessionLocal


def test_validate_invite_invalid_code(client):
    r = client.post("/api/invite/validate", json={"code": "NOPE"})
    assert r.status_code == 200
    j = r.json()
    assert j["is_valid"] is False
    assert "Invalid" in j["error_message"]


def test_validate_invite_valid_unlimited(client):
    # Create unlimited invite code
    code = f"T{int(time.time())%100000}A"
    with SessionLocal() as db:
        inv = InviteCode(code=code, is_used=False, is_active=True, expires_at=None, max_uses=None, used_count=0)
        db.add(inv)
        db.commit()

    r = client.post("/api/invite/validate", json={"code": code})
    assert r.status_code == 200
    j = r.json()
    assert j["is_valid"] is True
    assert j["code"] == code
    assert j["remaining_uses"] is None


def test_validate_invite_expired(client):
    code = f"E{int(time.time())%100000}X"
    with SessionLocal() as db:
        inv = InviteCode(code=code, is_used=False, is_active=True, expires_at=datetime.utcnow() - timedelta(days=1), max_uses=5, used_count=0)
        db.add(inv)
        db.commit()

    r = client.post("/api/invite/validate", json={"code": code})
    assert r.status_code == 200
    j = r.json()
    assert j["is_valid"] is False
    assert "expired" in j["error_message"].lower()


def test_validate_invite_deactivated(client):
    code = f"D{int(time.time())%100000}C"
    with SessionLocal() as db:
        inv = InviteCode(code=code, is_used=False, is_active=False, expires_at=None, max_uses=None, used_count=0)
        db.add(inv)
        db.commit()

    r = client.post("/api/invite/validate", json={"code": code})
    assert r.status_code == 200
    j = r.json()
    assert j["is_valid"] is False
    assert "deactivated" in j["error_message"].lower()


def test_validate_invite_max_uses_reached(client):
    code = f"M{int(time.time())%100000}U"
    with SessionLocal() as db:
        inv = InviteCode(code=code, is_used=False, is_active=True, expires_at=None, max_uses=2, used_count=2)
        db.add(inv)
        db.commit()

    r = client.post("/api/invite/validate", json={"code": code})
    assert r.status_code == 200
    j = r.json()
    assert j["is_valid"] is False
    assert "maximum" in j["error_message"].lower()
