-- 🎯 완전 제로 리셋: 시드계정 5개만 남기고 모든 데이터를 초기 상태로 만들기
-- 사용자 요구: 온보딩 환경, 모든 값 = 0, 깨끗한 상태

-- ===== STEP 1: 모든 사용자 관련 데이터 완전 삭제 =====
-- FK 제약 순서에 따라 연관 테이블부터 모든 데이터 삭제

DELETE FROM user_sessions;
DELETE FROM user_segments;
DELETE FROM user_actions;
DELETE FROM event_participations;
DELETE FROM user_missions;
DELETE FROM shop_transactions;
DELETE FROM shop_promo_usage;
DELETE FROM ab_test_participants;
DELETE FROM game_history;
DELETE FROM follow_relations;
DELETE FROM game_sessions;
DELETE FROM refresh_tokens;
DELETE FROM user_achievements;
DELETE FROM reward_audit;
DELETE FROM security_events;
DELETE FROM games;
DELETE FROM game_stats;
DELETE FROM daily_game_limits;
DELETE FROM user_activities;
DELETE FROM gacha_results;
DELETE FROM user_progress;
DELETE FROM notifications;
DELETE FROM quiz_results;
DELETE FROM user_preferences;
DELETE FROM content_personalizations;
DELETE FROM emotion_profiles;
DELETE FROM site_visits;
DELETE FROM user_analytics;
DELETE FROM page_views;
DELETE FROM conversion_events;
DELETE FROM custom_events;
DELETE FROM user_game_stats;
DELETE FROM user_rewards;
DELETE FROM vip_access_logs;
DELETE FROM user_recommendations;
DELETE FROM model_predictions;
DELETE FROM chat_participants;
DELETE FROM chat_messages;
DELETE FROM ai_conversations;
DELETE FROM content_views;
DELETE FROM content_likes;
DELETE FROM content_purchases;
DELETE FROM user_quiz_attempts;
DELETE FROM quiz_leaderboards;
DELETE FROM recommendation_interactions;
DELETE FROM message_reactions;
DELETE FROM chat_moderations;
DELETE FROM invite_codes;
DELETE FROM admin_audit_logs;
DELETE FROM token_blacklist;
DELETE FROM chat_rooms;

-- ===== STEP 2: 시드계정 외 모든 사용자 삭제 =====
DELETE FROM users WHERE id NOT IN (3, 4, 5, 6, 7);

-- ===== STEP 3: 시드계정들을 완전 제로 상태로 리셋 =====
-- 화폐/경험치/레벨 등 모든 수치를 0으로 초기화
UPDATE users SET 
    gold_balance = 1000,        -- 초기 지급 골드만 (신규 가입 보너스)
    gems_balance = 0,           -- 젬은 0
    premium_currency = 0,       -- 프리미엄 화폐 0
    experience_points = 0,      -- 경험치 0
    level = 1,                  -- 레벨 1 (초기값)
    total_spent = 0,           -- 총 지출 0
    last_login_at = created_at, -- 마지막 로그인 = 생성일
    login_streak = 0,          -- 로그인 스트릭 0
    total_games_played = 0,    -- 총 게임 플레이 0
    total_wins = 0,            -- 총 승리 0
    total_losses = 0,          -- 총 패배 0
    battlepass_level = 1,      -- 배틀패스 레벨 1
    vip_tier = 'STANDARD',     -- VIP 등급 기본
    phone_verified = false,    -- 폰 인증 미완료
    email_verified = false     -- 이메일 인증 미완료
WHERE id IN (3, 4, 5, 6, 7);

-- ===== STEP 4: 시스템 테이블 정리 (사용자 데이터만 제거) =====
-- 시스템 설정/게임 구성은 유지하되, 사용자별 데이터만 제거

-- 가챠 로그 테이블이 있다면 초기화
-- DELETE FROM gacha_logs WHERE user_id IN (3, 4, 5, 6, 7);

-- 업적 진행도 초기화
-- DELETE FROM achievement_progress WHERE user_id IN (3, 4, 5, 6, 7);

-- ===== STEP 5: 시퀀스/ID 정리 =====
-- 필요한 경우 AUTO INCREMENT 시퀀스 정리
-- ALTER SEQUENCE user_actions_id_seq RESTART WITH 1;
-- ALTER SEQUENCE shop_transactions_id_seq RESTART WITH 1;
-- ALTER SEQUENCE game_sessions_id_seq RESTART WITH 1;

-- ===== STEP 6: 최종 확인 =====
SELECT 'FINAL CHECK' as status;
SELECT COUNT(*) as total_users FROM users;
SELECT id, nickname, site_id, gold_balance, experience_points, total_games_played FROM users ORDER BY id;

-- 각 테이블의 데이터 확인
SELECT 'user_actions' as table_name, COUNT(*) as count FROM user_actions
UNION ALL
SELECT 'shop_transactions', COUNT(*) FROM shop_transactions  
UNION ALL
SELECT 'game_sessions', COUNT(*) FROM game_sessions
UNION ALL
SELECT 'user_achievements', COUNT(*) FROM user_achievements
UNION ALL
SELECT 'gacha_results', COUNT(*) FROM gacha_results;
