-- Non-destructive: disable known test/demo accounts by site_id or nickname patterns
-- Run this against the development DB only. This will set is_active = false for matched users.

UPDATE users
SET is_active = false
WHERE site_id IN ('shopper', 'demo', 'testsite')
   OR nickname ILIKE '%test%'
   OR site_id ILIKE '%test%'
   OR nickname ILIKE '%demo%'
RETURNING id, site_id, nickname, is_active;
