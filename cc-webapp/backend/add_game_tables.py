#!/usr/bin/env python3
"""
게임 로직용 데이터베이스 스키마 확장
슬롯, 룰렛, 가위바위보, 가챠 게임 테이블 추가
"""
import os
import psycopg2
import json
import time

def add_game_tables():
    # 데이터베이스 연결 정보
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'cc_webapp'),
        'user': os.getenv('DB_USER', 'cc_user'),
        'password': os.getenv('DB_PASSWORD', 'cc_password')
    }
    
    print("🎮 게임 로직 테이블 추가 중...")
    
    try:
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # 1. 게임 세션 상세 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_sessions_detail (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            game_type VARCHAR(50) NOT NULL,  -- SLOT, ROULETTE, RPS, GACHA
            session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            session_end TIMESTAMP,
            total_rounds INTEGER DEFAULT 0,
            total_bet INTEGER DEFAULT 0,
            total_win INTEGER DEFAULT 0,
            net_result INTEGER DEFAULT 0,
            daily_rounds_used INTEGER DEFAULT 0,  -- 일일 사용 횟수
            max_daily_rounds INTEGER DEFAULT 30,  -- 일일 최대 횟수
            status VARCHAR(20) DEFAULT 'active',  -- active, completed
            session_data JSONB
        );
        """)
        print("✅ 게임 세션 상세 테이블 생성")
        
        # 2. 게임 라운드 결과 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_rounds (
            id SERIAL PRIMARY KEY,
            session_id INTEGER NOT NULL REFERENCES game_sessions_detail(id) ON DELETE CASCADE,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            game_type VARCHAR(50) NOT NULL,
            round_number INTEGER NOT NULL,
            bet_amount INTEGER NOT NULL,
            win_amount INTEGER DEFAULT 0,
            result_type VARCHAR(50),  -- WIN, LOSE, BONUS, JACKPOT
            game_result JSONB,  -- 게임별 상세 결과
            probability_used DECIMAL(5,4),  -- 사용된 확률
            streak_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        print("✅ 게임 라운드 결과 테이블 생성")
        
        # 3. 일일 게임 제한 관리 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_game_limits (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            game_date DATE DEFAULT CURRENT_DATE,
            slot_rounds_used INTEGER DEFAULT 0,
            slot_max_rounds INTEGER DEFAULT 30,
            roulette_rounds_used INTEGER DEFAULT 0,
            roulette_max_rounds INTEGER DEFAULT 10,
            rps_rounds_used INTEGER DEFAULT 0,
            rps_max_rounds INTEGER DEFAULT 3,  -- VIP는 5로 업데이트
            gacha_rounds_used INTEGER DEFAULT 0,
            gacha_max_rounds INTEGER DEFAULT 3,  -- VIP는 5로 업데이트
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            UNIQUE(user_id, game_date)
        );
        """)
        print("✅ 일일 게임 제한 관리 테이블 생성")
        
        # 4. 게임 확률 설정 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_probability_config (
            id SERIAL PRIMARY KEY,
            game_type VARCHAR(50) NOT NULL,
            config_name VARCHAR(100) NOT NULL,
            probability_data JSONB NOT NULL,
            house_edge DECIMAL(5,4) DEFAULT 0.10,
            min_bet INTEGER DEFAULT 5000,
            max_bet INTEGER DEFAULT 10000,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        print("✅ 게임 확률 설정 테이블 생성")
        
        # 5. 유저 스트릭 및 통계 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_game_stats (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            game_type VARCHAR(50) NOT NULL,
            current_streak INTEGER DEFAULT 0,
            best_streak INTEGER DEFAULT 0,
            total_rounds INTEGER DEFAULT 0,
            total_wins INTEGER DEFAULT 0,
            total_losses INTEGER DEFAULT 0,
            total_bet INTEGER DEFAULT 0,
            total_win INTEGER DEFAULT 0,
            win_rate DECIMAL(5,4) DEFAULT 0.0000,
            last_played TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            UNIQUE(user_id, game_type)
        );
        """)
        print("✅ 유저 게임 통계 테이블 생성")
        
        # 인덱스 생성
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_game_sessions_user_type ON game_sessions_detail(user_id, game_type);",
            "CREATE INDEX IF NOT EXISTS idx_game_rounds_session ON game_rounds(session_id, round_number);",
            "CREATE INDEX IF NOT EXISTS idx_game_rounds_user_game ON game_rounds(user_id, game_type, created_at);",
            "CREATE INDEX IF NOT EXISTS idx_daily_limits_user_date ON daily_game_limits(user_id, game_date);",
            "CREATE INDEX IF NOT EXISTS idx_game_stats_user ON user_game_stats(user_id, game_type);",
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        print("✅ 게임 테이블 인덱스 생성 완료")
        
        # 기본 게임 확률 설정 데이터 삽입
        game_configs = [
            # 슬롯 머신 설정
            ('SLOT', 'basic_slot', {
                'win_probability': 0.15,
                'house_edge': 0.85,
                'payout_table': {
                    'lose': 0,
                    'small_win': 1.5,
                    'medium_win': 3.0,
                    'big_win': 10.0,
                    'jackpot': 50.0
                },
                'probability_distribution': {
                    'lose': 0.85,
                    'small_win': 0.10,
                    'medium_win': 0.04,
                    'big_win': 0.009,
                    'jackpot': 0.001
                }
            }, 0.85, 5000, 10000),
            
            # 룰렛 설정
            ('ROULETTE', 'european_roulette', {
                'house_edge': 0.10,
                'bet_types': {
                    'red_black': {'probability': 0.4865, 'payout': 2.0},
                    'odd_even': {'probability': 0.4865, 'payout': 2.0},
                    'single_number': {'probability': 0.027, 'payout': 36.0}
                }
            }, 0.10, 5000, 10000),
            
            # 가위바위보 설정
            ('RPS', 'basic_rps', {
                'house_edge': 0.12,
                'win_probability': 0.33,
                'lose_probability': 0.33,
                'draw_probability': 0.34,
                'payout_win': 1.88,  # 약간 하우스 유리하게
                'payout_draw': 1.0
            }, 0.12, 5000, 10000),
            
            # 가챠 설정
            ('GACHA', 'premium_gacha', {
                'house_edge': 1.0,  # 100% 수익
                'cost_per_spin': 50000,
                'reward_table': {
                    'common': {'probability': 0.60, 'value': 10000},
                    'uncommon': {'probability': 0.25, 'value': 25000},
                    'rare': {'probability': 0.10, 'value': 60000},
                    'epic': {'probability': 0.04, 'value': 150000},
                    'legendary': {'probability': 0.01, 'value': 500000}
                }
            }, 1.0, 50000, 50000)
        ]
        
        for game_type, config_name, prob_data, house_edge, min_bet, max_bet in game_configs:
            cursor.execute("""
            INSERT INTO game_probability_config 
            (game_type, config_name, probability_data, house_edge, min_bet, max_bet)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING;
            """, (game_type, config_name, json.dumps(prob_data), house_edge, min_bet, max_bet))
        
        print("✅ 기본 게임 확률 설정 데이터 삽입 완료")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("🎉 게임 로직 데이터베이스 확장 완료!")
        return True
        
    except Exception as e:
        print(f"❌ 게임 테이블 생성 실패: {e}")
        return False

if __name__ == "__main__":
    add_game_tables()
