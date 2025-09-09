import threading
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
    u = _create_user(site_id, f"nick_{site_id}", is_admin=is_admin)
    return u, _make_token(u, is_admin=is_admin)


def test_admin_grant_gold_concurrent_same_key(client: TestClient):
    admin_user, admin_token = _create_user_and_token("admgrantc", is_admin=True)
    target_user, _ = _create_user_and_token("targetgc", is_admin=False)

    idem_key = "concurrent1"
    body = {"amount": 70, "reason": "test", "idempotency_key": idem_key}
    results = []

    def worker():
        r = client.post(f"/api/admin/users/{target_user.id}/gold/grant", json=body, headers=_auth_headers(admin_token))
        results.append(r)

    t1 = threading.Thread(target=worker)
    t2 = threading.Thread(target=worker)
    t1.start(); t2.start(); t1.join(); t2.join()

    codes = sorted([r.status_code for r in results])
    # Expect one success 200 and one either 200(idempotent reuse) or 409 depending on timing
    assert codes[0] in (200, 409) and codes[1] == 200


def test_admin_grant_gold_rate_limit(client: TestClient):
    admin_user, admin_token = _create_user_and_token("admgrantrl", is_admin=True)
    target_user, _ = _create_user_and_token("targetgrl", is_admin=False)

    # Fire more than configured per-minute (assuming default 30, send 35 quickly) with unique keys
    exceeded = False
    for i in range(35):
        body = {"amount": 1, "reason": "rl", "idempotency_key": f"rk{i}"}
        r = client.post(f"/api/admin/users/{target_user.id}/gold/grant", json=body, headers=_auth_headers(admin_token))
        if r.status_code == 429:
            exceeded = True
            break
    assert exceeded, "Expected to hit rate limit"
