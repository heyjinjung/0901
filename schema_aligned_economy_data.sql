-- 🎯 실제 스키마에 맞춘 현실적인 경제구조 테스트 데이터 생성
-- 실제 DB 컬럼명에 맞춰서 수정된 버전

-- ===== STEP 1: 시드계정들을 현실적인 경제 활동 상태로 설정 =====

-- 어드민 (id=3): 관리자, 모든 기능 테스트용
UPDATE users SET 
    gold_balance = 100000,       -- 충분한 골드 (관리 테스트용)
    battlepass_level = 50,       -- 높은 배틀패스
    total_spent = 50000,         -- 상당한 지출 이력
    vip_tier = 'PREMIUM',        -- VIP 등급
    vip_points = 5000,           -- 높은 VIP 포인트
    last_login = NOW(),          -- 최근 로그인
    updated_at = NOW()
WHERE id = 3;

-- 유저01 (id=4): 헤비 게이머, 높은 활동
UPDATE users SET 
    gold_balance = 25000,        -- 충분한 골드
    battlepass_level = 35,       
    total_spent = 30000,         -- 높은 지출
    vip_tier = 'VIP',           -- VIP 사용자
    vip_points = 1000,           
    last_login = NOW() - INTERVAL '1 day',
    updated_at = NOW()
WHERE id = 4;

-- 유저02 (id=5): 중간 사용자, 균형잡힌 활동
UPDATE users SET 
    gold_balance = 8000,         -- 중간 골드
    battlepass_level = 15,       
    total_spent = 12000,         -- 적당한 지출
    vip_tier = 'STANDARD',      -- 일반 사용자
    vip_points = 200,            
    last_login = NOW() - INTERVAL '2 days',
    updated_at = NOW()
WHERE id = 5;

-- 유저03 (id=6): 라이트 게이머, 가챠 중심
UPDATE users SET 
    gold_balance = 3000,         -- 낮은 골드 (가챠로 소모)
    battlepass_level = 8,        
    total_spent = 15000,         -- 가챠에 많이 소모
    vip_tier = 'STANDARD',
    vip_points = 50,             
    last_login = NOW() - INTERVAL '3 days',
    updated_at = NOW()
WHERE id = 6;

-- 유저04 (id=7): 신규 사용자, 초기 활동
UPDATE users SET 
    gold_balance = 2500,         -- 초기 골드 + 약간의 활동
    battlepass_level = 3,        
    total_spent = 1500,          -- 적은 지출
    vip_tier = 'STANDARD',
    vip_points = 0,              
    last_login = NOW() - INTERVAL '1 day',
    updated_at = NOW()
WHERE id = 7;

-- ===== STEP 2: 현실적인 게임 통계 데이터 생성 =====

-- 기존 game_stats 데이터 삭제 (시드계정들 것만)
DELETE FROM game_stats WHERE user_id IN (3, 4, 5, 6, 7);

-- 어드민 게임 통계 (id=3)
INSERT INTO game_stats (user_id, game_type, total_games, total_wins, total_losses, total_bet, total_won, best_score, current_streak, best_streak, last_played) VALUES
(3, 'slot', 100, 65, 35, 50000, 47500, 5000, 5, 15, NOW()),
(3, 'gacha', 50, 30, 20, 250000, 200000, 8000, 3, 8, NOW()),
(3, 'crash', 50, 25, 25, 25000, 23750, 3000, 2, 7, NOW());

-- 유저01 게임 통계 (id=4)  
INSERT INTO game_stats (user_id, game_type, total_games, total_wins, total_losses, total_bet, total_won, best_score, current_streak, best_streak, last_played) VALUES
(4, 'slot', 80, 45, 35, 40000, 38000, 4500, 3, 12, NOW() - INTERVAL '1 day'),
(4, 'gacha', 40, 20, 20, 200000, 150000, 7000, 1, 6, NOW() - INTERVAL '1 day'),
(4, 'crash', 30, 20, 10, 15000, 14250, 2500, 4, 9, NOW() - INTERVAL '1 day');

-- 유저02 게임 통계 (id=5)
INSERT INTO game_stats (user_id, game_type, total_games, total_wins, total_losses, total_bet, total_won, best_score, current_streak, best_streak, last_played) VALUES
(5, 'slot', 50, 25, 25, 25000, 23750, 3000, 0, 8, NOW() - INTERVAL '2 days'),
(5, 'gacha', 20, 8, 12, 100000, 70000, 5000, 1, 4, NOW() - INTERVAL '2 days'),
(5, 'crash', 10, 7, 3, 5000, 4750, 1500, 2, 5, NOW() - INTERVAL '2 days');

-- 유저03 게임 통계 (id=6) - 가챠 중심
INSERT INTO game_stats (user_id, game_type, total_games, total_wins, total_losses, total_bet, total_won, best_score, current_streak, best_streak, last_played) VALUES
(6, 'slot', 15, 6, 9, 7500, 7125, 2000, 0, 3, NOW() - INTERVAL '3 days'),
(6, 'gacha', 60, 20, 40, 300000, 180000, 6000, 0, 5, NOW() - INTERVAL '3 days'),  -- 가챠에 집중
(6, 'crash', 5, 2, 3, 2500, 2375, 800, 0, 2, NOW() - INTERVAL '3 days');

-- 유저04 게임 통계 (id=7) - 신규 사용자
INSERT INTO game_stats (user_id, game_type, total_games, total_wins, total_losses, total_bet, total_won, best_score, current_streak, best_streak, last_played) VALUES
(7, 'slot', 8, 3, 5, 4000, 3800, 1000, 0, 2, NOW() - INTERVAL '1 day'),
(7, 'gacha', 2, 1, 1, 10000, 5000, 2000, 1, 1, NOW() - INTERVAL '1 day');

-- ===== STEP 3: 상점 거래 내역 생성 (실제 스키마에 맞춤) =====

-- 기존 shop_transactions 데이터 삭제 (시드계정들 것만)
DELETE FROM shop_transactions WHERE user_id IN (3, 4, 5, 6, 7);

-- 어드민 구매 내역
INSERT INTO shop_transactions (user_id, product_id, kind, quantity, unit_price, amount, payment_method, status, receipt_code, created_at, updated_at) VALUES
(3, 'premium_gold_pack', 'gold_package', 3, 10000, 30000, 'gold', 'success', 'RC_ADMIN_001', NOW() - INTERVAL '10 days', NOW() - INTERVAL '10 days'),
(3, 'epic_gacha_box', 'gacha_pull', 5, 5000, 25000, 'gold', 'success', 'RC_ADMIN_002', NOW() - INTERVAL '5 days', NOW() - INTERVAL '5 days');

-- 유저01 구매 내역
INSERT INTO shop_transactions (user_id, product_id, kind, quantity, unit_price, amount, payment_method, status, receipt_code, created_at, updated_at) VALUES
(4, 'value_gold_pack', 'gold_package', 2, 5000, 10000, 'gold', 'success', 'RC_USER01_001', NOW() - INTERVAL '7 days', NOW() - INTERVAL '7 days'),
(4, 'rare_gacha_box', 'gacha_pull', 4, 5000, 20000, 'gold', 'success', 'RC_USER01_002', NOW() - INTERVAL '3 days', NOW() - INTERVAL '3 days');

-- 유저02 구매 내역
INSERT INTO shop_transactions (user_id, product_id, kind, quantity, unit_price, amount, payment_method, status, receipt_code, created_at, updated_at) VALUES
(5, 'basic_gacha_box', 'gacha_pull', 2, 5000, 10000, 'gold', 'success', 'RC_USER02_001', NOW() - INTERVAL '4 days', NOW() - INTERVAL '4 days');

-- 유저03 구매 내역 (가챠 중심)
INSERT INTO shop_transactions (user_id, product_id, kind, quantity, unit_price, amount, payment_method, status, receipt_code, created_at, updated_at) VALUES
(6, 'epic_gacha_box', 'gacha_pull', 3, 5000, 15000, 'gold', 'success', 'RC_USER03_001', NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days'),
(6, 'rare_gacha_box', 'gacha_pull', 2, 5000, 10000, 'gold', 'success', 'RC_USER03_002', NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day');

-- 유저04 구매 내역 (신규)
INSERT INTO shop_transactions (user_id, product_id, kind, quantity, unit_price, amount, payment_method, status, receipt_code, created_at, updated_at) VALUES
(7, 'basic_gacha_box', 'gacha_pull', 1, 5000, 5000, 'gold', 'success', 'RC_USER04_001', NOW() - INTERVAL '1 day', NOW() - INTERVAL '1 day');

-- ===== STEP 4: 최종 확인 및 전역동기화 검증 =====
SELECT 'SCHEMA-ALIGNED REALISTIC ECONOMY DATA COMPLETE' as status;

-- 사용자 현황
SELECT 'USER OVERVIEW' as section;
SELECT id, nickname, gold_balance, battlepass_level, total_spent, vip_tier, vip_points FROM users WHERE id IN (3,4,5,6,7) ORDER BY id;

-- 게임 통계 현황  
SELECT 'GAME STATS OVERVIEW' as section;
SELECT user_id, game_type, total_games, total_wins, total_bet, total_won, current_streak, best_streak FROM game_stats WHERE user_id IN (3,4,5,6,7) ORDER BY user_id, game_type;

-- 구매 내역 현황
SELECT 'SHOP TRANSACTIONS OVERVIEW' as section;
SELECT user_id, product_id, kind, quantity, amount, status, created_at FROM shop_transactions WHERE user_id IN (3,4,5,6,7) ORDER BY user_id, created_at;

-- 경제 건전성 체크 (골드 in/out 밸런스)
SELECT 'ECONOMY HEALTH CHECK' as section;
SELECT 
    SUM(gold_balance) as total_gold_in_circulation,
    SUM(total_spent) as total_gold_spent,
    AVG(gold_balance) as avg_gold_per_user,
    COUNT(*) as total_active_users
FROM users WHERE id IN (3,4,5,6,7);
