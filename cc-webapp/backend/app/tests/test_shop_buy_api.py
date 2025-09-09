import time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def _signup(client: TestClient, prefix: str = "buyer"):
    payload = {
        "invite_code": "5858",
        "nickname": f"{prefix}_{int(time.time())}",
        "site_id": f"{prefix}_{int(time.time())}",
        "phone_number": "01012345678",
        "password": "pass1234",
    }
    r = client.post("/api/auth/signup", json=payload)
    assert r.status_code == 200
    site_id = payload["site_id"]
    r = client.post("/api/auth/login", json={"site_id": site_id, "password": "pass1234"})
    assert r.status_code == 200
    data = r.json()
    return data["access_token"], data["user"]["id"]


def test_buy_gold_and_item_flow():
    token, user_id = _signup(client)
    headers = {"Authorization": f"Bearer {token}"}

    # 1) Buy gold (top-up)
    r = client.post(
        "/api/shop/buy",
        headers=headers,
        json={
            "user_id": user_id,
            "product_id": "gold_pack_small",
            "amount": 500,
            "quantity": 1,
            "kind": "gold",
            "payment_method": "card",
        },
    )
    assert r.status_code == 200, r.text
    res = r.json()
    assert res["success"] is True
    assert res.get("granted_gold") == 500

    # 2) Try buying item with insufficient tokens (expect failure if price too high)
    r = client.post(
        "/api/shop/buy",
        headers=headers,
        json={
            "user_id": user_id,
            "product_id": "premium_box",
            "amount": 10_000_000,
            "quantity": 1,
            "kind": "item",
            "item_name": "프리미엄 박스",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is False

    # 3) Buy a reasonably priced item (should succeed)
    r = client.post(
        "/api/shop/buy",
        headers=headers,
        json={
            "user_id": user_id,
            "product_id": "daily_box",
            "amount": 200,
            "quantity": 1,
            "kind": "item",
            "item_name": "데일리 박스",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is True
    assert data["item_id"] == "daily_box"
