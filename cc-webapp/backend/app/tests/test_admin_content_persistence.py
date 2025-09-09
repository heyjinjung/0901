from datetime import datetime, timedelta
from fastapi.testclient import TestClient
import pytest

from app.routers.admin_content import require_admin
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def _override_admin_dependency():
    class _AdminUser:
        is_admin = True
    app.dependency_overrides[require_admin] = lambda: _AdminUser()
    yield
    app.dependency_overrides.pop(require_admin, None)


def test_event_crud(client: TestClient):
    # 진단: 라우트 매칭 여부 사전 검증 및 요청 path 로깅
    target_path = "/api/admin/content/events"
    # 1) 동일 app 인스턴스 내 라우트 존재 여부 assert
    route_paths = [getattr(r, 'path', None) for r in app.routes]
    assert target_path in route_paths, f"{target_path} not found in app.routes: {route_paths[:20]} ..."
    # 2) router 내부 중복/그 shadow 구분 (APIRouter 포함)
    admin_content_routes = [r.path for r in app.router.routes if getattr(r, 'path', '').startswith('/api/admin/content/events')]
    assert target_path in admin_content_routes, f"{target_path} not in root router compiled list: {admin_content_routes}"
    # 3) 1회만 진단 미들웨어 주입 (idempotent)
    flag_key = "_admin_content_diag_added"
    if not getattr(app.state, flag_key, False):
        @app.middleware("http")
        async def _diag_mw(request, call_next):  # type: ignore
            if request.url.path.startswith("/api/admin/content"):
                # 매칭 전 path 기록
                print(f"[DIAG admin_content] inbound path={request.url.path}")
            response = await call_next(request)
            if request.url.path.startswith("/api/admin/content"):
                print(f"[DIAG admin_content] outbound status={response.status_code}")
            return response
        app.state._admin_content_diag_added = True
    start = datetime.utcnow()
    end = start + timedelta(days=1)
    payload = {
        "name": "Test Event",
        "start_at": start.isoformat(),
        "end_at": end.isoformat(),
        "reward_scheme": {"gold": 100},
    }
    r = client.post("/api/admin/content/events", json=payload)
    if r.status_code not in (200, 201):
        print("DEBUG event create status", r.status_code, "body:", r.text)
    assert r.status_code in (200, 201), r.text
    data = r.json()
    eid = data["id"]

    r = client.get(f"/api/admin/content/events/{eid}")
    assert r.status_code == 200

    r = client.post(f"/api/admin/content/events/{eid}/deactivate")
    assert r.status_code == 200
    r = client.post(f"/api/admin/content/events/{eid}/activate")
    assert r.status_code == 200

    r = client.delete(f"/api/admin/content/events/{eid}")
    assert r.status_code == 200


def test_mission_template_crud(client: TestClient):
    payload = {
        "title": "Daily Spin",
        "mission_type": "daily",
        "target": 5,
        "reward": {"gold": 50},
    }
    r = client.post("/api/admin/content/missions/templates", json=payload)
    assert r.status_code in (200, 201), r.text
    mid = r.json()["id"]

    r = client.get("/api/admin/content/missions/templates")
    assert r.status_code == 200

    r = client.put(f"/api/admin/content/missions/templates/{mid}", json={"target": 10})
    assert r.status_code == 200

    r = client.delete(f"/api/admin/content/missions/templates/{mid}")
    assert r.status_code == 200


def test_reward_catalog_crud(client: TestClient):
    payload = {"code": "REWARD_PACK_1", "reward_type": "gold", "amount": 100, "metadata": {}}
    r = client.post("/api/admin/content/rewards/catalog", json=payload)
    assert r.status_code in (200, 201)
    rid = r.json()["id"]

    r = client.get("/api/admin/content/rewards/catalog")
    assert r.status_code == 200

    r = client.put(f"/api/admin/content/rewards/catalog/{rid}", json={"amount": 200})
    assert r.status_code == 200

    r = client.post(f"/api/admin/content/rewards/catalog/{rid}/deactivate")
    assert r.status_code == 200
    r = client.post(f"/api/admin/content/rewards/catalog/{rid}/activate")
    assert r.status_code == 200

    r = client.delete(f"/api/admin/content/rewards/catalog/{rid}")
    assert r.status_code == 200
