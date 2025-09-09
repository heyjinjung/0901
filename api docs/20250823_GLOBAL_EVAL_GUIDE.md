# 🎰 Casino-Club F2P 상용 기준 전역 가이드 & 점검 체크리스트 (v0.1 / 2025-08-23)

본 문서는 상용 카지노 게임 웹 수준을 기준으로, 현재 프로젝트를 전역적으로 평가·개선하기 위한 실행형 가이드와 체크리스트입니다. 최소 변경 원칙과 컨테이너 표준(docker-compose) 하에 진행하며, 테스트 그린·Alembic 단일 head·/docs 스키마 일관을 성공 기준으로 합니다.

## 1) 목적/범위
- 목적: 가입→로그인→플레이→보상/결제→이벤트→로그아웃 전 과정이 실시간으로 UI에 반영되고, 데이터/보안/관측성이 상용 기준을 충족하도록 보증.
- 범위: Backend(FastAPI) / Frontend(Next.js) / DB(PostgreSQL) / Cache(Redis) / MQ(Kafka) / OLAP(ClickHouse) / Monitoring(Prometheus+Grafana).

## 2) 성공 기준(SLO-ish)
- 가용성: 핵심 API(인증/게임/상점/리얼타임) 99.5%+ (개발 환경은 smoke 기준 충족).
- 성능: p95 API < 250ms(읽기), < 400ms(쓰기), WS 이벤트 전달 지연 p95 < 500ms.
- 데이터 일관: 경제(골드) 음수 잔액 0건, 멱등 키 재진행 성공률 100%(TTL 내), 클릭하우스 적재 누락률 < 0.5%.

## 2-bis) 최신 상태 요약(2025-08-24)
- 지금 되는 것
	- 모니터링 정상: Prometheus 기동/정상, 룰 로드 OK(purchase-health 4개, kafka_consumer_health 2개), /targets up.
	- Kafka Exporter up, Grafana Consumer Lag 패널 동작.
	- OpenAPI 스모크 통과(수동 수출 기준), Alembic head 단일 유지.
- 남은 것(우선순위)
	1) pytest 스모크: 결제(/api/shop/buy), 스트릭 경계 케이스 복구/검증.
	2) ALERT_PENDING_SPIKE_THRESHOLD 환경별 튜닝(.env.* 반영) 및 관찰값 기반 재보정.
	3) OpenAPI 재수출/CI 연계(PR 디프 코멘트), Kafka Lag 임계 재튜닝(관찰 후).

	## 2-ter) 최신 상태 추가(2025-08-25)
	- 런타임/헬스: `/health` 200, `/docs` 200. Alembic heads 단일 유지(`c6a1b5e2e2b1`).
	- 테스트: 제한/결제 스모크 9개 테스트 GREEN(경고는 기능 무영향).
	- 레거시 WS 메트릭: `/metrics`에 아래 지표 노출 및 증가 검증.
		- `ws_legacy_games_connections_total`: 총 연결 시도 카운터.
		- `ws_legacy_games_connections_by_result_total{result="accepted|rejected"}`: 결과 라벨별 카운터.
		- 비활성(ENABLE_LEGACY_GAMES_WS=0) 상태에서 스크립트 실행 시 `rejected` 증가 확인.
		- 활성 상태에서 `accepted` 검증 예정.
	 - 기준 브랜치: 업스트림 `7c07a00` 기준으로 재정렬 완료(`merge/upstream-base-7c07a00`).

## 3) 아키텍처 표준 요약
- 설정: `app.core.config.settings` 단일 소스. 레거시 `app/config.py`는 shim(확장 금지).
- 라우터: games 관련 엔드포인트는 `app/routers/games.py` 단일화.
- 리얼타임: `/api/realtime/sync` WS 허브 단일 채널. 메시지 스키마 `{ type, user_id, data, timestamp? }`.
- 마이그레이션: Alembic 단일 head 유지(현재 head: f79d04ea1016), merge 전략 엄수.

## 4) 기능 영역별 체크리스트(실행형)

### A. 인증/세션
- 구현 위치
	- 라우터: `backend/app/routers/auth.py`, `users.py`
	- 세션/토큰: `backend/app/services/auth_service.py`, `models/auth_models.py`
	- 메인 등록: `backend/app/main.py` (auth, users include)
- 검증 방법
	- REST: `POST /api/auth/signup`, `POST /api/auth/login`, `GET /api/auth/me`
	- 실패락: 잘못된 비밀번호 6회 → 429 확인(문서의 정책 5회/10분)
	- 토큰 회전: 만료 직전 요청 → 401 후 1회 refresh 재시도 성공
	- DB: Users/Refresh 토큰 레코드 생성/상태 확인
- 로그 포인트
	- `AuthService.verify_token`, `AuthService.login` INFO/ERROR
	- 실패락 카운터 증가 시 WARN (추가 권장)

### B. 프로필/스트릭/업적/배틀패스
- 구현 위치
	- 프로필/대시보드: `backend/app/routers/dashboard.py`, `users.py`
	- 스트릭: `backend/app/routers/streak.py`, Redis 유틸 `app/utils/redis.py`
	- 업적 서비스: `backend/app/services/achievement_service.py`
- 검증 방법
	- REST: `GET /api/dashboard`, `POST /api/streak/claim`
	- 프론트: 대시보드 진입 시 스냅샷 노출, 클레임 후 값 증가
	- Redis: 스트릭 키 증가/TTL 확인
- 로그 포인트
	- `streak.py` claim 처리 INFO, 멱등 예외 WARN
	- `dashboard` 조립 시간 DEBUG (성능 추적용)

### C. 경제/상점/보상
- 구현 위치
	- 상점/보상 라우터: `backend/app/routers/shop.py`, `rewards.py`
	- 결제/멱등/Fraud: `backend/app/services/payment_service.py`(예상), Redis 키 전략 문서
	- 경제 단일화: 관련 모델/서비스에서 gold-only 정책(문서: `api docs/20250808.md` 단일화 섹션)
- 검증 방법
	- REST: `/api/shop/catalog`, `/api/shop/buy`, 보상 지급 후 `/api/users/profile` 잔액 증가
	- 멱등: 동일 receipt/idempotency 키 재시도 → 단일 success 보장
	- Fraud: 짧은 윈도우 다회 요청 시 429 또는 정책 응답
- 로그 포인트
	- 구매 pending→success 전이 INFO, 실패 사유 포함
	- 멱등 충돌/선점 WARN, Fraud 차단 INFO/WARN

### D. 게임(슬롯/가챠/RPS/Crash) & 통계
- 구현 위치
	- 통합 게임 라우터: `backend/app/routers/games.py`
	- 액션: `backend/app/routers/actions.py` (DB+Kafka+허브 브로드캐스트)
	- Crash 상태: Redis 관리 유틸/서비스(파일 경로 주석 반영)
- 검증 방법
	- REST: `/api/games/*`, `/api/actions` 단건/벌크, `/api/actions/recent/{userId}`
	- Kafka: `app/kafka_client.py` consumer 레디 상태, 최근 메시지 확인
	- ClickHouse: 헬스 라우터 `backend/app/routers/olap.py` 기반 상태 확인
- 로그 포인트
	- `actions.log_action` 저장/브로드캐스트 INFO, Kafka 실패 WARN
	- 라운드 결과 처리 시 stats 업데이트 INFO

### E. 리얼타임(WS) 표준
- 구현 위치
	- 라우터: `backend/app/routers/realtime.py`
	- 허브: `backend/app/realtime/hub.py` (브로드캐스트/스로틀/최근 이벤트)
	- 프론트 클라이언트: `frontend/utils/wsClient.ts`, 대시보드 연동 `frontend/components/HomeDashboard.tsx`
- 검증 방법
	- WS 연결: `/api/realtime/sync` 접속, `sync_connected`/`initial_state` 수신
	- 이벤트: `user_action` 수신 시 최근 액션 자동 갱신(프론트 훅 트리거)
	- 유실 대비: 재연결 후 초기 상태 수신 확인
- 로그 포인트
	- 허브 register/unregister INFO, 브로드캐스트 DEBUG(샘플링), 스로틀 히트 카운트
	- 레거시 WS(제거 예정) 계측: `ws_legacy_games_connections_total`, `ws_legacy_games_connections_by_result_total{result}` 증가 여부.

### F. 데이터/스키마/계약
- [x] Postgres: 핵심 인덱스(`user_actions(user_id, created_at)` 등) 및 FK/UNIQUE 무결성. (증거: `cc_webapp_backup.sql` 내 `ix_user_actions_user_id`, `ix_user_actions_action_type`, `(action_type,"timestamp"), (user_id,"timestamp")` 인덱스 및 `ShopTransaction` 복합 UNIQUE `uq_shop_tx_user_product_idem` 확인)
- [x] Redis: 키 네이밍/TTL 정책, 멱등키/재고/스트릭 키 충돌 없음. (증거: `backend/app/utils/redis.py` 키 스킴 `user:{id}:streak:{action}` TTL=24h, `attendance:{YYYYMM}` TTL=120d, `session:{session_id}` TTL=1h; `shop.py` 멱등키/락키 `shop:idemp:*`, `shop:limited:idemp*` 일관)
- [x] Kafka: 토픽 존재/오프셋 모니터링, 재시작 시 재소비 전략 명시. (증거: `docker-compose.monitoring.yml`에 kafka_exporter 포함 및 `cc-webapp/monitoring/kafka_alerts.yml` 마운트, Prometheus job `kafka-exporter`, Grafana 대시보드 소비 지연 패널)

#### Kafka 운영 정책 요약(완료)
- 소비 그룹 네이밍: `cc.<domain>.<purpose>.<env>` 표준. 신규 그룹은 `auto_offset_reset=earliest`.
- 재시작/재소비: 일반 재시작은 동일 group.id 유지, 대규모 재소비는 전용 replay 그룹(`...replay.YYYYMMDDHH`).
- 오프셋 리셋: 장애 시 `--to-datetime` 우선, 필요 시 `--to-earliest`. 리셋 전/후 Lag 스냅샷과 알람 일시중지 포함.
- 모니터링: Grafana 패널 "Kafka Consumer Lag (by group/topic)" 지표 `sum(kafka_consumergroup_lag) by (consumergroup, topic)`.
- 알림: `KafkaHighConsumerLag`(5m lag>1000), `KafkaExporterDown`(2m) 활성. compose에 `kafka_alerts.yml` 마운트 완료.
- [x] ClickHouse: 파티션/정렬키 적용, 적재 지연/누락 모니터링. (증거: `backend/app/olap/clickhouse_client.py` MergeTree `PARTITION BY toYYYYMM(day)`/`ORDER BY` 구현; 모니터링 패널은 추후 보강)
- [x] 이벤트/HTTP 계약: OpenAPI 단일 소스, 메시지 스키마 문서와 일치(WS 스키마 표준 적용, OpenAPI 스냅샷 스크립트 준비).

### G. 관측성/운영
- 구현 위치
	- 글로벌 메트릭 라우터: `backend/app/routers/metrics.py` (`/api/metrics/global`, `/api/metrics/stream`)
	- Kafka/ClickHouse 클라이언트: `backend/app/kafka_client.py`, `backend/app/olap/clickhouse_client.py`
- Grafana 패널(예시)
	- 로그인 실패율(시간별), 결제 성공률, WS 연결 수/이벤트 지연, Kafka consumer lag, ClickHouse 적재 RPS/에러
- ClickHouse 쿼리 스니펫(예시)
	- 최근 1시간 액션 집계: `SELECT action_type, count() FROM events WHERE ts > now() - INTERVAL 1 HOUR GROUP BY action_type ORDER BY count() DESC;`
	- 사용자별 승/패 합계: `SELECT user_id, sum(wins) AS w, sum(losses) AS l FROM game_stats WHERE date >= today()-7 GROUP BY user_id ORDER BY w DESC LIMIT 50;`
- Prometheus 지표(추가 권장)
	- `ws_active_connections`, `realtime_event_lag_ms`, `shop_buy_success_total`, `shop_buy_failed_total`, `auth_login_locked_total`
	- 레거시 WS 지표: `ws_legacy_games_connections_total`, `ws_legacy_games_connections_by_result_total{result}`

#### 메트릭 검증(레거시 WS)
- 비활성 검증(rejected):
	1) backend에 `ENABLE_LEGACY_GAMES_WS=0` 적용(오버라이드 YAML backend.environment).
	2) `docker compose restart backend` 후 컨테이너 내부에서 `python -m app.scripts.ws_touch_legacy --host http://localhost:8000 --once` 실행.
	3) `/metrics`에서 `ws_legacy_games_connections_total`과 `{result="rejected"}` 증가 확인.
- 활성 검증(accepted):
	1) `ENABLE_LEGACY_GAMES_WS=1`로 전환 후 재시작.
	2) 동일 스크립트 실행 → `{result="accepted"}` 증가 확인.

#### 관측성 현황(2025-08-23)
- [x] Prometheus scrape 정합: backend job 라벨 `cc-webapp-backend`로 통일
- [x] Grafana 대시보드 프로비저닝: 기본 패널(HTTP/WS/구매 지표) 적용
- [x] Alert rules 마운트: `invite_code_alerts.yml` 로드 및 rule_files 활성화
- [x] 라이브 데이터 검증: 패널 실데이터 렌더 확인 및 임계치 1차 튜닝(5xx/P95 경보 추가, 구매 실패 사유 라벨 보정)

#### 관측성 업데이트(2025-08-24)
- [x] Prometheus 룰 파싱 오류 복구: `purchase_alerts.tmpl.yml` 들여쓰기/expr 정리 → 렌더 → `purchase_alerts.yml` 정상 로드.
- [x] Kafka 알림/패널 검증: `kafka_consumer_health` 그룹 로드, Kafka Exporter up, Grafana Consumer Lag 패널 동작.
- [ ] ENV 임계 튜닝: `ALERT_PENDING_SPIKE_THRESHOLD` 환경별 값 반영 및 관찰 후 재보정(다음 단계).

##### 알림 임계 및 외부화 계획(2025-08-24)
- 성공율 임계 98%→99% 상향 검토: 실데이터 추이 확인 후 `grafana_dashboard.json` thresholds green 기준 99로 상향 예정(스테이징에서 먼저 적용).
- Pending 스파이크 임계 외부화: [완료] ENV `ALERT_PENDING_SPIKE_THRESHOLD`(기본 20) 도입 → `scripts/render_prometheus_rules.ps1`가 `purchase_alerts.tmpl.yml`을 렌더링하여 `purchase_alerts.yml` 생성. `./cc-manage.ps1 tools start` 시 자동 실행.
- 운영 프로파일 분리: dev/tools/prod별 기본 임계 사전 정의(yaml 템플릿 생성 후 빌드 시 주입).

## 6-bis) 자동 스모크 시나리오(개발환경)
- Backend(pytest)
	- 로그인→/auth/me→스트릭 클레임→액션 생성→최근 액션 조회가 200/일관 JSON
	- 골드 잔액 증가·스트릭 카운트 증가 assert
	- 제한/결제 스모크: `app/tests/test_limited_holds_and_concurrency.py`, `app/tests/test_shop_buy.py`, `app/tests/test_limited_packages*.py` GREEN 유지
- 진행도(2025-08-24):
	- [ ] 결제 스모크: /api/shop/catalog → /api/shop/buy → profile 잔액 증가(멱등키 재시도 포함)
	- [ ] 스트릭 스모크: 최초/재시도/동시 요청 경계 테스트 복구
	- [x] OpenAPI 스모크: export_openapi → diff 테스트 그린 유지
- Frontend(Playwright)
	- 로그인 후 대시보드: 골드/스트릭/최근 액션 노출
	- 액션 발생 후 WS 이벤트 수신 → 최근 액션 DOM 갱신 확인
	- 재연결 시 초기 상태 DOM 값 일치 확인

### H. 보안/권한/규정 준수
- [ ] RBAC 역할(VIP/PREMIUM/STANDARD) 엔드포인트 가드.
- [ ] Admin API 보호/감사 로그, 비밀/키 관리(회전 계획 포함).
- [ ] 규정: PII 처리 구분, 성인콘텐츠 접근 연령검증 플로우.

### I. 신뢰성/마이그레이션/DR
- [x] Alembic 단일 head, destructive 변경 시 shadow+rename 전략. (현재 컨테이너 head: `c6a1b5e2e2b1`)
- [ ] 백업: pg_dump + WAL 보관 정책(개발은 스냅샷/시드로 대체), Redis cold-start seed.
- [ ] 롤백 절차/Compose 프로파일 분리(dev/tools/prod) 정리.

### J. 테스트/품질 게이트
- [ ] Build/Lint/Unit/Integration/E2E 스모크 그린.
- [ ] 핵심 시나리오: 인증, 스트릭, 상점 결제/프로모, 게임 액션, 리얼타임 반영, 한정 패키지.
- [x] OpenAPI 재수출 검증(수동 스냅샷/디프 스크립트 준비), 문서/테스트 동기화(진행 중).

## 5) 성숙도 단계(L1→L3)
- L1(MVP): 핵심 기능 작동 + REST 스냅샷 + 제한적 WS, 기본 지표/로그.
- L2(Beta): 전역 WS 커버리지, Fraud/HMAC/멱등 완비, 기본 대시보드, ClickHouse 적재.
- L3(Prod): 알림/자동화 수치 기반 운영, DR/백업 리허설 통과, SLA 수준 안정성.

## 6) “하루 사용자 여정” 실검증 시나리오
1) 초대코드로 가입 → 로그인(락/리프레시 확인) → 대시보드 스냅샷.
2) 스트릭 클레임 → 골드/레벨/스트릭 실시간 반영.
3) 슬롯 3판: 승/패/보상 반영, 최근 액션·통계 실시간 갱신.
4) 상점 구매 → 결제 성공 → 잔액 증가/보상 로그/실시간 배지 점등.
5) 이벤트 참여/진행/클레임 → 업적 업데이트 동시 확인.
6) 재접속(WS 재연결) → 초기 상태/백필 정상.

## 7) 위험/부채/우선순위
- 위험: 이벤트 스키마 분기/중복 라우터 잔존, 다중 Alembic head 재발, ClickHouse 지연 누락.
- 부채: 일부 레거시 API/유틸(단일화 대기), 전역 컨텍스트 없는 분산 상태 업데이트.
- 우선순위: WS 브로드캐스트 배선 완성 → 프론트 전역 리스너/스토어 → OLAP 위젯.

## 8) 부록: 리얼타임 이벤트 계약(초안)
- profile_update: { changes: { gold_balance?, level?, exp? } }
- reward_granted: { reward_type, amount, balance_after }
- streak_update: { action_type, streak_count }
- achievement_progress: { achievement_code, progress, unlocked }
- stats_update: { stats: { game_type?, wins?, losses?, ev? } }
- user_action: { action_type, client_ts?, context, server_ts }

— 본 문서는 운영 과정에서 계속 보강되며, 변경 요약은 `api docs/20250808.md`와 #final.md 파일에 누적 기록합니다.

## 9) 진행 현황 요약(2025-08-23)

### 완료(현재 반영됨)
- 리얼타임 허브 단일화: `/api/realtime/sync` 활성, 이벤트 스키마 표준 적용 `{type,user_id,data,timestamp?}`.
- 게임 액션 브로드캐스트: `POST /api/actions` → `user_action` 허브 전파.
- 보상 지급 브로드캐스트: `rewards.py` 경로에서 `reward_granted` + `profile_update` 허브 전파(비차단, 스로틀 준수).
- 환경 자동화: `cc-manage.ps1`에서 `.env.development → .env` 자동 복사(없을 때), README/문서 반영.
- 최근 액션 스냅샷: `GET /api/actions/recent/{user_id}` 엔드포인트 확인 및 테스트 커버리지 추가.
	- 테스트 추가: `cc-webapp/backend/app/tests/test_actions_recent_flow.py` (signup → action → recent 검증).
- 모니터링 정합: Prometheus job 라벨/스크레이프 타깃 정리(`cc-webapp-backend`), Grafana 대시보드/프로비저닝 적용, Alert rules 마운트.
- 구성 파일 오류 정리: Grafana 대시보드 JSON 이스케이프 수정, `docker-compose.override.local.yml` 스키마 오류 제거, `ci/export_openapi.ps1` 출력 보강.
- OpenAPI 스냅샷/디프: 컨테이너 내부 수출 후 루트 스냅샷/디프 파일 생성 스크립트 준비.

### 부분 진행/보강 예정
- 상점/결제 전 구간 WS 브로드캐스트 배선 보강(구매 성공/실패, 잔액 변경, 멱등 충돌 알림).
- Prometheus 지표 확장 및 Grafana 기본 대시보드(profiles: auth 실패율/WS 연결/consumer lag/적재 RPS).
- Frontend E2E(Playwright) 시나리오: 로그인→대시보드→액션→WS 반영→재연결 초기화.
- OpenAPI CI 통합: 스냅샷/디프 아티팩트 업로드 및 PR 코멘트 자동화.

### 검증/운영 메모
- 테스트: 컨테이너 내부에서 `pytest -q app/tests` 수행(핵심 스모크 포함), Alembic `upgrade head`로 단일 head 유지 확인.
- OpenAPI: 필요 시 `python -m app.export_openapi`로 재수출 후 `/docs` 단일성 확인.
- 트러블슈팅: 스키마 미반영 시 `app.openapi_schema=None` 재생성, JWT 실패는 `auth_token` 픽스처로 재현.

### 다음 단계 제안(우선순위)
1) 상점/결제 WS 브로드캐스트 완성(잔액/구매 상태 실시간 반영) → 프론트 전역 리스너 연결.
2) Prometheus/Grafana 프로비저닝 스크립트 추가 및 기본 패널 배치.
3) OpenAPI 재수출 자동화 + 변경 감시 테스트(`test_openapi_diff_ci.py`)와 연계.
4) 알림 임계 외부화(.env) 및 템플릿화로 환경별 기준 분기 적용.

#### 실행 현황(2025-08-23)
- WS 브로드캐스트는 buy/limited/webhook/settle 전 구간에서 발화하도록 정비(성공 시 profile_update 포함).
- Grafana 프로비저닝 스크립트 추가: `scripts/provision_grafana.ps1`(대시보드/데이터소스 템플릿 준비).
- OpenAPI 변경 감시 테스트 추가: `backend/app/tests/test_openapi_diff_ci.py`(핵심 경로 존재/스냅샷 대비 파괴적 변경 감지).

#### 사용 방법
- 모니터링 준비: PowerShell에서 `scripts/provision_grafana.ps1` 실행 후 `docker-compose.monitoring.yml`의 Grafana 프로비저닝 경로에 마운트.
- OpenAPI: 컨테이너 내부에서 `python -m app.export_openapi`로 `current_openapi.json` 갱신 후 pytest 실행.

#### 다음 보강 포인트
- Grafana 대시보드 실데이터 렌더 확인 및 임계치/패널 튜닝.
- OpenAPI 스냅샷/디프 CI 연동(아티팩트 업로드·PR 코멘트).
- 결제 전 구간 WS 브로드캐스트와 프론트 전역 리스너 보강.

---

## 10) 업데이트 메모(2025-08-24)

### 변경/검증
- 모니터링 네트워크: 외부 도커 네트워크 `ccnet` 연결(backend/postgres/redis/frontend) 후 Prometheus 컨테이너에서 `http://cc_backend:8000/metrics` 수신 확인.
- 백엔드 계측: FastAPI에 Prometheus Instrumentator 옵션 연동(`/metrics` 노출), 호스트에서도 200 OK 확인.
- Prometheus: `/-/ready` 200, `/targets` 접근 OK(PS 스크립트 이스케이프 이슈로 API 자동 검증은 부분 미완).
- 문서 동기화: `final.md`, `api docs/20250808.md`에 동일 변경 요약/검증/다음 단계 반영.

### 보강 필요(다음 단계)
1) 스크랩 타깃 고정화: compose에 `networks.ccnet.aliases: [backend]` 추가 또는 Prometheus 타깃을 `cc_backend:8000`로 변경 후 툴즈 재기동.
2) OpenAPI 재수출 및 테스트: 컨테이너 내부 `python -m app.export_openapi` → `openapi_diff_ci` 통과 확인(pytest).
3) Grafana 실데이터 확인과 알람 임계치 튜닝: `purchase_attempt_total` 등 핵심 카운터 패널 점검.

참고: Alembic head 단일 유지(문서 기준 f79d04ea1016), 스키마 변경 없음.

---

## 11) 업데이트 메모(2025-08-25)

### 변경 요약
- Backend pytest 스모크 일부 실행 결과 반영:
  - app/tests/test_reward_formula.py: 2 passed (경고 다수: passlib crypt, Pydantic v2 ConfigDict 전환 경고 – 기능 영향 없음).
  - app/tests/test_mvp_smoke.py::TestMVPSmoke::test_streak_claim_idempotency: FAIL (회원가입 500).
- 프론트 품질 규칙 강화: ESLint에 문자열 리터럴 `'/api/users/profile'` 사용 금지 룰 추가(대안: `'/api/users/me'`). 루트와 프론트 둘 다 적용하여 편차 방지.
- 알림 임계 외부화 현황: `.env.*`에 ALERT_PENDING_SPIKE_THRESHOLD dev=20, staging=25, prod=30 반영 상태.

### 검증 결과(원문 출력 요약)
```
FAILED app/tests/test_mvp_smoke.py::TestMVPSmoke::test_streak_claim_idempotency
AssertionError: {"detail":"Registration failed","error":{"code":"HTTP_500","message":"Registration failed","details":null,"request_id":"0b0fe75c84e2"}}
status_code: 500
Captured stdout: 🗄️ Alembic 데이터베이스 URL: postgres:5432/cc_webapp
```

### 트러블슈팅 요약(가설 → 점검 → 개선)
1) 가설
	- 초대코드 검증 실패 시 400이 반환되어야 하나 내부에서 500으로 승격되는 경로 존재(예외 매핑 미흡).
	- 혹은 회원가입 처리 중 DB 제약(UNIQUE/NOT NULL) 예외가 표준화되지 않고 500으로 전달.
	- INVITE_CODE 기본값(5858)과 런타임 설정 불일치 가능성(settings.UNLIMITED_INVITE_CODE).
2) 즉시 점검
	- 백엔드 컨테이너 로그 확인: `./cc-manage.ps1 logs backend` → /api/auth/register 호출 직후 Traceback/에러 원인 추출.
	- ENV 확인: `.env(.development)` 및 backend 환경에 `UNLIMITED_INVITE_CODE=5858` 노출 여부 확인.
	- FastAPI 예외 핸들러: Validation/도메인 에러가 HTTPException 4xx로 매핑되는지 확인.
3) 개선 제안
	- Invite 코드 불일치/중복 닉네임 등 사용자 입력 오류는 400 계열로 고정(메시지/에러코드 표준화).
	- AuthService.register 내 DB IntegrityError 캐치 → 409/400 변환.
	- 테스트 보강: register 실패 경로(잘못된 코드) 400 assert 추가.

### 다음 단계
- [ ] 컨테이너 로그에서 /api/auth/register 스택트레이스 캡처 후 원인 확정(Invite 검증/DB 제약/기타).
- [ ] 설정 정합성 확인: `UNLIMITED_INVITE_CODE=5858`이 런타임에서 유효한지 점검 및 문서화.
- [ ] 예외 매핑 보강(PR): 500 → 4xx 표준화, 에러페이로드 `{error:{code,message}}` 유지.
- [ ] 재검증: 아래 최소 스모크를 컨테이너 내부에서 재실행하여 GREEN 확인.
  - `pytest -q app/tests/test_mvp_smoke.py::TestMVPSmoke::test_streak_claim_idempotency`
  - `pytest -q app/tests/test_shop_buy.py::test_buy_gold_happy_path`

### 품질/운영 메모
- Pydantic v2 경고는 ConfigDict 전환으로 제거 가능(우선순위 낮음, 기능 영향 없음). 향후 모델별 config 마이그레이션 권장.
- ESLint 금지 경로 룰 추가로 프론트에서 레거시 프로필 엔드포인트 사용을 예방(권장 경로 `GET /api/users/me`).
