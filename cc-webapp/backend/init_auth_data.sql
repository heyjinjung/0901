-- 인증 시스템 초기 데이터 설정

-- 먼저 invite_codes 테이블에 존재하는 컬럼 확인 후 초대 코드 생성
INSERT INTO invite_codes (code, is_active, created_at)
VALUES ('5858', TRUE, NOW())
ON CONFLICT (code) DO UPDATE 
SET is_active = TRUE;

-- 관리자 계정 생성 (비밀번호: admin123)
INSERT INTO users (site_id, nickname, password_hash, is_admin, is_active, created_at, invite_code)
VALUES 
    ('admin@casino-club.local', 'AdminUser', 'admin123', TRUE, TRUE, NOW(), '5858'),
    ('admin', 'Admin', 'admin123', TRUE, TRUE, NOW(), '5858')
ON CONFLICT (site_id) DO UPDATE 
SET is_admin = TRUE, is_active = TRUE;

-- 테스트 사용자 계정 생성 (비밀번호: test1234)
INSERT INTO users (site_id, nickname, password_hash, is_admin, is_active, created_at, invite_code)
VALUES 
    ('test@casino-club.local', 'TestUser', 'test1234', FALSE, TRUE, NOW(), '5858')
ON CONFLICT (site_id) DO NOTHING;