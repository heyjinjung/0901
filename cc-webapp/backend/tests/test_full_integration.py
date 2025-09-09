"""
Casino-Club F2P 전체 API 통합 테스트
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_full_api_integration():
    """전체 API 엔드포인트 통합 테스트"""
    
    print("🎰 Casino-Club F2P API Integration Test")
    print("=" * 50)
    
    # 1. 회원가입 테스트
    print("\n1️⃣ Testing User Registration...")
    register_data = {
        "invite_code": "5858",
        "site_id": f"test_user_{int(datetime.now().timestamp())}",
        "nickname": "테스트유저",
        "phone_number": "010-1234-5678",
        "password": "test123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json() if response.status_code == 200 else response.text}")
    
    if response.status_code == 200:
        print("✅ Registration successful")
        user_data = response.json()
        access_token = user_data.get("access_token")
    else:
        print(f"❌ Registration failed: {response.text}")
        return
    
    # 헤더에 토큰 추가
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # 2. 사용자 정보 조회
    print("\n2️⃣ Testing User Profile...")
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json() if response.status_code == 200 else response.text}")
    
    if response.status_code == 200:
        print("✅ Profile retrieved successfully")
        user_info = response.json()
        user_id = user_info.get("id")
    else:
        print(f"❌ Profile retrieval failed: {response.text}")
    
    # 3. 퀴즈 시스템 테스트
    print("\n3️⃣ Testing Quiz System...")
    response = requests.get(f"{BASE_URL}/api/quiz/categories", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json() if response.status_code == 200 else response.text}")
    
    if response.status_code == 200:
        print("✅ Quiz categories retrieved")
    else:
        print(f"❌ Quiz categories failed: {response.text}")
    
    # 4. AI 추천 테스트
    print("\n4️⃣ Testing AI Recommendations...")
    response = requests.get(f"{BASE_URL}/api/ai/recommendations", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json() if response.status_code == 200 else response.text}")
    
    if response.status_code == 200:
        print("✅ AI recommendations retrieved")
    else:
        print(f"❌ AI recommendations failed: {response.text}")
    
    # 5. 채팅 시스템 테스트
    print("\n5️⃣ Testing Chat System...")
    chat_data = {
        "name": "테스트 채팅방",
        "room_type": "public"
    }
    response = requests.post(f"{BASE_URL}/api/chat/rooms", json=chat_data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json() if response.status_code == 200 else response.text}")
    
    if response.status_code == 200:
        print("✅ Chat room created")
    else:
        print(f"❌ Chat room creation failed: {response.text}")
    
    print("\n" + "=" * 50)
    print("🎯 API Integration Test Complete!")

if __name__ == "__main__":
    test_full_api_integration()
