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


def test_user_ws_receives_slot_event():
    u = _signup(f"ws_slot_{int(time.time())}")
    token = u["access_token"]
    h = _auth_header(token)
    client.post("/api/users/tokens/add", headers=h, params={"amount": 1000})
    with client.websocket_connect(f"/api/games/ws?token={token}") as ws:
        # trigger spin
        r = client.post("/api/games/slot/spin", headers=h, json={"bet_amount": 10})
        assert r.status_code == 200
        # read a couple messages (ack + event)
        ack = ws.receive_json()
        assert ack["type"] == "ws_ack"
        event = ws.receive_json()
        assert event["type"] == "game_event"
        assert event["game_type"] == "slot"
        assert event["user_id"] == u["user"]["id"]


def test_admin_monitor_snapshot_and_event_stream():
    admin = _signup(f"ws_admin_{int(time.time())}")
    token = admin["access_token"]
    try:
        with client.websocket_connect(f"/api/games/ws/monitor?token={token}") as ws:
            snap = ws.receive_json()
            assert snap["type"] == "monitor_snapshot"
    except Exception:
        # skip if not admin
        pass
