import os, sys
import pytest
from fastapi.testclient import TestClient

# Ensure repository root (cc-webapp/backend) is on sys.path when test invoked from upper directory
_here = os.path.dirname(__file__)
_backend_root = os.path.abspath(os.path.join(_here, "..", ".."))
if _backend_root not in sys.path:
    sys.path.insert(0, _backend_root)

from app.main import app  # noqa: E402
from app.database import SessionLocal  # noqa: E402
from app.models.auth_models import User  # noqa: E402
from app.services.auth_service import AuthService  # noqa: E402
from sqlalchemy.orm import Session

@pytest.fixture(scope="function")
def client() -> TestClient:
    return TestClient(app)

@pytest.fixture(scope="function")
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _auth_headers(client: TestClient, db: Session):
    # 직접 User 레코드 생성하여 토큰 발급(회원가입 500 회피)
    import uuid
    sid = uuid.uuid4().hex[:10]
    phone_number = "010" + sid[:8]
    user = User(
        site_id=sid,
        nickname="tester_" + sid[:4],
        phone_number=phone_number,
        password_hash=AuthService.get_password_hash("pass1234"),
        invite_code="5858",
        cyber_token_balance=100,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = AuthService.create_access_token({"sub": user.site_id, "user_id": user.id, "is_admin": False})
    return {"Authorization": f"Bearer {token}"}

def test_session_lifecycle(client: TestClient, db: Session):
    headers = _auth_headers(client, db)
    # start
    r = client.post("/api/games/session/start", json={"game_type": "slot", "bet_amount": 50}, headers=headers)
    assert r.status_code == 200, r.text
    sid = r.json()["session_id"]
    # duplicate start
    r2 = client.post("/api/games/session/start", json={"game_type": "slot", "bet_amount": 30}, headers=headers)
    assert r2.status_code == 409
    # active
    r3 = client.get("/api/games/session/active", headers=headers)
    assert r3.status_code == 200
    # end
    r4 = client.post("/api/games/session/end", json={"session_id": sid, "duration": 10, "rounds_played": 3, "total_bet": 150, "total_win": 40}, headers=headers)
    assert r4.status_code == 200
    body = r4.json()
    assert body.get("result_data"), "result_data missing in end response"
    assert body["result_data"]["rounds"] == 3
    assert body["result_data"]["total_bet"] == 150
    assert body["result_data"]["total_win"] == 40
    assert body["result_data"]["net"] == (40 - 150)
    # active after end
    r5 = client.get("/api/games/session/active", headers=headers)
    assert r5.status_code == 404

def test_session_end_roi_zero_and_persistence(client: TestClient, db: Session):
    headers = _auth_headers(client, db)
    # start with bet 0
    r = client.post("/api/games/session/start", json={"game_type": "slot", "bet_amount": 0}, headers=headers)
    assert r.status_code == 200
    sid = r.json()["session_id"]
    # end with total_bet=0 total_win=0
    r2 = client.post("/api/games/session/end", json={"session_id": sid, "duration": 5, "rounds_played": 1, "total_bet": 0, "total_win": 0}, headers=headers)
    assert r2.status_code == 200
    body = r2.json()
    assert body["result_data"]["roi"] == 0
    # DB 직접 확인
    from app.models.game_models import GameSession as GameSessionModel
    row = db.query(GameSessionModel).filter(GameSessionModel.external_session_id == sid).first()
    assert row is not None
    rd = row.result_data
    if isinstance(rd, str):
        import json as _json
        rd = _json.loads(rd)
    assert rd["total_bet"] == 0 and rd["roi"] == 0

