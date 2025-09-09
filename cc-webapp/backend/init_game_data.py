"""
게임 초기 데이터 생성 스크립트
"""
from app.database import SessionLocal, engine
from app.models.game_models import Game
from sqlalchemy import text
import json

def init_games():
    """게임 초기 데이터 생성"""
    db = SessionLocal()
    
    try:
        # 기존 게임 데이터 확인
        existing_games = db.query(Game).count()
        if existing_games > 0:
            print(f"✅ 이미 {existing_games}개의 게임이 존재합니다")
            return
        
        # 게임 데이터 정의
        games = [
            {
                "id": "slot_machine",
                "name": "슬롯머신",
                "description": "클래식 슬롯머신 게임",
                "type": "slot",
                "is_active": True,
                "min_bet": 10,
                "max_bet": 1000,
                "config": {
                    "symbols": ["🍒", "🍋", "🍊", "🍇", "💎", "7️⃣"],
                    "paylines": 5,
                    "reels": 3
                }
            },
            {
                "id": "gacha_basic",
                "name": "기본 가챠",
                "description": "다양한 아이템을 획득할 수 있는 가챠",
                "type": "gacha",
                "is_active": True,
                "min_bet": 100,
                "max_bet": 1000,
                "config": {
                    "rates": {
                        "common": 0.6,
                        "rare": 0.3,
                        "epic": 0.08,
                        "legendary": 0.02
                    }
                }
            },
            {
                "id": "neon_crash",
                "name": "네온크래시",
                "description": "실시간 멀티플라이어 게임",
                "type": "crash",
                "is_active": True,
                "min_bet": 50,
                "max_bet": 5000,
                "config": {
                    "min_multiplier": 1.0,
                    "max_multiplier": 100.0,
                    "house_edge": 0.03
                }
            },
            {
                "id": "rps_game",
                "name": "가위바위보",
                "description": "AI와 대결하는 가위바위보",
                "type": "rps",
                "is_active": True,
                "min_bet": 10,
                "max_bet": 500,
                "config": {
                    "win_multiplier": 2.0,
                    "draw_return": 1.0
                }
            },
            {
                "id": "quiz_game",
                "name": "퀴즈 게임",
                "description": "지식을 테스트하는 퀴즈 게임",
                "type": "quiz",
                "is_active": True,
                "min_bet": 0,
                "max_bet": 0,
                "config": {
                    "time_limit": 30,
                    "correct_reward": 100
                }
            }
        ]
        
        # 게임 데이터 삽입
        for game_data in games:
            game = Game(
                id=game_data["id"],
                name=game_data["name"],
                description=game_data["description"],
                type=game_data["type"],
                is_active=game_data["is_active"],
                min_bet=game_data["min_bet"],
                max_bet=game_data["max_bet"],
                config=game_data["config"]
            )
            db.add(game)
        
        db.commit()
        print(f"✅ {len(games)}개의 게임 데이터 생성 완료!")
        
        # 생성된 게임 확인
        created_games = db.query(Game).all()
        for game in created_games:
            print(f"  - {game.name} ({game.type})")
        
    except Exception as e:
        print(f"❌ 게임 데이터 생성 실패: {e}")
        db.rollback()
    finally:
        db.close()

def init_missions():
    """미션 초기 데이터 생성"""
    db = SessionLocal()
    
    try:
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
            }
        ]
        
        # 직접 SQL로 삽입
        for mission in missions:
            db.execute(text("""
                INSERT INTO missions (title, description, mission_type, category, 
                                    target_type, target_value, rewards, reset_period, 
                                    is_active, sort_order)
                VALUES (:title, :description, :mission_type, :category, 
                        :target_type, :target_value, :rewards, :reset_period, 
                        :is_active, :sort_order)
                ON CONFLICT (title, mission_type) DO NOTHING
            """), {
                **mission,
                "rewards": json.dumps(mission["rewards"])
            })
        
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
        # 이벤트 생성
        events = [
            {
                "title": "신규 가입 이벤트",
                "description": "신규 가입자를 위한 특별 보상",
                "event_type": "welcome",
                "rewards": {"tokens": 1000, "items": ["starter_pack"]},
                "requirements": {"new_user": True},
                "is_active": True,
                "priority": 100
            },
            {
                "title": "주말 특별 이벤트",
                "description": "주말 동안 게임 플레이시 추가 보상",
                "event_type": "weekend",
                "rewards": {"multiplier": 1.5},
                "requirements": {"weekend": True},
                "is_active": True,
                "priority": 50
            }
        ]
        
        # 직접 SQL로 삽입
        for event in events:
            db.execute(text("""
                INSERT INTO events (title, description, event_type, rewards, 
                                  requirements, is_active, priority,
                                  start_date, end_date)
                VALUES (:title, :description, :event_type, :rewards, 
                        :requirements, :is_active, :priority,
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '30 days')
                ON CONFLICT (title) DO NOTHING
            """), {
                **event,
                "rewards": json.dumps(event["rewards"]),
                "requirements": json.dumps(event["requirements"])
            })
        
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
    
    # 게임 데이터 생성
    init_games()
    
    # 미션 데이터 생성
    init_missions()
    
    # 이벤트 데이터 생성
    init_events()
    
    print("\n✅ 모든 초기 데이터 생성 완료!")

if __name__ == "__main__":
    main()
