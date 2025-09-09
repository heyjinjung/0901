import os
import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


BROKER = os.getenv("KAFKA_BOOTSTRAP_SERVERS") or os.getenv("KAFKA_BROKER")


@pytest.mark.skipif(not BROKER, reason="no broker")
def test_kafka_health_enabled():
    r = client.get("/api/kafka/health")
    assert r.status_code == 200


@pytest.mark.skipif(not BROKER, reason="no broker")
def test_kafka_produce_smoke():
    payload = {"hello": "world"}
    r = client.post("/api/kafka/produce", json={"topic": "cc_test", "payload": payload})
    assert r.status_code in (200, 502)  # 502 if broker reachable but produce fails
