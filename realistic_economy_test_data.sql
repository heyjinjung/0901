-- 🎯 실제 경제구조 기반 테스트 데이터 생성
-- 단일화폐.md + 전역동기화_솔루션.md 기준으로 현실적인 활동 시뮬레이션

-- ===== STEP 1: 기존 데이터 정리 (시드계정 외 모든 사용자 삭제) =====
-- FK 제약 순서에 따라 연관 테이블부터 삭제
DELETE FROM user_sessions WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM user_segments WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM user_actions WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM event_participations WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM user_missions WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM shop_transactions WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM shop_promo_usage WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM ab_test_participants WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM game_history WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM follow_relations WHERE user_id NOT IN (3, 4, 5, 6, 7) OR target_user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM game_sessions WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM refresh_tokens WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM user_achievements WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM reward_audit WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM security_events WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM games WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM game_stats WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM daily_game_limits WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM user_activities WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM gacha_results WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM user_progress WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM notifications WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM quiz_results WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM user_preferences WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM content_personalizations WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM emotion_profiles WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM site_visits WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM user_analytics WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM page_views WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM conversion_events WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM custom_events WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM user_game_stats WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM user_rewards WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM vip_access_logs WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM user_recommendations WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM model_predictions WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM chat_participants WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM chat_messages WHERE sender_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM ai_conversations WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM content_views WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM content_likes WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM content_purchases WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM user_quiz_attempts WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM quiz_leaderboards WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM recommendation_interactions WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM message_reactions WHERE user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM chat_moderations WHERE user_id NOT IN (3, 4, 5, 6, 7) OR moderator_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM invite_codes WHERE created_by NOT IN (3, 4, 5, 6, 7) OR used_by_user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM admin_audit_logs WHERE actor_user_id NOT IN (3, 4, 5, 6, 7);
DELETE FROM token_blacklist WHERE blacklisted_by NOT IN (3, 4, 5, 6, 7);
DELETE FROM chat_rooms WHERE created_by NOT IN (3, 4, 5, 6, 7);

-- 시드계정 외 모든 사용자 삭제
DELETE FROM users WHERE id NOT IN (3, 4, 5, 6, 7);

-- ===== STEP 2: 시드계정들을 현실적인 경제 활동 상태로 설정 =====

-- 어드민 (id=3): 관리자, 모든 기능 테스트용
UPDATE users SET 
    gold_balance = 100000,      -- 충분한 골드 (관리 테스트용)
    gems_balance = 5000,        -- 프리미엄 화폐
    experience_points = 5000,   -- 높은 경험치
    level = 10,                 -- 고레벨
    total_spent = 50000,        -- 상당한 지출 이력
    login_streak = 30,          -- 장기 사용자
    total_games_played = 200,   -- 많은 게임 플레이
    total_wins = 120,           -- 60% 승률
    total_losses = 80,
    battlepass_level = 50,      -- 높은 배틀패스
    vip_tier = 'PREMIUM'        -- VIP 등급
WHERE id = 3;

-- 유저01 (id=4): 헤비 게이머, 높은 활동
UPDATE users SET 
    gold_balance = 25000,       -- 충분한 골드
    gems_balance = 1000,        
    experience_points = 3000,   
    level = 7,                  
    total_spent = 30000,        -- 높은 지출
    login_streak = 15,          
    total_games_played = 150,   -- 많은 게임
    total_wins = 85,            -- 57% 승률
    total_losses = 65,
    battlepass_level = 35,      
    vip_tier = 'VIP'           -- VIP 사용자
WHERE id = 4;

-- 유저02 (id=5): 중간 사용자, 균형잡힌 활동
UPDATE users SET 
    gold_balance = 8000,        -- 중간 골드
    gems_balance = 200,         
    experience_points = 1500,   
    level = 4,                  
    total_spent = 12000,        -- 적당한 지출
    login_streak = 7,           
    total_games_played = 80,    -- 중간 게임 수
    total_wins = 40,            -- 50% 승률
    total_losses = 40,
    battlepass_level = 15,      
    vip_tier = 'STANDARD'      -- 일반 사용자
WHERE id = 5;

-- 유저03 (id=6): 라이트 게이머, 가챠 중심
UPDATE users SET 
    gold_balance = 3000,        -- 낮은 골드 (가챠로 소모)
    gems_balance = 50,          
    experience_points = 800,    
    level = 3,                  
    total_spent = 15000,        -- 가챠에 많이 소모
    login_streak = 3,           
    total_games_played = 30,    -- 적은 게임, 가챠 위주
    total_wins = 12,            -- 40% 승률
    total_losses = 18,
    battlepass_level = 8,       
    vip_tier = 'STANDARD'
WHERE id = 6;

-- 유저04 (id=7): 신규 사용자, 초기 활동
UPDATE users SET 
    gold_balance = 2500,        -- 초기 골드 + 약간의 활동
    gems_balance = 0,           
    experience_points = 300,    
    level = 2,                  
    total_spent = 1500,         -- 적은 지출
    login_streak = 1,           
    total_games_played = 10,    -- 초기 탐색
    total_wins = 4,             -- 40% 승률
    total_losses = 6,
    battlepass_level = 3,       
    vip_tier = 'STANDARD'
WHERE id = 7;

-- ===== STEP 3: 현실적인 게임 활동 데이터 생성 =====

-- 어드민 게임 통계 (id=3)
INSERT INTO game_stats (user_id, game_type, total_played, total_won, total_lost, total_bet, total_won_amount, created_at, updated_at) VALUES
(3, 'slot', 100, 65, 35, 50000, 47500, NOW(), NOW()),
(3, 'gacha', 50, 30, 20, 250000, 200000, NOW(), NOW()),
(3, 'crash', 50, 25, 25, 25000, 23750, NOW(), NOW());

-- 유저01 게임 통계 (id=4)  
INSERT INTO game_stats (user_id, game_type, total_played, total_won, total_lost, total_bet, total_won_amount, created_at, updated_at) VALUES
(4, 'slot', 80, 45, 35, 40000, 38000, NOW(), NOW()),
(4, 'gacha', 40, 20, 20, 200000, 150000, NOW(), NOW()),
(4, 'crash', 30, 20, 10, 15000, 14250, NOW(), NOW());

-- 유저02 게임 통계 (id=5)
INSERT INTO game_stats (user_id, game_type, total_played, total_won, total_lost, total_bet, total_won_amount, created_at, updated_at) VALUES
(5, 'slot', 50, 25, 25, 25000, 23750, NOW(), NOW()),
(5, 'gacha', 20, 8, 12, 100000, 70000, NOW(), NOW()),
(5, 'crash', 10, 7, 3, 5000, 4750, NOW(), NOW());

-- 유저03 게임 통계 (id=6) - 가챠 중심
INSERT INTO game_stats (user_id, game_type, total_played, total_won, total_lost, total_bet, total_won_amount, created_at, updated_at) VALUES
(6, 'slot', 15, 6, 9, 7500, 7125, NOW(), NOW()),
(6, 'gacha', 60, 20, 40, 300000, 180000, NOW(), NOW()),  -- 가챠에 집중
(6, 'crash', 5, 2, 3, 2500, 2375, NOW(), NOW());

-- 유저04 게임 통계 (id=7) - 신규 사용자
INSERT INTO game_stats (user_id, game_type, total_played, total_won, total_lost, total_bet, total_won_amount, created_at, updated_at) VALUES
(7, 'slot', 8, 3, 5, 4000, 3800, NOW(), NOW()),
(7, 'gacha', 2, 1, 1, 10000, 5000, NOW(), NOW()),
(7, 'crash', 0, 0, 0, 0, 0, NOW(), NOW());  -- 아직 시도 안함

-- ===== STEP 4: 상점 거래 내역 생성 (경제구조 반영) =====

-- 어드민 구매 내역
INSERT INTO shop_transactions (user_id, item_type, item_id, quantity, unit_price, total_amount, currency_type, status, created_at) VALUES
(3, 'gold_package', 'premium_gold', 3, 10000, 30000, 'gold', 'completed', NOW() - INTERVAL '10 days'),
(3, 'gacha_pull', 'epic_box', 5, 5000, 25000, 'gold', 'completed', NOW() - INTERVAL '5 days');

-- 유저01 구매 내역
INSERT INTO shop_transactions (user_id, item_type, item_id, quantity, unit_price, total_amount, currency_type, status, created_at) VALUES
(4, 'gold_package', 'value_gold', 2, 5000, 10000, 'gold', 'completed', NOW() - INTERVAL '7 days'),
(4, 'gacha_pull', 'rare_box', 4, 5000, 20000, 'gold', 'completed', NOW() - INTERVAL '3 days');

-- 유저02 구매 내역
INSERT INTO shop_transactions (user_id, item_type, item_id, quantity, unit_price, total_amount, currency_type, status, created_at) VALUES
(5, 'gacha_pull', 'basic_box', 2, 5000, 10000, 'gold', 'completed', NOW() - INTERVAL '4 days');

-- 유저03 구매 내역 (가챠 중심)
INSERT INTO shop_transactions (user_id, item_type, item_id, quantity, unit_price, total_amount, currency_type, status, created_at) VALUES
(6, 'gacha_pull', 'epic_box', 3, 5000, 15000, 'gold', 'completed', NOW() - INTERVAL '2 days'),
(6, 'gacha_pull', 'rare_box', 2, 5000, 10000, 'gold', 'completed', NOW() - INTERVAL '1 day');

-- 유저04 구매 내역 (신규)
INSERT INTO shop_transactions (user_id, item_type, item_id, quantity, unit_price, total_amount, currency_type, status, created_at) VALUES
(7, 'gacha_pull', 'basic_box', 1, 5000, 5000, 'gold', 'completed', NOW() - INTERVAL '1 day');

-- ===== STEP 5: 최종 확인 및 전역동기화 검증 =====
SELECT 'DATABASE RESET COMPLETE - REALISTIC ECONOMY TEST DATA' as status;

-- 사용자 현황
SELECT 'USER OVERVIEW' as section;
SELECT id, nickname, gold_balance, gems_balance, level, total_games_played, total_wins, vip_tier FROM users ORDER BY id;

-- 게임 통계 현황  
SELECT 'GAME STATS OVERVIEW' as section;
SELECT user_id, game_type, total_played, total_won, total_bet, total_won_amount FROM game_stats ORDER BY user_id, game_type;

-- 구매 내역 현황
SELECT 'SHOP TRANSACTIONS OVERVIEW' as section;
SELECT user_id, item_type, quantity, total_amount, currency_type, created_at FROM shop_transactions ORDER BY user_id, created_at;

-- 경제 건전성 체크 (골드 in/out 밸런스)
SELECT 'ECONOMY HEALTH CHECK' as section;
SELECT 
    SUM(gold_balance) as total_gold_in_circulation,
    SUM(total_spent) as total_gold_spent,
    AVG(gold_balance) as avg_gold_per_user,
    COUNT(*) as total_active_users
FROM users WHERE id IN (3,4,5,6,7);
