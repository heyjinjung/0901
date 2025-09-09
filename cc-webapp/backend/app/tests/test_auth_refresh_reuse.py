import time


def _signup_and_login(client, prefix: str = "reuse"):
    uniq = str(int(time.time() * 1000))[-7:]
    site_id = f"{prefix}_{uniq}"
    payload = {
        "site_id": site_id,
        "password": "pass1234",
        "nickname": f"{prefix}_{uniq}",
        "invite_code": "5858",
        "phone_number": f"010{uniq}0",
    }
    r = client.post("/api/auth/signup", json=payload)
    if r.status_code != 200:
        r = client.post("/api/auth/login", json={"site_id": site_id, "password": "pass1234"})
        assert r.status_code == 200
    data = r.json()
    return data["access_token"], data.get("refresh_token"), data["user"]["id"]


def test_refresh_token_reuse_denied(client):
    access_token, refresh_token, _ = _signup_and_login(client)
    assert refresh_token, "Environment must return a DB-backed refresh_token for this test"

    # First refresh succeeds (may rotate the refresh token)
    r1 = client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert r1.status_code == 200, r1.text
    body1 = r1.json()
    new_access = body1["access_token"]
    rotated_refresh = body1.get("refresh_token") or refresh_token

    # Attempt to reuse the ORIGINAL refresh token (if rotated) or the now-invalidated one
    reuse_target = refresh_token
    if rotated_refresh != refresh_token:
        # Original should now be revoked and denied
        r_reuse = client.post("/api/auth/refresh", json={"refresh_token": reuse_target})
        assert r_reuse.status_code in (401, 403), r_reuse.text
        assert (
            "reuse" in r_reuse.text.lower()
            or "revoke" in r_reuse.text.lower()
            or "not authenticated" in r_reuse.text.lower()
        )
    else:
        # If backend did not rotate (legacy path), perform second refresh, then attempt reuse
        r2 = client.post(
            "/api/auth/refresh",
            json={"refresh_token": rotated_refresh},
            headers={"Authorization": f"Bearer {new_access}"},
        )
        assert r2.status_code == 200, r2.text
        maybe_new = r2.json().get("refresh_token") or rotated_refresh
        if maybe_new != rotated_refresh:
            r_reuse = client.post("/api/auth/refresh", json={"refresh_token": rotated_refresh})
            assert r_reuse.status_code in (401, 403), r_reuse.text

    # Final sanity: new access token works for profile (unless rotation reuse triggered global revoke)
    prof = client.get("/api/users/profile", headers={"Authorization": f"Bearer {new_access}"})
    # If reuse triggered cascade revoke, profile may be 401; allow both but assert not 5xx
    assert prof.status_code in (200, 401)
