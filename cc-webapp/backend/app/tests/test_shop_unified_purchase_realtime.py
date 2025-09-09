import time, uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def _signup(prefix: str = "rt"):
    payload = {
        "invite_code": "5858",
        "nickname": f"{prefix}_{int(time.time())}",
        "site_id": f"{prefix}_{int(time.time())}",
        "phone_number": f"010{int(time.time())%100000000:08d}",
        "password": "pass1234",
    }
    r = client.post("/api/auth/signup", json=payload)
    assert r.status_code == 200, r.text
    r = client.post("/api/auth/login", json={"site_id": payload["site_id"], "password": "pass1234"})
    assert r.status_code == 200, r.text
    data = r.json()
    return data["access_token"], data["user"]["id"]

def test_unified_purchase_broadcast_monkeypatch(monkeypatch):
    token, user_id = _signup("rtp")
    headers = {"Authorization": f"Bearer {token}"}

    called = {"profile": [], "purchase": []}

    async def fake_profile(uid, changes):
        called["profile"].append((uid, changes))

    async def fake_purchase(uid, **payload):
        called["purchase"].append((uid, payload))

    # monkeypatch 대상 import 경로: routers.shop 내에서 .realtime import 사용
    from app.routers import shop as shop_router
    monkeypatch.setattr("app.routers.realtime.broadcast_profile_update", fake_profile)
    monkeypatch.setattr("app.routers.realtime.broadcast_purchase_update", fake_purchase)

    # 고립 상품 생성 (conversion)
    from app.database import SessionLocal
    from app import models
    conv_id = f"RTCONV_{uuid.uuid4().hex[:8]}"
    session = SessionLocal()
    try:
        p = models.ShopProduct(product_id=conv_id, name="RT Conv", price=1000, is_active=True, extra={"category":"conversion","gold_out":1000})
        session.add(p)
        session.commit()
    finally:
        session.close()

    idem = uuid.uuid4().hex
    r = client.post("/api/shop/purchase", json={"product_id": conv_id, "idempotency_key": idem}, headers=headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["success"] is True

    # 브로드캐스트 호출 기록 검증
    assert len(called["profile"]) == 1, called
    assert len(called["purchase"]) == 1, called
    prof_uid, prof_changes = called["profile"][0]
    pur_uid, pur_payload = called["purchase"][0]
    assert prof_uid == user_id
    assert pur_uid == user_id
    assert "gold_balance" in prof_changes
    assert pur_payload.get("product_id") == conv_id