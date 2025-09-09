import time
from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)


def _signup(client: TestClient, site_id: str):
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
    assert r.status_code == 200
    return r.json()


def _auth_header(token: str):
    return {"Authorization": f"Bearer {token}"}


def test_profile_privacy_self_vs_other():
    u1 = _signup(client, f"p1_{int(time.time())}")
    u2 = _signup(client, f"p2_{int(time.time())}")

    h1 = _auth_header(u1["access_token"])  # user1
    h2 = _auth_header(u2["access_token"])  # user2

    # self -> full details
    r_self = client.get(f"/api/users/{u1['user']['id']}", headers=h1)
    assert r_self.status_code == 200
    body_self = r_self.json()
    assert body_self["id"] == u1["user"]["id"]
    assert body_self["phone_number"] != "hidden"

    # other -> masked
    r_other = client.get(f"/api/users/{u1['user']['id']}", headers=h2)
    assert r_other.status_code == 200
    body_other = r_other.json()
    assert body_other["id"] == u1["user"]["id"]
    assert body_other["phone_number"] == "hidden"
    assert body_other["is_admin"] is False


def test_slot_bulk_spins_and_logging_smoke():
    u = _signup(client, f"slot_{int(time.time())}")
    h = _auth_header(u["access_token"]) 

    # grant some tokens if needed via /api/users/tokens/add (self)
    client.post("/api/users/tokens/add", headers=h, params={"amount": 10000})

    balances = []
    for _ in range(20):
        r = client.post("/api/games/slot/spin", headers=h, json={"bet_amount": 50})
        assert r.status_code == 200
        balances.append(r.json()["balance"])

    assert len(balances) == 20


def test_gacha_bulk_pulls_and_costs_smoke():
    u = _signup(client, f"gacha_{int(time.time())}")
    h = _auth_header(u["access_token"]) 

    client.post("/api/users/tokens/add", headers=h, params={"amount": 20000})

    # 5 pulls cost 1500
    r = client.post("/api/games/gacha/pull", headers=h, json={"pull_count": 5})
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["pull_count"] == 5
    assert body["balance"] >= 0
