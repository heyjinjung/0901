#!/usr/bin/env python
"""
Add image_url field to Game model
"""
import os
from sqlalchemy import create_engine, text

# 환경 변수에서 데이터베이스 정보 읽기
POSTGRES_SERVER = os.getenv('POSTGRES_SERVER', 'postgres')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'cc_user')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'cc_password')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'cc_webapp')

# 데이터베이스 URL 생성
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:5432/{POSTGRES_DB}"

def add_image_url_field():
    """Game 모델에 image_url 필드 추가"""
    print(f"✅ Game 모델에 image_url 필드 추가 시작 (DB: {DATABASE_URL})")
    
    # SQLAlchemy 엔진 직접 생성
    engine = create_engine(DATABASE_URL)
    
    try:
        # 필드 추가 SQL 실행
        with engine.connect() as conn:
            # 필드 존재 여부 확인
            result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='games' AND column_name='image_url'"))
            exists = False
            for row in result:
                exists = True
                break
            
            if not exists:
                print("✅ image_url 필드 추가 중...")
                conn.execute(text("ALTER TABLE games ADD COLUMN image_url VARCHAR(255)"))
                print("✅ image_url 필드 추가 완료")
            else:
                print("✅ image_url 필드가 이미 존재합니다")
            
            # 기본 이미지 URL 설정
            conn.execute(text("UPDATE games SET image_url = '/assets/games/' || game_type || '.png' WHERE image_url IS NULL"))
            conn.commit()
            print("✅ 모든 게임의 이미지 URL이 업데이트되었습니다")
    
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
    
    finally:
        engine.dispose()

if __name__ == "__main__":
    add_image_url_field()
