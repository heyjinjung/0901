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
    assert r.status_code == 200
    return r.json()


def _auth(token: str):
    return {"Authorization": f"Bearer {token}"}


def test_slot_spin_feedback_block():
    u = _signup(f"slotfb_{int(time.time())}")
    h = _auth(u["access_token"])
    # 토큰 충전
    client.post("/api/users/tokens/add", headers=h, params={"amount": 500})
    r = client.post("/api/games/slot/spin", headers=h, json={"bet_amount": 10})
    assert r.status_code == 200
    body = r.json()
    # 기본 필드
    assert "feedback" in body
    fb = body["feedback"]
    assert isinstance(fb, dict)
    assert "code" in fb and fb["code"].startswith("slot.")
    assert fb.get("message")
    assert body["success"] is True


def test_gacha_pull_feedback_block():
    u = _signup(f"gachafb_{int(time.time())}")
    h = _auth(u["access_token"])
    # 토큰 충전
    client.post("/api/users/tokens/add", headers=h, params={"amount": 2000})
    r = client.post("/api/games/gacha/pull", headers=h, json={"pull_count": 5})
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert "feedback" in body
    fb = body["feedback"]
    assert fb["code"].startswith("gacha.")
    assert fb.get("message")
    assert "rare_item_count" in body and "ultra_rare_item_count" in body
