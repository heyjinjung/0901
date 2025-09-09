import uuid
from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)


def _signup(prefix: str = 'idem'):
    unique = uuid.uuid4().hex
    site_id = f'{prefix}_{unique[:20]}'
    nickname = f'{prefix}_{unique[:12]}'
    payload = {
        'invite_code': '5858',
        'nickname': nickname,
        'site_id': site_id,
    # Randomize phone number to avoid unique constraint collisions across test runs
    'phone_number': '010' + unique[:8],
        'password': 'pass1234'
    }
    # Try modern signup first; if schema mismatch (500) fallback to legacy minimal register or direct user insert not available.
    r = client.post('/api/auth/signup', json=payload)
    if r.status_code == 200:
        data = r.json()
        return data['access_token'], data['user']['id']
    # Fallback: try login bootstrap path (create if absent not possible -> fail early)
    # Provide clearer diagnostic
    pytest.fail(f"signup failed status={r.status_code} body={r.text}")


def test_gem_purchase_idempotent_duplicate():
    token, user_id = _signup()
    headers = {'Authorization': f'Bearer {token}'}
    idem_key = 'TEST123'
    body = {
        'user_id': user_id,
        'product_id': 'gems_pack_small',
        'amount': 300,
        'quantity': 1,
        'kind': 'gems',
        'payment_method': 'card',
        'idempotency_key': idem_key,
    }
    r1 = client.post('/api/shop/buy', headers=headers, json=body)
    assert r1.status_code == 200, r1.text
    data1 = r1.json()
    assert data1['success'] is True
    receipt1 = data1.get('receipt_code') or data1.get('idempotent_receipt_code')

    # duplicate call with same idempotency key
    r2 = client.post('/api/shop/buy', headers=headers, json=body)
    assert r2.status_code == 200, r2.text
    data2 = r2.json()
    # Either it replays same receipt or returns success False with same receipt reference
    receipt2 = data2.get('receipt_code') or data2.get('idempotent_receipt_code')
    assert receipt1 == receipt2
