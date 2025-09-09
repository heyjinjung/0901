import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_global_metrics_basic_fields():
    r = client.get("/api/metrics/global")
    assert r.status_code == 200, r.text
    data = r.json()
    for k in ["online_users","spins_last_hour","big_wins_last_hour","generated_at"]:
        assert k in data
    assert isinstance(data["online_users"], int)
    assert isinstance(data["spins_last_hour"], int)
    assert isinstance(data["big_wins_last_hour"], int)
    # generated_at ISO8601 string
    assert isinstance(data["generated_at"], str)


def test_global_metrics_cache_window():
    r1 = client.get("/api/metrics/global")
    assert r1.status_code == 200
    g1 = r1.json()["generated_at"]
    # immediate second call should hit cache -> same timestamp
    r2 = client.get("/api/metrics/global")
    assert r2.status_code == 200
    g2 = r2.json()["generated_at"]
    assert g1 == g2
    # after ttl (~5s) timestamp should refresh
    time.sleep(5.2)
    r3 = client.get("/api/metrics/global")
    assert r3.status_code == 200
    g3 = r3.json()["generated_at"]
    assert g3 != g2
