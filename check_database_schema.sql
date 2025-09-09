-- FK 제약조건을 고려한 완전한 데이터베이스 초기화
-- 2025-09-06: 모든 관련 테이블 정리 후 5개 시드 계정 생성

-- 1. 모든 테이블 목록 확인
\dt

-- 2. users 테이블을 참조하는 FK 제약조건 확인
SELECT
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM 
    information_schema.table_constraints AS tc 
    JOIN information_schema.key_column_usage AS kcu
      ON tc.constraint_name = kcu.constraint_name
      AND tc.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage AS ccu
      ON ccu.constraint_name = tc.constraint_name
      AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY' 
  AND ccu.table_name='users';

-- 3. 현재 사용자 데이터 상태
SELECT id, site_id, nickname, email, phone_number FROM users ORDER BY id;
