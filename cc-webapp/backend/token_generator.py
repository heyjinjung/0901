from jose import jwt
import datetime
import os
import json

def generate_token():
    """Generate a token using environment variables"""
    # Get the JWT_SECRET_KEY from environment or use the default
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "secret_key_for_development_only")
    ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    
    print(f"Using JWT_SECRET_KEY: {SECRET_KEY}")
    print(f"Using JWT_ALGORITHM: {ALGORITHM}")
    
    # Create payload with necessary fields based on our findings
    payload = {
        "sub": "test_user789",  # Use our test user's site_id
        "user_id": 10,  # Assuming a user ID (will be verified later)
        "jti": "auth-token-" + datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S"),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
        "iat": datetime.datetime.utcnow(),
        "type": "access"
    }
    
    # Create token
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    print(f"Generated Token: {token}")
    
    # Save token to a file for later use
    with open("/app/token.json", "w") as f:
        json.dump({"token": token}, f)
    
    return token

# Run the token generator
if __name__ == "__main__":
    token = generate_token()
    print("\nTo use this token in your tests:")
    print(f"Authorization: Bearer {token}")
