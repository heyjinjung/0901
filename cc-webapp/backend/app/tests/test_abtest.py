from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_abtest_assignment_idempotent():
    # first assignment
    r1 = client.post('/api/abtest/assign', json={'test_name': 'homepage_cta', 'variants': ['A','B']}, params={'user_id': 123})
    assert r1.status_code == 200, r1.text
    data1 = r1.json()
    assert data1['test_name'] == 'homepage_cta'
    assert data1['variant'] in ['A','B']

    # second assignment returns same variant
    r2 = client.post('/api/abtest/assign', json={'test_name': 'homepage_cta', 'variants': ['A','B']}, params={'user_id': 123})
    assert r2.status_code == 200
    data2 = r2.json()
    assert data2['variant'] == data1['variant']


def test_abtest_get_variant_auto_assign():
    r = client.get('/api/abtest/variant', params={'test_name': 'pricing_banner', 'user_id': 999})
    assert r.status_code == 200
    data = r.json()
    assert data['test_name'] == 'pricing_banner'
    assert data['variant'] in ['A','B']
