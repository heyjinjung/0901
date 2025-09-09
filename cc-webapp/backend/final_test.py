from jose import jwt
import requests
import os
from datetime import datetime, timedelta
import time
import json

def test_api_with_token():
    """Test API access with generated token"""
    
    # JWT configuration
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "secret_key_for_development_only")
    ALGORITHM = "HS256"
    
    print(f"Using SECRET_KEY: {SECRET_KEY}")
    print(f"Using ALGORITHM: {ALGORITHM}")
    
    # Create a test token
    username = "test_user789"  # Use an existing test user from the database
    user_id = 10  # Use actual ID from database
    
    payload = {
        "sub": username,
        "user_id": user_id,
        "jti": f"auth-token-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "exp": int((datetime.utcnow() + timedelta(minutes=30)).timestamp()),
        "iat": int(datetime.utcnow().timestamp()),
        "type": "access"
    }
    
    # Encode token
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    print(f"Generated token: {token[:30]}...")
    
    # Save token to file for debugging
    with open("token.json", "w") as f:
        json.dump({"token": token}, f)
    
    print("Token saved to token.json")
    
    # Test API endpoints
    headers = {"Authorization": f"Bearer {token}"}
    endpoints = [
        "http://localhost:8000/auth/profile",
        "http://localhost:8000/api/users/profile"
    ]
    
    for url in endpoints:
        print(f"\nTesting endpoint: {url}")
        try:
            response = requests.get(url, headers=headers)
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
        except Exception as e:
            print(f"Error: {e}")

test_api_with_token()
