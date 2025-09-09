import pytest
from fastapi import status
from app.services.reward_service import calculate_streak_daily_reward

"""streak preview 엔드포인트 테스트 (동기 TestClient 사용)
auth_token 픽스처는 callable 을 반환하므로 먼저 token = auth_token() 형태로 호출"""


def test_streak_preview_initial(client, auth_token):
    """신규 사용자: streak 0 → today_reward 0, next_day_reward >0"""
    token = auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/api/streak/preview", headers=headers)
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["streak_count"] == 0
    assert data["claimed_today"] is False
    assert data["claimable"] is False  # streak 0 → claim 불가
    assert data["today_reward_gold"] == 0
    assert data["today_reward_xp"] == 0
    # next day reward (streak_count+1) 산식 검증
    g1, xp1 = calculate_streak_daily_reward(1)
    assert data["next_day_reward_gold"] == g1
    assert data["next_day_reward_xp"] == xp1


def test_streak_preview_after_tick_and_claim(client, auth_token):
    """streak 1 달성 후 preview → claim 전후 상태 확인"""
    token = auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    # tick으로 streak 증가
    t = client.post("/api/streak/tick", json={"action_type": "SLOT_SPIN"}, headers=headers)
    assert t.status_code == 200
    # preview (claim 전)
    pre = client.get("/api/streak/preview", headers=headers)
    assert pre.status_code == 200
    pdata = pre.json()
    assert pdata["streak_count"] == 1
    assert pdata["claimable"] is True
    assert pdata["today_reward_gold"] > 0
    assert pdata["today_reward_xp"] > 0
    # claim 수행
    c = client.post("/api/streak/claim", json={"action_type": "SLOT_SPIN"}, headers=headers)
    assert c.status_code == 200
    # claim 후 preview 재조회
    post = client.get("/api/streak/preview", headers=headers)
    post_data = post.json()
    assert post_data["streak_count"] == 1  # claim은 streak 증가시키지 않음
    assert post_data["claimed_today"] is True
    assert post_data["claimable"] is False
    # 오늘 보상 금액은 그대로 유지
    assert post_data["today_reward_gold"] == pdata["today_reward_gold"]
    assert post_data["today_reward_xp"] == pdata["today_reward_xp"]
    # next_day_reward 는 streak+1 기준
    g2, xp2 = calculate_streak_daily_reward(2)
    assert post_data["next_day_reward_gold"] == g2
    assert post_data["next_day_reward_xp"] == xp2
