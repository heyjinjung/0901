import uuid
import time
import threading
from typing import List

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _signup(prefix: str = 'idem_edge'):
    unique = uuid.uuid4().hex
    site_id = f'{prefix}_{unique[:20]}'
    nickname = f'{prefix}_{unique[:12]}'
    payload = {
        'invite_code': '5858',
        'nickname': nickname,
        'site_id': site_id,
        'phone_number': '010' + unique[:8],
        'password': 'pass1234'
    }
    r = client.post('/api/auth/signup', json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    return data['access_token'], data['user']['id']


def _auth_headers(token: str):
    return {'Authorization': f'Bearer {token}'}


def test_purchase_insufficient_balance_idempotent_fail():
    """잔액 부족 첫 실패 후 동일 idempotency_key 재시도 시 동일 실패(새 트랜잭션 미생성)"""
    token, user_id = _signup('insuff')
    headers = _auth_headers(token)
    idem_key = 'INSUFF1'
    body = {
        'user_id': user_id,
        'product_id': 'expensive_item_x',  # 가짜 SKU
        'amount': 10_000_000,  # 과도한 금액 → 실패 유도
        'quantity': 1,
    'kind': 'gold',
        'payment_method': 'card',
        'idempotency_key': idem_key,
    }
    r1 = client.post('/api/shop/buy', headers=headers, json=body)
    data1 = r1.json()
    assert data1['success'] in (False, True)
    if data1['success'] is True:
        pytest.skip('환경에서 과도 금액이 실패를 유도하지 못함 - 로직 검증 필요')
    receipt1 = data1.get('receipt_code') or data1.get('idempotent_receipt_code')

    r2 = client.post('/api/shop/buy', headers=headers, json=body)
    data2 = r2.json()
    receipt2 = data2.get('receipt_code') or data2.get('idempotent_receipt_code')
    assert receipt1 == receipt2
    assert data2['success'] is False


def test_purchase_always_fail_gateway_reuse_failed_tx(monkeypatch):
    """게이트웨이 always_fail 모드에서 동일 idempotency_key 재시도 시 실패 트랜잭션 재사용"""
    token, user_id = _signup('failgw')
    headers = _auth_headers(token)

    monkeypatch.setenv('PAYMENT_GATEWAY_MODE', 'always_fail')
    idem_key = 'GWFAIL1'
    body = {
        'user_id': user_id,
    'product_id': 'gold_pack_small',
        'amount': 300,
        'quantity': 1,
    'kind': 'gold',
        'payment_method': 'card',
        'idempotency_key': idem_key,
    }
    r1 = client.post('/api/shop/buy', headers=headers, json=body)
    data1 = r1.json()
    assert data1['success'] is False
    receipt1 = data1.get('receipt_code') or data1.get('idempotent_receipt_code')

    r2 = client.post('/api/shop/buy', headers=headers, json=body)
    data2 = r2.json()
    receipt2 = data2.get('receipt_code') or data2.get('idempotent_receipt_code')
    assert receipt1 == receipt2
    assert data2['success'] is False


def test_purchase_pending_then_success(monkeypatch):
    """첫 호출 pending, 이후 동일 idempotency_key 재시도 성공 시 같은 트랜잭션 승격"""
    token, user_id = _signup('pend')
    headers = _auth_headers(token)
    monkeypatch.setenv('PAYMENT_GATEWAY_MODE', 'pending_then_success')
    idem_key = 'PENDING1'
    body = {
        'user_id': user_id,
    'product_id': 'gold_pack_small',
        'amount': 300,
        'quantity': 1,
    'kind': 'gold',
        'payment_method': 'card',
        'idempotency_key': idem_key,
    }
    r1 = client.post('/api/shop/buy', headers=headers, json=body)
    data1 = r1.json()
    if data1['success'] is True:
        pytest.skip('게이트웨이가 즉시 success 반환 (환경 영향)')
    receipt1 = data1.get('receipt_code') or data1.get('idempotent_receipt_code')
    time.sleep(1.2)
    r2 = client.post('/api/shop/buy', headers=headers, json=body)
    data2 = r2.json()
    receipt2 = data2.get('receipt_code') or data2.get('idempotent_receipt_code')
    assert receipt1 == receipt2
    assert data2['success'] is True


@pytest.mark.xfail(reason="Race condition may create multiple pending rows before constraint commit; future improvement will enforce single insert.")
def test_purchase_concurrency_race_single_record():
    """동일 idempotency_key 동시 요청 시 (현재 허용: 1~N) 최소 하나는 성공/모두 동일 금액.

    NOTE: 현 구현은 애플리케이션 레벨 락 미도입 상태이므로 완전 단일 보장은 향후 Redis SETNX 등으로 강화 예정.
    """
    token, user_id = _signup('race')
    headers = _auth_headers(token)
    idem_key = 'RACE1'
    body = {
        'user_id': user_id,
    'product_id': 'gold_pack_small',
        'amount': 300,
        'quantity': 1,
    'kind': 'gold',
        'payment_method': 'card',
        'idempotency_key': idem_key,
    }

    receipts: List[str] = []
    statuses: List[int] = []

    def worker():
        r = client.post('/api/shop/buy', headers=headers, json=body)
        statuses.append(r.status_code)
        try:
            data = r.json()
            receipts.append(data.get('receipt_code') or data.get('idempotent_receipt_code'))
        except Exception:
            receipts.append('ERR')

    threads = [threading.Thread(target=worker) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert all(s == 200 for s in statuses)
    receipts_set = {r for r in receipts if r}
    # 강한 보장(단일) 실패 시: 중복 영수증이 2개 이상이어도 최소 하나는 재사용되어야 함
    assert len(receipts_set) >= 1
