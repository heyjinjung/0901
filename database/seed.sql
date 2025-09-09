-- Minimal seed data for local/dev
-- Users (assumes auth model columns)
INSERT INTO users (site_id, nickname, phone_number, password_hash, invite_code, is_active, vip_tier)
VALUES ('demo', '데모유저', '000-0000-0000', 'x', '5858', true, 'STANDARD')
ON CONFLICT DO NOTHING;

-- Shop products
INSERT INTO shop_products (product_id, name, description, price, is_active, extra)
VALUES
 ('gems_100', '100 Gems', 'Small gem pack', 100, true, '{"currency":"GEMS"}'),
 ('gems_500', '500 Gems', 'Medium gem pack', 450, true, '{"currency":"GEMS"}')
ON CONFLICT DO NOTHING;

-- Limited package
INSERT INTO shop_limited_packages (package_id, name, description, price, is_active, contents)
VALUES ('starter_bundle', 'Starter Bundle', 'Best value for starters', 999, true, '{"bonus_tokens":100}')
ON CONFLICT DO NOTHING;

-- Promo code
INSERT INTO shop_promo_codes (code, package_id, discount_type, value, is_active)
VALUES ('WELCOME10', 'starter_bundle', 'percent', 10, true)
ON CONFLICT DO NOTHING;

-- Notification sample
INSERT INTO notifications (user_id, title, message, is_read, is_sent)
SELECT id, '환영합니다', 'Casino-Club F2P에 오신 것을 환영합니다!', false, false
FROM users WHERE site_id='demo'
ON CONFLICT DO NOTHING;
