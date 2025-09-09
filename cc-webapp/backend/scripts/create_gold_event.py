#!/usr/bin/env python3
"""
더블 골드 이벤트를 데이터베이스에 생성하는 스크립트
"""
import os
import sys
from datetime import datetime, timedelta

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app.models.event_models import Event

def create_double_gold_event():
    """더블 골드 이벤트 생성"""
    db = SessionLocal()
    
    try:
        # 기존 더블 골드 이벤트가 있는지 확인
        existing_event = db.query(Event).filter(
            Event.title == "더블 골드 이벤트!"
        ).first()
        
        if existing_event:
            print("기존 더블 골드 이벤트가 있습니다. 업데이트합니다...")
            # 기존 이벤트 업데이트
            existing_event.description = "모든 게임에서 골드 2배 획득"
            existing_event.event_type = "special"
            existing_event.start_date = datetime.utcnow()
            existing_event.end_date = datetime.utcnow() + timedelta(hours=24)  # 24시간 이벤트
            existing_event.rewards = {"gold_multiplier": 2}
            existing_event.requirements = {}
            existing_event.priority = 100
            existing_event.is_active = True
            event = existing_event
        else:
            print("새로운 더블 골드 이벤트를 생성합니다...")
            # 새 이벤트 생성
            event = Event(
                title="더블 골드 이벤트!",
                description="모든 게임에서 골드 2배 획득",
                event_type="special",
                start_date=datetime.utcnow(),
                end_date=datetime.utcnow() + timedelta(hours=24),  # 24시간 이벤트
                rewards={"gold_multiplier": 2},
                requirements={},
                priority=100,
                is_active=True,
                image_url="https://example.com/double-gold-banner.jpg"
            )
            db.add(event)
        
        db.commit()
        print(f"더블 골드 이벤트가 성공적으로 생성/업데이트되었습니다!")
        print(f"이벤트 ID: {event.id}")
        print(f"시작 시간: {event.start_date}")
        print(f"종료 시간: {event.end_date}")
        
        return event
        
    except Exception as e:
        db.rollback()
        print(f"오류 발생: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_double_gold_event()
