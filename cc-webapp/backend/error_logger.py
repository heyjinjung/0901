import requests
import os
import json
import traceback
from datetime import datetime, timedelta
from jose import jwt

def test_with_logging():
    """Test API with detailed error logging"""
    
    # Create token
    SECRET_KEY = "secret_key_for_development_only"
    ALGORITHM = "HS256"
    
    # Use existing test user
    username = "test_user789"
    user_id = 10
    
    payload = {
        "sub": username,
        "user_id": user_id,
        "jti": f"auth-token-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "exp": int((datetime.utcnow() + timedelta(minutes=30)).timestamp()),
        "iat": int(datetime.utcnow().timestamp()),
        "type": "access"
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    print(f"Generated token: {token[:30]}...")
    
    # Save token
    with open("token.json", "w") as f:
        json.dump({"token": token}, f)
    
    # Try API
    headers = {"Authorization": f"Bearer {token}"}
    url = "http://localhost:8000/api/users/profile"
    
    try:
        print(f"\nSending request to {url}")
        print(f"With headers: {headers}")
        response = requests.get(url, headers=headers)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")
        traceback.print_exc()

test_with_logging()

# Test if token is correctly formed
print("\nVerifying token format:")
try:
    with open("token.json", "r") as f:
        data = json.load(f)
        token = data["token"]
    
    # Print token for inspection
    print(f"Token from file: {token}")
    
    # Check if token parts are correctly formatted
    parts = token.split(".")
    if len(parts) == 3:
        print(" Token has correct format (header.payload.signature)")
    else:
        print(f" Token has incorrect format: {len(parts)} parts instead of 3")
        
except Exception as e:
    print(f"Error reading token: {e}")
