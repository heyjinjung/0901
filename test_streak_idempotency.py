#!/usr/bin/env python3
"""
Simple test to verify streak reward idempotency
"""
import requests
import json

def test_streak_idempotency():
    # First, we need to get an auth token (simulate login)
    base_url = "http://localhost:8000"
    
    # Use the test user from the app or create one
    test_user = {
        "username": "testuser",
        "password": "password123"
    }
    
    # Try to login to get a token
    login_response = requests.post(f"{base_url}/api/auth/login", 
                                   json=test_user,
                                   headers={"Content-Type": "application/json"})
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return False
    
    token_data = login_response.json()
    access_token = token_data.get("access_token")
    
    if not access_token:
        print("No access token received")
        return False
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # First try: Tick to ensure we have a streak
    tick_response = requests.post(f"{base_url}/api/streak/tick",
                                  json={"action_type": "DAILY_LOGIN"},
                                  headers=headers)
    print(f"Tick response: {tick_response.status_code}")
    if tick_response.status_code == 200:
        print(f"Tick data: {tick_response.json()}")
    
    # First claim attempt
    print("\n=== First claim attempt ===")
    claim1 = requests.post(f"{base_url}/api/streak/claim",
                          json={"action_type": "DAILY_LOGIN"},
                          headers=headers)
    print(f"First claim status: {claim1.status_code}")
    print(f"First claim response: {claim1.text}")
    
    # Second claim attempt (should be rejected or return same result)
    print("\n=== Second claim attempt (should be idempotent) ===")
    claim2 = requests.post(f"{base_url}/api/streak/claim",
                          json={"action_type": "DAILY_LOGIN"},
                          headers=headers)
    print(f"Second claim status: {claim2.status_code}")
    print(f"Second claim response: {claim2.text}")
    
    # Third claim attempt
    print("\n=== Third claim attempt ===")
    claim3 = requests.post(f"{base_url}/api/streak/claim",
                          json={"action_type": "DAILY_LOGIN"},
                          headers=headers)
    print(f"Third claim status: {claim3.status_code}")
    print(f"Third claim response: {claim3.text}")
    
    # Check if the second and third attempts were properly handled
    if claim1.status_code == 200:
        if claim2.status_code == 400:
            print("\n✅ SUCCESS: Second claim was properly rejected!")
            return True
        elif claim2.status_code == 200:
            # Could be idempotent response
            claim1_data = claim1.json()
            claim2_data = claim2.json()
            if (claim1_data.get('awarded_gold') == claim2_data.get('awarded_gold') and 
                claim1_data.get('awarded_xp') == claim2_data.get('awarded_xp')):
                print("\n✅ SUCCESS: Second claim returned same idempotent result!")
                return True
            else:
                print(f"\n❌ FAILURE: Second claim returned different rewards!")
                print(f"First: {claim1_data}")
                print(f"Second: {claim2_data}")
                return False
    else:
        print(f"\n⚠️ First claim failed with status {claim1.status_code}")
        return False
    
    return False

if __name__ == "__main__":
    print("Testing streak reward idempotency...")
    success = test_streak_idempotency()
    if success:
        print("\n🎉 Test PASSED: Idempotency is working correctly!")
    else:
        print("\n💥 Test FAILED: Idempotency issues detected!")
