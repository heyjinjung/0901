from jose import jwt
import datetime
import requests
import json
import os

def generate_test_token():
    """Generate a test token for user ID 1"""
    # Get JWT configuration from environment variables or use defaults
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "secret_key_for_development_only")
    ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    
    print(f"Using SECRET_KEY: {SECRET_KEY}")
    print(f"Using ALGORITHM: {ALGORITHM}")
    
    # Create payload
    payload = {
        "sub": "1",  # User ID 1
        "jti": "12345678-1234-5678-1234-567812345678",  # JWT ID for blacklist checking
        "session_id": "session-12345",  # Session ID
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
        "iat": datetime.datetime.utcnow(),
        "type": "access"
    }
    
    # Create token
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    print(f"Generated Token: {token}")
    return token

def test_profile_endpoint():
    """Test the /auth/profile endpoint"""
    token = generate_test_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Try to access the profile endpoint
        response = requests.get("http://localhost:8000/auth/profile", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2) if response.status_code == 200 else response.text}")
    except Exception as e:
        print(f"Error: {e}")

# Run the test
print("== PROFILE ENDPOINT TEST ==")
test_profile_endpoint()
