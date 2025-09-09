from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models.event_models import Event, Mission

def seed_events_and_missions():
    db = SessionLocal()
    
    try:
        # 샘플 이벤트 생성
        events = [
            Event(
                title="신규 유저 환영 이벤트",
                description="새로운 카지노 클럽 회원을 위한 특별 이벤트!",
                event_type="special",
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=7),
                rewards={"gold": 5000, "gems": 50},
                requirements={"games_played": 10},
                priority=100,
                is_active=True
            ),
            Event(
                title="주말 보너스 이벤트",
                description="주말 동안 모든 게임에서 2배 보상!",
                event_type="weekly",
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(days=2),
                rewards={"multiplier": 2},
                requirements={},
                priority=50,
                is_active=True
            )
        ]
        
        # 샘플 미션 생성
        missions = [
            Mission(
                title="첫 게임 플레이",
                description="아무 게임이나 1회 플레이하세요",
                mission_type="daily",
                category="game",
                target_value=1,
                target_type="play_count",
                rewards={"gold": 100, "exp": 10},
                reset_period="daily",
                is_active=True
            ),
            Mission(
                title="슬롯 마스터",
                description="슬롯 게임을 5회 플레이하세요",
                mission_type="daily",
                category="game",
                target_value=5,
                target_type="slot_play",
                rewards={"gold": 500, "exp": 50},
                reset_period="daily",
                is_active=True
            ),
            Mission(
                title="승리의 기쁨",
                description="게임에서 3회 승리하세요",
                mission_type="daily",
                category="game",
                target_value=3,
                target_type="win_count",
                rewards={"gold": 1000, "exp": 100},
                reset_period="daily",
                is_active=True
            ),
            Mission(
                title="주간 챌린지",
                description="이번 주 20게임 플레이",
                mission_type="weekly",
                category="game",
                target_value=20,
                target_type="play_count",
                rewards={"gold": 5000, "gems": 10},
                reset_period="weekly",
                is_active=True
            )
        ]
        
        # 데이터베이스에 추가
        for event in events:
            db.add(event)
        
        for mission in missions:
            db.add(mission)
        
        db.commit()
        print("✅ 이벤트와 미션 데이터가 성공적으로 생성되었습니다!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_events_and_missions()