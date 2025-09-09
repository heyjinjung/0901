-- 시드/어드민 계정 외 모든 연관 데이터 삭제 스크립트 (실제 운영 데이터 기반)
-- 안전한 순서로 FK 제약이 걸린 모든 테이블에서 데이터 삭제
-- 시드계정관리.md 기준: 어드민(관리자), 유저01~04(시드유저)

-- 1. 실제 시드/어드민 계정 ID 조회 (보존할 계정들) 
SELECT id, nickname, site_id FROM users WHERE nickname IN ('어드민', '유저01', '유저02', '유저03', '유저04') OR site_id IN ('admin', 'user001', 'user002', 'user003', 'user004');

-- 2. 모든 연관 테이블에서 실제 시드/어드민 외 계정 데이터 삭제
-- 실제 운영 데이터를 반영한 WHERE 조건 사용
DELETE FROM user_sessions WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('어드민', '유저01', '유저02', '유저03', '유저04') OR site_id IN ('admin', 'user001', 'user002', 'user003', 'user004'));
DELETE FROM user_segments WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('어드민', '유저01', '유저02', '유저03', '유저04') OR site_id IN ('admin', 'user001', 'user002', 'user003', 'user004'));
DELETE FROM user_actions WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM event_participations WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM user_missions WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM shop_transactions WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM shop_promo_usage WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM ab_test_participants WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM game_history WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM follow_relations WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM follow_relations WHERE target_user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM game_sessions WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM refresh_tokens WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM user_achievements WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM reward_audit WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM security_events WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM games WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM game_stats WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM daily_game_limits WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM user_activities WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM gacha_results WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM user_progress WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM notifications WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM quiz_results WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM user_preferences WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM content_personalizations WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM emotion_profiles WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM site_visits WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM user_analytics WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM page_views WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM conversion_events WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM custom_events WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM user_game_stats WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM user_rewards WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM vip_access_logs WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM user_recommendations WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM model_predictions WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM chat_participants WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM chat_messages WHERE sender_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM ai_conversations WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM content_views WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM content_likes WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM content_purchases WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM user_quiz_attempts WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM quiz_leaderboards WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM recommendation_interactions WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM message_reactions WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM chat_moderations WHERE user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM chat_moderations WHERE moderator_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));

-- 3. invite_codes 테이블 처리 (created_by, used_by_user_id 모두 고려)
DELETE FROM invite_codes WHERE created_by NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));
DELETE FROM invite_codes WHERE used_by_user_id IS NOT NULL AND used_by_user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));

-- 4. admin_audit_logs 처리 (actor_user_id)
DELETE FROM admin_audit_logs WHERE actor_user_id NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));

-- 5. token_blacklist 처리 (blacklisted_by)
DELETE FROM token_blacklist WHERE blacklisted_by NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));

-- 6. chat_rooms 처리 (created_by)
DELETE FROM chat_rooms WHERE created_by NOT IN (SELECT id FROM users WHERE nickname IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin'));

-- 7. 마지막으로 users 테이블에서 시드/어드민 외 계정 삭제
DELETE FROM users WHERE nickname NOT IN ('seed1', 'seed2', 'seed3', 'seed4', 'admin');

-- 8. 최종 확인
SELECT COUNT(*) AS remaining_users FROM users;
SELECT id, nickname FROM users;
