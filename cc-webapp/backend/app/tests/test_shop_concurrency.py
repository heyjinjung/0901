import threading
import time
import uuid
from fastapi.testclient import TestClient
import pytest


def _auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


def _signup_login(client: TestClient, prefix: str = "user") -> str:
    site = f"{prefix}-{uuid.uuid4().hex[:10]}"
    r = client.post("/api/auth/signup", json={
        "site_id": site,
        "nickname": site,
        "password": "passw0rd!",
        "invite_code": "5858",
        "phone_number": "010" + str(int(time.time()*1000))[-9:],
    })
    assert r.status_code in (200, 201), r.text
    lr = client.post("/api/auth/login", json={"site_id": site, "password": "passw0rd!"})
    assert lr.status_code == 200, lr.text
    return lr.json()["access_token"]


@pytest.mark.timeout(10)
def test_unified_purchase_idempotent_race(client: TestClient):
    """동일 idempotency_key 10개 동시 호출 → 1 성공, 나머지 idempotent reuse 또는 409(IN_PROGRESS) 허용.

    재시도 없이 즉시 결과를 수집하여 레이스 창을 의도적으로 노출; IN_PROGRESS 비율이 높다면 추후 백오프 재시도 전략 필요.
    """
    token = _signup_login(client, "idem-race")
    h = _auth_headers(token)

    # 테스트용 product 생성 (admin 권한 우회: conftest override)
    pid = "UPR-" + uuid.uuid4().hex[:6]
    cr = client.post("/api/admin/products", json={
        "product_id": pid,
        "name": "RaceItem",
        "price": 10,
        "extra": {"category": "item"},
    }, headers=h)
    assert cr.status_code in (200, 400), cr.text  # 400 = 이미 존재 가능 (재시도 안전)

    idem_key = uuid.uuid4().hex
    results = []

    def _worker():
        r = client.post("/api/shop/purchase", json={"product_id": pid, "idempotency_key": idem_key}, headers=h)
        results.append((r.status_code, r.json() if r.headers.get("content-type", "").startswith("application/json") else {}))

    threads = [threading.Thread(target=_worker) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    success = [r for r in results if r[0] == 200 and r[1].get("success")]
    in_progress = [r for r in results if r[0] == 409]
    # 멱등 재사용 케이스: status 200 + idempotent True (성공 이후 재구성) or 400? 없음 (400은 실패)
    idempotent_reuse = [r for r in results if r[0] == 200 and r[1].get("idempotent")]

    assert len(success) >= 1, f"no success: {results}"
    # 총 10개 중 나머지는 재사용 또는 IN_PROGRESS 허용
    assert len(success) + len(in_progress) + len(idempotent_reuse) == len(results)
    # 최소 한 건은 idempotent 재사용 또는 IN_PROGRESS 이어야 의미 있는 레이스
    assert (len(idempotent_reuse) + len(in_progress)) >= 1, f"race not observed: {results}"


@pytest.mark.timeout(10)
def test_limited_package_atomic_stock(client: TestClient):
    """stock_remaining=1 패키지에 대해 5명 동시 구매 → 1 success, 나머지 Out of stock."""
    # 관리자 생성
    admin_token = _signup_login(client, "stock-admin")
    ah = _auth_headers(admin_token)
    pkg = "STOCK1-" + uuid.uuid4().hex[:6]
    up = client.post("/api/admin/limited-packages/upsert", json={
        "package_id": pkg,
        "name": "SingleStock",
        "description": "only one",
        "price": 10,
        "stock_total": 1,
        "stock_remaining": 1,
        "per_user_limit": 1,
        "is_active": True,
        "contents": {"bonus_tokens": 1},
    }, headers=ah)
    if up.status_code == 403:
        pytest.skip("Admin guard enforced")
    assert up.status_code == 200, up.text

    # 5 사용자 생성
    user_tokens = [_signup_login(client, f"stock-u{i}") for i in range(5)]
    headers_list = [_auth_headers(t) for t in user_tokens]
    for h in headers_list:
        client.post("/api/users/tokens/add", headers=h, params={"amount": 100})

    results = []
    def _buy(h):
        r = client.post("/api/shop/buy-limited", json={"package_id": pkg}, headers=h)
        results.append(r.json() if r.headers.get("content-type", "").startswith("application/json") else {"raw": r.text})

    threads = [threading.Thread(target=_buy, args=(h,)) for h in headers_list]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    success = [r for r in results if r.get("success") is True]
    failures = [r for r in results if r.get("success") is False]
    assert len(success) == 1, results
    # 실패 메시지 중 최소 하나는 out of stock
    assert any("stock" in (r.get("message", "").lower()) for r in failures), failures


@pytest.mark.timeout(10)
def test_promo_code_max_uses_atomic(client: TestClient):
    """max_uses=3 프로모 코드 동시 5회 적용 → 3 success 2 exhausted."""
    admin_token = _signup_login(client, "promo-admin")
    ah = _auth_headers(admin_token)
    # 패키지 생성 (충분한 stock)
    pkg = "PROMO-" + uuid.uuid4().hex[:6]
    up = client.post("/api/admin/limited-packages/upsert", json={
        "package_id": pkg,
        "name": "PromoPkg",
        "description": "promo test",
        "price": 30,
        "stock_total": 10,
        "stock_remaining": 10,
        "per_user_limit": 5,
        "is_active": True,
        "contents": {"bonus_tokens": 0},
    }, headers=ah)
    if up.status_code == 403:
        pytest.skip("Admin guard enforced")
    assert up.status_code == 200, up.text

    # 프로모 코드 직접 DB 경로 대신 admin 없으면 skip (단순화: promo 테이블 존재 가정) → 없을 경우 테스트 스킵
    promo_code = "PCODE" + uuid.uuid4().hex[:4]
    # promo 생성 엔드포인트가 없을 수도 있어 Raw SQL fallback (try/except)
    created = False
    try:
        r = client.post("/api/admin/promo-codes/create", json={
            "code": promo_code,
            "discount_type": "flat",
            "value": 10,
            "package_id": pkg,
            "max_uses": 3,
            "is_active": True,
        }, headers=ah)
        if r.status_code == 200:
            created = True
    except Exception:
        pass
    if not created:
        pytest.skip("Promo create endpoint missing; skip promo concurrency test")

    # 사용자 5명 생성
    user_tokens = [_signup_login(client, f"promo-u{i}") for i in range(5)]
    headers_list = [_auth_headers(t) for t in user_tokens]
    for h in headers_list:
        client.post("/api/users/tokens/add", headers=h, params={"amount": 500})

    results = []
    def _buy(h):
        r = client.post("/api/shop/buy-limited", json={"package_id": pkg, "promo_code": promo_code}, headers=h)
        results.append(r.json() if r.headers.get("content-type", "").startswith("application/json") else {"raw": r.text})

    threads = [threading.Thread(target=_buy, args=(h,)) for h in headers_list]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    success = [r for r in results if r.get("success") is True]
    failures = [r for r in results if r.get("success") is False]
    # promo exhausted 메시지 존재 (Invalid or exhausted promo code)
    assert len(success) == 3, results
    assert any("promo" in (r.get("message", "").lower()) for r in failures), failures
