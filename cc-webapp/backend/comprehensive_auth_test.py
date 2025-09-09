import os
import sys
import requests
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

# Base URL configuration
BASE_URL = "http://localhost:8000"  # Change if needed

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

def login_with_credentials(site_id: str, password: str) -> Tuple[Dict[str, Any], bool]:
    """Login with user credentials and get access token"""
    print_separator("User Login")
    
    # Form data for login
    form_data = {
        "username": site_id,
        "password": password
    }
    
    log(f"Logging in with credentials: {site_id}")
    result, success = make_request("POST", "/api/auth/login", form_data=form_data)
    
    if success and "access_token" in result:
        log(f"Login successful, token received", "SUCCESS")
        # Save token to file for future use
        with open("token.json", "w") as f:
            json.dump({"token": result["access_token"]}, f)
        log(f"Token saved to token.json", "SUCCESS")
        return result, True
    else:
        log("Login failed or token not received", "ERROR")
        return result, False

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

def test_auth_flow():
    """Run complete authentication test flow"""
    print_separator("AUTHENTICATION TEST FLOW")
    
    # Step 1: Create test user
    user_data, success1 = create_test_user()
    if not success1:
        log("Test failed at step 1: Creating test user", "ERROR")
        return False
    
    # Step 2: Login with credentials
    login_result, success2 = login_with_credentials(user_data["site_id"], user_data["password"])
    if not success2:
        log("Test failed at step 2: Logging in with credentials", "ERROR")
        return False
    
    # Step 3: Test protected endpoint access
    token = login_result.get("access_token", "")
    protected_result, success3 = check_protected_endpoint(token)
    if not success3:
        log("Test failed at step 3: Accessing protected endpoint", "ERROR")
        return False
    
    # All steps successful
    log("Authentication flow test completed successfully! ", "SUCCESS")
    return True

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

def debug_token_on_server():
    """Debug token verification on server"""
    print_separator("Debugging Token on Server")
    
    # Check if token file exists
    if not os.path.exists("token.json"):
        log("Token file not found. Please run login first.", "ERROR")
        return
        
    try:
        with open("token.json", "r") as f:
            data = json.load(f)
            token = data.get("token")
            
        if not token:
            log("No token found in file", "ERROR")
            return
            
        log(f"Token: {token}")
        
        # Copy token to server for debugging
        with open("/app/token.json", "w") as f:
            json.dump({"token": token}, f)
            
        log("Token copied to server for debugging", "SUCCESS")
        
    except Exception as e:
        log(f"Error debugging token: {str(e)}", "ERROR")

if __name__ == "__main__":
    # Print environment variables
    print_environment_variables()
    
    # Run the authentication flow test
    test_auth_flow()
    
    # Debug token on server
    debug_token_on_server()
