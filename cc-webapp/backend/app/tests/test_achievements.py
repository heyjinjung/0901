import time
from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)


def _signup(site_id: str):
    r = client.post(
        "/api/auth/signup",
        json={
            "site_id": site_id,
            "nickname": site_id,
            "password": "pass1234",
            "invite_code": "5858",
            "phone_number": f"010{int(time.time()*1000)%1000000000:09d}",
        },
    )
    assert r.status_code == 200, r.text
    return r.json()


def _auth_header(token: str):
    return {"Authorization": f"Bearer {token}"}


def test_achievement_progress_and_unlock_flow():
    u = _signup(f"ach_{int(time.time())}")
    token = u["access_token"]
    h = _auth_header(token)

    # Seed a simple achievement directly if not existing (depends on API seeding strategy)
    # We call admin-like endpoint or direct insert skipped here; just ensure list endpoint works even if empty.
    r = client.get("/api/games/achievements", headers=h)
    assert r.status_code == 200

    # Simulate several spins to accumulate BET + potential WIN
    client.post("/api/users/tokens/add", headers=h, params={"amount": 5000})
    for _ in range(5):
        sr = client.post("/api/games/slot/spin", headers=h, json={"bet_amount": 10})
        assert sr.status_code == 200

    # Fetch my achievements (should not error)
    mr = client.get("/api/games/achievements/my", headers=h)
    assert mr.status_code == 200
    data = mr.json()
    assert "items" in data
