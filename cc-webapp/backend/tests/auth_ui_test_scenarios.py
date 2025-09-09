"""
Casino-Club F2P - 인증 시스템 UI 테스트 시나리오
=============================================================================
프론트엔드에서 인증 흐름 테스트하기 위한 시나리오 및 체크리스트
"""

# 회원가입 UI 테스트
SIGNUP_TEST_SCENARIOS = [
    {
        "name": "정상 회원가입",
        "steps": [
            "1. 회원가입 페이지 접속",
            "2. 초대코드 '5858' 입력",
            "3. 닉네임 입력",
            "4. 회원가입 버튼 클릭"
        ],
        "expected": "회원가입 성공 및 메인 페이지로 리다이렉트"
    },
    {
        "name": "유효하지 않은 초대코드",
        "steps": [
            "1. 회원가입 페이지 접속",
            "2. 유효하지 않은 초대코드 입력",
            "3. 닉네임 입력",
            "4. 회원가입 버튼 클릭"
        ],
        "expected": "초대코드 유효성 오류 메시지 표시"
    },
    {
        "name": "중복된 닉네임",
        "steps": [
            "1. 회원가입 페이지 접속",
            "2. 초대코드 '5858' 입력",
            "3. 이미 존재하는 닉네임 입력",
            "4. 회원가입 버튼 클릭"
        ],
        "expected": "닉네임 중복 오류 메시지 표시"
    }
]

# 로그인 UI 테스트
LOGIN_TEST_SCENARIOS = [
    {
        "name": "정상 로그인",
        "steps": [
            "1. 로그인 페이지 접속",
            "2. 유효한 site_id 입력",
            "3. 로그인 버튼 클릭"
        ],
        "expected": "로그인 성공 및 메인 페이지로 리다이렉트"
    },
    {
        "name": "존재하지 않는 사용자",
        "steps": [
            "1. 로그인 페이지 접속",
            "2. 존재하지 않는 site_id 입력",
            "3. 로그인 버튼 클릭"
        ],
        "expected": "사용자를 찾을 수 없음 오류 메시지 표시"
    },
    {
        "name": "과도한 로그인 시도",
        "steps": [
            "1. 로그인 페이지 접속",
            "2. 잘못된 site_id로 로그인 5회 이상 시도"
        ],
        "expected": "로그인 시도 제한 메시지 표시 및 일정 시간 로그인 버튼 비활성화"
    }
]

# 토큰 관리 UI 테스트
TOKEN_MANAGEMENT_TEST_SCENARIOS = [
    {
        "name": "토큰 저장 확인",
        "steps": [
            "1. 로그인 성공 후",
            "2. 브라우저 개발자 도구 열기",
            "3. Application 탭에서 Local Storage 확인"
        ],
        "expected": "access_token과 refresh_token이 Local Storage에 저장되어 있음"
    },
    {
        "name": "토큰 자동 갱신 확인",
        "steps": [
            "1. 로그인 성공 후",
            "2. 액세스 토큰 만료 시간 단축 설정 (테스트 목적)",
            "3. 일정 시간 경과 후 보호된 리소스에 접근"
        ],
        "expected": "백그라운드에서 토큰 자동 갱신 및 요청 성공"
    },
    {
        "name": "리프레시 토큰 만료 처리",
        "steps": [
            "1. 리프레시 토큰 만료 시간 단축 설정 (테스트 목적)",
            "2. 액세스 토큰 만료 후 리프레시 토큰도 만료되도록 설정",
            "3. 일정 시간 경과 후 보호된 리소스에 접근"
        ],
        "expected": "로그인 페이지로 리다이렉트"
    }
]

# 로그아웃 UI 테스트
LOGOUT_TEST_SCENARIOS = [
    {
        "name": "정상 로그아웃",
        "steps": [
            "1. 로그인 상태에서",
            "2. 로그아웃 버튼 클릭"
        ],
        "expected": "로그아웃 성공 및 로그인 페이지로 리다이렉트, 토큰 제거됨"
    },
    {
        "name": "로그아웃 후 보호된 페이지 접근",
        "steps": [
            "1. 로그아웃 후",
            "2. 보호된 페이지 URL 직접 접근 시도"
        ],
        "expected": "로그인 페이지로 리다이렉트"
    }
]

# 세션 관리 UI 테스트
SESSION_MANAGEMENT_TEST_SCENARIOS = [
    {
        "name": "세션 목록 확인",
        "steps": [
            "1. 로그인 후 세션 관리 페이지 접속",
        ],
        "expected": "현재 활성 세션 목록 표시, 현재 세션 표시됨"
    },
    {
        "name": "다른 기기에서 로그인",
        "steps": [
            "1. 기존 기기에서 로그인 유지",
            "2. 다른 기기(또는 브라우저)에서 동일 계정으로 로그인",
            "3. 첫 번째 기기에서 세션 목록 새로고침"
        ],
        "expected": "두 개의 활성 세션이 목록에 표시됨"
    },
    {
        "name": "특정 세션 종료",
        "steps": [
            "1. 여러 기기에서 로그인 후",
            "2. 세션 관리 페이지에서 특정 세션 옆 '종료' 버튼 클릭"
        ],
        "expected": "선택한 세션만 종료되고 목록에서 제거됨"
    }
]

# 오류 처리 UI 테스트
ERROR_HANDLING_TEST_SCENARIOS = [
    {
        "name": "네트워크 오류",
        "steps": [
            "1. 로그인 상태에서",
            "2. 네트워크 연결 끊기",
            "3. 보호된 리소스에 접근 시도"
        ],
        "expected": "네트워크 오류 메시지 표시 및 재시도 옵션 제공"
    },
    {
        "name": "서버 오류 (500)",
        "steps": [
            "1. 서버에서 500 오류 발생 시나리오 설정",
            "2. API 요청 시도"
        ],
        "expected": "사용자 친화적인 오류 메시지 표시 및 문제 해결 안내"
    },
    {
        "name": "토큰 변조 시도",
        "steps": [
            "1. 로컬 스토리지의 액세스 토큰 수동 변조",
            "2. 보호된 리소스에 접근 시도"
        ],
        "expected": "인증 오류 메시지 표시 및 로그인 페이지로 리다이렉트"
    }
]

# 전체 테스트 시나리오 모음
ALL_TEST_SCENARIOS = {
    "회원가입": SIGNUP_TEST_SCENARIOS,
    "로그인": LOGIN_TEST_SCENARIOS,
    "토큰 관리": TOKEN_MANAGEMENT_TEST_SCENARIOS,
    "로그아웃": LOGOUT_TEST_SCENARIOS,
    "세션 관리": SESSION_MANAGEMENT_TEST_SCENARIOS,
    "오류 처리": ERROR_HANDLING_TEST_SCENARIOS
}

def print_test_scenarios():
    """모든 테스트 시나리오 출력"""
    for category, scenarios in ALL_TEST_SCENARIOS.items():
        print(f"\n=== {category} 테스트 시나리오 ===\n")
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"{i}. {scenario['name']}")
            print("   단계:")
            for step in scenario['steps']:
                print(f"   - {step}")
            print(f"   예상 결과: {scenario['expected']}")
            print()

if __name__ == "__main__":
    print_test_scenarios()
