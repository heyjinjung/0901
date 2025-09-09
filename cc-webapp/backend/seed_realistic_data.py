"""가짜 데이터 정리 - 시드계정만 남기기

목적: 모든 가짜 시드 데이터 삭제, 시드계정만 깨끗하게 유지
사용: docker compose exec backend python seed_realistic_data.py
"""

import os
from sqlalchemy import text, create_engine
from app.database import SessionLocal
from app.models.auth_models import User

def get_seed_user_ids():
    """실제 시드계정들의 user_id 가져오기"""
    db = SessionLocal()
    try:
        users = db.query(User).filter(
            User.site_id.in_(['admin','user001','user002','user003','user004'])
        ).all()
        return {u.site_id: u.id for u in users}
    finally:
        db.close()

def clean_all_fake_data():
    """모든 가짜 데이터 정리"""
    
    DB_URL = os.getenv("DATABASE_URL") or "postgresql://cc_user:cc_password@postgres:5432/cc_webapp"
    engine = create_engine(DB_URL)
    
    with engine.begin() as conn:
        print("🧹 모든 가짜 데이터 정리 중...")
        
        # 1. 모든 게임 세션 삭제 (seed- 접두사 있는 것들)
        result1 = conn.execute(text("""
            DELETE FROM game_sessions 
            WHERE external_session_id LIKE 'seed-%'
        """))
        print(f"   - 가짜 게임세션 삭제: {result1.rowcount}개")
        
        # 2. 시드가 아닌 상점 거래들 조건부 삭제 (필요시)
        # 우선 보존하고 나중에 결정
        
        print("✅ 가짜 데이터 정리 완료!")

def reset_seed_accounts():
    """시드계정들 기본 상태로 리셋"""
    
    seed_users = get_seed_user_ids()
    print(f"🔄 시드계정 리셋: {list(seed_users.keys())}")
    
    db = SessionLocal()
    try:
        for site_id, user_id in seed_users.items():
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                # 기본값으로 리셋
                user.gold_balance = 1000  # 기본 골드
                user.total_spent = 0
                # user.gems = 100  # gems 컬럼이 있다면
                
        db.commit()
        print("✅ 시드계정 기본 상태 리셋 완료!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 시드계정 리셋 실패: {e}")
    finally:
        db.close()

def show_current_status():
    """현재 시드계정들 상태 출력"""
    
    seed_users = get_seed_user_ids()
    
    DB_URL = os.getenv("DATABASE_URL") or "postgresql://cc_user:cc_password@postgres:5432/cc_webapp"
    engine = create_engine(DB_URL)
    
    print("\n📊 현재 시드계정 상태:")
    print("-" * 50)
    
    with engine.begin() as conn:
        for site_id, user_id in seed_users.items():
            # 게임 세션 수
            game_count = conn.execute(text("""
                SELECT COUNT(*) FROM game_sessions WHERE user_id = :uid
            """), {"uid": user_id}).scalar()
            
            # 상점 거래 수와 총액
            shop_result = conn.execute(text("""
                SELECT COUNT(*), COALESCE(SUM(amount), 0) 
                FROM shop_transactions WHERE user_id = :uid
            """), {"uid": user_id}).fetchone()
            
            shop_count = shop_result[0] if shop_result else 0
            total_spent = shop_result[1] if shop_result else 0
            
            print(f"{site_id:>8}: 게임 {game_count:>3}개 | 구매 {shop_count:>3}개 | 총 {total_spent:>6,}원")

if __name__ == '__main__':
    print("🚀 깨끗한 시드계정 환경 설정 시작\n")
    
    # 1. 가짜 데이터 정리
    clean_all_fake_data()
    
    # 2. 시드계정 기본 상태 리셋
    reset_seed_accounts()
    
    # 3. 현재 상태 출력
    show_current_status()
    
    print("\n✅ 완료! 이제 시드계정들로 실제 활동하시면 정직하게 반영됩니다!")
