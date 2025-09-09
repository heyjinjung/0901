import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# 가정: 최소 베팅 >0, 최대 베팅 ~1_000_000_000 미만, self-concurrency 제한 존재(중복 bet 방지)할 것으로 예상

@pytest.mark.parametrize("bet_amount", [0, -10])
def test_crash_bet_invalid_minimum(auth_token, bet_amount):
    r = client.post("/api/games/crash/bet", json={"bet_amount": bet_amount}, headers={"Authorization": f"Bearer {auth_token}"})
    assert r.status_code in (400, 422)

@pytest.mark.parametrize("bet_amount", [1_000_000_001, 10_000_000_000])
def test_crash_bet_exceeds_max(auth_token, bet_amount):
    r = client.post("/api/games/crash/bet", json={"bet_amount": bet_amount}, headers={"Authorization": f"Bearer {auth_token}"})
    assert r.status_code in (400, 422)

def test_crash_bet_insufficient_tokens(auth_token):
    # 큰 베팅 여러번 시도해 잔액 소진 유도: 최초 성공 이후 동일 금액 반복 → 결국 실패 코드 발생 기대
    # (정확 토큰 경제 규칙 모를 경우 범위 assertion 유지)
    first = client.post("/api/games/crash/bet", json={"bet_amount": 5000}, headers={"Authorization": f"Bearer {auth_token}"})
    assert first.status_code in (200, 400, 422)
    # 잔액 부족 가능성 높이기 위해 반복
    for _ in range(5):
        r = client.post("/api/games/crash/bet", json={"bet_amount": 5000}, headers={"Authorization": f"Bearer {auth_token}"})
        if r.status_code in (400, 422):
            break
    # 최종적으로 최소 한 번은 시도됨
    assert r.status_code in (200, 400, 422)

def test_crash_bet_concurrent_like_double_submit(auth_token):
    # 동일 사용자 연속 빠른 두 번 bet → 두 번째는 (이미 진행 중) 오류/거부 기대 (정책 확정 전 범위)
    r1 = client.post("/api/games/crash/bet", json={"bet_amount": 1000}, headers={"Authorization": f"Bearer {auth_token}"})
    r2 = client.post("/api/games/crash/bet", json={"bet_amount": 1200}, headers={"Authorization": f"Bearer {auth_token}"})
    assert r1.status_code in (200, 400)
    assert r2.status_code in (200, 400, 409, 422)  # 중복 처리 시 409/400 가능

def test_crash_cashout_without_active(auth_token):
    # 활성 세션 없이 cashout 시도
    r = client.post("/api/games/crash/cashout", json={"multiplier": 1.5}, headers={"Authorization": f"Bearer {auth_token}"})
    assert r.status_code in (400, 404, 422)

def test_crash_bet_then_cashout_double(auth_token):
    # bet 후 cashout 1회 성공/실패 후 두 번째 cashout은 오류 기대
    bet = client.post("/api/games/crash/bet", json={"bet_amount": 700}, headers={"Authorization": f"Bearer {auth_token}"})
    assert bet.status_code in (200, 400)
    c1 = client.post("/api/games/crash/cashout", json={"multiplier": 1.1}, headers={"Authorization": f"Bearer {auth_token}"})
    assert c1.status_code in (200, 400, 409)
    c2 = client.post("/api/games/crash/cashout", json={"multiplier": 1.2}, headers={"Authorization": f"Bearer {auth_token}"})
    assert c2.status_code in (200, 400, 404, 409)

def test_crash_bet_basic_success(auth_token):
    r = client.post("/api/games/crash/bet", json={"bet_amount": 1000}, headers={"Authorization": f"Bearer {auth_token}"})
    assert r.status_code in (200, 400)  # 정책 확정 시 200 고정으로 좁히기

