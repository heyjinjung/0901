def test_token_headers():
    import jwt
    import json
    import requests
    
    # Use existing token.json if available
    try:
        with open("token.json", "r") as f:
            token_data = json.load(f)
            token = token_data["token"]
            print(f"Using token from file: {token[:30]}...")
    except:
        # Generate a new token
        from datetime import datetime, timedelta
        
        # Create payload
        payload = {
            "sub": "test_user789",
            "user_id": 10,
            "jti": f"auth-token-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "exp": int((datetime.utcnow() + timedelta(minutes=30)).timestamp()),
            "iat": int(datetime.utcnow().timestamp()),
            "type": "access"
        }
        
        # Create token
        secret_key = "your-secret-key-here"
        token = jwt.encode(payload, secret_key, algorithm="HS256")
        print(f"Generated new token: {token[:30]}...")
    
    # Test different header formats
    header_formats = [
        {"Authorization": f"Bearer {token}"},
        {"Authorization": f"bearer {token}"},
        {"Authorization": token},
    ]
    
    url = "http://localhost:8000/api/users/profile"
    
    for i, headers in enumerate(header_formats):
        print(f"\nTest {i+1}: Using headers: {headers}")
        try:
            response = requests.get(url, headers=headers)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

# Run the test
test_token_headers()
