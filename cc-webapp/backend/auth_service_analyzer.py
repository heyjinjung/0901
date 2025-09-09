import os
import jwt
from jose import jwt as jose_jwt
import json
import datetime

def analyze_auth_service():
    """Analyze the current auth_service implementation and configuration"""
    # Print environment variables
    print("\n=== Environment Variables ===\n")
    env_vars = {
        "JWT_SECRET_KEY": os.getenv("JWT_SECRET_KEY", "secret_key_for_development_only"),
        "JWT_ALGORITHM": os.getenv("JWT_ALGORITHM", "HS256"),
        "JWT_EXPIRE_MINUTES": os.getenv("JWT_EXPIRE_MINUTES", "60")
    }
    
    for key, value in env_vars.items():
        print(f"{key}: {value}")
    
    # Load our token
    try:
        with open("/app/token.json", "r") as f:
            data = json.load(f)
            token = data["token"]
            
        # Print token details
        print("\n=== Token Details ===\n")
        print(f"Token: {token}")
        
        # Decode token with PyJWT (without verification)
        decoded_jwt = jwt.decode(token, options={"verify_signature": False})
        print(f"\nDecoded token (PyJWT, no verification): {json.dumps(decoded_jwt, indent=2)}")
        
        # Decode token with PyJWT (with verification)
        try:
            decoded_jwt_verified = jwt.decode(
                token, 
                env_vars["JWT_SECRET_KEY"], 
                algorithms=[env_vars["JWT_ALGORITHM"]]
            )
            print(f"\nDecoded token (PyJWT, verified): {json.dumps(decoded_jwt_verified, indent=2)}")
        except Exception as e:
            print(f"\nPyJWT Verification failed: {e}")
        
        # Decode token with jose-jwt (without verification)
        decoded_jose = jose_jwt.decode(token, options={"verify_signature": False})
        print(f"\nDecoded token (jose-jwt, no verification): {json.dumps(decoded_jose, indent=2)}")
        
        # Decode token with jose-jwt (with verification)
        try:
            decoded_jose_verified = jose_jwt.decode(
                token, 
                env_vars["JWT_SECRET_KEY"], 
                algorithms=[env_vars["JWT_ALGORITHM"]]
            )
            print(f"\nDecoded token (jose-jwt, verified): {json.dumps(decoded_jose_verified, indent=2)}")
        except Exception as e:
            print(f"\njose-jwt Verification failed: {e}")
            
    except Exception as e:
        print(f"Error analyzing token: {e}")
    
    # Create a test token with both libraries
    print("\n=== Creating Test Tokens ===\n")
    
    payload = {
        "sub": "test_user",
        "user_id": 123,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
        "iat": datetime.datetime.utcnow()
    }
    
    # Create token with PyJWT
    pyjwt_token = jwt.encode(payload, env_vars["JWT_SECRET_KEY"], algorithm=env_vars["JWT_ALGORITHM"])
    print(f"PyJWT token: {pyjwt_token}")
    
    # Create token with jose-jwt
    jose_token = jose_jwt.encode(payload, env_vars["JWT_SECRET_KEY"], algorithm=env_vars["JWT_ALGORITHM"])
    print(f"jose-jwt token: {jose_token}")
    
    # Check if the tokens are compatible
    print(f"\nTokens are identical: {pyjwt_token == jose_token}")
    
    # Try to verify the PyJWT token with jose-jwt
    try:
        jose_jwt.decode(pyjwt_token, env_vars["JWT_SECRET_KEY"], algorithms=[env_vars["JWT_ALGORITHM"]])
        print("PyJWT token can be verified by jose-jwt")
    except Exception as e:
        print(f"PyJWT token verification with jose-jwt failed: {e}")
    
    # Try to verify the jose-jwt token with PyJWT
    try:
        jwt.decode(jose_token, env_vars["JWT_SECRET_KEY"], algorithms=[env_vars["JWT_ALGORITHM"]])
        print("jose-jwt token can be verified by PyJWT")
    except Exception as e:
        print(f"jose-jwt token verification with PyJWT failed: {e}")

# Run the analysis
analyze_auth_service()
