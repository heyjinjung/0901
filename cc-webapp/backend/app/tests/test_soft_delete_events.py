import pytest
from datetime import datetime, timedelta


@pytest.mark.usefixtures("client")
def test_event_soft_delete_flow(client, auth_token):
    # admin 토큰 확보 (role='admin' 없으면 표준 사용자이므로 is_admin 필요 시 skip)
    token = auth_token(role='admin')
    headers = {"Authorization": f"Bearer {token}"}

    # 1. 이벤트 생성
    payload = {
        "title": "SoftDelete EVT",
        "description": "temp",
        "event_type": "daily",
        "start_date": datetime.utcnow().isoformat(),
        "end_date": (datetime.utcnow() + timedelta(days=1)).isoformat(),
        "rewards": {"gold": 5},
        "requirements": {"plays": 1},
        "priority": 1
    }
    r = client.post("/api/events/admin", json=payload, headers=headers)
    if r.status_code == 403:
        pytest.skip("admin 권한 부재 – is_admin 토큰 필요")
    assert r.status_code == 200, r.text
    ev_id = r.json()["id"] if "id" in r.json() else None
    assert ev_id is not None

    # 2. 목록 기본 (deleted 제외)
    r = client.get("/api/events/admin/list", headers=headers)
    assert r.status_code == 200
    ids = [e["id"] if isinstance(e, dict) and "id" in e else e.get("id") for e in r.json()] if isinstance(r.json(), list) else []

    # 3. 삭제
    dr = client.delete(f"/api/events/admin/{ev_id}", headers=headers)
    assert dr.status_code == 200
    # 4. 기본 목록에서 사라짐 확인
    r2 = client.get("/api/events/admin/list", headers=headers)
    assert r2.status_code == 200
    assert all(e.get("id") != ev_id for e in r2.json())
    # 5. include_deleted 로 확인
    r3 = client.get("/api/events/admin/list?include_deleted=true", headers=headers)
    assert any(e.get("id") == ev_id and e.get("deleted_at") for e in r3.json())
    # 6. 복구
    rr = client.post(f"/api/events/admin/{ev_id}/restore", headers=headers)
    assert rr.status_code == 200
    r4 = client.get("/api/events/admin/list", headers=headers)
    assert any(e.get("id") == ev_id for e in r4.json())


@pytest.mark.usefixtures("client")
def test_shop_product_soft_delete_flow(client, auth_token):
    token = auth_token(role='admin')
    headers = {"Authorization": f"Bearer {token}"}
    # 1. 생성
    p = {"product_id": "softprod-1", "name": "SoftProd", "price": 100}
    r = client.post("/api/shop/admin/products", json=p, headers=headers)
    if r.status_code == 403:
        pytest.skip("admin 권한 부재 – is_admin 토큰 필요")
    assert r.status_code in (200, 400)  # 중복 생성 허용 (400 already exists)
    # 2. 삭제
    d = client.delete("/api/shop/admin/products/softprod-1", headers=headers)
    assert d.status_code == 200
    # 3. 기본 목록 제외 검증
    l = client.get("/api/shop/admin/products", headers=headers)
    assert all(it["product_id"] != "softprod-1" for it in l.json())
    # 4. include_deleted 로 존재
    ld = client.get("/api/shop/admin/products?include_deleted=true", headers=headers)
    assert any(it["product_id"] == "softprod-1" and it["deleted_at"] for it in ld.json())
    # 5. 복구
    rrestore = client.post("/api/shop/admin/products/softprod-1/restore", headers=headers)
    assert rrestore.status_code == 200
    l2 = client.get("/api/shop/admin/products", headers=headers)
    assert any(it["product_id"] == "softprod-1" for it in l2.json())
