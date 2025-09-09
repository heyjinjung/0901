import time
from starlette.testclient import TestClient
from app.main import app

client = TestClient(app)


def _signup(site_id: str):
    r = client.post(
        "/api/auth/signup",
        json={
            "site_id": site_id,
            "nickname": site_id,
            "password": "pass1234",
            "invite_code": "5858",
            "phone_number": f"010{int(time.time()*1000)%1000000000:09d}",
        },
    )
    assert r.status_code == 200
    return r.json()


def _auth(token: str):
    return {"Authorization": f"Bearer {token}"}


def test_game_history_and_follow_flow():
    # 사용자 2명 가입
    u1 = _signup(f"hist1_{int(time.time())}")
    u2 = _signup(f"hist2_{int(time.time())}")
    h1 = _auth(u1["access_token"])
    h2 = _auth(u2["access_token"])

    # 토큰 충전
    client.post("/api/users/tokens/add", headers=h1, params={"amount": 2000})
    # 슬롯 스핀 몇 번 -> GameHistory 기록 기대
    for _ in range(3):
        r = client.post("/api/games/slot/spin", headers=h1, json={"bet_amount": 10})
        assert r.status_code == 200

    # 히스토리 조회
    r_hist = client.get("/api/games/history", headers=h1)
    assert r_hist.status_code == 200
    body_hist = r_hist.json()
    assert body_hist["total"] >= 1
    assert len(body_hist["items"]) >= 1

    # 게임 타입별 통계
    r_stats = client.get("/api/games/slot/stats", headers=h1)
    assert r_stats.status_code == 200
    slot_stats = r_stats.json()
    assert slot_stats["game_type"] == "slot"
    assert slot_stats["play_count"] >= 1

    # 프로필 통계
    r_profile = client.get("/api/games/profile/stats", headers=h1)
    assert r_profile.status_code == 200
    prof = r_profile.json()
    assert prof["total_play_count"] >= 1

    # Follow add(idempotent) / list / unfollow
    target_id = u2["user"]["id"]
    r_follow = client.post(f"/api/games/follow/{target_id}", headers=h1)
    assert r_follow.status_code == 200
    rf_body = r_follow.json()
    assert rf_body["following"] is True

    # 중복 follow 시도 → 여전히 following True
    r_follow2 = client.post(f"/api/games/follow/{target_id}", headers=h1)
    assert r_follow2.status_code == 200
    assert r_follow2.json()["following"] is True

    # following 리스트
    r_list = client.get("/api/games/follow/list", headers=h1)
    assert r_list.status_code == 200
    lst = r_list.json()
    assert lst["total"] >= 1

    # followers (u2 관점에서 u1 표시)
    r_followers = client.get("/api/games/follow/followers", headers=h2)
    assert r_followers.status_code == 200
    flw = r_followers.json()
    assert any(item["user_id"] == u1["user"]["id"] for item in flw["items"])

    # unfollow
    r_unfollow = client.delete(f"/api/games/follow/{target_id}", headers=h1)
    assert r_unfollow.status_code == 200
    assert r_unfollow.json()["following"] is False

    # 리스트 재확인 (total 감소 혹은 0)
    r_list2 = client.get("/api/games/follow/list", headers=h1)
    assert r_list2.status_code == 200
