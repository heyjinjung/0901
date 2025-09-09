#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Game API Tester
==============
Tests the game API endpoints to verify responses match expected schemas
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
AUTH_ENDPOINT = f"{BASE_URL}/api/auth/login"
GAMES_LIST_ENDPOINT = f"{BASE_URL}/api/games"
SLOT_SPIN_ENDPOINT = f"{BASE_URL}/api/games/slot/spin"
RPS_PLAY_ENDPOINT = f"{BASE_URL}/api/games/rps/play"
GACHA_PULL_ENDPOINT = f"{BASE_URL}/api/games/gacha/pull"
CRASH_BET_ENDPOINT = f"{BASE_URL}/api/games/crash/bet"

# Credentials
USERNAME = "test_user"
PASSWORD = "password123"

# Colors for terminal output
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

def print_header(message):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{message.center(60)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.RESET}\n")

def print_result(endpoint, status_code, message, details=None):
    """Print test result with color-coding"""
    if 200 <= status_code < 300:
        status = f"{Colors.GREEN}✓ PASS{Colors.RESET}"
    elif status_code == 400:
        status = f"{Colors.YELLOW}⚠ VALIDATION ERROR{Colors.RESET}"
    else:
        status = f"{Colors.RED}✗ FAIL{Colors.RESET}"
    
    print(f"{status} | {endpoint} | Status: {status_code} | {message}")
    
    if details:
        print(f"  Details: {details}")

def get_auth_token():
    """Get authentication token"""
    form_data = {
        "username": USERNAME,
        "password": PASSWORD
    }
    
    try:
        response = requests.post(AUTH_ENDPOINT, data=form_data)
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"{Colors.RED}Authentication failed: {response.text}{Colors.RESET}")
            return None
    except Exception as e:
        print(f"{Colors.RED}Authentication error: {str(e)}{Colors.RESET}")
        return None

def test_games_list(auth_token):
    """Test games list endpoint"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.get(GAMES_LIST_ENDPOINT, headers=headers)
        status_code = response.status_code
        
        if status_code == 200:
            data = response.json()
            message = f"Retrieved {len(data)} games"
            details = None
            
            # Verify each game has required fields
            if data and isinstance(data, list):
                missing_fields = []
                for game in data:
                    required_fields = ["id", "name", "description", "type", "image_url"]
                    for field in required_fields:
                        if field not in game:
                            missing_fields.append(field)
                
                if missing_fields:
                    message = "Missing required fields in response"
                    details = ", ".join(set(missing_fields))
        else:
            message = f"Request failed: {response.text}"
            details = None
            
        print_result("Games List", status_code, message, details)
        return status_code == 200
        
    except Exception as e:
        print_result("Games List", 500, f"Exception: {str(e)}")
        return False

def test_slot_spin(auth_token):
    """Test slot spin endpoint"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    payload = {
        "bet_amount": 10,
        "lines": 1
    }
    
    try:
        response = requests.post(SLOT_SPIN_ENDPOINT, headers=headers, json=payload)
        status_code = response.status_code
        
        if status_code == 200:
            data = response.json()
            message = f"Spin result: Win amount {data.get('win_amount', 'N/A')}"
            
            # Verify response has required fields
            required_fields = ["success", "reels", "win_amount", "is_jackpot", "message", "balance"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                message = "Missing required fields in response"
                details = ", ".join(missing_fields)
            else:
                details = None
        else:
            message = f"Request failed: {response.text}"
            details = None
            
        print_result("Slot Spin", status_code, message, details)
        return status_code == 200
        
    except Exception as e:
        print_result("Slot Spin", 500, f"Exception: {str(e)}")
        return False

def test_rps_play(auth_token):
    """Test rock-paper-scissors endpoint"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    payload = {
        "choice": "rock",
        "bet_amount": 10
    }
    
    try:
        response = requests.post(RPS_PLAY_ENDPOINT, headers=headers, json=payload)
        status_code = response.status_code
        
        if status_code == 200:
            data = response.json()
            message = f"Result: {data.get('result', 'N/A')}, Win amount: {data.get('win_amount', 'N/A')}"
            
            # Verify response has required fields
            required_fields = ["success", "player_choice", "computer_choice", "result", "win_amount", "message", "balance"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                message = "Missing required fields in response"
                details = ", ".join(missing_fields)
            else:
                details = None
        else:
            message = f"Request failed: {response.text}"
            details = None
            
        print_result("RPS Play", status_code, message, details)
        return status_code == 200
        
    except Exception as e:
        print_result("RPS Play", 500, f"Exception: {str(e)}")
        return False

def test_gacha_pull(auth_token):
    """Test gacha pull endpoint"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    payload = {
        "gacha_id": "standard",
        "pull_count": 1,
        "use_premium_currency": False
    }
    
    try:
        response = requests.post(GACHA_PULL_ENDPOINT, headers=headers, json=payload)
        status_code = response.status_code
        
        if status_code == 200:
            data = response.json()
            message = f"Pulled {len(data.get('items', []))} items, Rare items: {data.get('rare_item_count', 'N/A')}"
            
            # Verify response has required fields
            required_fields = ["success", "items", "message", "currency_balance"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                message = "Missing required fields in response"
                details = ", ".join(missing_fields)
            else:
                details = None
        else:
            message = f"Request failed: {response.text}"
            details = None
            
        print_result("Gacha Pull", status_code, message, details)
        return status_code == 200
        
    except Exception as e:
        print_result("Gacha Pull", 500, f"Exception: {str(e)}")
        return False

def test_crash_bet(auth_token):
    """Test crash bet endpoint"""
    headers = {"Authorization": f"Bearer {auth_token}"}
    payload = {
        "bet_amount": 10,
        "auto_cashout_multiplier": 1.5
    }
    
    try:
        response = requests.post(CRASH_BET_ENDPOINT, headers=headers, json=payload)
        status_code = response.status_code
        
        if status_code == 200:
            data = response.json()
            message = f"Bet amount: {data.get('bet_amount', 'N/A')}, Potential win: {data.get('potential_win', 'N/A')}"
            
            # Verify response has required fields
            required_fields = ["success", "game_id", "bet_amount", "potential_win", "message", "balance"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                message = "Missing required fields in response"
                details = ", ".join(missing_fields)
            else:
                details = None
        else:
            message = f"Request failed: {response.text}"
            details = None
            
        print_result("Crash Bet", status_code, message, details)
        return status_code == 200
        
    except Exception as e:
        print_result("Crash Bet", 500, f"Exception: {str(e)}")
        return False

def main():
    """Main test function"""
    print_header("Casino-Club F2P Game API Test")
    print(f"Testing against {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get auth token
    print("\nAuthenticating...")
    auth_token = get_auth_token()
    if not auth_token:
        print(f"{Colors.RED}Failed to get auth token. Exiting.{Colors.RESET}")
        sys.exit(1)
    
    print(f"{Colors.GREEN}Authentication successful{Colors.RESET}")
    
    # Run tests
    print("\nRunning API tests:")
    results = []
    
    results.append(test_games_list(auth_token))
    results.append(test_slot_spin(auth_token))
    results.append(test_rps_play(auth_token))
    results.append(test_gacha_pull(auth_token))
    results.append(test_crash_bet(auth_token))
    
    # Summary
    success_count = results.count(True)
    total_count = len(results)
    
    print("\n" + "-" * 60)
    print(f"Test Summary: {success_count}/{total_count} tests passed")
    
    if success_count == total_count:
        print(f"{Colors.GREEN}All tests passed!{Colors.RESET}")
        return 0
    else:
        print(f"{Colors.YELLOW}Some tests failed. Check output for details.{Colors.RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
