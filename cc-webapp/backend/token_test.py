from jose import jwt, JWTError
import os
from datetime import datetime, timedelta
import json

def test_token_validation():
    """Test token validation directly in the backend container"""
    
    # Get JWT configuration
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
    ALGORITHM = "HS256"
    
    print(f"Using SECRET_KEY: {SECRET_KEY}")
    print(f"Using ALGORITHM: {ALGORITHM}")
    
    # Create a test token
    username = "test_direct_validation"
    user_id = 42
    
    payload = {
        "sub": username,
        "user_id": user_id,
        "exp": int((datetime.utcnow() + timedelta(minutes=30)).timestamp()),
        "iat": int(datetime.utcnow().timestamp()),
        "jti": f"test-token-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "type": "access"
    }
    
    # Encode token
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    print(f"Generated token: {token[:30]}...")
    
    # Try to decode and validate token
    try:
        decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Successfully validated token!")
        print(f"Decoded payload: {json.dumps(decoded_payload, indent=2)}")
        
        # Check if required fields are present
        site_id = decoded_payload.get("sub")
        user_id = decoded_payload.get("user_id")
        
        if site_id is None or user_id is None:
            print("ERROR: Missing required fields in payload")
        else:
            print(f"Token is fully valid with site_id: {site_id}, user_id: {user_id}")
        
    except JWTError as e:
        print(f"ERROR: Token validation failed: {e}")

test_token_validation()
