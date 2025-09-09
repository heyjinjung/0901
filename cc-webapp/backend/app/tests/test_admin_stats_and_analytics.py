import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from app.database import Base, engine, SessionLocal
from app.models import User, UserAction
from app.services.auth_service import AuthService


def _seed_admin(db):
    # Create an admin user with known credentials
    admin = User(
        site_id="admin1",
        nickname="admin",
        phone_number="01000000000",
        password_hash=AuthService.get_password_hash("pass1234"),
        invite_code="5858",
        is_admin=True,
        is_active=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def _auth_headers(client: TestClient, site_id: str, password: str):
    resp = client.post("/api/auth/admin/login", json={"site_id": site_id, "password": password})
    assert resp.status_code == 200, resp.text
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_admin_stats_and_games_stats(client: TestClient):
    # Prepare data
    db = SessionLocal()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    admin = _seed_admin(db)
    # Seed some user actions
    u = User(
        site_id="user1",
        nickname="user1",
        phone_number="01000000001",
        password_hash=AuthService.get_password_hash("pw"),
        invite_code="5858",
        is_admin=False,
        is_active=True,
        cyber_token_balance=100,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    for i in range(3):
        db.add(UserAction(user_id=u.id, action_type="slot_play", action_data="{}"))
    for i in range(2):
        db.add(UserAction(user_id=u.id, action_type="rps_play", action_data="{}"))
    db.commit()
    db.close()

    headers = _auth_headers(client, "admin1", "pass1234")

    # /api/admin/stats
    r = client.get("/api/admin/stats", headers=headers)
    assert r.status_code == 200, r.text
    data = r.json()
    assert "total_users" in data and data["total_users"] >= 2
    assert "total_games_played" in data and data["total_games_played"] == 5

    # /api/analytics/games/stats
    r2 = client.get("/api/analytics/games/stats", headers=headers)
    assert r2.status_code == 200, r2.text
    g = r2.json()
    assert g["total_games"] >= 1
    names = {x["game_type"] for x in g["games"]}
    assert {"slot_play", "rps_play"}.issubset(names)
