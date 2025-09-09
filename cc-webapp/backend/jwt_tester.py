import os
import sys
import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

# Base URL configuration
BASE_URL = "http://localhost:8000"  # Change if needed

# Make sure environment variables are set correctly
os.environ["JWT_SECRET_KEY"] = "secret_key_for_development_only"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["JWT_EXPIRE_MINUTES"] = "60"

def log(message: str, level: str = "INFO") -> None:
    """Simple logging function"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{level}] {timestamp} - {message}")

def print_separator(title: str = "") -> None:
    """Print a separator line with optional title"""
    width = 80
    if title:
        padding = (width - len(title) - 4) // 2
        print("=" * padding + f" {title} " + "=" * padding)
    else:
        print("=" * width)

def make_request(method: str, url: str, headers: Dict[str, str] = None, 
                json_data: Dict[str, Any] = None, 
                form_data: Dict[str, Any] = None,
                expected_status: int = 200) -> Tuple[Dict[str, Any], bool]:
    """Make an HTTP request and handle response"""
    full_url = f"{BASE_URL}{url}"
    log(f"Making {method} request to {full_url}")
    
    response = None
    try:
        if method.lower() == "get":
            response = requests.get(full_url, headers=headers)
        elif method.lower() == "post":
            if json_data:
                response = requests.post(full_url, headers=headers, json=json_data)
            elif form_data:
                response = requests.post(full_url, headers=headers, data=form_data)
            else:
                response = requests.post(full_url, headers=headers)
        else:
            log(f"Unsupported method: {method}", "ERROR")
            return {}, False
            
        log(f"Response status: {response.status_code}")
        
        # Try to parse response as JSON
        try:
            result = response.json()
            log(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
        except Exception as e:
            log(f"Failed to parse response as JSON: {str(e)}", "ERROR")
            log(f"Response text: {response.text}")
            result = {"text": response.text}
            
        # Check if status code matches expected
        if response.status_code != expected_status:
            log(f"Expected status {expected_status}, got {response.status_code}", "ERROR")
            return result, False
            
        return result, True
            
    except Exception as e:
        log(f"Request failed: {str(e)}", "ERROR")
        return {}, False

def create_test_user() -> Tuple[Dict[str, Any], bool]:
    """Create a test user through the test endpoint"""
    print_separator("Creating Test User")
    
    user_data = {
        "site_id": f"test_user{int(time.time()) % 1000}",
        "password": "testpassword",
        "nickname": f"TestUser{int(time.time()) % 1000}"
    }
    
    log(f"Creating test user: {user_data['site_id']}")
    result, success = make_request("POST", "/test/simple-register", json_data=user_data)
    
    if success:
        log(f"Test user created: {result.get('user')}", "SUCCESS")
        return user_data, True
    else:
        log("Failed to create test user", "ERROR")
        return {}, False

def create_auth_token(payload: Dict[str, Any]) -> str:
    """Create a JWT token using PyJWT or jose"""
    try:
        # Try importing both libraries
        import jwt
        print("Using PyJWT library")
        
        # Add standard claims
        payload["exp"] = datetime.utcnow() + timedelta(minutes=60)
        payload["iat"] = datetime.utcnow()
        payload["jti"] = f"auth-token-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        payload["type"] = "access"
        
        # Create token
        token = jwt.encode(
            payload, 
            os.environ.get("JWT_SECRET_KEY", "secret_key_for_development_only"),
            algorithm=os.environ.get("JWT_ALGORITHM", "HS256")
        )
        
        # PyJWT might return bytes in some versions
        if isinstance(token, bytes):
            token = token.decode('utf-8')
            
        return token
        
    except ImportError:
        try:
            from jose import jwt as jose_jwt
            print("Using jose-jwt library")
            
            # Add standard claims
            payload["exp"] = datetime.utcnow() + timedelta(minutes=60)
            payload["iat"] = datetime.utcnow()
            payload["jti"] = f"auth-token-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            payload["type"] = "access"
            
            # Create token
            token = jose_jwt.encode(
                payload, 
                os.environ.get("JWT_SECRET_KEY", "secret_key_for_development_only"),
                algorithm=os.environ.get("JWT_ALGORITHM", "HS256")
            )
            
            return token
        except ImportError:
            log("Neither PyJWT nor jose-jwt is installed", "ERROR")
            return ""

def check_protected_endpoint(token: str) -> Tuple[Dict[str, Any], bool]:
    """Check access to a protected endpoint with token"""
    print_separator("Testing Protected Endpoint")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    log("Testing access to protected endpoint /api/users/me")
    result, success = make_request("GET", "/api/users/me", headers=headers)
    
    if success:
        log("Successfully accessed protected endpoint", "SUCCESS")
        return result, True
    else:
        log("Failed to access protected endpoint", "ERROR")
        return result, False

def print_environment_variables():
    """Print JWT-related environment variables"""
    print_separator("JWT Environment Variables")
    
    env_vars = {
        "JWT_SECRET_KEY": os.environ.get("JWT_SECRET_KEY", "Not set"),
        "JWT_ALGORITHM": os.environ.get("JWT_ALGORITHM", "Not set"),
        "JWT_EXPIRE_MINUTES": os.environ.get("JWT_EXPIRE_MINUTES", "Not set")
    }
    
    for key, value in env_vars.items():
        log(f"{key}: {value}")
    
    print_separator()

def test_api_key():
    """Test with known API key"""
    print_separator("Testing With Known API Key")
    
    # Make sure environment variables are set correctly
    os.environ["JWT_SECRET_KEY"] = "secret_key_for_development_only"
    os.environ["JWT_ALGORITHM"] = "HS256"
    os.environ["JWT_EXPIRE_MINUTES"] = "60"
    
    # Import necessary modules
    try:
        from datetime import timedelta
        import jwt
        
        log("Using PyJWT library")
        
        # Create payload
        payload = {
            "sub": "test_user123",
            "user_id": 123,
            "exp": int((datetime.utcnow() + timedelta(minutes=60)).timestamp()),
            "iat": int(datetime.utcnow().timestamp()),
            "jti": f"auth-token-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "type": "access"
        }
        
        # Create token
        token = jwt.encode(
            payload, 
            os.environ.get("JWT_SECRET_KEY", "secret_key_for_development_only"),
            algorithm=os.environ.get("JWT_ALGORITHM", "HS256")
        )
        
        # PyJWT might return bytes in some versions
        if isinstance(token, bytes):
            token = token.decode('utf-8')
            
        log(f"Generated token: {token}")
        
        # Save token to file
        with open("/app/token.json", "w") as f:
            json.dump({"token": token}, f)
            
        log("Token saved to /app/token.json", "SUCCESS")
        
        # Test with the token
        check_protected_endpoint(token)
        
    except ImportError:
        try:
            from jose import jwt as jose_jwt
            from datetime import timedelta
            
            log("Using jose-jwt library")
            
            # Create payload
            payload = {
                "sub": "test_user123",
                "user_id": 123,
                "exp": int((datetime.utcnow() + timedelta(minutes=60)).timestamp()),
                "iat": int(datetime.utcnow().timestamp()),
                "jti": f"auth-token-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "type": "access"
            }
            
            # Create token
            token = jose_jwt.encode(
                payload, 
                os.environ.get("JWT_SECRET_KEY", "secret_key_for_development_only"),
                algorithm=os.environ.get("JWT_ALGORITHM", "HS256")
            )
            
            log(f"Generated token: {token}")
            
            # Save token to file
            with open("/app/token.json", "w") as f:
                json.dump({"token": token}, f)
                
            log("Token saved to /app/token.json", "SUCCESS")
            
            # Test with the token
            check_protected_endpoint(token)
            
        except ImportError:
            log("Neither PyJWT nor jose-jwt is installed", "ERROR")

if __name__ == "__main__":
    # Print environment variables
    print_environment_variables()
    
    # Test with known API key
    test_api_key()
