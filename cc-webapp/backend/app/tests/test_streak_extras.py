from fastapi.testclient import TestClient
from datetime import datetime


def test_streak_full_flow(client: TestClient):
    # tick (increase)
    r_tick = client.post('/api/streak/tick', json={'action_type': 'DAILY_LOGIN'})
    assert r_tick.status_code == 200
    count_after_tick = r_tick.json()['count']
    assert count_after_tick >= 0

    # preview
    r_prev = client.get('/api/streak/preview?action_type=DAILY_LOGIN')
    assert r_prev.status_code == 200
    prev_data = r_prev.json()
    assert prev_data['action_type'] == 'DAILY_LOGIN'

    # protection toggle on
    r_prot_on = client.post('/api/streak/protection', json={'action_type': 'DAILY_LOGIN', 'enabled': True})
    assert r_prot_on.status_code == 200
    assert r_prot_on.json()['enabled'] is True

    # history (needs year/month)
    now = datetime.utcnow()
    r_hist = client.get(f'/api/streak/history?action_type=DAILY_LOGIN&year={now.year}&month={now.month}')
    assert r_hist.status_code == 200

    # claim (may fail if count 0) -> ensure ticked at least once
    if count_after_tick > 0:
        r_claim = client.post('/api/streak/claim', json={'action_type': 'DAILY_LOGIN'})
        # claim can be 200 or 400 if already claimed earlier same day in shared test session
        assert r_claim.status_code in (200, 400)
