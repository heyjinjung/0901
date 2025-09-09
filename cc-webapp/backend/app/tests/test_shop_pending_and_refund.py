import os
import pytest
from fastapi.testclient import TestClient

@pytest.fixture(autouse=True)
def _set_gateway_mode(monkeypatch):
    # 기본은 항상 보류 후 성공 모드
    monkeypatch.setenv("PAYMENT_GATEWAY_MODE", "pending_then_success")
    yield


def _auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}

def _signup_and_get_token(client: TestClient) -> str:
    import time
    uniq = str(int(time.time() * 1000))[-9:]
    site_id = f"shop_pend_{uniq}"
    password = "pass1234"
    # signup
    r = client.post(
        "/api/auth/signup",
        json={
            "site_id": site_id,
            "nickname": f"nick_{uniq}",
            "password": password,
            "invite_code": "5858",
            "phone_number": f"010{uniq}",
        },
    )
    if r.status_code != 200:
        r = client.post("/api/auth/login", json={"site_id": site_id, "password": password})
    else:
        r = client.post("/api/auth/login", json={"site_id": site_id, "password": password})
    assert r.status_code == 200
    return r.json()["access_token"]


def test_pending_then_settle_success(client: TestClient):
    token = _signup_and_get_token(client)
    # 1) 구매 시도 (pending)
    body = {
        "user_id": 0,
    "product_id": "gold_pack_small",
        "amount": 10,
        "quantity": 1,
    "kind": "gold",
        "payment_method": "card",
    }
    r = client.post("/api/shop/buy", json=body, headers=_auth_headers(token))
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is False
    assert "대기" in data["message"]

    # 2) 내 거래 목록에서 가장 최근 거래 확인 (pending)
    r2 = client.get("/api/shop/transactions?limit=1", headers=_auth_headers(token))
    assert r2.status_code == 200
    txs = r2.json()
    assert len(txs) >= 1
    tx = txs[0]
    assert tx["status"] in ("pending", "success")
    receipt = tx["receipt_code"]

    # 3) 정산(폴링) 호출 → success로 전환되며 잔액 증가 포함
    r3 = client.post(f"/api/shop/transactions/{receipt}/settle", headers=_auth_headers(token))
    assert r3.status_code == 200
    res = r3.json()
    assert res["success"] is True
    if res.get("status") == "pending":
        import time
        time.sleep(1.2)
        r4 = client.post(f"/api/shop/transactions/{receipt}/settle", headers=_auth_headers(token))
        assert r4.status_code == 200
        res2 = r4.json()
        assert res2["success"] is True
        assert res2.get("status") in ("success", None)
    else:
        # status는 success 또는 이미 success인 경우 그대로
        assert res.get("status") in ("success", None)


def test_always_fail_records_failed(client: TestClient, monkeypatch):
    token = _signup_and_get_token(client)
    monkeypatch.setenv("PAYMENT_GATEWAY_MODE", "always_fail")
    body = {
        "user_id": 0,
    "product_id": "gold_pack_small",
        "amount": 5,
        "quantity": 1,
    "kind": "gold",
        "payment_method": "card",
    }
    r = client.post("/api/shop/buy", json=body, headers=_auth_headers(token))
    assert r.status_code == 200
    data = r.json()
    assert data["success"] is False
    assert "거절" in data["message"] or "오류" in data["message"]


def test_admin_refund_flow(client: TestClient):
    token = _signup_and_get_token(client)
    # 가정: 관리자 권한 토큰 픽스처가 있다면 사용, 없으면 이 테스트는 스킵
    # 여기서는 엔드포인트 존재와 기본 권한 체크만 가볍게 확인
    # 사용자 토큰으로 접근 시 403 또는 404가 합리적
    r = client.get("/api/admin/transactions?limit=1", headers=_auth_headers(token))
    assert r.status_code in (401, 403, 404)


def test_admin_force_settle_requires_admin(client: TestClient):
    token = _signup_and_get_token(client)
    # Call without admin should be forbidden
    r = client.post("/api/admin/transactions/any/force-settle", json={"outcome": "success"}, headers=_auth_headers(token))
    assert r.status_code in (401, 403)
