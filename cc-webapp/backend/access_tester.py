import requests
import json
import os

def test_protected_endpoints():
    """Test accessing protected endpoints with our token"""
    # Load the token from our file
    try:
        with open("/app/token.json", "r") as f:
            data = json.load(f)
            token = data["token"]
    except Exception as e:
        print(f"Error loading token: {e}")
        return
    
    # Setup headers with our token
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # List of endpoints to test
    endpoints = [
        "/auth/profile",
        "/api/users/info",
        "/api/users/profile"
    ]
    
    print("\n=== Testing Protected Endpoints ===\n")
    
    # Test each endpoint
    for endpoint in endpoints:
        url = f"http://localhost:8000{endpoint}"
        print(f"\nTesting: {url}")
        try:
            response = requests.get(url, headers=headers)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            
            if response.status_code != 200:
                print("Failed to access endpoint")
        except Exception as e:
            print(f"Error: {e}")

# Run the tests
test_protected_endpoints()
