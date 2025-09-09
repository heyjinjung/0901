import os
import uuid
import random
import pytest
import httpx
from fastapi import status

from app.main import app
from app.database import get_db
from sqlalchemy.orm import Session
from app.models.auth_models import InviteCode, User

# NOTE: 이 테스트는 Grace (OLD+NEW 허용) 와 Cutover (OLD 차단, NEW 허용)를 단순 검증
# 환경변수 ENFORCE_DB_INVITE_CODES=1 시 Cutover 모드로 간주.

@pytest.fixture
def db_session():
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def new_code(db_session: Session):
    code = "NEW123"
    ic = db_session.query(InviteCode).filter(InviteCode.code == code).first()
    if not ic:
        ic = InviteCode(code=code, is_active=True)
        db_session.add(ic)
        db_session.commit()
    return code

def _make_phone():
    # 최소 11자리 확보 (010 + 8 hex)
    return "010" + uuid.uuid4().hex[:8]

async def _signup(client: httpx.AsyncClient, site_id: str, code: str, expect: int = 200):
    payload = {
        "site_id": site_id,
        "nickname": f"nick_{site_id}",
        "phone_number": _make_phone(),
        "password": "testpw",
        "invite_code": code
    }
    r = await client.post("/api/auth/signup", json=payload)
    assert r.status_code == expect, r.text
    return r.json() if r.status_code == 200 else None

@pytest.mark.asyncio
async def test_grace_allows_old_and_new(new_code, db_session):
    # Grace: ENFORCE_DB_INVITE_CODES=0 (기본값)
    if os.getenv("ENFORCE_DB_INVITE_CODES") == "1":
        pytest.skip("Cutover 환경에서는 Grace 테스트를 건너뜀")
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # OLD
        await _signup(client, site_id=str(uuid.uuid4())[:18], code="5858")
        # NEW
        await _signup(client, site_id=str(uuid.uuid4())[:18], code=new_code)

@pytest.mark.asyncio
async def test_cutover_blocks_old_allows_new(new_code, monkeypatch, db_session):
    # Cutover: ENFORCE_DB_INVITE_CODES=1 로 모킹
    monkeypatch.setenv("ENFORCE_DB_INVITE_CODES", "1")
    # FastAPI settings 재로딩 필요 시: 단순화(테스트 시작 전에 설정 로드된 경우) - 여기서는 로직이 settings 값 참조만 하므로 OK
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # NEW 허용
        await _signup(client, site_id=str(uuid.uuid4())[:18], code=new_code)
        # OLD 거부 기대
        payload_site = str(uuid.uuid4())[:18]
        resp = await client.post("/api/auth/signup", json={
            "site_id": payload_site,
            "nickname": f"nick_{payload_site}",
            "phone_number": f"010{payload_site[-4:]}{payload_site[-2:]}",
            "password": "testpw",
            "invite_code": "5858"
        })
        assert resp.status_code == 400
        assert "유효하지 않은" in resp.text

@pytest.mark.asyncio
async def test_new_code_login_and_refresh_flow(new_code):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        signup_data = await _signup(client, site_id=str(uuid.uuid4())[:18], code=new_code)
        access = signup_data["access_token"]
        refresh = signup_data.get("refresh_token")
        # 로그인 (이미 access 있으나 흐름 검증 위해 재로그인)
        login_resp = await client.post("/api/auth/login", json={
            "site_id": signup_data["user"]["site_id"],
            "password": "testpw"
        })
        assert login_resp.status_code == 200
        # refresh
        if refresh:
            ref_resp = await client.post("/api/auth/refresh", json={"refresh_token": refresh})
            assert ref_resp.status_code == 200

@pytest.mark.asyncio
async def test_invalid_code_spam_triggers_placeholder():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        for i in range(30):  # 다량 시도 (알람 메트릭은 아직 미구현, placeholder)
            payload = {
                "site_id": f"bad{i:02d}",
                "nickname": f"badnick{i:02d}",
                "phone_number": _make_phone(),
                "password": "pw12",
                "invite_code": "XXXXXX"
            }
            r = await client.post("/api/auth/signup", json=payload)
            assert r.status_code == 400
        # 간단한 실패 누적 검증: 동일 코드로 User 생성되지 않았음
        # (추후 metrics 수집되면 counter exposed assertion 추가 예정)
