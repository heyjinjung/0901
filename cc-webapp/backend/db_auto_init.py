#!/usr/bin/env python3
"""
데이터베이스 자동 초기화 및 마이그레이션 스크립트
Docker 환경에서 PostgreSQL 연결 및 Alembic 마이그레이션 자동 실행
"""
import os
import sys
import time
import logging
from pathlib import Path
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import OperationalError
import subprocess

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_database_url():
    """환경 변수에서 데이터베이스 URL 구성"""
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'cc_webapp')
    db_user = os.getenv('DB_USER', 'cc_user')
    db_password = os.getenv('DB_PASSWORD', 'cc_password')
    
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

def wait_for_postgres(max_retries=30, retry_interval=2):
    """PostgreSQL 연결 대기"""
    database_url = get_database_url()
    
    for attempt in range(max_retries):
        try:
            engine = create_engine(database_url)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("✅ PostgreSQL 연결 성공!")
            return True
        except OperationalError as e:
            logger.warning(f"PostgreSQL 연결 시도 {attempt + 1}/{max_retries} 실패: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_interval)
    
    logger.error("❌ PostgreSQL 연결 실패 - 최대 재시도 횟수 초과")
    return False

def check_alembic_setup():
    """Alembic 설정 확인"""
    alembic_ini = Path("alembic.ini")
    alembic_dir = Path("alembic")
    
    if not alembic_ini.exists():
        logger.error("❌ alembic.ini 파일이 없습니다")
        return False
    
    if not alembic_dir.exists():
        logger.error("❌ alembic 디렉토리가 없습니다")
        return False
    
    logger.info("✅ Alembic 설정 확인 완료")
    return True

def run_alembic_command(command):
    """Alembic 명령 실행"""
    try:
        logger.info(f"🔄 Alembic 명령 실행: {command}")
        result = subprocess.run(
            f"alembic {command}",
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"✅ 명령 성공: {command}")
        if result.stdout:
            logger.info(f"출력: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ 명령 실패: {command}")
        logger.error(f"오류: {e.stderr}")
        return False

def check_database_tables():
    """데이터베이스 테이블 존재 확인"""
    try:
        database_url = get_database_url()
        engine = create_engine(database_url)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        logger.info(f"📊 현재 데이터베이스 테이블: {tables}")
        
        # 필수 테이블 확인
        required_tables = ['users', 'invite_codes', 'user_sessions']
        missing_tables = [table for table in required_tables if table not in tables]
        
        if missing_tables:
            logger.warning(f"⚠️ 누락된 테이블: {missing_tables}")
            return False
        else:
            logger.info("✅ 필수 테이블 모두 존재")
            return True
            
    except Exception as e:
        logger.error(f"❌ 테이블 확인 중 오류: {e}")
        return False

def initialize_database():
    """데이터베이스 초기화 및 마이그레이션 실행"""
    logger.info("🚀 데이터베이스 자동 초기화 시작")
    
    # 1. PostgreSQL 연결 대기
    if not wait_for_postgres():
        sys.exit(1)
    
    # 2. Alembic 설정 확인
    if not check_alembic_setup():
        sys.exit(1)
    
    # 3. 현재 마이그레이션 상태 확인
    logger.info("📋 현재 마이그레이션 상태 확인")
    run_alembic_command("current")
    
    # 4. 데이터베이스 테이블 확인
    tables_exist = check_database_tables()
    
    # 5. 마이그레이션 실행
    if not tables_exist:
        logger.info("🔧 초기 마이그레이션 실행")
        if not run_alembic_command("upgrade head"):
            logger.error("❌ 마이그레이션 실패")
            sys.exit(1)
    else:
        logger.info("🔄 최신 마이그레이션 적용")
        if not run_alembic_command("upgrade head"):
            logger.warning("⚠️ 마이그레이션 업그레이드 중 경고 발생")
    
    # 6. 최종 상태 확인
    logger.info("🔍 최종 데이터베이스 상태 확인")
    check_database_tables()
    run_alembic_command("current")
    
    logger.info("✅ 데이터베이스 초기화 완료!")

if __name__ == "__main__":
    try:
        initialize_database()
    except KeyboardInterrupt:
        logger.info("👋 사용자에 의해 중단됨")
        sys.exit(0)
    except Exception as e:
        logger.error(f"💥 예상치 못한 오류 발생: {e}")
        sys.exit(1)
