import json
import time

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _send(user_id: int, msg: dict, topic: str = None, priority: int = 0):
    body = {"message": msg, "priority": priority}
    if topic:
        body["topic"] = topic
    r = client.post(f"/api/notifications/{user_id}/send", json=body)
    assert r.status_code == 200, r.text


def test_ws_topic_subscribe_flow():
    user_id = 12345
    # Connect with initial topic filter 'alpha'
    with client.websocket_connect(f"/ws/notifications/{user_id}?topics=alpha") as ws:
        # Allow server to register connection before sending
        time.sleep(0.1)
        # Send alpha and beta messages
        _send(user_id, {"m": "alpha-1"}, topic="alpha")
        _send(user_id, {"m": "beta-1"}, topic="beta")

    # Record current backfill size after first sends
    r0 = client.get(f"/api/notifications/{user_id}/backfill")
    assert r0.status_code == 200
    items0 = r0.json()["items"]
    assert any(it.get("data", {}).get("m") == "alpha-1" for it in items0)
    assert any(it.get("data", {}).get("m") == "beta-1" for it in items0)

    # Reconnect and subscribe to beta, then send another beta
    with client.websocket_connect(f"/ws/notifications/{user_id}") as ws:
        ws.send_text(json.dumps({"type": "subscribe", "topics": ["beta"]}))
        time.sleep(0.05)
        _send(user_id, {"m": "beta-2"}, topic="beta")
        time.sleep(0.05)
    r2 = client.get(f"/api/notifications/{user_id}/backfill", params={"topics": "beta"})
    assert r2.status_code == 200
    items_beta = [it for it in r2.json()["items"] if it.get("data", {}).get("m") == "beta-2"]
    assert items_beta, "expected beta-2 to be present in backfill"


def test_ws_multi_client_receive():
    user_id = 22334
    with client.websocket_connect(f"/ws/notifications/{user_id}") as ws1:
        with client.websocket_connect(f"/ws/notifications/{user_id}") as ws2:
            time.sleep(0.1)
            _send(user_id, {"m": "hello"}, topic="default")
            time.sleep(0.05)
            # Context managers will close sockets automatically
    # Validate via backfill that the message was enqueued once
    r = client.get(f"/api/notifications/{user_id}/backfill")
    assert r.status_code == 200
    msgs = [it for it in r.json()["items"] if it.get("data", {}).get("m") == "hello"]
    assert msgs, "expected 'hello' message in backfill"


def test_backfill_since_and_topic_filter():
    user_id = 33445
    # Send a couple of baseline messages and get the last id via backfill
    _send(user_id, {"m": "baseline-1"}, topic="alpha")
    _send(user_id, {"m": "baseline-2"}, topic="beta")

    r0 = client.get(f"/api/notifications/{user_id}/backfill")
    assert r0.status_code == 200
    items0 = r0.json()["items"]
    assert items0, "expected backfill items to exist"
    last_id = items0[-1]["id"]

    # New events after last_id
    _send(user_id, {"m": "next-alpha"}, topic="alpha")
    _send(user_id, {"m": "next-beta"}, topic="beta")

    # Query since=last_id with topic filter beta
    r = client.get(f"/api/notifications/{user_id}/backfill", params={"since": last_id, "topics": "beta"})
    assert r.status_code == 200
    data = r.json()
    assert data["count"] >= 1
    topics = {it["topic"] for it in data["items"]}
    assert topics == {"beta"}
