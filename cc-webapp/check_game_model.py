#!/usr/bin/env python
"""
Game Model Schema Check
"""
from app.models.game_models import Game
from app.database import SessionLocal

def check_game_model():
    """게임 모델 필드 확인"""
    print("✅ 게임 모델 필드 확인 시작")
    
    db = SessionLocal()
    
    try:
        # 첫번째 게임 가져오기
        game = db.query(Game).first()
        
        # 필드 확인
        print("게임 객체 필드:")
        for key, value in game.__dict__.items():
            if not key.startswith('_'):
                print(f"  - {key}: {value}")
        
        # 게임 테이블의 모든 필드 확인 (SQLAlchemy reflection)
        from sqlalchemy import inspect
        inspector = inspect(db.bind)
        columns = inspector.get_columns('games')
        
        print("\n게임 테이블 스키마:")
        for column in columns:
            print(f"  - {column['name']}: {column['type']}")
    
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
    
    finally:
        db.close()

if __name__ == "__main__":
    check_game_model()
