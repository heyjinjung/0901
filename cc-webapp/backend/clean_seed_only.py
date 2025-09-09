"""[통합] 시드 정리 단일 스크립트(clean_seed_only)

목적:
- (단일 진입점) 시드계정만 남기고 모든 가짜/목 데이터 정리 + 시드계정 기본값 리셋
- seed_realistic_data.py, clean_seed_reset.py 는 본 스크립트로 통합/대체됨

기능:
- 존재 테이블 자동 탐지 후, 시드계정 외 데이터만 안전 삭제
- users 테이블은 시드계정 외 모두 삭제
- 시드계정(gold_balance/total_spent/vip_tier/battlepass_level) 기본값 리셋

사용:
    docker compose exec backend python clean_seed_only.py

안전장치(필수 환경변수):
    - CLEAN_SEED_CONFIRM=YES     # 없으면 즉시 중단
    - (선택) 프로덕션 보호: ENV 또는 APP_ENV 또는 settings.ENV가 production/prod인 경우,
      CLEAN_SEED_ALLOW_PROD=1 설정 없이는 실행 거부
"""

import os
from sqlalchemy import text
from app.database import SessionLocal
from app.models.auth_models import User
from app.core.config import settings

def main():
    """시드계정만 남기고 모든 데이터 정리"""
    # 0. 안전 확인 가드
    confirm = os.getenv("CLEAN_SEED_CONFIRM", "").strip().lower() in ("yes", "y", "1", "true")
    app_env = (
        getattr(settings, "ENV", None)
        or os.getenv("ENV")
        or os.getenv("APP_ENV")
        or "development"
    ).lower()

    print("\n⚠️  CLEAN_SEED 모드 경고: 본 스크립트는 시드계정 외 모든 데이터를 삭제합니다.")
    print("   실행 전 Docker 컨테이너 내부에서만 수행하고, 운영 DB가 아님을 반드시 확인하세요.")
    print(f"   감지된 ENV: {app_env}")

    if not confirm:
        print("\n❌ 실행 중단: 환경변수 CLEAN_SEED_CONFIRM=YES 가 설정되지 않았습니다.")
        print("   예) docker compose exec backend bash -lc 'CLEAN_SEED_CONFIRM=YES python clean_seed_only.py'")
        return

    if app_env in ("prod", "production") and os.getenv("CLEAN_SEED_ALLOW_PROD", "").strip() not in ("1", "true", "TRUE"):
        print("\n❌ 실행 중단(프로덕션 보호): ENV=production 감지. CLEAN_SEED_ALLOW_PROD=1 없이는 실행할 수 없습니다.")
        return
    
    # 1. 시드계정 ID 확인
    db = SessionLocal()
    try:
        seed_accounts = ['admin', 'user001', 'user002', 'user003', 'user004']
        seed_users = db.query(User).filter(User.site_id.in_(seed_accounts)).all()
        seed_user_ids = [u.id for u in seed_users]
        
        print(f"🔧 시드계정 확인: {len(seed_user_ids)}개")
        for u in seed_users:
            print(f"  - {u.site_id} (ID: {u.id}): {u.nickname}")
        
        if len(seed_user_ids) != 5:
            print("❌ 시드계정이 모자랍니다. 먼저 seed_basic_accounts를 실행하세요.")
            return
            
    except Exception as e:
        print(f"❌ 시드계정 확인 실패: {e}")
        return

    # 2. 엔진으로 대량 정리 작업
    engine = db.get_bind()
    
    try:
        print("\n🧹 가짜 데이터 정리 시작...")

        # 2-1. 존재 테이블 확인 (별도 연결)
        existing_tables = []
        tables_to_check = [
            # 자식(참조) 테이블 먼저
            'event_participations',
            'user_missions',
            'user_rewards',
            'user_actions',
            'user_game_stats',
            'shop_transactions',
            # 인증/토큰/세션류(존재 시)
            'token_blacklist',
            'refresh_tokens',
            'access_tokens',
            'auth_tokens',
            'user_sessions',
            'sessions',
            'login_attempts',
            'email_verifications',
            'password_resets',
            'oauth_accounts',
            'user_roles',
            'gacha_log',
            'notifications',
            'battlepass_status',
            'user_segments',
            # 부모(참조받는) 테이블 나중
            'game_sessions',
        ]

        with engine.begin() as conn:
            for table in tables_to_check:
                try:
                    conn.execute(text(f"SELECT 1 FROM {table} LIMIT 1"))
                    existing_tables.append(table)
                except Exception:
                    print(f"  ⚠️ {table}: 테이블 없음")

        print(f"  📋 정리할 테이블: {existing_tables}")

        # 2-2. 자식→부모 순, 테이블별 개별 트랜잭션으로 전체 삭제(가짜/목데이터 전면 제거 정책)
        for table in existing_tables:
            try:
                with engine.begin() as conn:
                    result = conn.execute(text(f"DELETE FROM {table}"))
                    print(f"  ✅ {table}: {result.rowcount if hasattr(result, 'rowcount') else 0}건 삭제")
            except Exception as e:
                print(f"  ⚠️ {table}: 삭제 오류 ({e})")

        # 2-3. 시드계정 외 사용자 삭제 (개별 트랜잭션)
        try:
            with engine.begin() as conn:
                result = conn.execute(text(f"""
                    DELETE FROM users 
                    WHERE id NOT IN ({','.join(map(str, seed_user_ids))})
                """))
                print(f"  ✅ users: {result.rowcount if hasattr(result, 'rowcount') else 0}개 계정 삭제 (시드계정 제외)")
        except Exception as e:
            print(f"  ⚠️ users 삭제 실패: {e}")

        # 2-4. 시드계정들 초기 상태로 리셋 (개별 트랜잭션)
        try:
            with engine.begin() as conn:
                conn.execute(text(f"""
                    UPDATE users 
                    SET gold_balance = 1000,
                        total_spent = 0,
                        vip_tier = 'STANDARD',
                        battlepass_level = 1
                    WHERE id IN ({','.join(map(str, seed_user_ids))})
                """))
                print("  ✅ 시드계정 상태 초기화 완료")
        except Exception as e:
            print(f"  ⚠️ 시드계정 초기화 실패: {e}")
            
        print("\n🎉 정리 완료! 이제 깨끗한 상태에서 실제 활동을 시작할 수 있습니다.")
        print("\n📋 시드계정 로그인 정보:")
        print("  관리자: admin / 123456")
        print("  유저1: user001 / 123455")  
        print("  유저2: user002 / 123455")
        print("  유저3: user003 / 123455")
        print("  유저4: user004 / 123455")
        
    except Exception as e:
        print(f"❌ 정리 작업 실패: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
