-- 전체 시드 사용자 데이터 정리 및 재설정
-- 2025-09-06: 5개 계정으로 일관성 있게 정리

BEGIN;

-- 1. 모든 사용자 삭제 (FK CASCADE로 관련 데이터도 정리)
DELETE FROM users;

-- 2. 시퀀스 리셋
ALTER SEQUENCE users_id_seq RESTART WITH 1;

-- 3. 올바른 5개 시드 계정 생성
-- 비밀번호는 모두 bcrypt로 해시됨: 123456 -> $2b$12$hash...
INSERT INTO users (site_id, nickname, email, phone_number, password_hash, created_at) VALUES
-- admin 계정 (관리자)
('admin', 'admin', 'admin@test.com', '010-0000-0000', '$2b$12$LQv3c1yqBwuvHOSO.9lWNOQi5/jMv2UwX8RBjfyfKOW1XzMnHgKzW', NOW()),

-- 일반 사용자 4명
('seed1', 'seed1', 'seed1@test.com', '010-0000-0001', '$2b$12$LQv3c1yqBwuvHOSO.9lWNOQi5/jMv2UwX8RBjfyfKOW1XzMnHgKzW', NOW()),
('seed2', 'seed2', 'seed2@test.com', '010-0000-0002', '$2b$12$LQv3c1yqBwuvHOSO.9lWNOQi5/jMv2UwX8RBjfyfKOW1XzMnHgKzW', NOW()),
('seed3', 'seed3', 'seed3@test.com', '010-0000-0003', '$2b$12$LQv3c1yqBwuvHOSO.9lWNOQi5/jMv2UwX8RBjfyfKOW1XzMnHgKzW', NOW()),
('seed4', 'seed4', 'seed4@test.com', '010-0000-0004', '$2b$12$LQv3c1yqBwuvHOSO.9lWNOQi5/jMv2UwX8RBjfyfKOW1XzMnHgKzW', NOW());

-- 4. 각 사용자에 기본 잔액 1000 gold 설정
INSERT INTO user_balances (user_id, gold_balance, gems_balance, last_updated) 
SELECT 
    id, 
    1000, -- 기본 gold
    0,    -- 기본 gems
    NOW()
FROM users;

-- 5. 기본 사용자 통계 생성
INSERT INTO user_analytics (user_id, total_spent, vip_tier, battlepass_level, created_at, updated_at)
SELECT 
    id,
    0.0,  -- total_spent
    'STANDARD', -- vip_tier
    1,    -- battlepass_level
    NOW(),
    NOW()
FROM users;

-- 6. 확인 쿼리
SELECT 'Created users:' as info;
SELECT id, site_id, nickname, email, phone_number FROM users ORDER BY id;

SELECT 'User balances:' as info;
SELECT ub.user_id, u.site_id, ub.gold_balance, ub.gems_balance 
FROM user_balances ub 
JOIN users u ON u.id = ub.user_id 
ORDER BY ub.user_id;

COMMIT;
