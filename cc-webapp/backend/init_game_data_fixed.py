"""
게임 초기 데이터 생성 스크립트
"""
from app.database import SessionLocal, engine
from app.models.game_models import Game
from app.models.event_models import Event
from sqlalchemy import text
import json
from datetime import datetime, timedelta
# Mission 모델을 event_models에서 가져옵니다 (중복 정의 문제 해결)
from app.models import event_models
Mission = event_models.Mission

def check_db_connection():
    """데이터베이스 연결 확인"""
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        print("✅ 데이터베이스 연결 성공")
        return True
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        return False

def init_games():
    """게임 초기 데이터 생성"""
    db = SessionLocal()
    try:
        # 기존 게임 데이터 확인
        existing_games = db.query(Game).count()
        if existing_games > 0:
            print(f"이미 {existing_games}개의 게임이 존재합니다.")
            return
        
        # 게임 데이터 정의
        games = [
            {
                "name": "슬롯머신",
                "description": "클래식 3x3 슬롯머신 게임",
                "game_type": "slot",
                "is_active": True
            },
            {
                "name": "가챠",
                "description": "다양한 아이템을 획득할 수 있는 가챠",
                "game_type": "gacha",
                "is_active": True
            },
            {
                "name": "네온크래시",
                "description": "실시간 멀티플라이어 게임",
                "game_type": "crash",
                "is_active": True
            },
            {
                "name": "가위바위보",
                "description": "AI와 대결하는 가위바위보",
                "game_type": "rps",
                "is_active": True
            },
            {
                "name": "퀴즈게임",
                "description": "지식을 테스트하는 퀴즈 게임",
                "game_type": "quiz",
                "is_active": True
            }
        ]
        
        # 게임 데이터 삽입
        for game_data in games:
            game = Game(**game_data)
            db.add(game)
        
        db.commit()
        print(f"✅ {len(games)}개의 게임 데이터 생성 완료!")
        
        # 생성된 게임 확인
        created_games = db.query(Game).all()
        for game in created_games:
            print(f"  - {game.name} ({game.game_type})")
        
    except Exception as e:
        print(f"❌ 게임 데이터 생성 실패: {e}")
        db.rollback()
    finally:
        db.close()

def init_missions():
    """미션 초기 데이터 생성"""
    db = SessionLocal()
    try:
        # 기존 미션 확인
        existing_missions = db.query(Mission).count()
        if existing_missions > 0:
            print(f"이미 {existing_missions}개의 미션이 존재합니다.")
            return
        
        # 일일 미션 생성
        missions = [
            {
                "title": "일일 로그인",
                "description": "오늘 한 번 로그인하기",
                "mission_type": "daily",
                "category": "login",
                "target_type": "login",
                "target_value": 1,
                "rewards": {"tokens": 100},
                "reset_period": "daily",
                "is_active": True,
                "sort_order": 1
            },
            {
                "title": "슬롯머신 10회 플레이",
                "description": "슬롯머신을 10회 플레이하기",
                "mission_type": "daily",
                "category": "game",
                "target_type": "play_count",
                "target_value": 10,
                "rewards": {"tokens": 200},
                "reset_period": "daily",
                "is_active": True,
                "sort_order": 2
            },
            {
                "title": "가챠 3회 뽑기",
                "description": "가챠를 3회 뽑기",
                "mission_type": "daily",
                "category": "game",
                "target_type": "gacha_pull",
                "target_value": 3,
                "rewards": {"tokens": 300},
                "reset_period": "daily",
                "is_active": True,
                "sort_order": 3
            },
            {
                "title": "첫 승리",
                "description": "아무 게임에서 1번 승리하기",
                "mission_type": "achievement",
                "category": "game",
                "target_type": "win_count",
                "target_value": 1,
                "rewards": {"tokens": 500},
                "reset_period": "never",
                "is_active": True,
                "sort_order": 4
            },
            {
                "title": "주간 플레이어",
                "description": "이번 주 50게임 플레이",
                "mission_type": "weekly",
                "category": "game",
                "target_type": "play_count",
                "target_value": 50,
                "rewards": {"tokens": 1000},
                "reset_period": "weekly",
                "is_active": True,
                "sort_order": 5
            }
        ]
        
        # 미션 데이터 삽입
        for mission_data in missions:
            mission = Mission(**mission_data)
            db.add(mission)
        
        db.commit()
        print(f"✅ {len(missions)}개의 미션 데이터 생성 완료!")
        
    except Exception as e:
        print(f"❌ 미션 데이터 생성 실패: {e}")
        db.rollback()
    finally:
        db.close()

def init_events():
    """이벤트 초기 데이터 생성"""
    db = SessionLocal()
    try:
        # 기존 이벤트 확인
        existing_events = db.query(Event).count()
        if existing_events > 0:
            print(f"이미 {existing_events}개의 이벤트가 존재합니다.")
            return
        
        # 이벤트 생성
        events = [
            {
                "title": "신규 가입 이벤트",
                "description": "신규 가입자를 위한 특별 보상",
                "event_type": "special",
                "start_date": datetime.utcnow(),
                "end_date": datetime.utcnow() + timedelta(days=30),
                "rewards": {"tokens": 1000, "items": ["starter_pack"]},
                "requirements": {"new_user": True},
                "is_active": True,
                "priority": 100
            },
            {
                "title": "주말 특별 이벤트",
                "description": "주말 동안 게임 플레이시 추가 보상",
                "event_type": "weekly",
                "start_date": datetime.utcnow(),
                "end_date": datetime.utcnow() + timedelta(days=7),
                "rewards": {"multiplier": 1.5},
                "requirements": {"weekend": True},
                "is_active": True,
                "priority": 50
            },
            {
                "title": "일일 접속 이벤트",
                "description": "매일 접속시 보상 지급",
                "event_type": "daily",
                "start_date": datetime.utcnow(),
                "end_date": datetime.utcnow() + timedelta(days=14),
                "rewards": {"tokens": 50, "exp": 100},
                "requirements": {"daily_login": True},
                "is_active": True,
                "priority": 75
            }
        ]
        
        # 이벤트 데이터 삽입
        for event_data in events:
            event = Event(**event_data)
            db.add(event)
        
        db.commit()
        print(f"✅ {len(events)}개의 이벤트 데이터 생성 완료!")
        
    except Exception as e:
        print(f"❌ 이벤트 데이터 생성 실패: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """메인 실행 함수"""
    print("🎮 게임 초기 데이터 생성 시작...")
    
    # 데이터베이스 연결 확인
    if not check_db_connection():
        return
    
    # 게임 데이터 생성
    init_games()
    
    # 미션 데이터 생성
    init_missions()
    
    # 이벤트 데이터 생성
    init_events()
    
    print("\n✅ 모든 초기 데이터 생성 완료!")

if __name__ == "__main__":
    main()
