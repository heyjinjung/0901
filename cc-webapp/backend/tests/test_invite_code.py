"""
초대코드 유효성 검증 API 테스트
- 유효한 초대코드: 6969, 6974, 2560
- 테스트 케이스:
  1. 유효한 코드 검증
  2. 존재하지 않는 코드 검증
  3. 만료된 코드 검증
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import os
import sys

from app.main import app
from app.database import Base
from app.dependencies import get_db
from app.models import InviteCode

# Test valid invite code
def test_valid_invite_code(client):
    # Test valid code: 6969
    response = client.get("/api/invite/validate/6969")
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.text}")
    if response.status_code != 200:
        print(f"Response headers: {response.headers}")
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["detail"] == "유효한 초대코드입니다."
    assert data["is_special"] is True

# Test nonexistent invite code
def test_nonexistent_invite_code(client):
    # Test nonexistent code: 9999
    response = client.get("/api/invite/validate/9999")
    assert response.status_code == 200  # Still 200, but with valid=False
    data = response.json()
    assert data["valid"] is False
    assert "존재하지 않습니다" in data["detail"]

# Test used invite code
def test_used_invite_code(client, db_session):
    # Test used code: 1234
    used_code = InviteCode(code="1234", is_used=True, used_at=datetime.utcnow())
    db_session.add(used_code)
    db_session.commit()
    response = client.get("/api/invite/validate/1234")
    assert response.status_code == 200  # Still 200, but with valid=False
    data = response.json()
    assert data["valid"] is False
    assert "이미 사용" in data["detail"]

# Test expired invite code
def test_expired_invite_code(client, db_session):
    # Test expired code: 5678
    expired_code = InviteCode(code="5678", is_used=False, expires_at=datetime.utcnow() - timedelta(days=1))
    db_session.add(expired_code)
    db_session.commit()
    response = client.get("/api/invite/validate/5678")
    assert response.status_code == 200  # Still 200, but with valid=False
    data = response.json()
    assert data["valid"] is False
    assert "만료" in data["detail"]

# Test max uses exceeded
def test_max_uses_exceeded(client, db_session):
    # Test max uses exceeded: 9876
    max_uses_code = InviteCode(code="9876", is_used=False, max_uses=3, use_count=3)
    db_session.add(max_uses_code)
    db_session.commit()
    response = client.get("/api/invite/validate/9876")
    assert response.status_code == 200  # Still 200, but with valid=False
    data = response.json()
    assert data["valid"] is False
    assert "사용 횟수" in data["detail"]

# Test multi-use code
def test_multi_use_code(client, db_session):
    # Test multi-use code: 6969 (max_uses=5)
    valid_codes = [
        InviteCode(code="6969", is_used=False, expires_at=datetime.utcnow() + timedelta(days=30), max_uses=5, use_count=0),
        InviteCode(code="6974", is_used=False, expires_at=datetime.utcnow() + timedelta(days=30), max_uses=1, use_count=0),
        InviteCode(code="2560", is_used=False, expires_at=datetime.utcnow() + timedelta(days=30), max_uses=None, use_count=0),
    ]
    for code in valid_codes:
        db_session.add(code)
    db_session.commit()
    response = client.get("/api/invite/validate/6969")
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["max_uses"] == 5
    assert data["use_count"] == 0

# Run tests if executed directly
if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
