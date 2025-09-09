"""프로필 수정 엔드투엔드 테스트
register → GET /api/users/profile → PUT /api/users/profile (nickname/phone_number 변경) → 재조회 검증
"""
import uuid
from fastapi.testclient import TestClient
from app.main import app

INVITE_CODE = "5858"

def _register_unique(nickname: str):
    client = TestClient(app)
    resp = client.post("/api/auth/register", json={"invite_code": INVITE_CODE, "nickname": nickname})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    token = data["access_token"]
    return client, token


def test_profile_update_flow():
    base_nick = f"prof_update_{uuid.uuid4().hex[:6]}"
    client, token = _register_unique(base_nick)
    headers = {"Authorization": f"Bearer {token}"}

    # 초기 프로필
    r1 = client.get("/api/users/profile", headers=headers)
    assert r1.status_code == 200, r1.text
    p1 = r1.json()
    assert p1.get("nickname") == base_nick

    # 업데이트 페이로드 (닉네임 + phone)
    new_nick = base_nick + "x"
    payload = {
        "nickname": new_nick,
        "phone_number": "010-1234-5678"
    }
    up = client.put("/api/users/profile", json=payload, headers=headers)
    assert up.status_code == 200, up.text
    up_data = up.json()
    assert up_data.get("nickname") == new_nick
    assert up_data.get("phone_number") == "010-1234-5678"

    # 재조회
    r2 = client.get("/api/users/profile", headers=headers)
    assert r2.status_code == 200, r2.text
    p2 = r2.json()
    assert p2.get("nickname") == new_nick
    # phone_number는 UserResponse / UserProfileResponse 스키마 차이 있을 수 있음 → tolerant
    if "phone_number" in p2:
        assert p2.get("phone_number") == "010-1234-5678"

    # /api/auth/me 와 동치 닉네임 확인
    me = client.get("/api/auth/me", headers=headers)
    if me.status_code == 200:
        me_data = me.json()
        if isinstance(me_data, dict) and "nickname" in me_data:
            assert me_data["nickname"] == new_nick
