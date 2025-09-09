from jose import jwt
import datetime

def test_jwt():
    """Test JWT functionality"""
    # JWT configuration
    SECRET_KEY = "secret_key_for_testing"
    ALGORITHM = "HS256"
    
    # Create payload
    payload = {
        "sub": "test_user",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
        "iat": datetime.datetime.utcnow()
    }
    
    # Create token
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    print(f"Encoded Token: {token}")
    
    # Decode token
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    print(f"Decoded Token: {decoded}")
    
    print("JWT test successful!")

# Run the test
test_jwt()
