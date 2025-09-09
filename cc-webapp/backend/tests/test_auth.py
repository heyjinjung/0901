"""
초대코드 기반 인증 시스템 테스트
RFM 세그먼테이션 유지 + 인증 단순화
"""
import pytest
from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db
from app.models import Base, User, InviteCode, UserSegment
from app.services.auth_service import AuthService

# 테스트용 인메모리 DB
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    del app.dependency_overrides[get_db]

class TestAuthAPI:
    """초대코드 기반 인증 API 테스트"""
    
    def test_register_success(self, client):
        """정상 가입 테스트"""
        response = client.post(
            "/api/auth/signup",
            json={
                "invite_code": "5858",
                "nickname": "테스트유저",
                "site_id": "testuser123",
                "phone_number": "010-1234-5678",
                "password": "testpass"
            }
        )
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        assert response.status_code == 200
        data = response.json()
        assert data["user"]["nickname"] == "테스트유저"
    
    def test_register_invalid_invite_code(self, client):
        """잘못된 초대코드로 가입 테스트"""
        response = client.post(
            "/api/auth/signup",
            json={
                "invite_code": "WRONG1",
                "nickname": "테스트유저",
                "site_id": "wronguser",
                "phone_number": "010-5555-6666",
                "password": "testpass123"
            }
        )
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        assert response.status_code == 400
        assert "유효하지 않은 초대코드" in response.json()["detail"]
    
    def test_register_duplicate_nickname(self, client, db_session):
        """중복 닉네임 가입 테스트"""
        # 첫 번째 사용자 등록
        auth_service = AuthService()
        hashed_password = auth_service.get_password_hash("password")
        user = User(
            site_id="test_site_duplicate",
            nickname="중복닉네임",
            phone_number="010-1234-5678",
            hashed_password=hashed_password,
            invite_code="5858"
        )
        db_session.add(user)
        db_session.commit()
        
        # 중복 닉네임으로 가입 시도
        response = client.post(
            "/api/auth/signup",
            json={
                "invite_code": "5858",
                "nickname": "중복닉네임",
                "site_id": "dupuser",
                "phone_number": "010-7777-8888",
                "password": "testpass123"
            }
        )
        print(f"Response status: {response.status_code}")
        print(f"Response content: {response.text}")
        assert response.status_code == 400
        assert "이미 존재하는 닉네임" in response.json()["detail"]

class TestRFMSegmentation:
    """RFM 세그먼테이션 유지 테스트"""
    
    def test_user_segment_relationship(self, db_session):
        """User-UserSegment 관계 테스트"""
        # 사용자 생성
        auth_service = AuthService()
        hashed_password = auth_service.get_password_hash("password")
        user = User(
            site_id="test_site_segment",
            nickname="세그먼트테스트",
            phone_number="010-8888-8888",
            hashed_password=hashed_password,
            invite_code="5858"
        )
        db_session.add(user)
        db_session.flush()
        
        # 세그먼트 생성
        segment = UserSegment(
            user_id=user.id,
            rfm_group="Medium",
            risk_profile="Medium"
        )
        db_session.add(segment)
        db_session.commit()
        
        # 관계 확인
        db_session.refresh(user)
        assert user.segment is not None
        assert user.segment.rfm_group == "Medium"
        assert user.segment.risk_profile == "Medium"
    
    def test_segment_levels(self):
        """세그먼트 레벨 매핑 테스트"""
        segment_levels = {
            "Low": 1,
            "Medium": 2,
            "Whale": 3
        }
        
        # 다양한 세그먼트 레벨 테스트
        assert segment_levels["Low"] < segment_levels["Medium"]
        assert segment_levels["Medium"] < segment_levels["Whale"]
