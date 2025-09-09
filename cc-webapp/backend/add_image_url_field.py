#!/usr/bin/env python
"""
Add image_url field to Game model
"""
from app.models.game_models import Game
from app.database import SessionLocal
from sqlalchemy import Column, String
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from app.core.config import settings

def add_image_url_field():
    """Game 모델에 image_url 필드 추가"""
    print("✅ Game 모델에 image_url 필드 추가 시작")
    
    # SQLAlchemy 엔진 직접 생성
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        # 필드 추가 SQL 실행
        with engine.connect() as conn:
            # 필드 존재 여부 확인
            result = conn.execute("SELECT column_name FROM information_schema.columns WHERE table_name='games' AND column_name='image_url'")
            if result.rowcount == 0:
                print("✅ image_url 필드 추가 중...")
                conn.execute("ALTER TABLE games ADD COLUMN image_url VARCHAR(255)")
                print("✅ image_url 필드 추가 완료")
            else:
                print("✅ image_url 필드가 이미 존재합니다")
            
            # 기본 이미지 URL 설정
            conn.execute("UPDATE games SET image_url = '/assets/games/' || game_type || '.png' WHERE image_url IS NULL")
            print("✅ 모든 게임의 이미지 URL이 업데이트되었습니다")
    
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
    
    finally:
        engine.dispose()

if __name__ == "__main__":
    add_image_url_field()
