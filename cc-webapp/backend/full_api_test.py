#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Casino-Club F2P 전체 API 테스트 스크립트
========================================
모든 주요 API 엔드포인트를 빠르게 테스트
"""

import requests
import json
import time
from typing import Optional, Dict, Any

# colorama는 개발 편의용이며 테스트 환경에서 누락될 수 있으므로 안전 가드
try:
    from colorama import init, Fore, Style  # type: ignore
    init()
except Exception:  # pragma: no cover - optional dependency
    class _Dummy:
        RESET_ALL = ""
    class _F:
        RED = GREEN = YELLOW = CYAN = MAGENTA = ""
    Fore = _F()  # type: ignore
    Style = _Dummy()  # type: ignore
    def init():
        return None

# Colorama 초기화
init()

BASE_URL = "http://localhost:8000"

class APITester:
    def __init__(self):
        self.access_token: Optional[str] = None
        self.user_id: Optional[int] = None
        self.test_results = []
        
    def print_header(self, text):
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}🔍 {text}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}\n")
    
    def print_success(self, text):
        print(f"{Fore.GREEN}✅ {text}{Style.RESET_ALL}")
        self.test_results.append(("SUCCESS", text))
    
    def print_error(self, text):
        print(f"{Fore.RED}❌ {text}{Style.RESET_ALL}")
        self.test_results.append(("ERROR", text))
    
    def print_warning(self, text):
        print(f"{Fore.YELLOW}⚠️ {text}{Style.RESET_ALL}")
        self.test_results.append(("WARNING", text))
    
    def test_health(self):
        """서버 상태 확인"""
        self.print_header("서버 상태 확인")
        try:
            response = requests.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                self.print_success("서버가 정상 작동 중입니다")
                return True
            else:
                self.print_error(f"서버 응답 오류: {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"서버 연결 실패: {str(e)}")
            return False
    
    def test_registration(self):
        """회원가입 테스트"""
        self.print_header("회원가입 테스트")
        
        # 고유한 사용자 정보 생성
        timestamp = int(time.time())
        test_data = {
            "invite_code": "5858",
            "nickname": f"test_user_{timestamp}",
            "site_id": f"test_{timestamp}@casino-club.local",
            "phone_number": f"010{timestamp % 100000000:08d}"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/auth/register",
                params=test_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.access_token = data["access_token"]
                    self.print_success(f"회원가입 성공: {test_data['site_id']}")
                    return True
                else:
                    self.print_error("토큰이 반환되지 않았습니다")
            else:
                self.print_error(f"회원가입 실패: {response.status_code}")
                if response.text:
                    print(f"  응답: {response.text}")
        except Exception as e:
            self.print_error(f"회원가입 요청 오류: {str(e)}")
        
        return False
    
    def test_login(self):
        """로그인 테스트"""
        self.print_header("로그인 테스트")
        
        # 기존 테스트 계정으로 로그인 시도
        test_accounts = [
            "test@casino-club.local",
            "admin@casino-club.local"
        ]
        
        for site_id in test_accounts:
            try:
                response = requests.post(
                    f"{BASE_URL}/auth/login",
                    params={"site_id": site_id}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "access_token" in data:
                        self.access_token = data["access_token"]
                        self.print_success(f"로그인 성공: {site_id}")
                        return True
                    else:
                        self.print_warning(f"로그인 응답에 토큰 없음: {site_id}")
                else:
                    self.print_warning(f"로그인 실패 ({site_id}): {response.status_code}")
            except Exception as e:
                self.print_warning(f"로그인 요청 오류 ({site_id}): {str(e)}")
        
        return False
    
    def test_profile(self):
        """프로필 조회 테스트"""
        self.print_header("프로필 조회 테스트")
        
        if not self.access_token:
            self.print_warning("로그인이 필요합니다")
            return False
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            response = requests.get(f"{BASE_URL}/auth/profile", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.print_success(f"프로필 조회 성공: {data.get('site_id', 'Unknown')}")
                return True
            else:
                self.print_error(f"프로필 조회 실패: {response.status_code}")
        except Exception as e:
            self.print_error(f"프로필 조회 오류: {str(e)}")
        
        return False
    
    def test_game_apis(self):
        """게임 API 테스트"""
        self.print_header("게임 API 테스트")
        
        if not self.access_token:
            self.print_warning("로그인이 필요합니다")
            return False
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        results = []
        
        # 게임 목록 조회
        try:
            response = requests.get(f"{BASE_URL}/api/games/", headers=headers)
            if response.status_code == 200:
                self.print_success("게임 목록 조회 성공")
                results.append(True)
            else:
                self.print_error(f"게임 목록 조회 실패: {response.status_code}")
                results.append(False)
        except Exception as e:
            self.print_error(f"게임 목록 조회 오류: {str(e)}")
            results.append(False)
        
        # RPS 게임 테스트
        try:
            rps_data = {
                "choice": "rock",
                "bet_amount": 100
            }
            response = requests.post(
                f"{BASE_URL}/api/games/rps/play",
                json=rps_data,
                headers=headers
            )
            if response.status_code in [200, 201]:
                self.print_success("RPS 게임 플레이 성공")
                results.append(True)
            else:
                self.print_warning(f"RPS 게임 플레이 실패: {response.status_code}")
                results.append(False)
        except Exception as e:
            self.print_warning(f"RPS 게임 오류: {str(e)}")
            results.append(False)
        
        return any(results)
    
    def test_missions(self):
        """미션 API 테스트"""
        self.print_header("미션 API 테스트")
        
        if not self.access_token:
            self.print_warning("로그인이 필요합니다")
            return False
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            response = requests.get(f"{BASE_URL}/api/missions/", headers=headers)
            if response.status_code == 200:
                self.print_success("미션 목록 조회 성공")
                return True
            else:
                self.print_warning(f"미션 목록 조회 실패: {response.status_code}")
        except Exception as e:
            self.print_warning(f"미션 API 오류: {str(e)}")
        
        return False
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print(f"\n{Fore.MAGENTA}🚀 Casino-Club F2P 전체 API 테스트 시작{Style.RESET_ALL}\n")
        
        # 1. 서버 상태 확인
        if not self.test_health():
            print(f"\n{Fore.RED}서버가 응답하지 않습니다. 테스트를 중단합니다.{Style.RESET_ALL}")
            return
        
        # 2. 인증 테스트
        if not self.test_registration():
            print(f"{Fore.YELLOW}회원가입 실패, 로그인 시도...{Style.RESET_ALL}")
            if not self.test_login():
                print(f"{Fore.YELLOW}인증 실패, 일부 테스트가 제한될 수 있습니다.{Style.RESET_ALL}")
        
        # 3. 프로필 테스트
        self.test_profile()
        
        # 4. 게임 API 테스트
        self.test_game_apis()
        
        # 5. 미션 API 테스트
        self.test_missions()
        
        # 결과 요약
        self.print_summary()
    
    def print_summary(self):
        """테스트 결과 요약"""
        self.print_header("테스트 결과 요약")
        
        success_count = sum(1 for status, _ in self.test_results if status == "SUCCESS")
        error_count = sum(1 for status, _ in self.test_results if status == "ERROR")
        warning_count = sum(1 for status, _ in self.test_results if status == "WARNING")
        
        print(f"{Fore.GREEN}성공: {success_count}개{Style.RESET_ALL}")
        print(f"{Fore.RED}실패: {error_count}개{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}경고: {warning_count}개{Style.RESET_ALL}")
        
        total = success_count + error_count + warning_count
        if total > 0:
            success_rate = (success_count / total) * 100
            print(f"\n{Fore.CYAN}성공률: {success_rate:.1f}%{Style.RESET_ALL}")
            
            if success_rate >= 80:
                print(f"{Fore.GREEN}✨ 테스트가 대체로 성공적입니다!{Style.RESET_ALL}")
            elif success_rate >= 50:
                print(f"{Fore.YELLOW}⚠️ 일부 문제가 있지만 기본 기능은 작동합니다.{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}🔧 많은 문제가 발견되었습니다. 수정이 필요합니다.{Style.RESET_ALL}")

if __name__ == "__main__":  # pragma: no cover
    tester = APITester()
    tester.run_all_tests()

# pytest 수집 방지 힌트: 본 파일은 독립 실행 스크립트이며 테스트 프레임워크에서 무시되어야 함