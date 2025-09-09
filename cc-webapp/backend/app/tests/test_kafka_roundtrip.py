import os
import time
import uuid
import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)
BROKER = os.getenv("KAFKA_BOOTSTRAP_SERVERS") or os.getenv("KAFKA_BROKER")
ENABLED = os.getenv("KAFKA_ENABLED", "0") == "1"


@pytest.mark.skipif(not (BROKER and ENABLED), reason="kafka disabled")
def test_kafka_roundtrip_via_peek():
    """
    Deterministic roundtrip using one-shot debug/peek reader from beginning.
    This avoids dependence on the in-process buffer and consumer timing.
    """
    topic = os.getenv("KAFKA_TEST_TOPIC", "cc_test")
    marker = str(uuid.uuid4())
    payload = {"marker": marker, "src": "roundtrip_peek"}

    # Optional: wait briefly for app startup
    time.sleep(0.25)

    # Produce
    r = client.post("/api/kafka/produce", json={"topic": topic, "payload": payload})
    assert r.status_code in (200, 502)

    # Poll debug/peek for up to ~30s
    seen = False
    for _ in range(60):
        time.sleep(0.5)
        resp = client.get(f"/api/kafka/debug/peek?topic={topic}&max_messages=200&from_beginning=1&timeout_ms=500")
        if resp.status_code != 200:
            # Broker temporarily unavailable or disabled
            continue
        items = resp.json().get("items", [])
        if any((i.get("value") or {}).get("marker") == marker for i in items):
            seen = True
            break
    assert seen, "produced marker not observed via peek"
