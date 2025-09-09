import time
from starlette.testclient import TestClient
from app.main import app


def _signup_and_login(client: TestClient, site_id: str, nickname: str, password: str = "pass1234"):
    r = client.post(
        "/api/auth/signup",
        json={
            "site_id": site_id,
            "nickname": nickname,
            "password": password,
            "invite_code": "5858",
            "phone_number": f"012{int(time.time()*1000)%1000000000}",
        },
    )
    if r.status_code != 200:
        r = client.post("/api/auth/login", json={"site_id": site_id, "password": password})
        assert r.status_code == 200
    body = r.json()
    return body["access_token"], body.get("user", {}).get("id")


def test_refresh_creates_active_session_and_allows_profile_access():
    client = TestClient(app)

    uniq = str(int(time.time()))[-6:]
    access_token, user_id = _signup_and_login(client, f"rsess_{uniq}", f"rsess_{uniq}")

    # Call refresh using Authorization header
    r = client.post(
        "/api/auth/refresh",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert r.status_code == 200
    new_access = r.json()["access_token"]
    assert new_access and new_access != access_token

    # New token must work on protected endpoints (session recorded by refresh)
    h = {"Authorization": f"Bearer {new_access}"}
    prof = client.get("/api/users/profile", headers=h)
    assert prof.status_code == 200

    me = client.get("/api/auth/me", headers=h)
    assert me.status_code == 200
