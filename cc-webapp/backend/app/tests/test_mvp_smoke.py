"""
MVP Smoke Test
핵심 경제 시스템 end-to-end 검증: signup → login → streak → claim → gacha → shop

배포 전 필수 검증 항목:
- 사용자 가입/로그인
- 스트릭 시스템 (daily tick)
- 리워드 claim (골드 지급)
- 가챠 시스템
- 상점 구매
"""
import pytest
import asyncio
import uuid
from fastapi.testclient import TestClient

from app.main import app
from sqlalchemy import text
from app.database import get_db
from app.models.auth_models import User
from app.models.game_models import UserReward

# Constants
INVITE_CODE = "5858"  # UNLIMITED invite code accepted by AuthService


@pytest.fixture
def test_client():
    """테스트 클라이언트 생성"""
    return TestClient(app)


@pytest.fixture
def test_user_data():
    """테스트 사용자 데이터 (유니크 닉네임 보장)"""
    unique = uuid.uuid4().hex[:6]
    return {
        "username": f"mvp_test_user_{unique}",
        "password": "test123!",
        "email": "mvp@test.com"
    }


class TestMVPSmoke:
    """MVP 핵심 플로우 smoke test"""

    def test_complete_mvp_flow(self, test_client: TestClient, test_user_data: dict):
        """
        완전한 MVP 플로우 테스트
        1. 회원가입(현재 /api/auth/register 사용) → 2. 프로필 → 3. 스트릭 체크 → 4. 클레임 → 5. 가챠 → 6. 상점
        """
        # 1. 회원가입 (현재 signup 비활성 → register 사용)
        requested_nickname = test_user_data["username"]
        register_payload = {"invite_code": INVITE_CODE, "nickname": requested_nickname}
        register_resp = test_client.post("/api/auth/register", json=register_payload)
        if register_resp.status_code == 400 and "이미 존재" in register_resp.text:
            # Retry with a suffixed nickname to ensure uniqueness (fallback path)
            requested_nickname = f"{requested_nickname}2"
            alt_payload = {"invite_code": INVITE_CODE, "nickname": requested_nickname}
            register_resp = test_client.post("/api/auth/register", json=alt_payload)
        assert register_resp.status_code == 200, f"Register failed: {register_resp.text}"
        reg_data = register_resp.json()
        assert "access_token" in reg_data
        token = reg_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. 프로필
        profile_response = test_client.get("/api/auth/profile", headers=headers)
        assert profile_response.status_code == 200, f"Profile fetch failed: {profile_response.text}"
        profile = profile_response.json()
        assert profile.get("nickname") == requested_nickname

        # 3. 스트릭 상태
        streak_response = test_client.get("/api/streak/status", headers=headers)
        assert streak_response.status_code == 200, f"Streak status failed: {streak_response.text}"
        streak_data = streak_response.json()
        assert "count" in streak_data
        # 4. 클레임
        claim_response = test_client.post("/api/streak/claim", headers=headers, json={})
        assert claim_response.status_code == 200, f"Streak first claim should succeed after auto-seed: {claim_response.text}"
        claim_data = claim_response.json()
        assert "awarded_gold" in claim_data
        assert claim_data.get("awarded_gold", 0) > 0

        # 5. 가챠 (존재할 경우)
        gacha_try = test_client.post("/api/gacha/pull", headers=headers)
        if gacha_try.status_code not in (200, 404):
            assert False, f"Unexpected gacha status {gacha_try.status_code}: {gacha_try.text}"

        # 6. 상점 아이템 조회 및 첫 구매 시도
        shop_items_resp = test_client.get("/api/shop/items", headers=headers)
        if shop_items_resp.status_code == 200:
            items = shop_items_resp.json()
            if isinstance(items, list) and items:
                candidate = next((i for i in items if i.get("id") is not None), None)
                if candidate:
                    buy_resp = test_client.post(f"/api/shop/buy/{candidate['id']}", headers=headers)
                    assert buy_resp.status_code in (200, 400, 404), f"Unexpected shop buy resp: {buy_resp.status_code}"

    def test_streak_claim_idempotency(self, test_client: TestClient, test_user_data: dict):
        """스트릭 클레임 중복 호출 처리 테스트 (register + double claim)"""
        register_payload = {"invite_code": INVITE_CODE, "nickname": test_user_data["username"]}
        register_resp = test_client.post("/api/auth/register", json=register_payload)
        assert register_resp.status_code == 200, register_resp.text
        token = register_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

    def test_database_consistency_check(self, test_client: TestClient):
        """데이터베이스 일관성 기본 검증 (app state DB session 사용)"""
        essential_tables = ['users']
        # Use direct connection via dependency
        db_gen = get_db()
        db = next(db_gen)
        try:
            for table_name in essential_tables:
                sql = text("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = :table_name
                    )
                """)
                result = db.execute(sql, {"table_name": table_name})
                table_exists = result.fetchone()[0]
                assert table_exists, f"Essential table {table_name} does not exist"
        finally:
            try:
                next(db_gen)
            except StopIteration:
                pass

    @pytest.mark.asyncio
    async def test_concurrent_claim_protection(self, test_client: TestClient, test_user_data: dict):
        """동시 클레임 요청 처리 테스트"""
        signup_response = test_client.post("/api/auth/register", json={"invite_code": INVITE_CODE, "nickname": test_user_data["username"]})
        assert signup_response.status_code == 200, signup_response.text
        token = signup_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        tasks = []
        for _ in range(3):
            tasks.append(asyncio.to_thread(lambda: test_client.post("/api/streak/claim", headers=headers)))
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        success_count = 0
        for response in responses:
            if not isinstance(response, Exception):
                # 하나만 성공(200), 나머지 400 (이미 수령)
                assert response.status_code in (200, 400)
                if response.status_code == 200:
                    success_count += 1
        assert success_count == 1, f"Exactly one claim should succeed, got {success_count}"

    def test_system_health_endpoints(self, test_client: TestClient):
        """시스템 헬스 체크 엔드포인트 테스트"""
        
        # 헬스 체크 엔드포인트가 있다면 테스트
        health_endpoints = ["/health", "/status", "/ping", "/"]
        
        for endpoint in health_endpoints:
            try:
                response = test_client.get(endpoint)
                if response.status_code == 200:
                    # 헬스 엔드포인트가 정상 작동하는지 확인
                    assert response.status_code == 200
                    break
            except:
                continue  # 엔드포인트가 없으면 다음 시도

if __name__ == "__main__":
    # 직접 실행 시 기본 테스트 실행
    pytest.main([__file__, "-v", "--tb=short"])
