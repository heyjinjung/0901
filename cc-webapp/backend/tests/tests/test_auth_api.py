import pytest
pytest.skip("Duplicate legacy auth API script (tests/tests) – skipped", allow_module_level=True)

"""(SKIPPED DUPLICATE)
원본: 절차형 requests 스크립트. 상위 tests/test_auth_api.py와 중복.
"""

import requests
import time
import json
from pprint import pprint

# 테스트 설정
BASE_URL = "http://localhost:8000"  # FastAPI 서버 주소
HEADERS = {"Content-Type": "application/json"}
AUTH_HEADERS = {}  # 인증 토큰이 추가될 예정

# 결과 저장용 변수
test_results = {
    "signup": False,
    "login": False,
    "token_refresh": False,
    "profile": False,
    "sessions": False,
    "logout": False
}

access_token = None
refresh_token = None
user_info = None

def print_section(title):
    """섹션 제목 출력"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_result(test_name, success, response=None):
    """테스트 결과 출력"""
    global test_results
    
    test_results[test_name] = success
    
    if success:
        print(f"✅ {test_name} 테스트 성공!")
    else:
        print(f"❌ {test_name} 테스트 실패!")
        
    if response:
        try:
            print(f"응답 코드: {response.status_code}")
            print("응답 데이터:")
            pprint(response.json())
        except:
            print(f"원본 응답: {response.text}")

# 1. 회원가입 테스트
def test_signup():
    print_section("1. 회원가입 테스트")
    
    # 테스트용 사용자 생성
    test_user = {
        "invite_code": "5858",  # 무제한 초대 코드
        "nickname": f"tester_{int(time.time())}"  # 고유한 닉네임
    }
    
    print(f"테스트 사용자: {test_user}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/register", 
            headers=HEADERS,
            json=test_user
        )
        
        if response.status_code == 200:
            global access_token, refresh_token, user_info
            data = response.json()
            
            # 토큰 저장
            access_token = data.get("access_token")
            refresh_token = data.get("refresh_token")
            user_info = {
                "user_id": data.get("user_id"),
                "nickname": data.get("nickname"),
                "cyber_tokens": data.get("cyber_tokens")
            }
            
            print_result("signup", True, response)
            return True
        else:
            print_result("signup", False, response)
            return False
    except Exception as e:
        print(f"회원가입 테스트 중 오류 발생: {e}")
        print_result("signup", False)
        return False

# 2. 로그인 테스트
def test_login():
    print_section("2. 로그인 테스트")
    
    if not user_info:
        print("사용자 정보가 없습니다. 회원가입 테스트가 먼저 성공해야 합니다.")
        print_result("login", False)
        return False
    
    try:
        # 가입한 사용자의 site_id로 로그인
        # 일반적으로 casino_user_타임스탬프 형식이므로 유추할 수 있음
        login_data = {
            "site_id": f"casino_user_{int(time.time())}"
        }
        
        print(f"로그인 시도: {login_data}")
        
        response = requests.post(
            f"{BASE_URL}/auth/login",
            headers=HEADERS,
            json=login_data
        )
        
        if response.status_code == 200:
            data = response.json()
            
            global access_token, refresh_token
            # 새 토큰 저장
            access_token = data.get("access_token")
            refresh_token = data.get("refresh_token")
            
            print_result("login", True, response)
            return True
        else:
            print_result("login", False, response)
            return False
    except Exception as e:
        print(f"로그인 테스트 중 오류 발생: {e}")
        print_result("login", False)
        return False

# 3. 인증 헤더 설정
def setup_auth_headers():
    global AUTH_HEADERS
    if access_token:
        AUTH_HEADERS = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        print("인증 헤더가 설정되었습니다.")
        return True
    else:
        print("액세스 토큰이 없습니다. 로그인 또는 회원가입이 필요합니다.")
        return False

# 4. 토큰 갱신 테스트
def test_token_refresh():
    print_section("3. 토큰 갱신 테스트")
    
    if not refresh_token:
        print("리프레시 토큰이 없습니다. 로그인 또는 회원가입이 필요합니다.")
        print_result("token_refresh", False)
        return False
    
    try:
        refresh_data = {
            "refresh_token": refresh_token
        }
        
        response = requests.post(
            f"{BASE_URL}/auth/refresh",
            headers=HEADERS,
            json=refresh_data
        )
        
        if response.status_code == 200:
            data = response.json()
            
            global access_token, refresh_token
            # 새 토큰 저장
            access_token = data.get("access_token")
            if data.get("refresh_token"):  # 새 리프레시 토큰이 있으면 업데이트
                refresh_token = data.get("refresh_token")
            
            # 인증 헤더 업데이트
            setup_auth_headers()
            
            print_result("token_refresh", True, response)
            return True
        else:
            print_result("token_refresh", False, response)
            return False
    except Exception as e:
        print(f"토큰 갱신 테스트 중 오류 발생: {e}")
        print_result("token_refresh", False)
        return False

# 5. 사용자 프로필 조회 테스트
def test_profile():
    print_section("4. 사용자 프로필 조회 테스트")
    
    if not setup_auth_headers():
        print_result("profile", False)
        return False
    
    try:
        response = requests.get(
            f"{BASE_URL}/auth/profile",
            headers=AUTH_HEADERS
        )
        
        if response.status_code == 200:
            print_result("profile", True, response)
            return True
        else:
            print_result("profile", False, response)
            return False
    except Exception as e:
        print(f"프로필 조회 테스트 중 오류 발생: {e}")
        print_result("profile", False)
        return False

# 6. 세션 목록 조회 테스트
def test_sessions():
    print_section("5. 세션 목록 조회 테스트")
    
    if not setup_auth_headers():
        print_result("sessions", False)
        return False
    
    try:
        response = requests.get(
            f"{BASE_URL}/auth/sessions",
            headers=AUTH_HEADERS
        )
        
        if response.status_code == 200:
            print_result("sessions", True, response)
            return True
        else:
            print_result("sessions", False, response)
            return False
    except Exception as e:
        print(f"세션 목록 조회 테스트 중 오류 발생: {e}")
        print_result("sessions", False)
        return False

# 7. 로그아웃 테스트
def test_logout():
    print_section("6. 로그아웃 테스트")
    
    if not setup_auth_headers():
        print_result("logout", False)
        return False
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/logout",
            headers=AUTH_HEADERS
        )
        
        if response.status_code == 200:
            print_result("logout", True, response)
            
            # 로그아웃 후 프로필 접근 시도 (실패해야 정상)
            print("\n로그아웃 후 프로필 접근 시도 (401 에러가 발생해야 정상):")
            try:
                profile_response = requests.get(
                    f"{BASE_URL}/auth/profile",
                    headers=AUTH_HEADERS
                )
                print(f"응답 코드: {profile_response.status_code}")
                if profile_response.status_code == 401:
                    print("✅ 정상적으로 인증이 거부되었습니다.")
                else:
                    print("⚠️ 로그아웃 후에도 인증이 유지됩니다. 확인이 필요합니다.")
            except Exception as e:
                print(f"로그아웃 후 프로필 접근 테스트 중 오류 발생: {e}")
            
            return True
        else:
            print_result("logout", False, response)
            return False
    except Exception as e:
        print(f"로그아웃 테스트 중 오류 발생: {e}")
        print_result("logout", False)
        return False

# 전체 테스트 실행
def run_all_tests():
    print_section("🧪 인증 시스템 테스트 시작")
    
    # 테스트 순서대로 실행
    signup_success = test_signup()
    
    if signup_success:
        setup_auth_headers()
        test_profile()
        test_sessions()
    else:
        print("회원가입 실패로 인해 나머지 테스트를 건너뜁니다.")
        return
    
    test_token_refresh()
    
    # 리프레시 후 인증이 필요한 요청 테스트
    test_profile()
    
    # 마지막으로 로그아웃 테스트
    test_logout()
    
    # 결과 요약
    print_section("📊 테스트 결과 요약")
    for test_name, success in test_results.items():
        status = "✅ 성공" if success else "❌ 실패"
        print(f"{test_name}: {status}")

# 테스트 실행
if __name__ == "__main__":
    run_all_tests()
