"""간단한 초대코드 생성 및 테스트"""
import os
import sys
sys.path.append('/app')

from sqlalchemy import create_engine, text

def create_invite_code():
    """초대코드 5858 생성"""
    try:
        # 환경변수에서 DB 설정 가져오기
        db_host = os.getenv('DB_HOST', 'postgres')
        db_port = os.getenv('DB_PORT', '5432')
        db_name = os.getenv('DB_NAME', 'cc_webapp')
        db_user = os.getenv('DB_USER', 'cc_user')
        db_password = os.getenv('DB_PASSWORD', 'cc_password')
        
        # PostgreSQL 연결
        engine = create_engine(
            f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        )
        
        print(f"🔗 데이터베이스 연결: {db_host}:{db_port}/{db_name}")
        
        with engine.connect() as conn:
            # 초대코드 테이블이 없으면 생성
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS invite_codes (
                    id SERIAL PRIMARY KEY,
                    code VARCHAR(20) UNIQUE NOT NULL,
                    max_uses INTEGER,
                    current_uses INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER
                )
            """))
            
            # 초대코드 5858 확인 또는 생성
            result = conn.execute(text("SELECT * FROM invite_codes WHERE code = '5858'"))
            if result.fetchone() is None:
                conn.execute(text("""
                    INSERT INTO invite_codes (code, max_uses, current_uses, is_active) 
                    VALUES ('5858', NULL, 0, TRUE)
                """))
                print("✅ 초대코드 5858 생성 완료")
            else:
                print("✅ 초대코드 5858 이미 존재")
            
            conn.commit()
            
    except Exception as e:
        print(f"❌ 초대코드 생성 오류: {e}")

if __name__ == "__main__":
    create_invite_code()
