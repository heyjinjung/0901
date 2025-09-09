-- ClickHouse DDL (Phase C Draft) - apply manually via clickhouse-client

CREATE TABLE IF NOT EXISTS events_raw
(
  event_date Date DEFAULT toDate(ts),
  ts DateTime64(3) CODEC(Delta, ZSTD(3)),
  event_type LowCardinality(String),
  user_id UInt64,
  entity_id UInt64 DEFAULT 0,
  progress_version UInt32 DEFAULT 0,
  delta_gold Int64 DEFAULT 0,
  balance_after Int64 DEFAULT 0,
  payload_json JSON,
  dedupe_key String,
  version UInt32 DEFAULT progress_version,
  received_at DateTime64(3) DEFAULT now(),
  partition_tag String DEFAULT formatDateTime(ts, '%Y%m%d')
)
ENGINE = ReplacingMergeTree(version)
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_type, user_id, ts, entity_id)
SETTINGS index_granularity=8192;

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_user_daily
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, user_id)
AS
SELECT
  event_date,
  user_id,
  countIf(event_type = 'auth.events') AS sessions,
  sumIf(delta_gold, event_type IN ('reward.granted','shop.purchase')) AS net_gold_delta,
  countIf(event_type = 'event.claim') AS event_claims
FROM events_raw
GROUP BY event_date, user_id;

CREATE MATERIALIZED VIEW IF NOT EXISTS mv_event_completion
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, entity_id)
AS
SELECT
  event_date,
  entity_id,
  countIf(event_type='event.progress') AS progress_updates,
  countIf(event_type='event.claim') AS claims
FROM events_raw
GROUP BY event_date, entity_id;
