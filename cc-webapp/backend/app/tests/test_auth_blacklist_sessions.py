import time


def _signup(client, site_id: str, nickname: str, password: str = "pass1234"):
    suffix = str(int(time.time() * 1000))[-7:]
    phone = f"010{suffix}0"
    return client.post(
        "/api/auth/signup",
        json={
            "site_id": site_id,
            "nickname": nickname,
            "password": password,
            "invite_code": "5858",
            "phone_number": phone,
        },
    )


def _login(client, site_id: str, password: str = "pass1234"):
    return client.post("/api/auth/login", json={"site_id": site_id, "password": password})


def test_logout_blacklists_token(client):
    uniq = str(int(time.time()))[-6:]
    r = _signup(client, f"lo_{uniq}", f"lo_{uniq}")
    assert r.status_code == 200
    token = r.json()["access_token"]
    h = {"Authorization": f"Bearer {token}"}
    # Verify works before logout
    prof = client.get("/api/users/profile", headers=h)
    assert prof.status_code == 200
    # Logout -> blacklist current token
    out = client.post("/api/auth/logout", headers=h)
    assert out.status_code in (200, 204)
    # Using old token should now fail
    prof2 = client.get("/api/users/profile", headers=h)
    assert prof2.status_code == 401


def test_single_session_enforced_old_token_invalid(client):
    uniq = str(int(time.time()))[-6:]
    site = f"con_{uniq}"
    r = _signup(client, site, site)
    assert r.status_code == 200
    t1 = r.json()["access_token"]
    h1 = {"Authorization": f"Bearer {t1}"}
    # First token works
    assert client.get("/api/users/profile", headers=h1).status_code == 200
    # Login again -> should create new session and deactivate old
    r2 = _login(client, site)
    assert r2.status_code == 200
    t2 = r2.json()["access_token"]
    h2 = {"Authorization": f"Bearer {t2}"}
    # Old token should now fail
    assert client.get("/api/users/profile", headers=h1).status_code == 401
    # New token should work
    assert client.get("/api/users/profile", headers=h2).status_code == 200


def test_logout_all_revokes_sessions(client):
    uniq = str(int(time.time()))[-6:]
    site = f"loa_{uniq}"
    r = _signup(client, site, site)
    assert r.status_code == 200
    t = r.json()["access_token"]
    h = {"Authorization": f"Bearer {t}"}
    # Verify works
    assert client.get("/api/users/profile", headers=h).status_code == 200
    # Logout-all
    out = client.post("/api/auth/logout-all", headers=h)
    assert out.status_code in (200, 204)
    # Old token fails now
    assert client.get("/api/users/profile", headers=h).status_code == 401
    # New login works
    r2 = _login(client, site)
    assert r2.status_code == 200
    h2 = {"Authorization": f"Bearer {r2.json()['access_token']}"}
    assert client.get("/api/users/profile", headers=h2).status_code == 200
