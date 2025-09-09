import pytest
import random, uuid
from fastapi.testclient import TestClient
from app.services.limited_package_service import LimitedPackageService
from app.utils.redis import get_redis_manager


def _auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


def signup_and_login(client: TestClient, site_id: str, password: str) -> str:
    client.post(
        "/api/auth/signup",
        json={
            "site_id": site_id,
            "nickname": f"nick_{site_id}",
            "password": password,
            "invite_code": "5858",
            # 고유 전화번호 생성: site_id 기반 9자리
            "phone_number": "010" + str(abs(hash(site_id)) % 1_000_000_000).zfill(9),
        },
    )
    r = client.post("/api/auth/login", json={"site_id": site_id, "password": password})
    assert r.status_code == 200
    return r.json()["access_token"]


def _reset_limited_state():
    LimitedPackageService._catalog.clear()  # noqa: SLF001
    LimitedPackageService._user_purchases.clear()  # noqa: SLF001
    LimitedPackageService._promo_discounts.clear()  # noqa: SLF001
    LimitedPackageService._promo_max_uses.clear()  # noqa: SLF001
    LimitedPackageService._promo_used_count.clear()  # noqa: SLF001
    LimitedPackageService._stock_counts.clear()  # noqa: SLF001
    LimitedPackageService._holds_mem.clear()  # noqa: SLF001
    try:
        rm = get_redis_manager()
        rc = rm.redis_client
        if rc:
            cursor = 0
            patterns = [
                "limited:*",
                "rl:buy-limited:*",
                "shop:limited:idemp:*",
                "shop:limited:idemp_lock:*",
                "limited:*:user:*:purchased",
            ]
            for pat in patterns:
                cursor = 0
                while True:
                    cursor, keys = rc.scan(cursor=cursor, match=pat, count=100)
                    if keys:
                        rc.delete(*keys)
                    if cursor == 0:
                        break
    except Exception:
        pass


def test_limited_promos_and_limits(client: TestClient):
    _reset_limited_state()
    # Deterministic payment success handled by global fixture in conftest
    admin_site = "admin_lpromo-" + uuid.uuid4().hex[:8]
    admin = signup_and_login(client, admin_site, "passw0rd!")
    # 테스트 전용 관리자 권한 부여 (dev/test 환경에서만 허용)
    client.post("/api/admin/users/elevate", json={"site_id": admin_site})
    headers = _auth_headers(admin)

    # Attempt upsert as non-admin; if forbidden, skip suite (admin guard enforced)
    pkg_code = "PKG-PROMO-" + uuid.uuid4().hex[:5]
    up = client.post(
        "/api/admin/limited-packages/upsert",
        json={
            "package_id": pkg_code,
            "name": "Promo Pack",
            "price": 100,
            "stock_total": 2,
            "stock_remaining": 2,
            "per_user_limit": 2,
            "is_active": True,
            "contents": {"bonus_tokens": 10},
        },
        headers=headers,
    )
    if up.status_code == 403:
        # 환경 가드로 elevate가 차단된 경우 방어적 스킵
        pytest.skip("Admin guard enforced; skipping admin-required promo tests")
    assert up.status_code == 200

    # Create a promo code max_uses=1
    promo_code = "ONEUSE" + uuid.uuid4().hex[:4].upper()
    pu = client.post(
        "/api/admin/promo-codes/upsert",
        json={
            "code": promo_code,
            "package_id": pkg_code,
            "discount_type": "flat",
            "value": 50,
            "max_uses": 1,
            "is_active": True,
        },
        headers=headers,
    )
    assert pu.status_code == 200

    u1 = signup_and_login(client, "user_lpromo1-" + uuid.uuid4().hex[:8], "passw0rd!")
    uh1 = _auth_headers(u1)

    # First purchase with promo succeeds (price discounted to 50)
    random.seed(7)
    r1 = client.post("/api/shop/buy-limited", json={"package_id": pkg_code, "promo_code": promo_code}, headers=uh1)
    assert r1.status_code == 200 and r1.json()["success"] is True

    # Second purchase with promo should fail due to max_uses reached and reason_code PROMO_EXHAUSTED
    r2 = client.post("/api/shop/buy-limited", json={"package_id": pkg_code, "promo_code": promo_code}, headers=uh1)
    assert r2.status_code == 200
    body2 = r2.json()
    assert body2["success"] is False and body2.get("reason_code") == "PROMO_EXHAUSTED"

    # Per-user limit is 2. We have 1 success so far; next without promo should succeed (2nd purchase)
    r3 = client.post("/api/shop/buy-limited", json={"package_id": pkg_code}, headers=uh1)
    assert r3.status_code == 200 and r3.json()["success"] is True

    # Now the next attempt should fail due to per-user limit reached
    r4 = client.post("/api/shop/buy-limited", json={"package_id": pkg_code}, headers=uh1)
    assert r4.status_code == 200 and r4.json()["success"] is False

    # Emergency disable then verify still blocked
    dis = client.post(f"/api/admin/limited-packages/{pkg_code}/disable", headers=headers)
    assert dis.status_code == 200
    r5 = client.post("/api/shop/buy-limited", json={"package_id": pkg_code}, headers=uh1)
    assert r5.status_code == 200 and r5.json()["success"] is False

def test_promo_zero_uses_is_exhausted(client: TestClient):
    # Admin setup
    # Deterministic payment handled globally (fixture)
    admin = signup_and_login(client, "admin_zero_uses", "passw0rd!")
    client.post("/api/admin/users/elevate", json={"site_id": "admin_zero_uses"})
    headers = _auth_headers(admin)
    # Upsert package
    up = client.post(
        "/api/admin/limited-packages/upsert",
        json={
            "package_id": "PKG-PROMO-0",
            "name": "Promo Zero",
            "price": 100,
            "stock_total": 5,
            "stock_remaining": 5,
            "per_user_limit": 1,
            "is_active": True,
            "contents": {"bonus_tokens": 10},
        },
        headers=headers,
    )
    if up.status_code == 403:
        pytest.skip("Admin guard enforced; skipping")
    assert up.status_code == 200
    # Upsert promo with max_uses=0 (effectively exhausted)
    pu = client.post(
        "/api/admin/promo-codes/upsert",
        json={"code": "ZERO", "package_id": "PKG-PROMO-0", "discount_type": "flat", "value": 99, "max_uses": 0, "is_active": True},
        headers=headers,
    )
    assert pu.status_code == 200
    # Buyer
    u = signup_and_login(client, "user_zero_uses-" + uuid.uuid4().hex[:8], "passw0rd!")
    uh = _auth_headers(u)
    r = client.post("/api/shop/buy-limited", json={"package_id": "PKG-PROMO-0", "promo_code": "ZERO"}, headers=uh)
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is False and body.get("reason_code") == "PROMO_EXHAUSTED"

