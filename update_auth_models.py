#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Casino-Club F2P 데이터베이스 모델 업데이트 스크립트
================================================
인증 시스템에 필요한 모델 필드 수정 및 추가

실행 방법:
1. 백엔드 컨테이너에서 실행: docker exec -it cc_backend python update_auth_models.py
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

# 데이터베이스 연결 설정
DB_USER = os.getenv("POSTGRES_USER", "cc_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "cc_password")
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "cc_webapp")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 엔진 및 세션 생성
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def execute_sql(sql, message=None):
    """SQL 실행 및 결과 출력"""
    with engine.connect() as conn:
        try:
            conn.execute(text(sql))
            conn.commit()
            if message:
                print(f"✅ {message}")
            return True
        except Exception as e:
            print(f"❌ SQL 실행 오류: {str(e)}")
            print(f"SQL: {sql}")
            return False

def check_column_exists(table, column):
    """열이 존재하는지 확인"""
    with engine.connect() as conn:
        result = conn.execute(text(f"""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = '{table}'
                AND column_name = '{column}'
            );
        """))
        return result.scalar()

def update_user_model():
    """User 모델 업데이트"""
    print("\n🔄 User 모델 업데이트 중...")
    
    # password_hash 필드 이름 변경 (hashed_password → password_hash)
    if check_column_exists("users", "hashed_password") and not check_column_exists("users", "password_hash"):
        execute_sql(
            "ALTER TABLE users RENAME COLUMN hashed_password TO password_hash;",
            "hashed_password 필드를 password_hash로 이름 변경함"
        )
    elif not check_column_exists("users", "password_hash") and not check_column_exists("users", "hashed_password"):
        # 둘 다 없으면 password_hash 추가
        execute_sql(
            "ALTER TABLE users ADD COLUMN password_hash VARCHAR(255);",
            "password_hash 필드 추가됨"
        )
        # 기존 사용자를 위한 기본값 설정 (테스트용)
        execute_sql(
            "UPDATE users SET password_hash = 'default_hashed_password' WHERE password_hash IS NULL;",
            "기존 사용자의 password_hash에 기본값 설정됨"
        )
        # NOT NULL 제약조건 추가
        execute_sql(
            "ALTER TABLE users ALTER COLUMN password_hash SET NOT NULL;",
            "password_hash NOT NULL 제약조건 추가됨"
        )
    
    # phone_number 필드 옵션 변경 (nullable: true)
    if check_column_exists("users", "phone_number"):
        execute_sql(
            "ALTER TABLE users ALTER COLUMN phone_number DROP NOT NULL;",
            "phone_number 필드가 nullable로 변경됨"
        )

def update_login_attempt_model():
    """LoginAttempt 모델 업데이트"""
    print("\n🔄 LoginAttempt 모델 업데이트 중...")
    
    # attempted_at 필드 추가
    if not check_column_exists("login_attempts", "attempted_at"):
        execute_sql(
            """
            ALTER TABLE login_attempts 
            ADD COLUMN attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
            """,
            "attempted_at 필드 추가됨"
        )
        # 기존 데이터에 created_at 값을 복사
        execute_sql(
            """
            UPDATE login_attempts 
            SET attempted_at = created_at 
            WHERE attempted_at IS NULL;
            """,
            "기존 데이터의 attempted_at에 created_at 값 복사됨"
        )
    
    # user_id 필드 추가
    if not check_column_exists("login_attempts", "user_id"):
        execute_sql(
            """
            ALTER TABLE login_attempts 
            ADD COLUMN user_id INTEGER REFERENCES users(id) ON DELETE CASCADE;
            """,
            "user_id 필드 추가됨"
        )

def create_test_user():
    """테스트 계정 생성"""
    print("\n🧪 테스트 계정 생성 중...")
    
    # 테스트 계정이 존재하는지 확인
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1 FROM users WHERE site_id = 'test@casino-club.local' LIMIT 1;"))
        exists = result.scalar() is not None
    
    if not exists:
        # 테스트 계정 생성
        execute_sql(
            """
            INSERT INTO users (
                site_id, nickname, password_hash, invite_code, 
                is_active, is_admin, rank, created_at, updated_at
            ) VALUES (
                'test@casino-club.local', 'test', 'test_password_hash', '5858', 
                TRUE, FALSE, 'STANDARD', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            );
            """,
            "테스트 계정 'test@casino-club.local' 생성됨"
        )
    
    # 관리자 계정이 존재하는지 확인
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1 FROM users WHERE site_id = 'admin@casino-club.local' LIMIT 1;"))
        exists = result.scalar() is not None
    
    if not exists:
        # 관리자 계정 생성
        execute_sql(
            """
            INSERT INTO users (
                site_id, nickname, password_hash, invite_code, 
                is_active, is_admin, rank, created_at, updated_at
            ) VALUES (
                'admin@casino-club.local', 'admin', 'admin_password_hash', '5858', 
                TRUE, TRUE, 'VIP', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
            );
            """,
            "관리자 계정 'admin@casino-club.local' 생성됨"
        )

def main():
    """메인 함수"""
    print("🛠️ Casino-Club F2P 데이터베이스 모델 업데이트 시작")
    
    try:
        # 데이터베이스 연결 확인
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("✅ 데이터베이스 연결 성공")
        
        # User 모델 업데이트
        update_user_model()
        
        # LoginAttempt 모델 업데이트
        update_login_attempt_model()
        
        # 테스트 계정 생성
        create_test_user()
        
        print("\n✅ 데이터베이스 모델 업데이트 완료!")
    
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")

if __name__ == "__main__":
    main()
