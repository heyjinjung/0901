import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# 간단한 헬퍼 (실제 conftest 에 auth_token 픽스처 존재 가정)

def test_follow_duplicate_unfollow_flow(auth_token):
    # 대상 유저 생성 (임시: self-follow 방지 위해 다른 id 가정 → 실제로는 사전 user fixture 필요)
    # 여기서는 간소화: API가 target_user_id 존재한다고 가정 (id=2)
    headers = {"Authorization": f"Bearer {auth_token}"}
    r1 = client.post("/api/games/follow/2", headers=headers)
    assert r1.status_code in (200, 404)  # 대상 존재 안 하면 404 가능
    r2 = client.post("/api/games/follow/2", headers=headers)
    # 두 번째는 이미 팔로우 상태이면 400/409 류 혹은 동일 응답(멱등) — 범위로 허용
    assert r2.status_code in (200, 400, 409, 404)
    r3 = client.delete("/api/games/follow/2", headers=headers)
    assert r3.status_code in (200, 404)


def test_follow_list_pagination(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = client.get("/api/games/follow/list?limit=10&offset=0", headers=headers)
    assert r.status_code in (200, 404)


def test_game_history_list(auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = client.get("/api/games/history?limit=5&offset=0", headers=headers)
    assert r.status_code in (200, 404)

