#!/usr/bin/env python3
"""
PrizeRoulette 게임 전용 데이터베이스 테이블 생성 스크립트

프론트엔드 PrizeRoulette.tsx 로직에 맞춘 데이터베이스 스키마:
- 일일 3회 스핀 제한
- 고정된 상품 목록 (코인, 젬, 특별아이템, 잭팟, 보너스 스핀)
- 확률 기반 보상 시스템
- 스핀 히스토리 추적
- 쿨다운 시스템
"""

import os
import psycopg2
from psycopg2.extras import Json
import json
from datetime import datetime, timedelta

def add_prize_roulette_tables():
    """PrizeRoulette 게임을 위한 테이블들을 추가합니다."""
    
    try:
        # 환경변수에서 데이터베이스 연결 정보 가져오기
        DB_HOST = os.getenv('DB_HOST', 'localhost')
        DB_PORT = os.getenv('DB_PORT', '5432')
        DB_NAME = os.getenv('DB_NAME', 'cc_webapp')
        DB_USER = os.getenv('DB_USER', 'cc_user')
        DB_PASSWORD = os.getenv('DB_PASSWORD', 'cc_password')
        
        # PostgreSQL 연결
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        
        cursor = conn.cursor()
        print("🎰 PrizeRoulette 데이터베이스 테이블 생성 시작...")
        
        # 1. 프라이즈 룰렛 상품 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS prize_roulette_prizes (
            id SERIAL PRIMARY KEY,
            prize_id VARCHAR(50) UNIQUE NOT NULL,
            name VARCHAR(100) NOT NULL,
            value INTEGER NOT NULL DEFAULT 0,
            color VARCHAR(7) NOT NULL,  -- HEX 색상 코드
            probability DECIMAL(6,5) NOT NULL,  -- 0.00001 ~ 1.00000
            icon VARCHAR(10),
            prize_type VARCHAR(20) NOT NULL DEFAULT 'COINS',  -- COINS, GEMS, SPECIAL, JACKPOT, BONUS
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        print("✅ 프라이즈 룰렛 상품 테이블 생성")
        
        # 2. 사용자별 일일 스핀 제한 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS prize_roulette_daily_limits (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            game_date DATE NOT NULL DEFAULT CURRENT_DATE,
            spins_used INTEGER DEFAULT 0,
            max_spins INTEGER DEFAULT 3,
            cooldown_expires TIMESTAMP,
            bonus_spins INTEGER DEFAULT 0,  -- 보너스 스핀으로 얻은 추가 스핀
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            UNIQUE(user_id, game_date)
        );
        """)
        print("✅ 일일 스핀 제한 테이블 생성")
        
        # 3. 프라이즈 룰렛 스핀 기록 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS prize_roulette_spins (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            spin_id VARCHAR(50) UNIQUE NOT NULL,  -- 고유 스핀 ID
            prize_id VARCHAR(50) NOT NULL,
            prize_won JSONB NOT NULL,  -- 당첨된 상품 정보 저장
            rotation_angle INTEGER NOT NULL,  -- 룰렛 최종 회전 각도
            animation_type VARCHAR(20) DEFAULT 'normal',  -- normal, jackpot, near_miss
            is_near_miss BOOLEAN DEFAULT FALSE,
            result_message TEXT,
            spin_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (prize_id) REFERENCES prize_roulette_prizes(prize_id)
        );
        """)
        print("✅ 스핀 기록 테이블 생성")
        
        # 4. 프라이즈 룰렛 사용자 통계 테이블
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS prize_roulette_user_stats (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            total_spins INTEGER DEFAULT 0,
            total_coins_won INTEGER DEFAULT 0,
            total_gems_won INTEGER DEFAULT 0,
            special_items_won INTEGER DEFAULT 0,
            jackpots_won INTEGER DEFAULT 0,
            bonus_spins_won INTEGER DEFAULT 0,
            best_streak INTEGER DEFAULT 0,
            current_streak INTEGER DEFAULT 0,
            last_spin_date DATE,
            lucky_number INTEGER DEFAULT 7,  -- 사용자별 럭키 넘버
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            UNIQUE(user_id)
        );
        """)
        print("✅ 사용자 통계 테이블 생성")
        
        # 5. 프라이즈 룰렛 설정 테이블 (관리자용)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS prize_roulette_config (
            id SERIAL PRIMARY KEY,
            config_key VARCHAR(50) UNIQUE NOT NULL,
            config_value JSONB NOT NULL,
            description TEXT,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        print("✅ 룰렛 설정 테이블 생성")
        
        # 인덱스 생성
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_roulette_daily_limits_user_date ON prize_roulette_daily_limits(user_id, game_date);",
            "CREATE INDEX IF NOT EXISTS idx_roulette_spins_user_timestamp ON prize_roulette_spins(user_id, spin_timestamp);",
            "CREATE INDEX IF NOT EXISTS idx_roulette_spins_prize ON prize_roulette_spins(prize_id);",
            "CREATE INDEX IF NOT EXISTS idx_roulette_stats_user ON prize_roulette_user_stats(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_roulette_prizes_active ON prize_roulette_prizes(is_active, probability);",
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        print("✅ 프라이즈 룰렛 인덱스 생성 완료")
        
        # 기본 상품 데이터 삽입 (PrizeRoulette.tsx의 PRIZES 배열 기반)
        prizes_data = [
            ('coins_100', '코인 100개', 100, '#FFD700', 0.35, '🪙', 'COINS'),
            ('coins_500', '코인 500개', 500, '#FF8C00', 0.25, '🪙', 'COINS'),
            ('gems_10', '젬 10개', 10, '#00CED1', 0.2, '💎', 'GEMS'),
            ('gems_50', '젬 50개', 50, '#9370DB', 0.1, '💎', 'GEMS'),
            ('special_item', '특별 아이템', 0, '#FF69B4', 0.085, '🎁', 'SPECIAL'),
            ('jackpot', '잭팟! 젬 200개', 200, '#FF0080', 0.015, '🎰', 'JACKPOT'),
            ('bonus', '보너스 스핀', 1, '#00FF88', 0.005, '🎁', 'BONUS')
        ]
        
        for prize_id, name, value, color, probability, icon, prize_type in prizes_data:
            cursor.execute("""
            INSERT INTO prize_roulette_prizes 
            (prize_id, name, value, color, probability, icon, prize_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (prize_id) DO UPDATE SET
                name = EXCLUDED.name,
                value = EXCLUDED.value,
                color = EXCLUDED.color,
                probability = EXCLUDED.probability,
                icon = EXCLUDED.icon,
                prize_type = EXCLUDED.prize_type,
                updated_at = CURRENT_TIMESTAMP;
            """, (prize_id, name, value, color, probability, icon, prize_type))
        
        print("✅ 기본 상품 데이터 삽입 완료")
        
        # 기본 룰렛 설정 데이터 삽입
        config_data = [
            ('daily_max_spins', {'value': 3}, '일일 최대 스핀 횟수'),
            ('spin_cooldown_minutes', {'value': 0}, '스핀 간 쿨다운 시간(분)'),
            ('jackpot_animation_enabled', {'value': True}, '잭팟 특별 애니메이션 활성화'),
            ('near_miss_probability', {'value': 0.05}, '니어미스 확률'),
            ('bonus_spin_multiplier', {'value': 1}, '보너스 스핀 배수'),
            ('roulette_enabled', {'value': True}, '프라이즈 룰렛 활성화 여부')
        ]
        
        for config_key, config_value, description in config_data:
            cursor.execute("""
            INSERT INTO prize_roulette_config 
            (config_key, config_value, description)
            VALUES (%s, %s, %s)
            ON CONFLICT (config_key) DO UPDATE SET
                config_value = EXCLUDED.config_value,
                description = EXCLUDED.description,
                updated_at = CURRENT_TIMESTAMP;
            """, (config_key, Json(config_value), description))
        
        print("✅ 기본 룰렛 설정 데이터 삽입 완료")
        
        # 테스트 사용자 '지민'에 대한 초기 데이터 생성
        cursor.execute("SELECT id FROM users WHERE nickname = '지민' LIMIT 1;")
        user_result = cursor.fetchone()
        
        if user_result:
            user_id = user_result[0]
            
            # 오늘 날짜로 스핀 제한 레코드 생성
            cursor.execute("""
            INSERT INTO prize_roulette_daily_limits (user_id, game_date, spins_used, max_spins)
            VALUES (%s, CURRENT_DATE, 0, 3)
            ON CONFLICT (user_id, game_date) DO NOTHING;
            """, (user_id,))
            
            # 사용자 통계 레코드 생성
            cursor.execute("""
            INSERT INTO prize_roulette_user_stats (user_id, total_spins, lucky_number)
            VALUES (%s, 0, %s)
            ON CONFLICT (user_id) DO NOTHING;
            """, (user_id, 7))
            
            print(f"✅ 테스트 사용자 '지민'(ID: {user_id})의 룰렛 데이터 초기화 완료")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("🎉 PrizeRoulette 게임 데이터베이스 확장 완료!")
        print("\n📊 생성된 테이블:")
        print("- prize_roulette_prizes: 상품 정보")
        print("- prize_roulette_daily_limits: 일일 스핀 제한")
        print("- prize_roulette_spins: 스핀 기록")
        print("- prize_roulette_user_stats: 사용자 통계")
        print("- prize_roulette_config: 룰렛 설정")
        
        return True
        
    except Exception as e:
        print(f"❌ PrizeRoulette 테이블 생성 실패: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False

if __name__ == "__main__":
    add_prize_roulette_tables()
