-- Safe indexes for common access patterns
-- shop_transactions
CREATE INDEX IF NOT EXISTS idx_shop_tx_user_created ON shop_transactions (user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_shop_tx_status_created ON shop_transactions (status, created_at DESC);
-- UNIQUE may already exist; skip if present
DO $$ BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND indexname = 'uq_shop_tx_receipt_code'
  ) THEN
    EXECUTE 'CREATE UNIQUE INDEX uq_shop_tx_receipt_code ON shop_transactions (receipt_code)';
  END IF;
END $$;

-- shop_promo_usage
CREATE INDEX IF NOT EXISTS idx_promo_usage_code ON shop_promo_usage (promo_code);
CREATE INDEX IF NOT EXISTS idx_promo_usage_user_time ON shop_promo_usage (user_id, used_at DESC);

-- notifications
CREATE INDEX IF NOT EXISTS idx_notifications_user_read_created ON notifications (user_id, is_read, created_at DESC);

-- shop_products / shop_limited_packages guards (already indexed in models, but ensure in DB)
CREATE INDEX IF NOT EXISTS idx_shop_discounts_product_id ON shop_discounts (product_id);
