-- User 02 익명화 / 리셋 스크립트 (DEV 전용)
-- 안전장치: 반드시 prod 환경이 아님을 확인 후 실행
BEGIN;
-- 1. 기본 프로필 초기화
UPDATE users
SET nickname = 'user02_reset',
    email = NULL,
    gold_balance = 0,
    experience = 0,
    updated_at = NOW()
WHERE id = 2;

-- 2. streak 관련 Redis 키는 애플리케이션 계층에서 삭제 필요 (문서화)
--    DEL user:2:streak:* user:2:streak_protection:*

-- 3. 선택적: 사용자 관련 보상 멱등키 재사용 방지 위해 user_rewards.idempotency_key NULL 처리 (원본 추적 유지)
UPDATE user_rewards SET idempotency_key = NULL WHERE user_id = 2;

COMMIT;
