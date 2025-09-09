import pytest
from datetime import datetime
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_db
from app.models.auth_models import User
from app.models.game_models import UserReward

# Assumes dependency overrides / fixtures similar to existing tests environment.
# Minimal test focusing on idempotent behavior within same day.

client = TestClient(app)


def auth_headers(db):
    # Reuse first user or create one
    user = db.query(User).first()
    if not user:
        user = User(site_id="viptester", nickname="viptester", phone_number="01000000000", invite_code="5858", password_hash="x")
        db.add(user)
        db.commit()
        db.refresh(user)
    # Issue token manually (simplified) - use /api/auth/login if full flow required
    token = f"fake-{user.id}"  # If JWT required, adjust to use AuthService.create_access_token
    # Some existing tests may patch token verification; for now rely on potential bypass or adjust later.
    return {"Authorization": f"Bearer {token}"}, user


def test_vip_daily_claim_idempotent(monkeypatch):
    db = next(get_db())
    headers, user = auth_headers(db)

    # Monkeypatch token verification to return user directly if needed
    from app.services import auth_service
    def fake_verify_token(token: str, db=None):
        class Obj: pass
        o = Obj()
        o.user_id = user.id
        o.site_id = user.site_id
        return o
    if hasattr(auth_service.AuthService, 'verify_token'):
        monkeypatch.setattr(auth_service.AuthService, 'verify_token', staticmethod(fake_verify_token))

    # First claim
    r1 = client.post("/api/vip/claim", headers=headers)
    assert r1.status_code == 200, r1.text
    data1 = r1.json()
    assert data1["awarded_points"] == 50
    first_points = data1["new_vip_points"]

    # Duplicate claim same day
    r2 = client.post("/api/vip/claim", headers=headers)
    assert r2.status_code == 200
    data2 = r2.json()
    assert data2["awarded_points"] == 50
    assert data2["new_vip_points"] == first_points  # no double increment
    assert data2["idempotent"] is True

    # Ensure exactly one reward row with today's idempotency key
    today = datetime.utcnow().date().isoformat()
    rewards = db.query(UserReward).filter(UserReward.user_id == user.id, UserReward.idempotency_key == f"vip:{user.id}:{today}").all()
    assert len(rewards) == 1
