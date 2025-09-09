import time
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def _signup(unique: str):
    r = client.post(
        "/api/auth/signup",
        json={
            "site_id": unique,
            "nickname": unique,
            "password": "pass1234",
            "invite_code": "5858",
            "phone_number": f"010{int(time.time()*1000)%1000000000:09d}",
        },
    )
    assert r.status_code == 200, r.text
    return r.json()


def _auth(token: str):
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.game
def test_follow_flow_and_lists():
    u1 = _signup(f"fw1_{int(time.time())}")
    u2 = _signup(f"fw2_{int(time.time())}")
    h1 = _auth(u1["access_token"])
    h2 = _auth(u2["access_token"])

    # self-follow 금지
    r_self = client.post(f"/api/games/follow/{u1['user']['id']}", headers=h1)
    assert r_self.status_code == 400
    assert "자기 자신" in r_self.text

    # 존재하지 않는 대상 404
    r_404 = client.post("/api/games/follow/9999999", headers=h1)
    assert r_404.status_code == 404

    target_id = u2["user"]["id"]
    # 최초 follow
    r1 = client.post(f"/api/games/follow/{target_id}", headers=h1)
    assert r1.status_code == 200
    body1 = r1.json()
    assert body1["success"] is True and body1["following"] is True
    base_follower_count = body1["follower_count"]

    # 중복 follow (idempotent) follower_count 증가 없어야 함
    r_dup = client.post(f"/api/games/follow/{target_id}", headers=h1)
    assert r_dup.status_code == 200
    body_dup = r_dup.json()
    assert body_dup["following"] is True
    assert body_dup["follower_count"] == base_follower_count

    # following list
    r_list = client.get("/api/games/follow/list", headers=h1)
    assert r_list.status_code == 200
    lst = r_list.json()
    assert lst["total"] >= 1
    assert any(item["user_id"] == target_id for item in lst["items"])

    # followers (u2 입장에서 u1 확인)
    r_followers = client.get("/api/games/follow/followers", headers=h2)
    assert r_followers.status_code == 200
    flw = r_followers.json()
    assert any(item["user_id"] == u1["user"]["id"] for item in flw["items"])

    # 언팔로우
    r_unf = client.delete(f"/api/games/follow/{target_id}", headers=h1)
    assert r_unf.status_code == 200
    assert r_unf.json()["following"] is False

    # 리스트 재확인 (해당 target 제거)
    r_list2 = client.get("/api/games/follow/list", headers=h1)
    assert r_list2.status_code == 200
    lst2 = r_list2.json()
    assert all(item["user_id"] != target_id for item in lst2["items"])


@pytest.mark.game
def test_history_filters_and_pagination():
    u = _signup(f"histf_{int(time.time())}")
    h = _auth(u["access_token"])
    # 토큰 충전 후 슬롯 스핀 몇번 (game_type=slot, action=spin)
    client.post("/api/users/tokens/add", headers=h, params={"amount": 1000})
    for _ in range(5):
        r_spin = client.post("/api/games/slot/spin", headers=h, json={"bet_amount": 5})
        assert r_spin.status_code == 200

    # 기본 조회
    base = client.get("/api/games/history?limit=3&offset=0", headers=h)
    assert base.status_code == 200
    body = base.json()
    assert body["limit"] == 3 and body["offset"] == 0
    assert body["total"] >= len(body["items"]) >= 1

    # game_type 필터
    slot_hist = client.get("/api/games/history?game_type=slot", headers=h)
    assert slot_hist.status_code == 200
    sh = slot_hist.json()
    assert all(item["game_type"] == "slot" for item in sh["items"])

    # since 필터 (미래 시간을 줘서 0 기대)
    future_iso = "2999-01-01T00:00:00"
    fut = client.get(f"/api/games/history?since={future_iso}", headers=h)
    assert fut.status_code == 200
    assert fut.json()["total"] == 0

    # 잘못된 since → 400
    bad = client.get("/api/games/history?since=not-a-date", headers=h)
    assert bad.status_code == 400

    # pagination 두 번째 페이지
    page2 = client.get("/api/games/history?limit=2&offset=2", headers=h)
    assert page2.status_code == 200
    p2 = page2.json()
    assert p2["limit"] == 2 and p2["offset"] == 2
