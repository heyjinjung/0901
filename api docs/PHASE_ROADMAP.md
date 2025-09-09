# Phased Roadmap (Core Loop & Analytics Enablement)
문서 버전: 2025-08-21

## Overview
- 목표: 가입→로그인→대시보드→이벤트/미션 진행→게임→보상/상점 구매 → 재방문 루프 최적화
- 전략: 작은 스키마 안정화(Phase A) → 이벤트 발행/수집 기반(Data Layer) → 실시간 피드백 및 자동화 → 성능/거버넌스 강화

## Phase A (완료)
| Goal | Deliverables | Status | Success Metric |
|------|--------------|--------|----------------|
| Aggregation & Integrity | /api/dashboard 통합, progress_version 컬럼, last_progress_at, unique constraints, claim response reward_items[] | DONE | 테스트 통과 + Claim 응답 표준 적용 |
| Deterministic Tests | Limited Package 안정화, 시퀀스 drift 스크립트 | DONE | 한정 패키지 관련 flaky 0 |

Exit Criteria: Unified dashboard 사용 준비 / 이벤트 & 미션 모델 버전 필드 반영 / Claim response 스키마 확정

## Phase B (Event Emission & Standardization)
| Goal | Work Items | Notes | Owner |
|------|------------|-------|-------|
| Outbox 기반 신뢰성 | event_outbox 테이블 + daemon | 멱등 publish, retry 메트릭 | Backend |
| Kafka Topics Provisioning | auth/events/progress/claim/purchase/session | IaC 문서 / config map | DevOps |
| Mission Claim 스키마 정렬 | mission.claim 응답 events.claim 동일화 | reward_items standard | Backend |
| Unified RewardService | 모든 보상 지급 단일 경로 (이벤트/미션/상점/기타) | idempotency_key 관리 | Backend |
| Health & Metrics | produce_fail_total, outbox_pending | Prometheus | SRE |

Exit Criteria: 주요 도메인 이벤트 95%+ Kafka 전송 / Mission claim 표준화 / RewardService 단일화

## Phase C (Ingestion & Real-time Feedback)
| Goal | Work Items | Notes |
|------|------------|-------|
| ClickHouse Raw + MV | events_raw + mv_user_daily + mv_event_completion | DDL + smoke query |
| Ingestion Worker | Batch insert (1s/5k/1MB) with LZ4 | Backpressure 로그 |
| Real-time Push (SSE) | progress/claim/reward.granted → client invalidate | gap>1 refetch 전략 |
| Gameplay Hooks | slot/rps 결과 → 자동 event.progress emit | 기존 manual PUT 축소 |
| Anomaly Detection Proto | high delta_gold / rapid claims | simple rule engine |

Exit Criteria: Dashboard KPI (DAU, claims) p95 query <500ms / Progress UI latency <2s after server commit

## Phase D (Optimization & Governance)
| Goal | Work Items | Notes |
|------|------------|-------|
| Query Cost Optimization | Materialized rollups / TTL / partition pruning | storage forecast |
| Config & Flags Service | Runtime flag store (DB or Redis backed) | remove scattered ENV toggles |
| Security Hardening | token rotation automation / audit trails | risk table align |
| Data Quality Rules | Negative balance auto-fix, duplicate claim anomaly alerts | metrics integration |
| Backfill & Replay Tooling | raw → domain state reconstruct scripts | disaster recovery |

Exit Criteria: Stable cost curve / automated DQ alerts / minimal manual ops for rollback/replay

## Cross-Phase Considerations
| Topic | Decision |
|-------|----------|
| Schema Evolution | additive + versioned (schema_version, progress_version) |
| Idempotency | purchase/claim/reward unified key strategy (source_type:source_id:user) |
| Concurrency | optimistic UI + authoritative server (progress_version) |
| Observability | Prometheus + structured logs + (later) tracing hooks |
| Security | minimal PII, hashed user_id optional in CH |

## Testing Strategy by Phase
| Phase | Layer | Tests |
|-------|-------|-------|
| A | API & Model | existing pytest + claim schema asserts |
| B | Outbox & Produce | unit (publish), integration (Kafka mock), e2e emit count |
| C | Ingestion & SSE | consumer idempotency, latency SLA, UI contract tests |
| D | Governance | DQ rule simulation, replay correctness, perf regression |

## Rollback Guidelines
| Change Type | Rollback Action |
|-------------|-----------------|
| New Column Add | ignore column in code (backward safe) |
| Outbox Enable | disable daemon, resume direct publish (temp) |
| SSE Push | revert to polling intervals |
| RewardService Merge | feature flag: REWARD_UNIFIED=0 |
| ClickHouse MV | detach view (preserve raw) |

## Metrics & SLO
| Metric | Target |
|--------|--------|
| Event Loss Rate | <0.1% (sample diff vs outbox) |
| Progress UI Latency | p95 < 2s commit→render |
| Ingestion Lag | < 5s median | 
| Claim Double-Payout | 0 confirmed incidents |
| Negative Balance | 0 persisted rows |

## Open Questions
- Mission progress_version 별도 분리 vs 재활용? (현재 재활용 구조 가정)
- SSE vs WebSocket: Stage C 최소 구현 SSE, 고빈도 필요 시 WSS 재평가
- Reward audit trail: 별도 ledger 테이블 필요 시점 (Phase D 가능성)

## High-Level Timeline (Indicative)
| Week | Focus |
|------|-------|
| W1 | Finish Phase A (완료) |
| W2 | Outbox + Topics (B) |
| W3 | RewardService unify + Mission claim align (B) |
| W4 | ClickHouse DDL + Ingestion (C) |
| W5 | SSE + Gameplay hooks (C) |
| W6 | Optimization kickoff (D) |

---
Changelog:
- 2025-08-21: Initial draft created after Phase A completion.
