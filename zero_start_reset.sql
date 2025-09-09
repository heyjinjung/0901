-- 🎯 진짜 제로 시작 상태로 리셋 (실제 게임 플레이 테스트용)
-- 시드계정들을 완전 초기 상태로 설정 (기본 골드 1000만)

-- ===== STEP 1: 시드계정들을 완전 초기 상태로 리셋 =====

-- 모든 시드계정을 초기 신규 가입 상태로 설정
UPDATE users SET 
    gold_balance = 1000,         -- 신규 가입 기본 골드만
    battlepass_level = 0,        -- 초기 레벨
    total_spent = 0,             -- 아무것도 안 썼음
    vip_tier = 'STANDARD',       -- 기본 등급
    vip_points = 0,              -- 포인트 없음
    last_login = NOW(),          -- 방금 가입
    updated_at = NOW()
WHERE id IN (3, 4, 5, 6, 7);

-- ===== STEP 2: 모든 게임/구매 내역 완전 삭제 =====

-- 게임 통계 완전 삭제 (실제 플레이로 생성되도록)
DELETE FROM game_stats WHERE user_id IN (3, 4, 5, 6, 7);

-- 상점 거래 내역 완전 삭제 (실제 구매로 생성되도록)  
DELETE FROM shop_transactions WHERE user_id IN (3, 4, 5, 6, 7);

-- 게임 세션 내역 삭제
DELETE FROM game_sessions WHERE user_id IN (3, 4, 5, 6, 7);

-- 가챠 결과 삭제
DELETE FROM gacha_results WHERE user_id IN (3, 4, 5, 6, 7);

-- 사용자 액션 내역 삭제 (실제 플레이로 기록되도록)
DELETE FROM user_actions WHERE user_id IN (3, 4, 5, 6, 7);

-- 사용자 보상 내역 삭제
DELETE FROM user_rewards WHERE user_id IN (3, 4, 5, 6, 7);

-- ===== STEP 3: 초기 상태 확인 =====
SELECT 'ZERO START STATE RESET COMPLETE' as status;

-- 완전 초기 상태 확인
SELECT 'INITIAL STATE CHECK' as section;
SELECT 
    id, 
    nickname, 
    gold_balance, 
    battlepass_level, 
    total_spent, 
    vip_tier, 
    vip_points,
    created_at,
    last_login
FROM users 
WHERE id IN (3,4,5,6,7) 
ORDER BY id;

-- 연관 데이터도 모두 0인지 확인
SELECT 'DATA VERIFICATION' as section;
SELECT 
    'game_stats' as table_name,
    COUNT(*) as record_count
FROM game_stats 
WHERE user_id IN (3,4,5,6,7)
UNION ALL
SELECT 
    'shop_transactions' as table_name,
    COUNT(*) as record_count
FROM shop_transactions 
WHERE user_id IN (3,4,5,6,7)
UNION ALL
SELECT 
    'user_actions' as table_name,
    COUNT(*) as record_count
FROM user_actions 
WHERE user_id IN (3,4,5,6,7)
UNION ALL
SELECT 
    'gacha_results' as table_name,
    COUNT(*) as record_count
FROM gacha_results 
WHERE user_id IN (3,4,5,6,7);

SELECT 'READY FOR REAL GAMEPLAY TESTING' as final_status;
