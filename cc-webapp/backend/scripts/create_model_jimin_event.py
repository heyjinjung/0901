"""모델지민 이벤트(테스트1) 시드/업서트 스크립트

요구사항:
- 제목: 모델지민 이벤트 테스트1
- 지속시간: 1주일 (UTC 기준 지금부터)
- 적용 대상: 모든 게임 (game_type = "all")
- 기본 참여 보상: 1000 골드 (claim 조건: 최소 5회 플레이)
- 진행 규칙(progress 요구치): total_plays >= 5 → 완료 가능

구조:
events.rewards JSON 예시
{
  "gold": 1000,
  "bonus": {
     "type": "flat_win_bonus",
     "value": 50,            # 각 게임 승리 시 추가 골드 (별도 적용 로직은 후속 개발 필요)
     "apply_to": "all"
  }
}

현재 reward 추가 승리별 보너스 적용 로직은 게임별 엔드포인트에 아직 미반영 → 후속 작업 메모 남김.
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.event_models import Event

TITLE = "모델지민 이벤트 테스트1"

def upsert_event(db: Session):
    now = datetime.utcnow()
    end = now + timedelta(days=7)

    existing = db.query(Event).filter(Event.title == TITLE).first()

    rewards = {
        "gold": 1000,
        "bonus": {
            "type": "flat_win_bonus",
            "value": 50,
            "apply_to": "all"
        }
    }
    requirements = {"total_plays": 5}

    if existing:
        existing.description = "모든 게임 플레이 누적 5회 달성 후 1000골드 수령 + 승리 시 추가 50골드 (향후 반영)"
        existing.event_type = "special"
        existing.start_date = now
        existing.end_date = end
        existing.rewards = rewards
        existing.requirements = requirements
        existing.is_active = True
        existing.priority = 100
        db.commit()
        db.refresh(existing)
        print(f"업데이트 완료: {existing.id}")
        return existing.id
    else:
        ev = Event(
            title=TITLE,
            description="모든 게임 5회 플레이하고 1000골드 획득! (승리 추가보너스 준비)",
            event_type="special",
            start_date=now,
            end_date=end,
            rewards=rewards,
            requirements=requirements,
            image_url=None,
            is_active=True,
            priority=100,
        )
        db.add(ev)
        db.commit()
        db.refresh(ev)
        print(f"생성 완료: {ev.id}")
        return ev.id

def deactivate_double_gold(db: Session):
    q = db.query(Event).filter(Event.title == "더블 골드 이벤트!")
    # count 먼저 수행 후 상태 변경
    disabled_any = False
    for ev in q.all():
        ev.is_active = False
        disabled_any = True
    if disabled_any:
        db.commit()
        print("기존 더블 골드 이벤트 비활성화")

def main():
    db = SessionLocal()
    try:
        deactivate_double_gold(db)
        eid = upsert_event(db)
        print(f"모델지민 이벤트 준비 완료 (id={eid})")
    finally:
        db.close()

if __name__ == "__main__":
    main()
