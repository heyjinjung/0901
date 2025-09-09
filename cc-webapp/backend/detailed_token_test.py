from jose import jwt, JWTError
import datetime
import requests
import json
import os

def generate_test_token():
    """Generate a test token for user ID 1"""
    # Get JWT configuration from environment variables or use defaults
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "casino-club-secret-key-2024")
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

def test_decode_token():
    """Test decoding a token with various secret keys"""
    token = generate_test_token()
    
    # Try different secret keys
    secret_keys = [
        "casino-club-secret-key-2024",
        "secret_key_for_development_only",
        "secret-key-for-testing"
    ]
    
    for secret_key in secret_keys:
        try:
            decoded = jwt.decode(token, secret_key, algorithms=["HS256"])
            print(f"Success with key: {secret_key}")
            print(f"Decoded: {decoded}")
        except JWTError as e:
            print(f"Failed with key: {secret_key} - {e}")

# Run the tests
print("== JWT TEST ==")
test_decode_token()
