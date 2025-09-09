"""
Casino-Club F2P 깨끗한 시드계정 초기화 스크립트

목적: 
- 모든 가짜 게임/상점/이벤트 데이터 삭제
- 시드계정(admin, user001~004)만 유지
- 깨끗한 상태로 시스템 초기화

사용:
    docker compose exec backend python clean_seed_reset.py
"""

import os
from sqlalchemy import create_engine, text
from app.database import SessionLocal
from app.models.auth_models import User

# 현재 확인된 시드계정 ID들
SEED_USER_IDS = [2, 3, 4, 5, 6]  # admin=2, user001=3, user002=4, user003=5, user004=6
SEED_SITE_IDS = ['admin', 'user001', 'user002', 'user003', 'user004']

def clean_reset():
    """모든 가짜 데이터 삭제 및 깨끗한 시드계정만 유지"""
    
    db = SessionLocal()
    
    try:
        print("🧹 Casino-Club F2P 깨끗한 초기화 시작...")
        
        # 1. 게임 관련 데이터 전체 삭제
        print("📱 게임 데이터 삭제 중...")
        tables_to_clean = [
            'game_sessions',
            'gacha_log', 
            'slot_sessions',
            'crash_sessions',
            'user_actions',
            'user_rewards'
        ]
        
        for table in tables_to_clean:
            try:
                result = db.execute(text(f"DELETE FROM {table}"))
                print(f"   ✅ {table}: {result.rowcount}건 삭제")
            except Exception as e:
                print(f"   ⚠️ {table}: 테이블 없음 또는 오류 ({e})")
        
        # 2. 상점/거래 데이터 전체 삭제
        print("💰 상점/거래 데이터 삭제 중...")
        shop_tables = [
            'shop_transactions',
            'purchase_transactions',
            'payment_logs',
            'limited_packages_log'
        ]
        
        for table in shop_tables:
            try:
                result = db.execute(text(f"DELETE FROM {table}"))
                print(f"   ✅ {table}: {result.rowcount}건 삭제")
            except Exception as e:
                print(f"   ⚠️ {table}: 테이블 없음 또는 오류 ({e})")
        
        # 3. 이벤트/미션 데이터 전체 삭제
        print("🎯 이벤트/미션 데이터 삭제 중...")
        event_tables = [
            'events',
            'missions', 
            'user_missions',
            'mission_progress',
            'notifications'
        ]
        
        for table in event_tables:
            try:
                result = db.execute(text(f"DELETE FROM {table}"))
                print(f"   ✅ {table}: {result.rowcount}건 삭제")
            except Exception as e:
                print(f"   ⚠️ {table}: 테이블 없음 또는 오류 ({e})")
        
        # 4. 시드가 아닌 모든 사용자 삭제
        print("👥 논시드 사용자 삭제 중...")
        try:
            # 시드계정이 아닌 모든 사용자 삭제
            result = db.execute(text("""
                DELETE FROM users 
                WHERE site_id NOT IN :seed_ids 
                AND id NOT IN :seed_user_ids
            """), {
                'seed_ids': tuple(SEED_SITE_IDS),
                'seed_user_ids': tuple(SEED_USER_IDS)
            })
            print(f"   ✅ 논시드 사용자: {result.rowcount}명 삭제")
        except Exception as e:
            print(f"   ⚠️ 사용자 삭제 오류: {e}")
        
        # 5. 사용자 관련 데이터 정리 (시드계정 제외)
        print("🧹 사용자 관련 데이터 정리 중...")
        user_related_tables = [
            'user_segments',
            'user_stats',
            'user_inventory',
            'user_battlepass',
            'user_streaks'
        ]
        
        for table in user_related_tables:
            try:
                result = db.execute(text(f"""
                    DELETE FROM {table} 
                    WHERE user_id NOT IN :seed_user_ids
                """), {'seed_user_ids': tuple(SEED_USER_IDS)})
                print(f"   ✅ {table}: {result.rowcount}건 정리")
            except Exception as e:
                print(f"   ⚠️ {table}: 테이블 없음 또는 오류 ({e})")
        
        # 6. 시드계정 상태 초기화
        print("🔄 시드계정 상태 초기화 중...")
        try:
            # 모든 시드계정의 포인트/젬 초기화
            db.execute(text("""
                UPDATE users 
                SET points = 10000, gems = 100, 
                    total_spent = 0, battlepass_level = 1,
                    updated_at = NOW()
                WHERE id IN :seed_user_ids
            """), {'seed_user_ids': tuple(SEED_USER_IDS)})
            print("   ✅ 시드계정 포인트/젬 초기화 완료")
        except Exception as e:
            print(f"   ⚠️ 시드계정 초기화 오류: {e}")
        
        db.commit()
        
        # 7. 최종 상태 확인
        print("\n📊 최종 상태 확인:")
        users = db.query(User).all()
        print(f"   총 사용자 수: {len(users)}명")
        for user in users:
            print(f"   - {user.site_id}: {user.nickname} (포인트:{user.points}, 젬:{user.gems})")
        
        print("\n✅ 깨끗한 초기화 완료!")
        print("🎯 이제 시드계정들만 남아있고, 모든 가짜 데이터가 삭제되었습니다.")
        
    except Exception as e:
        print(f"❌ 초기화 실패: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    clean_reset()
