import jwt
import json
import requests
from datetime import datetime, timedelta

def test_with_proper_token():
    """Test with a properly encoded token"""
    
    # Create payload
    payload = {
        "sub": "test_user789",
        "user_id": 10,
        "jti": f"auth-token-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "exp": int((datetime.utcnow() + timedelta(minutes=30)).timestamp()),
        "iat": int(datetime.utcnow().timestamp()),
        "type": "access"
    }
    
    # Generate token
    secret_key = "your-secret-key-here"
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    
    # Convert token to string if it's bytes
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    
    print(f"Generated token (type {type(token)}): {token[:30]}...")
    
    # Test endpoint
    url = "http://localhost:8000/api/users/profile"
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\nTesting {url} with headers: {headers}")
    response = requests.get(url, headers=headers)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Save working token for reference
    with open("working_token.json", "w") as f:
        json.dump({"token": token, "headers": {"Authorization": f"Bearer {token}"}}, f, indent=2)

# Run the test
test_with_proper_token()
