import time
from fastapi import status


def test_streak_tick_daily_guard(client, auth_token):
    """동일 UTC 날짜 내 /api/streak/tick 중복 호출 시 두번째부터 증가하지 않아야 한다.

    1) 첫 tick → count 1
    2) 연속 두번째 tick → count 그대로 1 (증가 금지)
    3) 세번째 tick → 동일 날짜이므로 여전히 1

    NOTE: 날짜 교차(UTC 자정) 테스트는 별도 time travel 인프라 필요 → 여기선 생략.
    """
    token = auth_token()
    headers = {"Authorization": f"Bearer {token}"}

    r1 = client.post("/api/streak/tick", json={"action_type": "SLOT_SPIN"}, headers=headers)
    assert r1.status_code == status.HTTP_200_OK
    c1 = r1.json()["count"]
    assert c1 == 1

    r2 = client.post("/api/streak/tick", json={"action_type": "SLOT_SPIN"}, headers=headers)
    assert r2.status_code == status.HTTP_200_OK
    c2 = r2.json()["count"]
    assert c2 == 1, "두번째 호출에서 streak 증가하면 안됨"

    r3 = client.post("/api/streak/tick", json={"action_type": "SLOT_SPIN"}, headers=headers)
    assert r3.status_code == status.HTTP_200_OK
    c3 = r3.json()["count"]
    assert c3 == 1, "세번째 호출에서도 동일 날짜 내 증가 금지"
