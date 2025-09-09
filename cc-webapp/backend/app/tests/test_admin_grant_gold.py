import pytest
import uuid
from fastapi.testclient import TestClient
from app.database import SessionLocal
from app.models.auth_models import User
from app.services.auth_service import AuthService


def _auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


def _create_user(site_id: str, nickname: str, is_admin: bool = False) -> User:
    db = SessionLocal()
    try:
        u = User(
            site_id=site_id,
            nickname=nickname,
            phone_number=None,
            password_hash=AuthService.get_password_hash("passw0rd!"),
            invite_code="5858",
            is_admin=is_admin,
        )
        db.add(u)
        db.commit()
        db.refresh(u)
        return u
    finally:
        db.close()


def _make_token(user: User, is_admin: bool = False) -> str:
    return AuthService.create_access_token({"sub": user.site_id, "user_id": user.id, "is_admin": is_admin or user.is_admin})


def _create_user_and_token(site_id: str, is_admin: bool = False):
    # append short uuid to ensure uniqueness across repeated test process startups
    import uuid as _uuid
    unique_site_id = f"{site_id}_{_uuid.uuid4().hex[:6]}"
    u = _create_user(unique_site_id, f"nick_{unique_site_id}", is_admin=is_admin)
    return u, _make_token(u, is_admin=is_admin)


def test_admin_grant_gold_basic_and_idempotent(client: TestClient):
    admin_user, admin_token = _create_user_and_token("admgrant", is_admin=True)
    target_user, _ = _create_user_and_token("targetg", is_admin=False)

    idem_key = f"k1_{uuid.uuid4().hex[:8]}"
    body = {"amount": 150, "reason": "compensation", "idempotency_key": idem_key}
    r1 = client.post(f"/api/admin/users/{target_user.id}/gold/grant", json=body, headers=_auth_headers(admin_token))
    assert r1.status_code == 200, r1.text
    data1 = r1.json()
    assert data1["granted"] == 150
    assert data1["new_gold_balance"] >= 150
    assert data1.get("idempotent_reuse") is False

    # reuse same key
    r2 = client.post(f"/api/admin/users/{target_user.id}/gold/grant", json=body, headers=_auth_headers(admin_token))
    assert r2.status_code == 200
    data2 = r2.json()
    assert data2["idempotent_reuse"] is True
    assert data2["receipt_code"] == data1["receipt_code"]
    assert data2["new_gold_balance"] == data1["new_gold_balance"]

    # new key with different amount
    body2 = {"amount": 50, "reason": "bonus", "idempotency_key": "k2"}
    r3 = client.post(f"/api/admin/users/{target_user.id}/gold/grant", json=body2, headers=_auth_headers(admin_token))
    assert r3.status_code == 200
    data3 = r3.json()
    assert data3["granted"] == 50
    assert data3["new_gold_balance"] >= data1["new_gold_balance"] + 50


def test_admin_grant_gold_negative_amount_rejected(client: TestClient):
    admin_user, admin_token = _create_user_and_token("admgrant2", is_admin=True)
    target_user, _ = _create_user_and_token("targetg2", is_admin=False)
    body = {"amount": -5, "reason": "bad", "idempotency_key": "neg1"}
    r = client.post(f"/api/admin/users/{target_user.id}/gold/grant", json=body, headers=_auth_headers(admin_token))
    assert r.status_code in (400, 422)
