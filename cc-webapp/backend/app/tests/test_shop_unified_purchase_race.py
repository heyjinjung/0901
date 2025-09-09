import concurrent.futures, uuid, time
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def _signup(prefix: str = "race"):
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

def test_unified_purchase_race_idempotency():
    token, user_id = _signup("raceid")
    headers = {"Authorization": f"Bearer {token}"}

    # 고립 conversion 상품 생성
    from app.database import SessionLocal
    from app import models
    conv_id = f"RCONV_{uuid.uuid4().hex[:8]}"
    session = SessionLocal()
    try:
        p = models.ShopProduct(product_id=conv_id, name="Race Conv", price=1000, is_active=True, extra={"category":"conversion","gold_out":1000})
        session.add(p)
        session.commit()
    finally:
        session.close()

    idem = uuid.uuid4().hex

    def do_req():
        return client.post("/api/shop/purchase", json={"product_id": conv_id, "idempotency_key": idem}, headers=headers)

    # 병렬 5요청 실행
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        futures = [ex.submit(do_req) for _ in range(5)]
        results = [f.result() for f in futures]

    successes = [r for r in results if r.status_code == 200 and r.json().get('success')]
    # 모두 200이어야 하되, 정확히 하나만 최초(success & idempotent!=True) 나머지는 idempotent True 형태 허용
    assert len(successes) == 5, [r.status_code for r in results]
    first = [r for r in successes if not r.json().get('idempotent')]
    assert len(first) == 1, f"expected 1 first tx, got {len(first)}"
    after_balances = {r.json().get('gold_after') for r in successes}
    # gold_after 값은 모두 동일해야 함 (중복 증가 방지)
    assert len(after_balances) == 1, after_balances