-- 전체 게임 스키마 생성 SQL (누락된 테이블들)
-- ===============================================
-- 1. 크래시 게임 테이블
-- ===============================================

-- crash_sessions 테이블 생성
CREATE TABLE IF NOT EXISTS crash_sessions (
    id SERIAL PRIMARY KEY,
    external_session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id),
    bet_amount INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    auto_cashout_multiplier DECIMAL(10,2),
    actual_multiplier DECIMAL(10,2),
    win_amount INTEGER DEFAULT 0,
    game_id VARCHAR(255) NOT NULL,
    max_multiplier DECIMAL(10,2),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL
);

-- crash_bets 테이블 생성
CREATE TABLE IF NOT EXISTS crash_bets (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES crash_sessions(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    bet_amount INTEGER NOT NULL,
    payout_amount INTEGER,
    cashout_multiplier DECIMAL(10,2),
    status VARCHAR(20) NOT NULL DEFAULT 'placed',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL
);

-- ===============================================
-- 2. 슬롯 게임 테이블
-- ===============================================

-- slot_sessions 테이블 (슬롯 게임 세션)
CREATE TABLE IF NOT EXISTS slot_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    bet_amount INTEGER NOT NULL,
    symbols VARCHAR(255) NOT NULL, -- JSON array of symbols
    win_amount INTEGER DEFAULT 0,
    is_jackpot BOOLEAN DEFAULT FALSE,
    multiplier DECIMAL(10,2) DEFAULT 1.0,
    status VARCHAR(20) NOT NULL DEFAULT 'completed',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL
);

-- slot_configurations 테이블 (슬롯 설정)
CREATE TABLE IF NOT EXISTS slot_configurations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    reel_count INTEGER NOT NULL DEFAULT 5,
    symbol_weights JSON NOT NULL, -- 심볼별 가중치
    payout_table JSON NOT NULL,   -- 배당표
    jackpot_threshold DECIMAL(10,4) DEFAULT 0.001,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL
);

-- ===============================================
-- 3. 가챠 게임 테이블 확장
-- ===============================================

-- gacha_configurations 테이블 (가챠 설정)
CREATE TABLE IF NOT EXISTS gacha_configurations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    cost_per_pull INTEGER NOT NULL DEFAULT 100,
    rarity_rates JSON NOT NULL, -- 등급별 확률
    item_pool JSON NOT NULL,    -- 아이템 풀
    daily_limit INTEGER DEFAULT 10,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL
);

-- gacha_items 테이블 (가챠 아이템)
CREATE TABLE IF NOT EXISTS gacha_items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    rarity VARCHAR(20) NOT NULL, -- COMMON, RARE, EPIC, LEGENDARY
    item_type VARCHAR(50) NOT NULL, -- CURRENCY, ITEM, BOOST, etc.
    value INTEGER DEFAULT 0,
    description TEXT,
    icon_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL
);

-- ===============================================
-- 4. 룰렛 게임 테이블
-- ===============================================

-- roulette_sessions 테이블 (룰렛 게임 세션)
CREATE TABLE IF NOT EXISTS roulette_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    bet_amount INTEGER NOT NULL,
    bet_type VARCHAR(20) NOT NULL, -- NUMBER, COLOR, ODD_EVEN, etc.
    bet_value VARCHAR(50), -- 베팅한 값 (숫자, 색상 등)
    winning_number INTEGER NOT NULL,
    winning_color VARCHAR(10), -- RED, BLACK, GREEN
    win_amount INTEGER DEFAULT 0,
    is_win BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL
);

-- roulette_configurations 테이블 (룰렛 설정)
CREATE TABLE IF NOT EXISTS roulette_configurations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    wheel_type VARCHAR(20) NOT NULL DEFAULT 'EUROPEAN', -- AMERICAN, EUROPEAN
    payout_multipliers JSON NOT NULL,
    max_bet_amount INTEGER DEFAULT 10000,
    min_bet_amount INTEGER DEFAULT 10,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL
);

-- ===============================================
-- 5. 블랙잭 게임 테이블
-- ===============================================

-- blackjack_sessions 테이블 (블랙잭 게임 세션)
CREATE TABLE IF NOT EXISTS blackjack_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    bet_amount INTEGER NOT NULL,
    player_cards JSON NOT NULL, -- 플레이어 카드 배열
    dealer_cards JSON NOT NULL, -- 딜러 카드 배열
    player_score INTEGER NOT NULL,
    dealer_score INTEGER NOT NULL,
    result VARCHAR(20) NOT NULL, -- WIN, LOSE, PUSH, BLACKJACK
    win_amount INTEGER DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'completed',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL
);

-- ===============================================
-- 6. 바카라 게임 테이블
-- ===============================================

-- baccarat_sessions 테이블 (바카라 게임 세션)
CREATE TABLE IF NOT EXISTS baccarat_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    bet_amount INTEGER NOT NULL,
    bet_type VARCHAR(20) NOT NULL, -- PLAYER, BANKER, TIE
    player_cards JSON NOT NULL,
    banker_cards JSON NOT NULL,
    player_score INTEGER NOT NULL,
    banker_score INTEGER NOT NULL,
    result VARCHAR(20) NOT NULL, -- PLAYER_WIN, BANKER_WIN, TIE
    win_amount INTEGER DEFAULT 0,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL
);

-- ===============================================
-- 7. 포커 게임 테이블
-- ===============================================

-- poker_sessions 테이블 (포커 게임 세션)
CREATE TABLE IF NOT EXISTS poker_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    bet_amount INTEGER NOT NULL,
    player_hand JSON NOT NULL, -- 플레이어 패
    dealer_hand JSON NOT NULL, -- 딜러 패
    player_hand_rank VARCHAR(50) NOT NULL, -- HIGH_CARD, PAIR, etc.
    dealer_hand_rank VARCHAR(50) NOT NULL,
    result VARCHAR(20) NOT NULL, -- WIN, LOSE, PUSH
    win_amount INTEGER DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'completed',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL
);

-- ===============================================
-- 8. 게임 통계 및 리더보드 테이블
-- ===============================================

-- game_leaderboards 테이블 (게임별 리더보드)
CREATE TABLE IF NOT EXISTS game_leaderboards (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    game_type VARCHAR(50) NOT NULL,
    score BIGINT NOT NULL DEFAULT 0,
    rank_position INTEGER,
    period_type VARCHAR(20) NOT NULL DEFAULT 'ALL_TIME', -- DAILY, WEEKLY, MONTHLY, ALL_TIME
    period_start DATE,
    period_end DATE,
    last_updated TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL,
    UNIQUE(user_id, game_type, period_type, period_start)
);

-- game_tournaments 테이블 (토너먼트)
CREATE TABLE IF NOT EXISTS game_tournaments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    game_type VARCHAR(50) NOT NULL,
    start_time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    end_time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    entry_fee INTEGER DEFAULT 0,
    prize_pool INTEGER DEFAULT 0,
    max_participants INTEGER,
    current_participants INTEGER DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'UPCOMING', -- UPCOMING, ACTIVE, COMPLETED, CANCELLED
    rules JSON,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL
);

-- tournament_participants 테이블 (토너먼트 참가자)
CREATE TABLE IF NOT EXISTS tournament_participants (
    id SERIAL PRIMARY KEY,
    tournament_id INTEGER NOT NULL REFERENCES game_tournaments(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    score BIGINT DEFAULT 0,
    rank_position INTEGER,
    prize_amount INTEGER DEFAULT 0,
    joined_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL,
    UNIQUE(tournament_id, user_id)
);

-- ===============================================
-- 인덱스 생성
-- ===============================================

-- Crash 게임 인덱스
CREATE INDEX IF NOT EXISTS idx_crash_sessions_user_id ON crash_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_crash_sessions_status ON crash_sessions(status);
CREATE INDEX IF NOT EXISTS idx_crash_sessions_created_at ON crash_sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_crash_bets_user_id ON crash_bets(user_id);
CREATE INDEX IF NOT EXISTS idx_crash_bets_session_id ON crash_bets(session_id);

-- Slot 게임 인덱스
CREATE INDEX IF NOT EXISTS idx_slot_sessions_user_id ON slot_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_slot_sessions_created_at ON slot_sessions(created_at);
CREATE INDEX IF NOT EXISTS idx_slot_sessions_is_jackpot ON slot_sessions(is_jackpot);

-- Gacha 게임 인덱스
CREATE INDEX IF NOT EXISTS idx_gacha_items_rarity ON gacha_items(rarity);
CREATE INDEX IF NOT EXISTS idx_gacha_items_item_type ON gacha_items(item_type);

-- Roulette 게임 인덱스
CREATE INDEX IF NOT EXISTS idx_roulette_sessions_user_id ON roulette_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_roulette_sessions_created_at ON roulette_sessions(created_at);

-- Blackjack 게임 인덱스
CREATE INDEX IF NOT EXISTS idx_blackjack_sessions_user_id ON blackjack_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_blackjack_sessions_created_at ON blackjack_sessions(created_at);

-- Baccarat 게임 인덱스
CREATE INDEX IF NOT EXISTS idx_baccarat_sessions_user_id ON baccarat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_baccarat_sessions_created_at ON baccarat_sessions(created_at);

-- Poker 게임 인덱스
CREATE INDEX IF NOT EXISTS idx_poker_sessions_user_id ON poker_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_poker_sessions_created_at ON poker_sessions(created_at);

-- 리더보드 인덱스
CREATE INDEX IF NOT EXISTS idx_leaderboards_game_type_period ON game_leaderboards(game_type, period_type, period_start);
CREATE INDEX IF NOT EXISTS idx_leaderboards_rank ON game_leaderboards(rank_position);
CREATE INDEX IF NOT EXISTS idx_leaderboards_score ON game_leaderboards(score DESC);

-- 토너먼트 인덱스
CREATE INDEX IF NOT EXISTS idx_tournaments_game_type ON game_tournaments(game_type);
CREATE INDEX IF NOT EXISTS idx_tournaments_status ON game_tournaments(status);
CREATE INDEX IF NOT EXISTS idx_tournaments_start_time ON game_tournaments(start_time);
CREATE INDEX IF NOT EXISTS idx_tournament_participants_score ON tournament_participants(score DESC);
