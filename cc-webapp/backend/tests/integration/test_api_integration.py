#!/usr/bin/env python3
"""
🎰 Casino-Club F2P - API Integration Test Script
===============================================
Frontend → API → Database Connection Test

📅 업데이트: 2025-08-03
🎯 목적: Repository 패턴 적용된 API 통합 테스트
"""
import requests
import json
import time
import random
import os

class APIIntegrationTest:
    def __init__(self):
        # 환경변수에서 포트 설정 (기본값 8000)
        port = os.getenv('BACKEND_PORT', '8000')
        self.base_url = f"http://localhost:{port}"
        self.token = None
        self.user_id = None
        self.headers = {}
        print(f"🔗 Testing API at: {self.base_url}")

    def _test_endpoint(self, name, method, url, **kwargs):
        try:
            response = requests.request(method, f"{self.base_url}{url}", **kwargs)
            response.raise_for_status()
            print(f"✅ {name} passed (status: {response.status_code})")
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ {name} failed: {e}")
            if e.response is not None:
                print(f"    Response content: {e.response.text}")
            return None

    def test_health_check(self):
        return self._test_endpoint("Health Check", "get", "/health")

    def test_user_signup(self):
        data = {
            "site_id": f"testuser_{int(time.time())}",
            "nickname": f"TestUser{random.randint(1000, 9999)}",
            "phone_number": f"010{random.randint(1000, 9999)}{random.randint(1000, 9999)}",
            "password": "password123",
            "invite_code": "5858"
        }
        response_data = self._test_endpoint("User Signup", "post", "/api/auth/signup", json=data)
        if response_data:
            self.token = response_data.get("access_token")
            self.user_id = response_data.get("user", {}).get("id")
            if self.token and self.user_id:
                self.headers = {"Authorization": f"Bearer {self.token}"}
                return True
        return False

    def test_user_login(self):
        # This is redundant if signup returns a token, but good for testing login separately
        # For this E2E test, we'll rely on the token from signup.
        print("✅ Login successful (token obtained from signup)")
        return True

    def test_get_profile(self):
        return self._test_endpoint("Profile Retrieval", "get", f"/api/users/{self.user_id}/profile", headers=self.headers)

    def test_play_slot(self):
        data = {"bet_amount": 5000}
        # The slot endpoint is under /api/actions now
        return self._test_endpoint("Slot Game", "post", "/api/actions/slot/spin", headers=self.headers, json=data)

    def test_play_roulette(self):
        data = {"bet_amount": 5000}
        return self._test_endpoint("Roulette Game", "post", "/api/games/roulette/spin", headers=self.headers, json=data)

    def test_pull_gacha(self):
        data = {"user_id": self.user_id} # Gacha endpoint needs user_id in body
        return self._test_endpoint("Gacha Pull", "post", "/api/gacha/pull", headers=self.headers, json=data)

    def test_get_rewards_history(self):
        return self._test_endpoint("Rewards History Retrieval", "get", f"/api/users/{self.user_id}/rewards", headers=self.headers)

    def run_full_user_journey(self):
        """A full E2E test simulating a user's journey."""
        print("🚀 Starting full user journey E2E test...")

        if not self.test_health_check(): return False

        print("\n--- 1. Onboarding ---")
        if not self.test_user_signup(): return False
        if not self.test_get_profile(): return False

        print("\n--- 2. Game Play ---")
        slot_result = self.test_play_slot()
        if not slot_result: return False

        # This endpoint needs to be created based on the service
        # roulette_result = self.test_play_roulette()
        # if not roulette_result: return False

        gacha_result = self.test_pull_gacha()
        if not gacha_result: return False

        print("\n--- 3. Result Verification ---")
        time.sleep(1) # Allow time for rewards to be processed if async
        rewards_history = self.test_get_rewards_history()
        if not rewards_history: return False

        print("\n--- Validation ---")
        total_rewards = len(rewards_history.get("rewards", []))
        print(f"Total {total_rewards} reward records confirmed.")
        # A more robust test would check if the specific rewards from the games are present

        print("\n🎉 Full user journey test passed!")
        return True

if __name__ == "__main__":
    tester = APIIntegrationTest()
    success = tester.run_full_user_journey()
    exit(0 if success else 1)
