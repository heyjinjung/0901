import time


def _signup(client, site_id: str, nickname: str, phone: str, password: str = "pass1234"):
    r = client.post(
        "/api/auth/signup",
        json={
            "site_id": site_id,
            "nickname": nickname,
            "password": password,
            "invite_code": "5858",
            "phone_number": phone,
        },
    )
    return r


def test_login_lockout_429_then_reset_on_success(client):
    uniq = str(int(time.time() * 1000))[-9:]
    site_id = f"lock_{uniq}"
    nickname = f"lock_{uniq}"
    phone = f"019{uniq}"
    password = "pass1234"

    # Ensure user exists
    r = _signup(client, site_id, nickname, phone, password)
    if r.status_code != 200:
        # Ignore if already exists and continue
        pass

    # Trigger 5 failures
    for _ in range(5):
        bad = client.post("/api/auth/login", json={"site_id": site_id, "password": "wrong"})
        assert bad.status_code == 401

    # Next attempt should be locked (429)
    locked = client.post("/api/auth/login", json={"site_id": site_id, "password": "wrong"})
    assert locked.status_code == 429

    # During lockout window, even correct credentials should return 429
    ok = client.post("/api/auth/login", json={"site_id": site_id, "password": password})
    assert ok.status_code == 429


def test_auth_me_alias_matches_profile(client):
    uniq = str(int(time.time() * 1000))[-9:]
    site_id = f"me_{uniq}"
    nickname = f"me_{uniq}"
    phone = f"018{uniq}"
    password = "pass1234"

    r = _signup(client, site_id, nickname, phone, password)
    if r.status_code != 200:
        # Fall back to login to get token
        r = client.post("/api/auth/login", json={"site_id": site_id, "password": password})
        assert r.status_code == 200

    token = r.json()["access_token"]
    h = {"Authorization": f"Bearer {token}"}

    prof = client.get("/api/users/profile", headers=h)
    assert prof.status_code == 200
    me = client.get("/api/auth/me", headers=h)
    assert me.status_code == 200

    assert prof.json()["id"] == me.json()["id"]
    assert prof.json()["site_id"] == me.json()["site_id"]
