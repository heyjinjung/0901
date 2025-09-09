#!/usr/bin/env python3
"""
데이터베이스 연결 문제 해결 스크립트
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import time

def test_db_connection():
    """데이터베이스 연결 테스트"""

    # 환경변수에서 DB 정보 가져오기
    db_host = os.getenv('DB_HOST', 'postgres')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'cc_webapp')
    db_user = os.getenv('DB_USER', 'cc_user')
    db_password = os.getenv('DB_PASSWORD', 'cc_secret_password_2025')

    database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    print(f"🔍 데이터베이스 연결 테스트...")
    print(f"📍 연결 정보: {db_host}:{db_port}/{db_name}")

    max_retries = 30
    for attempt in range(max_retries):
        try:
            engine = create_engine(database_url)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                print(f"✅ 데이터베이스 연결 성공!")
                return True

        except OperationalError as e:
            print(f"⏳ 연결 시도 {attempt + 1}/{max_retries} 실패: {str(e)[:100]}...")
            time.sleep(2)

    print(f"❌ 데이터베이스 연결 실패!")
    return False

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
import time
from dotenv import load_dotenv

# .env.development 파일 로드
load_dotenv(dotenv_path='../../.env.development')

from app.database import engine, Base
from app.models import *  # 모든 모델 import

def create_tables():
    """테이블 생성"""
    try:
        print("🏗️ 테이블 생성 중...")
        Base.metadata.create_all(bind=engine)
        print("✅ 테이블 생성 완료!")
        return True

    except Exception as e:
        print(f"❌ 테이블 생성 실패: {e}")
        return False

def run_migrations():
    """Alembic 마이그레이션 실행"""
    try:
        import subprocess

        print("🔄 Alembic 마이그레이션 실행...")

        # 마이그레이션 상태 확인
        result = subprocess.run(['alembic', 'current'],
                              capture_output=True, text=True)
        print(f"현재 마이그레이션 상태: {result.stdout}")

        # 마이그레이션 실행
        result = subprocess.run(['alembic', 'upgrade', 'head'],
                              capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ 마이그레이션 완료!")
            return True
        else:
            print(f"❌ 마이그레이션 실패: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ 마이그레이션 오류: {e}")
        return False

if __name__ == "__main__":
    print("🚀 데이터베이스 연결 문제 해결 시작...")

    # 1. 연결 테스트
    if not test_db_connection():
        sys.exit(1)

    # 2. 테이블 생성
    if not create_tables():
        print("⚠️ 테이블 생성 실패, 마이그레이션으로 재시도...")

    # 3. 마이그레이션 실행
    if not run_migrations():
        sys.exit(1)

    print("🎉 데이터베이스 설정 완료!")
