# 결제/구매 보안 상태 요약 (업데이트)

## Top 10 리스크 (최근 상태 반영)
1. (해결) 제한 상품 구매 기록 누락 → ShopTransaction 영속화 + integrity_hash 저장
2. (해결) 엔드포인트 Rate Limiting 부재 → /limited/buy 10초 5회 제한 적용
3. (부분) Fraud / Velocity 스코어링 미적용 → ZSET 수집만 (차단 룰 미도입)
4. (해결) Webhook 재생 방어 없음 → X-Timestamp + X-Nonce 재생차단(SETNX)
5. (해결) Webhook 멱등 처리 없음 → event_id 기반 Redis SETNX 중복 차단
6. (미구현) 부분 실패(Authorize 성공, Capture 불명확) VOID 스케줄러 부재
7. (부분) Redis 장애 시 Idempotency 약화 → pre-lock 적용했으나 Redis 단일 의존
8. (부분) 영수증 위변조 방지 → integrity_hash 저장 (HMAC 영수증 서명 TODO)
9. (진행) 감사 추적 누락 → 핵심 성공 경로 기록 완료, 일부 실패/예외 경로 미기록
10. (해결) Metric/지표 부재 → purchase_attempt_total Counter(flow/result/reason)

---
## High 우선순위 작업 (상태 태그)
제한상품 트랜잭션 영속화 - (완료) integrity_hash 포함
Rate Limiting 추가 - (완료) 10초 5회
Fraud Velocity 기본 룰 - (수집) 차단 룰 TODO
Webhook Replay 방어 - (완료) Timestamp+Nonce SETNX
Webhook 멱등 저장 - (완료) event_id SETNX 24h
부분 실패 VOID 처리 - (미구현) 타임아웃 큐 & gateway void
Idempotency 사전 락 - (완료) processing 키 60s
영수증 서명 도입 - (대기) HMAC 영수증, 현재 hash만
감사 추적 보강 - (진행) 실패/예외 전수 기록 남기기 TODO
구매 메트릭 계측 - (완료) Counter(flow/result/reason)

---
## 1. 핵심 구매 흐름
- 상품 판매 기간 검증: [OK] start/end & is_active 확인
- 1인 한도: [OK] per_user_limit 초과 차단
- 재고 + 홀드 TTL: [OK] 예약 & hold + 만료 스윕
- 프로모션 사용량 제한: [OK] can_use_promo / 기록
- Idempotency (사전 락 + 성공 키): [개선] pre-lock(SetNX) + 성공시 확정 키, Redis 의존
- 금액 서버 계산: [OK] 저장된 price 기반 산출
- 통화 검증: [부분] 허용 목록 TODO(USD/EUR/KRW 화이트리스트 예정)
- 구매 이벤트 Kafka 전송: [부분] 재시도/DLQ 없음 (데이터 누락 가능)

## 2. 결제/영수증 무결성
- Auth→Capture 2단계: [OK] 실패 시 재고 롤백
- Gateway 재시도 Wrapper: [부분] 혼재된 호출 패턴
- Receipt 고유성: [부분] 모델 unique 있으나 제한상품 경로 미삽입
- Webhook HMAC 서명: [OK] X-Signature sha256
- Webhook 재생 방어: [OK] timestamp+nonce+replay SETNX
- Receipt 위조 방지: [부분] integrity_hash 저장 (독립 HMAC 서명 TODO)
- Fraud/Velocity 감지: [부분] ZSET 기록 수집 (차단 기준 미적용)
- Rate Limiting: [OK] 10초 5회 제한
- 일일/누적 한도: [미구현]
- 고액 수동 리뷰 큐: [미구현]
- Refund/Chargeback 워크플로: [부분] 토큰 클로백 자동검증 없음
- 관리자 감사 로그: [OK]

## 3. 데이터 / 스키마 준비도
- shop_transactions 범용성: [부분] 일부 흐름 누락
- user_segments (rfm/ltv): [부분] 갱신 잡 미완
- user_actions / user_rewards 연결: [OK]
- 프로모션 사용 기록: [OK]
- risk_profile 필드: [부분] 채움 로직 미흡

## 4. 복구 / 재시도
- Auth 실패 정리: [OK]
- Capture 실패 정리: [OK]
- 성공 후 hold 제거: [OK] 베스트에포트
- 부분 실패 보상(VOID): [미구현]
- Webhook 멱등 처리: [OK] event_id SETNX 24h
- Pending 스위퍼: [미구현]
- Redis 장애 시 Idempotency 약화: [부분]

## 5. 관측성 / 로깅
- 구조화 Action 로그: [부분] 문자열 JSON, 스키마 강제 없음
- 구매 분석 이벤트: [부분] Fire-and-forget
- 감사 추적 완결성: [부분] 트랜잭션 누락 구간
- 메트릭 계측: [OK] purchase_attempt_total Counter

## 6. 보안 위생
- Webhook 시크릿 관리: [부분] 단일 고정 키, 롤테이션 없음
- 입력 검증 (currency, card_token): [미구현] 기본 타입만
- 결제 별도 최소 권한 DB 계층: [미구현]
- 민감정보 저장 회피: [OK] 토큰만 사용 (추가 검증 필요)

## 7. 로드맵 (요약)
1) Fraud 차단 룰(임계치) 적용 → 2) VOID/Refund 스케줄러 → 3) Receipt HMAC 서명 & 실패 경로 기록 전수 → 4) Metrics/Logging 스키마 표준화 → 5) Segmentation 갱신 잡 → 6) 고액 리뷰 & 고급 Fraud/ML.

## 8. 48시간 Quick Wins
- 제한상품 성공 경로: ShopTransaction insert + 영수증 서명 (HMAC)
- /buy-limited RateLimit: (완료) 10초 5회 → 429
- 통화 허용 목록(USD, EUR, KRW) & 미허용 400 반환
- Webhook X-Timestamp + 재생방지 Redis setnx (완료)
- Idempotency pre-lock (processing 키) 도입 (완료)

## 9. 지연(전략) 항목
- ML 기반 Fraud 스코어링
- 글로벌/멀티리전 영수증 검증 서비스
- 이벤트 소싱 기반 재무 원장
- Feature Store + 실시간 이상탐지

## 10. 요약
핵심 구매 제한·재고·기본 멱등 로직은 동작하지만 감사·Fraud·Webhook 재생·보상/VOID·관측성 공백이 크므로 “감사 추적 + 재시도/재생 방어 + 초기 Fraud 신호 + 메트릭” 순으로 강화가 최단 ROI.

---
생성: 자동 상태 스냅샷 (표 -> 목록 구조 전환)
