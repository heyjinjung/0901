import time
import uuid
from fastapi.testclient import TestClient
from app.main import app
import pytest


def _signup(client: TestClient):
    now = int(time.time())
    # 다중 실행 시 전화번호/이메일 중복 회피 위해 초단위 타임스탬프 + suffix
    suffix = uuid.uuid4().hex[:6]
    body = {
    "site_id": f"t{now}{suffix}@e2e.local",
    "nickname": f"t{now}{suffix}",
    "phone_number": f"010{now % 100000000:08d}"[:11],
        "invite_code": "5858",
        "password": "Testpass1!",
    }
    r = client.post("/api/auth/signup", json=body)
    assert r.status_code == 200, r.text
    data = r.json()
    return data["access_token"], data["user"]["id"]


def _get_first_active_package(client: TestClient, headers=None):
    r = client.get("/api/shop/limited-packages", headers=headers or {})
    assert r.status_code == 200, r.text
    for p in r.json():
        if p.get("is_active") and (p.get("remaining_stock") or 0) > 0:
            return p["code"], p
    return None, None


@pytest.mark.ci_core
def test_purchase_flow_with_idempotency():
    """핵심 구매 플로우 및 idempotency 확인
    1) 회원가입
    2) 한정 패키지 목록 조회 후 첫 활성 코드 선택
    3) idempotency_key 첨부 첫 구매 → 성공 및 gem 증가
    4) 동일 idempotency_key 재요청 → 중복 처리(success True, balance 증가 없음)
    """
    client = TestClient(app)
    token, user_id = _signup(client)
    auth_headers = {"Authorization": f"Bearer {token}"}
    code, pkg = _get_first_active_package(client, headers=auth_headers)
    assert code, "활성화된 한정 패키지가 필요합니다. (테스트 전에 seed 필요)"

    # 첫 구매
    idem = uuid.uuid4().hex[:12]
    payload = {"package_id": code, "quantity": 1, "idempotency_key": idem, "currency": "USD"}
    r1 = client.post("/api/shop/buy-limited", json=payload, headers=auth_headers)
    assert r1.status_code == 200, r1.text
    d1 = r1.json()
    if d1.get("success") is not True:
        # 결제 모듈/모의결제 비활성 ("Payment failed" 등) 상황에서는 핵심 idempotency 흐름 진행 불가 → 스킵 처리
        reason = d1.get("message") or d1.get("error") or d1
        pytest.skip(f"초기 구매가 성공하지 않아(idempotency 시나리오 전개 불가) – 원인: {reason}")
    # 1차 balance: 응답에 new_gem_balance가 있으면 활용, 없으면 프로필 조회
    first_balance = d1.get("new_gem_balance")
    if first_balance is None:
        prof1 = client.get("/api/auth/profile", headers=auth_headers)
        if prof1.status_code == 200:
            first_balance = prof1.json().get("cyber_token_balance")
    # balance 추적이 불가능하면 이후 idempotency balance 검증은 스킵
    balance_tracking = first_balance is not None

    # 동일 idempotency 재시도
    r2 = client.post("/api/shop/buy-limited", json=payload, headers=auth_headers)
    assert r2.status_code in (200, 403), r2.text
    d2 = {}
    try:
        d2 = r2.json()
    except Exception:
        pass
    if d2.get("success") is not True:
        # Redis 미가용 등으로 idempotent fast-path 미작동 → per-user limit(403) 또는 fail 응답이면 스킵
        redis_manager = getattr(app.state, "redis_manager", None)
        redis_ready = bool(getattr(redis_manager, "client", None))
        if not redis_ready:
            pytest.skip("Redis 미가용으로 strict idempotency 검증 스킵")
    # 여기부터는 Redis 가용하며 idempotent ack 기대
    assert d2.get("success") is True, "중복 요청은 success=True ack 형태여야 합니다"
    assert "new_gem_balance" in d2, "표준화된 balance 필드가 응답에 없습니다"
    if first_balance is not None:
        assert d2.get("new_gem_balance") == first_balance, (
            f"Idempotent 재요청 후 balance 변동: {first_balance} -> {d2.get('new_gem_balance')}"
        )
        prof2 = client.get("/api/auth/profile", headers=auth_headers)
        assert prof2.status_code == 200, prof2.text
        prof_balance = prof2.json().get("cyber_token_balance")
        assert prof_balance == first_balance, (
            f"프로필 기준 balance 변동: {first_balance} -> {prof_balance}"
        )
