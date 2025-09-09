from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app import models
import json

client = TestClient(app)


def test_create_action_persists_and_sanitizes():
    body = {
        "user_id": 1,
        "action_type": "LOGIN",
        "context": {"email": "user@example.com", "ip": "127.0.0.1"}
    }
    r = client.post("/api/actions", json=body)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["user_id"] == 1
    assert data["action_type"] == "LOGIN"
    # action_data JSON contains sanitized email
    ad = json.loads(data.get("action_data") or "{}")
    assert ad.get("context", {}).get("email") == "***"
    assert ad.get("context", {}).get("ip") == "127.0.0.1"


def test_create_actions_batch_inserts_multiple():
    batch = {
        "actions": [
            {"user_id": 2, "action_type": "SLOT_SPIN", "context": {"bet": 50}},
            {"user_id": 2, "action_type": "GACHA_PULL", "context": {"count": 10}},
        ]
    }
    r = client.post("/api/actions/batch", json=batch)
    assert r.status_code == 200, r.text
    out = r.json()
    assert out.get("inserted") == 2


def test_action_validation_errors():
    # missing action_type
    r = client.post("/api/actions", json={"user_id": 3})
    assert r.status_code == 422
