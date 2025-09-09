#!/usr/bin/env python3
# -* - coding: utf - 8 -* -

  """
Casino - Club F2P API 탐색
======================
사용 가능한 API 엔드포인트 확인 및 테스트
"""

import requests
import json

# 테스트 설정
BASE_URL = "http://localhost:8000"

def print_header(title):
    """섹션 헤더 출력"""
    print("\n" + "="*80)
    print(f" {title} ")
    print("="*80)

def print_response(response, label="응답"):
    """응답 데이터 출력"""
    print(f"\n{label} (상태코드: {response.status_code}):")
    try:
        print(json.dumps(response.json(), ensure_ascii=False, indent=2))
    except:
        print(response.text)

def check_api_root():
    """API 루트 엔드포인트 확인"""
    print_header("API 루트 엔드포인트 확인")

    response = requests.get(f"{BASE_URL}")
    print_response(response, "API 루트 응답")

def check_login_endpoint():
    """로그인 엔드포인트 테스트"""
    print_header("로그인 엔드포인트 테스트")

    # 기존 테스트 사용자 데이터
    site_id = "test_user_1754543804_3926"  # 이전에 만든 사용자

    # 1. 쿼리 파라미터로 테스트
    print("\n방식 1: 쿼리 파라미터 사용")
    response = requests.post(f"{BASE_URL}/auth/login?site_id={site_id}")
    print_response(response, "로그인 응답 (쿼리 파라미터)")

    # 2. JSON 요청 바디로 테스트
    print("\n방식 2: JSON 요청 바디 사용")
    response = requests.post(f"{BASE_URL}/auth/login", json={"site_id": site_id})
    print_response(response, "로그인 응답 (JSON 요청 바디)")

    # 3. Form 데이터로 테스트
    print("\n방식 3: Form 데이터 사용")
    response = requests.post(f"{BASE_URL}/auth/login", data={"site_id": site_id})
    print_response(response, "로그인 응답 (Form 데이터)")

def main():
    """API 탐색 테스트 실행"""
    print("\n🔍 Casino-Club F2P API 탐색 시작")

    # API 루트 확인
    check_api_root()

    # 로그인 엔드포인트 테스트
    check_login_endpoint()

    print("\n🏁 API 탐색 완료")

if __name__ == "__main__":
    main()
