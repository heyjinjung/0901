from fastapi.testclient import TestClient
from app.main import app


def _make_client() -> TestClient:
    return TestClient(app)


def test_admin_catalog_routes_exist():
    c = _make_client()
    r = c.get("/api/admin/shop/items")
    assert r.status_code in (200, 401, 403)


def test_gacha_config_update_route_exists():
    c = _make_client()
    r = c.post("/api/admin/gacha/config", json={"rarity_table": [["Epic", 0.03]]})
    assert r.status_code in (200, 401, 403)


def test_campaign_routes_exist():
    c = _make_client()
    r = c.post("/api/admin/campaigns", json={"title": "t", "message": "m"})
    assert r.status_code in (200, 401, 403)