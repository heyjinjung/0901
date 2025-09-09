"""컨테이너 내부 API 테스트"""
import requests
import json

try:
    response = requests.post(
        "http://localhost:8000/auth/signup",
        json={
            "site_id": "containertest",
            "nickname": "컨테이너테스터",
            "phone_number": "01099887766",
            "invite_code": "5858",
            "password": "container123"
        },
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
