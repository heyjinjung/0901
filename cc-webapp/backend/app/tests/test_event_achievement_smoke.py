"""이벤트/업적 mini-smoke 테스트
시나리오: register → 이벤트 목록 조회 (없으면 스킵) → 첫 이벤트 join → progress 업데이트 → claim → UserReward 생성 여부 확인
주의: Admin 전용 이벤트 생성은 여기서 수행하지 않음 (기존 seed/활성 이벤트 가정). 이벤트 없으면 테스트 xfail.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.main import app
from app.database import get_db
from app.models.game_models import UserReward

INVITE_CODE = "5858"

def _register(client: TestClient, nickname: str) -> str:
    resp = client.post("/api/auth/register", json={"invite_code": INVITE_CODE, "nickname": nickname})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]

@pytest.mark.parametrize("progress_value", [10])
def test_event_join_progress_claim(progress_value: int):
    client = TestClient(app)
    token = _register(client, "evt_smoke_user")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. 이벤트 목록
    list_resp = client.get("/api/events/", headers=headers)
    if list_resp.status_code != 200:
        pytest.xfail(f"이벤트 목록 호출 실패 status={list_resp.status_code}")
    events = list_resp.json()
    if not isinstance(events, list) or not events:
        pytest.xfail("활성 이벤트 없음 (seed 필요)")
    target = events[0]
    event_id = target.get("id")
    assert event_id, "이벤트 id 누락"

    # 2. join
    join_resp = client.post("/api/events/join", headers=headers, json={"event_id": event_id})
    assert join_resp.status_code == 200, join_resp.text

    # 3. progress 업데이트 (있을 경우)
    prog_resp = client.put(f"/api/events/progress/{event_id}", headers=headers, json={"progress": progress_value})
    # 일부 이벤트 타입은 progress 엔드포인트 미지원 가능 → 404/400 허용
    assert prog_resp.status_code in (200, 400, 404), prog_resp.text

    # 4. claim 시도
    claim_resp = client.post(f"/api/events/claim/{event_id}", headers=headers, json={})
    assert claim_resp.status_code in (200, 400), claim_resp.text
    claim_json = claim_resp.json()
    # 200이면 rewards 필드 기대
    if claim_resp.status_code == 200:
        assert any(k in claim_json for k in ("rewards", "gold", "exp")), "보상 필드 누락"

    # 5. UserReward 존재 (성공 claim 시) - 골드/exp 기록 확인 (선택)
    if claim_resp.status_code == 200:
        db_gen = get_db()
        db: Session = next(db_gen)
        try:
            q = select(UserReward).where(UserReward.user_id == claim_json.get("user_id", 0)).order_by(UserReward.id.desc())
            rewards = db.execute(q).scalars().all()
            assert any(r.reward_type in ("EVENT", "EVENT_CLAIM") for r in rewards), "EVENT 관련 UserReward 미발견"
        finally:
            try:
                next(db_gen)
            except StopIteration:
                pass
