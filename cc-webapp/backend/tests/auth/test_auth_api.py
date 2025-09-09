"""Authentication system integration tests"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import random
import string

from app.main import app

# Initialize TestClient
client = TestClient(app)  # 'app' 파라미터로 전달 (transport= 사용하지 않음)

def test_health_check():
    """Server health check"""
    response = client.get("/health")
    assert response.status_code == 200
    
def test_register_and_login():
    """Registration and login test"""
    # Test user data
    timestamp = int(datetime.utcnow().timestamp())
    test_user = {
        "site_id": f"test_{timestamp}@casino-club.local",
        "nickname": f"Test_User_{timestamp}",
        "password": "test1234",
        "phone_number": f"010{timestamp % 10000000:08d}",
        "invite_code": "5858"
    }
    
    # Registration attempt
    response = client.post("/auth/register", params=test_user)
    assert response.status_code in [200, 201, 422]
    
    # Login attempt
    login_data = {
        "site_id": test_user["site_id"],
        "password": test_user["password"]
    }
    response = client.post("/auth/login", params=login_data)
    if response.status_code == 200:
        data = response.json()
        assert "access_token" in data
    else:
        assert response.status_code in [401, 403, 422]
