import os, sys
import pytest
from fastapi.testclient import TestClient

_here = os.path.dirname(__file__)
_backend_root = os.path.abspath(os.path.join(_here, "..", ".."))
if _backend_root not in sys.path:
    sys.path.insert(0, _backend_root)

from app.main import app  # noqa: E402
import time

@pytest.fixture(scope="function")
def client() -> TestClient:
    return TestClient(app)

def _auth_headers(client: TestClient):
    import uuid
    sid = str(uuid.uuid4())[:8]
    phone_number = "010" + sid + "0000"
    payload = {
        "site_id": sid,
        "nickname": sid,
    "phone_number": phone_number,
        "password": "pass1234",
        "invite_code": "5858"
    }
    r = client.post("/api/auth/signup", json=payload)
    assert r.status_code in (200,201), r.text
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# 간단 이벤트 브로드캐스트 확인: 토큰 증가 후 사용자 프로필 재조회
# (웹소켓 직접 캡처 대신 상태 변화로 간접 검증)

def test_token_update_add(client: TestClient):
    headers = _auth_headers(client)
    # 초기 me
    me1 = client.get("/api/auth/me", headers=headers)
    assert me1.status_code == 200
    before = me1.json().get("cyber_token_balance", 0)
    # 토큰 지급 엔드포인트 존재 가정 (없으면 스킵)
    give_payload = {"amount": 25, "reason": "test_add"}
    r = client.post("/api/tokens/add", json=give_payload, headers=headers)
    if r.status_code == 404:
        pytest.skip("/api/tokens/add 엔드포인트 없음")
    assert r.status_code == 200, r.text
    me2 = client.get("/api/auth/me", headers=headers)
    after = me2.json().get("cyber_token_balance", 0)
    assert after - before == 25

