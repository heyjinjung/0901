import requests
import os
import jwt
from datetime import datetime, timedelta
import json

def test_full_flow():
    """Test the full authentication flow directly in the container"""
    
    BASE_URL = "http://localhost:8000"
    
    # 1. Create a test user
    username = f"test_user_{int(datetime.now().timestamp())}"
    password = "password123"
    
    register_data = {
        "site_id": username,
        "password": password,
        "nickname": username
    }
    
    print(f"1. Creating test user: {username}")
    register_response = requests.post(f"{BASE_URL}/test/simple-register", json=register_data)
    print(f"Register status: {register_response.status_code}")
    print(f"Register response: {register_response.text}")
    
    # 2. Generate token manually using the correct secret key
    print("\n2. Generating token manually")
    secret_key = os.environ.get("JWT_SECRET_KEY", "your-secret-key-here")
    algorithm = "HS256"
    
    payload = {
        "sub": username,
        "user_id": 123,
        "jti": f"auth-token-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "exp": int((datetime.utcnow() + timedelta(minutes=30)).timestamp()),
        "iat": int(datetime.utcnow().timestamp()),
        "type": "access"
    }
    
    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    print(f"Secret key used: {secret_key}")
    print(f"Generated token: {token[:30]}...")
    
    # Save token to file
    with open("token.json", "w") as f:
        json.dump({"token": token}, f)
    
    # 3. Test protected endpoints
    headers = {"Authorization": f"Bearer {token}"}
    
    endpoints = [
        f"{BASE_URL}/auth/profile",
        f"{BASE_URL}/api/users/profile"
    ]
    
    for url in endpoints:
        print(f"\n3. Testing endpoint: {url}")
        try:
            response = requests.get(url, headers=headers)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code != 200:
                print(f" Access failed: {response.text}")
            else:
                print(f" Access successful")
        except Exception as e:
            print(f" Error: {e}")

test_full_flow()
