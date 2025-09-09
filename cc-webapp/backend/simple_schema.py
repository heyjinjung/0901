#!/usr/bin/env python3
"""
간단한 PostgreSQL 초기 스키마 생성
복잡한 마이그레이션 없이 기본 테이블만 생성
"""
import os
import psycopg2
from psycopg2 import sql
import time

def create_simple_schema():
    # 데이터베이스 연결 정보
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'cc_webapp'),
        'user': os.getenv('DB_USER', 'cc_user'),
        'password': os.getenv('DB_PASSWORD', 'cc_password')
    }
    
    print("🔗 PostgreSQL 연결 중...")
    
    # PostgreSQL 연결 대기
    for i in range(30):
        try:
            conn = psycopg2.connect(**db_config)
            print("✅ PostgreSQL 연결 성공!")
            break
        except Exception as e:
            print(f"⏳ 연결 시도 {i+1}/30: {e}")
            time.sleep(2)
    else:
        print("❌ PostgreSQL 연결 실패")
        return False
    
    try:
        cursor = conn.cursor()
        
        print("🏗️ 전체 데이터베이스 스키마 생성 중...")
        
        # 1. Users 테이블 (메인 사용자 테이블)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            site_id VARCHAR(50) UNIQUE NOT NULL,
            nickname VARCHAR(50) UNIQUE NOT NULL,
            phone_number VARCHAR(20) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            invite_code VARCHAR(6) NOT NULL,
            cyber_token_balance INTEGER DEFAULT 200,
            premium_gems INTEGER DEFAULT 0,
            rank VARCHAR(20) DEFAULT 'STANDARD',
            vip_tier VARCHAR(20) DEFAULT 'STANDARD',
            is_active BOOLEAN DEFAULT TRUE,
            is_verified BOOLEAN DEFAULT FALSE,
            is_adult_verified BOOLEAN DEFAULT FALSE,
            profile_image VARCHAR(500),
            bio VARCHAR(500),
            birth_date TIMESTAMP,
            gender VARCHAR(10),
            experience_points INTEGER DEFAULT 0,
            battlepass_level INTEGER DEFAULT 1,
            battlepass_xp INTEGER DEFAULT 0,
            total_spent DECIMAL(10,2) DEFAULT 0.00,
            streak_count INTEGER DEFAULT 0,
            login_count INTEGER DEFAULT 0,
            corporate_visit_count INTEGER DEFAULT 0,
            last_corporate_visit TIMESTAMP,
            avg_session_duration INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login_at TIMESTAMP
        );
        """)
        print("✅ Users 테이블 생성")

        # 2. Invite Codes 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS invite_codes (
            id SERIAL PRIMARY KEY,
            code VARCHAR(6) UNIQUE NOT NULL,
            max_uses INTEGER DEFAULT 1,
            current_uses INTEGER DEFAULT 0,
            expires_at TIMESTAMP,
            created_by_user_id INTEGER REFERENCES users(id),
            used_by_user_id INTEGER REFERENCES users(id),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        print("✅ Invite Codes 테이블 생성")

        # 3. User Sessions 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_sessions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            session_token VARCHAR(255) UNIQUE NOT NULL,
            refresh_token VARCHAR(255) UNIQUE,
            expires_at TIMESTAMP NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        print("✅ User Sessions 테이블 생성")

        # 4. Login Attempts 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS login_attempts (
            id SERIAL PRIMARY KEY,
            phone_number VARCHAR(20) NOT NULL,
            ip_address VARCHAR(45),
            user_agent TEXT,
            success BOOLEAN DEFAULT FALSE,
            failure_reason VARCHAR(255),
            attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        print("✅ Login Attempts 테이블 생성")

        # 5. Refresh Tokens 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS refresh_tokens (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            token VARCHAR(255) UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            is_revoked BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        print("✅ Refresh Tokens 테이블 생성")

        # 6. Security Events 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS security_events (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            event_type VARCHAR(50) NOT NULL,
            ip_address VARCHAR(45),
            user_agent TEXT,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        print("✅ Security Events 테이블 생성")

        # 7. User Actions 테이블 (게임 행동 추적)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_actions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            action_type VARCHAR(50) NOT NULL,
            target_id VARCHAR(100),
            details JSONB,
            reward_amount INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        print("✅ User Actions 테이블 생성")

        # 8. User Rewards 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_rewards (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            reward_type VARCHAR(50) NOT NULL,
            amount INTEGER NOT NULL,
            source VARCHAR(50),
            details JSONB,
            claimed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        print("✅ User Rewards 테이블 생성")

        # 9. Game Sessions 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_sessions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            session_type VARCHAR(50) NOT NULL,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            duration_seconds INTEGER,
            tokens_earned INTEGER DEFAULT 0,
            tokens_spent INTEGER DEFAULT 0,
            data JSONB
        );
        """)
        print("✅ Game Sessions 테이블 생성")

        # 10. User Activity 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_activity (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            activity_type VARCHAR(50) NOT NULL,
            activity_data JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        print("✅ User Activity 테이블 생성")

        # 11. Rewards 테이블 (보상 정의)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS rewards (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            reward_type VARCHAR(50) NOT NULL,
            amount INTEGER NOT NULL,
            rarity VARCHAR(20) DEFAULT 'COMMON',
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        print("✅ Rewards 테이블 생성")

        # 12. User Segments 테이블 (사용자 세분화)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_segments (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            rfm_group VARCHAR(50),
            ltv_score DECIMAL(10,2),
            risk_profile VARCHAR(50),
            behavioral_tags JSONB,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        print("✅ User Segments 테이블 생성")

        # 13. Battle Pass 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS battle_pass (
            id SERIAL PRIMARY KEY,
            season_name VARCHAR(100) NOT NULL,
            start_date TIMESTAMP NOT NULL,
            end_date TIMESTAMP NOT NULL,
            max_level INTEGER DEFAULT 100,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        print("✅ Battle Pass 테이블 생성")

        # 14. Battle Pass Progress 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS battle_pass_progress (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            battle_pass_id INTEGER NOT NULL REFERENCES battle_pass(id) ON DELETE CASCADE,
            current_level INTEGER DEFAULT 1,
            current_xp INTEGER DEFAULT 0,
            is_premium BOOLEAN DEFAULT FALSE,
            purchased_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        print("✅ Battle Pass Progress 테이블 생성")

        # 15. Battle Pass Rewards 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS battle_pass_rewards (
            id SERIAL PRIMARY KEY,
            battle_pass_id INTEGER NOT NULL REFERENCES battle_pass(id) ON DELETE CASCADE,
            level_required INTEGER NOT NULL,
            reward_type VARCHAR(50) NOT NULL,
            reward_amount INTEGER NOT NULL,
            is_premium_only BOOLEAN DEFAULT FALSE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        print("✅ Battle Pass Rewards 테이블 생성")

        # 16. Battle Pass Claimed 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS battle_pass_claimed (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            battle_pass_reward_id INTEGER NOT NULL REFERENCES battle_pass_rewards(id) ON DELETE CASCADE,
            claimed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        print("✅ Battle Pass Claimed 테이블 생성")

        # 17. Gacha Pool 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS gacha_pool (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            cost_type VARCHAR(20) NOT NULL,
            cost_amount INTEGER NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        print("✅ Gacha Pool 테이블 생성")

        # 18. Gacha Items 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS gacha_items (
            id SERIAL PRIMARY KEY,
            gacha_pool_id INTEGER NOT NULL REFERENCES gacha_pool(id) ON DELETE CASCADE,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            rarity VARCHAR(20) NOT NULL,
            drop_rate DECIMAL(5,4) NOT NULL,
            reward_type VARCHAR(50) NOT NULL,
            reward_amount INTEGER NOT NULL,
            image_url VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        print("✅ Gacha Items 테이블 생성")

        # 19. Gacha Log 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS gacha_log (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            gacha_pool_id INTEGER NOT NULL REFERENCES gacha_pool(id) ON DELETE CASCADE,
            gacha_item_id INTEGER NOT NULL REFERENCES gacha_items(id) ON DELETE CASCADE,
            cost_paid INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        print("✅ Gacha Log 테이블 생성")

        # 20. Adult Content 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS adult_content (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            content_type VARCHAR(50) NOT NULL,
            unlock_tier VARCHAR(20) NOT NULL,
            unlock_cost INTEGER DEFAULT 0,
            thumbnail_url VARCHAR(500),
            content_url VARCHAR(500),
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        print("✅ Adult Content 테이블 생성")

        # 21. VIP Access Log 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS vip_access_log (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            content_id INTEGER NOT NULL REFERENCES adult_content(id) ON DELETE CASCADE,
            access_type VARCHAR(50) NOT NULL,
            tokens_spent INTEGER DEFAULT 0,
            accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        print("✅ VIP Access Log 테이블 생성")

        # 22. Purchases 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchases (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            item_name VARCHAR(100) NOT NULL,
            item_type VARCHAR(50) NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            currency VARCHAR(10) NOT NULL,
            payment_method VARCHAR(50),
            transaction_id VARCHAR(100) UNIQUE,
            status VARCHAR(20) DEFAULT 'PENDING',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        );
        """)
        print("✅ Purchases 테이블 생성")

        # 23. Shop 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS shop (
            id SERIAL PRIMARY KEY,
            item_name VARCHAR(100) NOT NULL,
            description TEXT,
            item_type VARCHAR(50) NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            currency VARCHAR(10) NOT NULL,
            discount_percent INTEGER DEFAULT 0,
            stock_quantity INTEGER DEFAULT -1,
            is_featured BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE,
            image_url VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        print("✅ Shop 테이블 생성")

        # 24. Notifications 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title VARCHAR(200) NOT NULL,
            message TEXT NOT NULL,
            notification_type VARCHAR(50) NOT NULL,
            is_read BOOLEAN DEFAULT FALSE,
            data JSONB,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            read_at TIMESTAMP
        );
        """)
        print("✅ Notifications 테이블 생성")

        # 모든 인덱스 생성
        print("🔍 인덱스 생성 중...")
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_nickname ON users(nickname);",
            "CREATE INDEX IF NOT EXISTS idx_users_site_id ON users(site_id);",
            "CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone_number);",
            "CREATE INDEX IF NOT EXISTS idx_users_rank ON users(rank);",
            "CREATE INDEX IF NOT EXISTS idx_invite_codes_code ON invite_codes(code);",
            "CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token);",
            "CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_login_attempts_phone ON login_attempts(phone_number);",
            "CREATE INDEX IF NOT EXISTS idx_user_actions_user_id ON user_actions(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_user_actions_type ON user_actions(action_type);",
            "CREATE INDEX IF NOT EXISTS idx_user_rewards_user_id ON user_rewards(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_game_sessions_user_id ON game_sessions(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_user_segments_user_id ON user_segments(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_battlepass_progress_user_id ON battle_pass_progress(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_gacha_log_user_id ON gacha_log(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_notifications_user_id ON notifications(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_purchases_user_id ON purchases(user_id);"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        print("✅ 모든 인덱스 생성 완료")
        
        
        # 테스트 데이터 삽입
        print("🎯 테스트 데이터 삽입 중...")
        
        # 기본 초대 코드들
        invite_codes = [
            ('INV001', 100, True),
            ('INV002', 50, True),
            ('WELCOM', 1000, True),  # 6글자로 수정
            ('VIP001', 10, True),
            ('SPEC01', 20, True)     # 6글자로 수정
        ]
        
        for code, max_uses, is_active in invite_codes:
            cursor.execute("""
            INSERT INTO invite_codes (code, max_uses, is_active)
            VALUES (%s, %s, %s)
            ON CONFLICT (code) DO NOTHING;
            """, (code, max_uses, is_active))
        
        # 테스트 사용자들 (올바른 해시 사용)
        import hashlib
        def simple_hash(password):
            return hashlib.sha256(password.encode()).hexdigest()[:20]  # 20글자로 제한
        
        test_users = [
            ('jimin_001', '지민', '010-1234-5678', simple_hash('password123'), 'INV001', 1000, 'PREMIUM'),
            ('admin_001', '관리자', '010-0000-0000', simple_hash('admin123'), 'INV001', 5000, 'ADMIN'),
            ('test_001', '테스터1', '010-1111-1111', simple_hash('test123'), 'INV002', 500, 'VIP'),
            ('demo_001', '데모유저', '010-2222-2222', simple_hash('demo123'), 'WELCOM', 200, 'STANDARD')
        ]
        
        for site_id, nickname, phone, password_hash, invite_code, balance, rank in test_users:
            cursor.execute("""
            INSERT INTO users (site_id, nickname, phone_number, password_hash, invite_code, cyber_token_balance, rank)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (site_id) DO NOTHING;
            """, (site_id, nickname, phone, password_hash, invite_code, balance, rank))
        
        # 기본 배틀패스 시즌
        cursor.execute("""
        INSERT INTO battle_pass (season_name, start_date, end_date, max_level, is_active)
        VALUES ('시즌 1: 네온 런', '2025-07-01', '2025-09-30', 100, TRUE)
        ON CONFLICT DO NOTHING;
        """)
        
        # 기본 가챠 풀
        cursor.execute("""
        INSERT INTO gacha_pool (name, description, cost_type, cost_amount, is_active)
        VALUES ('럭키 박스', '일반 럭키 박스 - 다양한 보상을 획득하세요!', 'CYBER_TOKEN', 100, TRUE)
        ON CONFLICT DO NOTHING;
        """)
        
        # 기본 상점 아이템들
        shop_items = [
            ('프리미엄 젬 100개', '프리미엄 화폐 100개', 'PREMIUM_CURRENCY', 9.99, 'USD'),
            ('프리미엄 젬 500개', '프리미엄 화폐 500개 + 보너스 50개', 'PREMIUM_CURRENCY', 49.99, 'USD'),
            ('사이버 토큰 1000개', '게임 내 화폐 1000개', 'CYBER_TOKEN', 4.99, 'USD'),
            ('VIP 멤버십 1개월', 'VIP 혜택 1개월', 'VIP_MEMBERSHIP', 19.99, 'USD')
        ]
        
        for item_name, description, item_type, price, currency in shop_items:
            cursor.execute("""
            INSERT INTO shop (item_name, description, item_type, price, currency, is_active)
            VALUES (%s, %s, %s, %s, %s, TRUE)
            ON CONFLICT DO NOTHING;
            """, (item_name, description, item_type, price, currency))
        
        # 기본 보상들
        rewards = [
            ('데일리 로그인', '매일 로그인 보상', 'CYBER_TOKEN', 50, 'COMMON'),
            ('첫 스핀 보너스', '첫 번째 스핀 보너스', 'CYBER_TOKEN', 100, 'UNCOMMON'),
            ('연속 로그인 7일', '7일 연속 로그인 보상', 'PREMIUM_GEMS', 10, 'RARE'),
            ('VIP 웰컴 보너스', 'VIP 가입 환영 보상', 'CYBER_TOKEN', 500, 'EPIC')
        ]
        
        for name, description, reward_type, amount, rarity in rewards:
            cursor.execute("""
            INSERT INTO rewards (name, description, reward_type, amount, rarity, is_active)
            VALUES (%s, %s, %s, %s, %s, TRUE)
            ON CONFLICT DO NOTHING;
            """, (name, description, reward_type, amount, rarity))
        
        conn.commit()
        print("✅ 데이터베이스 스키마 생성 완료!")
        print("✅ 테스트 사용자 '지민' 추가 완료!")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 스키마 생성 실패: {e}")
        return False

if __name__ == "__main__":
    create_simple_schema()
