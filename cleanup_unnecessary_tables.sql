-- 불필요한 게임 테이블 정리 SQL
-- 실제로 구현되지 않은 게임들의 테이블 삭제

-- 블랙잭 테이블 삭제
DROP TABLE IF EXISTS blackjack_sessions CASCADE;

-- 바카라 테이블 삭제  
DROP TABLE IF EXISTS baccarat_sessions CASCADE;

-- 포커 테이블 삭제
DROP TABLE IF EXISTS poker_sessions CASCADE;

-- 토너먼트 관련 테이블 삭제 (아직 구현되지 않음)
DROP TABLE IF EXISTS tournament_participants CASCADE;
DROP TABLE IF EXISTS game_tournaments CASCADE;

-- 룰렛 설정 테이블 삭제 (기존 구현과 중복)
DROP TABLE IF EXISTS roulette_configurations CASCADE;
DROP TABLE IF EXISTS roulette_sessions CASCADE;

-- 슬롯 설정 테이블 삭제 (기존 구현과 중복 가능성)
DROP TABLE IF EXISTS slot_configurations CASCADE;
DROP TABLE IF EXISTS slot_sessions CASCADE;

-- 실제 필요한 테이블들만 남김:
-- ✅ crash_sessions, crash_bets (크래시 게임용)
-- ✅ gacha_configurations, gacha_items (가챠 게임 확장용)
-- ✅ game_leaderboards (리더보드는 유용할 수 있음)

-- 현재 남은 게임 테이블 확인
SELECT table_name 
FROM information_schema.tables 
WHERE table_name LIKE '%game%' 
   OR table_name LIKE '%crash%' 
   OR table_name LIKE '%gacha%' 
   OR table_name LIKE '%slot%' 
   OR table_name LIKE '%roulette%' 
   OR table_name LIKE '%tournament%'
ORDER BY table_name;
