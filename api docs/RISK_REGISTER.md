# Risk Register (Core Loop & Data Pipeline)
문서 버전: 2025-08-21

## Legend
| Severity | Definition |
|----------|------------|
| H | 사용자 영향 or 재무 손실 가능성 높음 |
| M | 기능 저하 / 지연 |
| L | 경미한 UX 영향 |

| Likelihood | Definition |
|------------|------------|
| H |  >30% 6주 내 발생 가능 |
| M | 10~30% |
| L | <10% |

## 1. Technical Risks
| ID | Category | Description | Impact | Likelihood | Mitigation | Owner | Status |
|----|----------|------------|--------|------------|------------|-------|--------|
| R1 | Data Integrity | progress_version desync (로컬 optimistic 누락) | Wrong UI state / duplicate progress PUT | M | gap>1 detector + refetch | Frontend | Open |
| R2 | Reward Duplication | Double claim race (네트워크 retry) | 재무 손실 (gold 과지급) | H | idempotency_key + unique constraint + audit log | Backend | Open |
| R3 | Negative Balance | 동시 purchase/claim 경쟁 조건 | 데이터 무결성 손상 | M | DB level CHECK(>=0) + serialized wallet update (Phase D) | Backend | Planned |
| R4 | Outbox Lag | daemon crash / backlog 증가 | 실시간 KPI 지연 | M | pending gauge alert, restart policy | SRE | Planned |
| R5 | Event Loss | producer 실패 (네트워크) | 분석 why-not, 모델 편향 | L | retry w/ exponential backoff + local fail log | Backend | Planned |
| R6 | Kafka Unavailability | broker outage | emit 실패 → 손실 위험 | M | outbox buffer (durable) + circuit breaker | DevOps | Planned |
| R7 | ClickHouse Storage Bloat | 파티션 증가 / TTL 미적용 | 비용 증가 & 성능 저하 | M | TTL + rollup strategy doc (Phase D) | Data | Planned |
| R8 | Schema Drift | consumer 파싱 실패 | ingest 중단 | M | schema_version + compatibility rules | Data | Open |
| R9 | Dedupe Memory Pressure | LRU eviction 과다 | 중복 이벤트 집계 | L | metrics (dedupe_lru_evictions) + size tuning | Data | Planned |
| R10 | Mission Claim Non-Standard | 이벤트와 이질적 응답 | 클라이언트 처리 분기 증가 | H | align schema Phase B | Backend | Planned |

## 2. Security & Compliance
| ID | Category | Description | Impact | Likelihood | Mitigation | Owner | Status |
|----|----------|------------|--------|------------|------------|-------|--------|
| S1 | Token Replay | refresh 토큰 탈취 재사용 | 계정 탈취 | L | reuse detection + revoke all active | Backend | Existing |
| S2 | PII Leakage | 분석 경로에 nickname 등 PII 유입 | 규제 / 프라이버시 우려 | L | raw events exclude PII, hash option | Data | Open |
| S3 | Unauthorized Reward Injection | 내부 API misuse | 재무 손실 | L | RewardService allowlist source_type + audit | Backend | Planned |
| S4 | Rate Abuse (progress spam) | 봇 자동 진행 | 비용/지표 왜곡 | M | rate limiter (user,event) + anomaly scoreboard | Backend | Planned |

## 3. Operational
| ID | Category | Description | Impact | Likelihood | Mitigation | Owner | Status |
|----|----------|------------|--------|------------|------------|-------|--------|
| O1 | Monitoring Gaps | produce_fail_total 미노출 | 지연 탐지 실패 | M | metrics instrumentation Phase B | SRE | Planned |
| O2 | Alert Fatigue | 과도한 경고 (lag, loss) | 무시 → 실 사고 | M | severity 기준 초기 튜닝 | SRE | Planned |
| O3 | Manual Backfills | 장애 후 수동 재주입 복잡 | 복구 지연 | M | replay tooling Phase D | Data | Planned |

## 4. Product / UX
| ID | Category | Description | Impact | Likelihood | Mitigation | Owner | Status |
|----|----------|------------|--------|------------|------------|-------|--------|
| P1 | Dashboard Staleness | polling 간격 동안 오래된 gold 표시 | 혼란, 신뢰 저하 | M | SSE push Phase C | Frontend | Planned |
| P2 | Catalog Price Drift | flag ON/OFF 타이밍 mismatch | 잘못된 할인 UI | L | refetch on mismatch error | Frontend | Open |
| P3 | Limited Stock Race | 동시에 0→구매 실패 UX | 좌절감 | M | stock optimistic disable + retry guidance | Frontend | Planned |

## 5. Tracking & Review
- 주간 리뷰: 신규 incident / 변경된 likelihood 재평가
- 변경 관리: Mitigation 상태 변경 시 commit 메시지에 R# 참조
- Deprecation: resolved & stable 4주 유지 시 CLOSE 마킹 후 하단 아카이브 이동

## 6. Near-Term Actions
| Action | Related Risks | ETA |
|--------|---------------|-----|
| Mission claim schema align | R10 | Phase B W2 |
| Outbox migration | R4,R5,R6 | Phase B W2 |
| RewardService unify | R2,S3 | Phase B W3 |
| SSE progress push | P1,R1 | Phase C W5 |
| DQ negative balance rule | R3 | Phase D W6 |

---
Archive: (empty)
