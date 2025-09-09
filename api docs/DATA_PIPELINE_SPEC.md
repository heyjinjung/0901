# Data Pipeline & Analytics Spec (Kafka → ClickHouse Ingestion)
문서 버전: 2025-08-21
Scope: Phase A 완료 직후 ~ Phase C 준비

## 1. 목표
- 코어 유저 루프(가입→로그인→이벤트/미션 진행→게임플레이→보상/상점 구매)의 행동 이벤트를 저지연 수집
- Progress / Claim / Economy 변경을 재현(replay) 가능하게 하고 중복 지급 및 손실 리스크 최소화
- ClickHouse 단일 사실 테이블(events) + 보조 집계(Materialized Views) 구조로 실시간 KPI (DAU, ARPDAU, Event Completion Rate) 서빙

## 2. 이벤트 표준 Envelope
```json
{
  "schema_version": 1,
  "event_type": "event.progress",        // 네임스페이스.액션
  "event_id": "evt_2025-08-21T12:34:56.789Z_ab12", // uuid 혹은 조합키
  "user_id": 123,
  "source": { "service": "backend", "host": "api-1" },
  "ts": "2025-08-21T12:34:56.789Z",      // ISO8601 UTC
  "ingested_at": "2025-08-21T12:34:56.900Z", // 파이프라인 주입 시각(옵션)
  "sequence": 4567890123,                 // Kafka 파티션 offset 기반 증가 (소비 측 계산도 가능)
  "payload": { ... domain specific ... },
  "dedupe_key": "event.progress:123:55:7" // event_type:user_id:entity_id:progress_version 등
}
```

필수 필드: event_type, user_id, ts, payload
멱등성 기준: dedupe_key (ClickHouse ReplacingMergeTree + version column) or Collapsing / Aggregating 전략

## 3. Kafka 토픽 설계
| Topic | Key | Partitioning Strategy | Payload 핵심 | 소비자 |
|-------|-----|-----------------------|--------------|--------|
| auth.events | user_id | hash(user_id) | signup/login/logout | analytics, session-service |
| event.progress | event_id | hash(event_id) | {event_id, user_id, progress_version, current[]} | analytics, realtime-push |
| event.claim | event_id | hash(event_id) | {event_id, user_id, reward_items[], progress_version, balance} | analytics, anti-fraud |
| mission.progress | mission_id | hash(mission_id) | {mission_id, user_id, progress_version, current[]} | analytics |
| mission.claim | mission_id | hash(mission_id) | {mission_id, user_id, reward_items[], progress_version, balance} | analytics |
| reward.granted | user_id | hash(user_id) | {source_type, source_id, delta_gold, balance, reason} | balance-audit, analytics |
| shop.purchase | user_id | hash(user_id) | {tx_id, status, product_id, amount_gold, price_cents} | revenue-aggregator |
| game.session | session_id | hash(session_id) | {session_id, user_id, game_type, started_at, ended_at?, delta_gold} | gameplay-insights |

압축: LZ4 (기본) / retention 7~14일 (DLQ 백업 전 단계)
DLQ 정책: 파싱 실패/스키마 미스매치 이벤트는 `<topic>.dlq` (단일 파티션)

## 4. ClickHouse 스키마
### 4.1 Raw Events (단일 테이블)
엔진: MergeTree (ReplacingMergeTree(version))
```sql
CREATE TABLE events_raw
(
  event_date Date DEFAULT toDate(ts),
  ts DateTime64(3) CODEC(Delta, ZSTD(3)),
  event_type LowCardinality(String),
  user_id UInt64,
  entity_id UInt64 DEFAULT 0,          -- event_id / mission_id / tx_id 등 맵핑
  progress_version UInt32 DEFAULT 0,
  delta_gold Int64 DEFAULT 0,
  balance_after Int64 DEFAULT 0,
  payload_json JSON,                   -- 원문 payload (JSON)
  dedupe_key String,
  version UInt32 DEFAULT progress_version, -- Replacing 기준
  received_at DateTime64(3) DEFAULT now(),
  partition_tag String DEFAULT formatDateTime(ts, '%Y%m%d')
)
ENGINE = ReplacingMergeTree(version)
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_type, user_id, ts, entity_id)
SETTINGS index_granularity=8192;
```

주의:
- JSON 타입(Cloud / 최신 CH) 미지원 환경이면 String + JSONExtract 사용
- version = progress_version (claim 이 progress 보다 늦게 arrive 하면 최신 버전 승리)

### 4.2 Materialized Views
1) 일자/사용자 KPI (DAU, Gold Earn/Spend)
```sql
CREATE MATERIALIZED VIEW mv_user_daily
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, user_id)
AS
SELECT
  event_date,
  user_id,
  uniqCombinedIf(sessionUniq, event_type IN ('auth.events')) AS sessions,
  sumIf(delta_gold, event_type IN ('reward.granted','shop.purchase')) AS net_gold_delta,
  countIf(event_type = 'event.claim') AS event_claims
FROM events_raw
GROUP BY event_date, user_id;
```
(실제 구현 시 sessionUniq 대체 컬럼 필요 → signup/login 구분 등 조정)

2) 이벤트 완료율
```sql
CREATE MATERIALIZED VIEW mv_event_completion
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMM(event_date)
ORDER BY (event_date, entity_id)
AS
SELECT
  event_date,
  entity_id,                                   -- event_id
  countIf(event_type='event.progress') AS progress_updates,
  countIf(event_type='event.claim') AS claims
FROM events_raw
GROUP BY event_date, entity_id;
```

## 5. Ingestion Flow
1. Backend emits domain events (sync path) after DB commit (outbox 패턴 권장 Phase B)
2. Kafka Producer (async) 전송 → 실패 시 재시도 + 로컬 fallback 로그(파일) → 수동 재주입 스크립트
3. Kafka Connect or Custom Consumer → ClickHouse HTTP batch insert (1~2s flush interval, 1MB or 5k rows)
4. Materialized Views 자동 집계 → Downstream API (metrics service) 질의

## 6. Outbox 패턴 (Phase B)
테이블 예시: `event_outbox(id BIGSERIAL, event_type TEXT, payload JSONB, created_at, published_at NULLABLE)`
- 트랜잭션 내 INSERT
- Publisher Daemon: `WHERE published_at IS NULL` pull + produce + set published_at
- 재시도 횟수 초과 row alerting (Prometheus counter)

## 7. 멱등/중복 제거 전략
| Layer | Mechanism | Notes |
|-------|-----------|-------|
| Backend | idempotency keys (claim, purchase) | 이미 구현 일부 확장 |
| Kafka Consumer | dedupe_key Memory LRU (TTL=10m) | 고빈도 progress 폭주 보호 |
| ClickHouse | ReplacingMergeTree(version) | progress_version 우선 |
| Downstream Query | `FINAL` (필요 시) | 비용 고려 (주요 리포트만) |

## 8. 스키마 진화
- schema_version 필드 증가 시: 새 필드 payload_json.* 접근은 `JSONHas` 가드
- 이벤트 타입 추가: event_type LowCardinality 컬럼 자동 사전 확장 (Cardinality 폭증 모니터링)
- 제거/변경: 구 버전 consumer deprecate 일정 문서화 (최소 2주 overlap)

## 9. KPI / 질의 예시
최근 7일 Active Users:
```sql
SELECT count(DISTINCT user_id) FROM events_raw WHERE event_type='auth.events' AND ts > now() - INTERVAL 7 DAY;
```
Event Claim Conversion:
```sql
SELECT entity_id, claims / NULLIF(progress_updates,0) AS claim_rate
FROM mv_event_completion WHERE event_date >= today()-7
ORDER BY claim_rate DESC LIMIT 20;
```
Whale 정의 (30일 결제 ≥ 50000 gold):
```sql
SELECT user_id
FROM events_raw
WHERE event_type='shop.purchase' AND ts > now() - INTERVAL 30 DAY
GROUP BY user_id
HAVING sum(delta_gold) >= 50000;
```

## 10. 보안 & 프라이버시
- PII 최소화: nickname 등 가명 미수집 (user_id 만 사용)
- 필요 시 user_id → UInt64(hash(user_id + salt)) materialized column 추가
- 데이터 보존: raw 400일, MV 동일 파티션 정책; Rollup 테이블로 400일 이후 요약 유지 예정

## 11. 모니터링
| Metric | Type | Source |
|--------|------|--------|
| kafka_produce_fail_total | Counter | backend producer wrapper |
| outbox_pending | Gauge | outbox poller |
| ch_insert_batch_size | Histogram | ingestion worker |
| ch_insert_latency_ms | Histogram | ingestion worker |
| dedupe_lru_evictions | Counter | consumer dedupe cache |

Alert Rules (초안):
- produce 실패율 >1% (5m) → WARN
- outbox_pending > 10k rows → CRITICAL (lag)
- ch_insert_latency_p95 > 2000ms (5m) → WARN

## 12. Phase Rollout
| Phase | Scope | Success Criteria |
|-------|-------|------------------|
| A | Backend progress_version & unified dashboard (완료) | Claim 응답 표준 적용 |
| B | Outbox + Kafka emission (progress/claim/purchase) | 이벤트 누락률 <0.1% (샘플 대조) |
| C | ClickHouse ingest + Materialized Views | KPI 쿼리 p95 < 500ms |
| D | Real-time push (SSE/WS) + anomaly alerts | progress UI latency < 2s from server commit |

## 13. 리스크 & 대응
| Risk | Impact | Mitigation |
|------|--------|------------|
| Outbox 누락 (daemon crash) | 이벤트 손실 | 재시작 시 미발행 row 재처리, published_at NULL 기준 |
| Kafka 적재 지연 | 실시간 KPI 늦음 | 배치 flush 조건 조정, backpressure 로그 |
| CH 파티션 폭증 | 스토리지 비용 | TTL + rollup, low-cardinality 관리 |
| Progress 폭주(봇) | 비용/노이즈 | rate limit + dedupe LRU hit ratio 모니터 |
| Schema drift 미문서화 | 소비자 크래시 | schema_registry.md + 버전 필드 증가 프로세스 |

## 14. TODO (Implementation Backlog)
1. `event_outbox` 테이블 + Alembic migration
2. Producer wrapper (sync emit → enqueue outbox, async flush)
3. Outbox Poller (async task / separate service)
4. Kafka topics provisioning IaC 문서화
5. ClickHouse DDL 적용 스크립트 및 smoke query
6. Ingestion Worker (python or kcat+materialize) 프로토타입
7. Metrics exporter 통합 (Prometheus)
8. Dashboards (Grafana) 패널 정의 파일 초안

---
Appendix A. Sample Payloads
```json
// event.progress
{ "event_id":55, "user_id":123, "progress_version":7, "current":[{"type":"plays","current":4,"target":5}] }
// event.claim
{ "event_id":55, "user_id":123, "progress_version":8, "reward_items":[{"type":"gold","amount":1000}], "balance":5600 }
// shop.purchase
{ "tx_id":991, "user_id":123, "status":"success", "product_id":2001, "amount_gold":2600, "price_cents":199 }
```
