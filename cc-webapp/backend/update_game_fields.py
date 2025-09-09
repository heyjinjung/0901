#!/usr/bin/env python
"""
게임 모델 필드 업데이트 스크립트
이 스크립트는 DB에 있는 게임 데이터의 필드를 업데이트합니다.
"""
from app.models.game_models import Game
from app.database import SessionLocal

def update_game_fields():
    """게임 모델 필드 업데이트"""
    print("✅ 게임 데이터 업데이트 시작")
    
    db = SessionLocal()
    
    try:
        # 모든 게임 가져오기
        games = db.query(Game).all()
        
        for game in games:
            # 게임 타입별 이미지 URL 설정
            image_url = f"/assets/games/{game.game_type}.png"
            
            # 필드 업데이트
            game.image_url = image_url
            
            print(f"✅ {game.name} 업데이트 완료: image_url = {image_url}")
        
        # 변경사항 저장
        db.commit()
        print("✅ 모든 게임 데이터가 성공적으로 업데이트되었습니다.")
    
    except Exception as e:
        db.rollback()
        print(f"❌ 오류 발생: {str(e)}")
    
    finally:
        db.close()

if __name__ == "__main__":
    update_game_fields()
