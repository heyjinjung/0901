# Kafka 운영 표준(SOP)

본 문서는 개발/스테이징/프로덕션 환경에서 Kafka 소비자 운영 시 일관된 정책을 제공하기 위한 지침입니다.

## 1) 소비 그룹 네이밍 규칙
- 형식: cc_<service>_<env>[_<role>]
  - 예시: cc_app_dev, cc_app_staging, cc_app_prod, cc_olap_worker
- 원칙: 환경(DEV/STG/PRD)별 고유 그룹 사용으로 오프셋 격리. Job/워크커별 세분화 필요 시 suffix 부여.

환경 변수
- KAFKA_CONSUMER_GROUP: 기본 소비 그룹. .env.*에서 환경별 기본값 제공
- KAFKA_TOPICS: 구독 토픽 목록(콤마 구분). 예: cc_user_actions,cc_rewards,buy_package

## 2) 오프셋 초기화(auto_offset_reset)
- 정책: earliest
  - 신규 그룹 또는 저장된 오프셋이 없는 경우, 가장 이른 오프셋부터 소비하여 데이터 유실 없이 초기 싱크 보장.
  - 운영 중인 그룹에 대해 수동 초기화는 신중히 수행(대규모 재소비 유발 가능).

구현 참고
- app/consumers/olap_worker.py: auto_offset_reset="earliest", enable_auto_commit=False (처리 완료 후 커밋)
- backend/kafka/kafka_config.py: auto_offset_reset='earliest', enable_auto_commit=True (샘플)

## 3) 재시작/재소비 전략
- 정상 재시작: 저장된 오프셋부터 재개. OLAP 워커는 처리 단위 커밋 후 정확히-최소 1회 보장.
- 유실 의심/백필 필요: 일시적 신규 그룹명 사용으로 과거부터 재소비 → 검증 완료 후 기존 그룹으로 복귀.
- 강제 초기화가 필요한 경우(runbook):
  1) 대상 그룹/토픽 확인(kafka-consumer-groups.sh --bootstrap-server ... --describe)
  2) 점검 시간 확보 및 다운스트림 영향 공지
  3) 소비자 정지 → 오프셋 리셋(--reset-offsets --to-earliest --group <name> --topic <t>)
  4) 소비자 기동 및 backlog 처리 모니터링(Grafana lag 패널)

## 4) 모니터링과 알림
- Exporter: danielqsj/kafka-exporter, 9308 포트. Prometheus 스크레이프 job: kafka-exporter
- Grafana: "Kafka Consumer Lag (by group/topic)" 패널(sum(kafka_consumergroup_lag) by consumergroup,topic)
- Alerts:
  - KafkaHighConsumerLag: sum by(consumergroup) > 임계(예: 1000) 5m 지속 시 경보
  - KafkaExporterDown: exporter up==0 2m 지속 시 경보

## 5) 환경 변수 표준(.env.*)
- KAFKA_ENABLED=0|1
- KAFKA_BOOTSTRAP_SERVERS=kafka:9092
- KAFKA_CONSUMER_GROUP=cc_app_<env>
- KAFKA_TOPICS=cc_user_actions,cc_rewards,buy_package
- ALERT_PENDING_SPIKE_THRESHOLD=20..30 (환경별 상이)

## 6) 체크리스트(운영)
- [ ] 신규 배포 전 exporter/스크레이프/대시보드/알림 로드 확인
- [ ] 신규 토픽 추가 시 .env.*와 대시보드 패널 업데이트
- [ ] backlog 증가 시 처리량/워커 스케일과 파티션 수 점검 → 필요 시 파티션 및 워커 확장
- [ ] 오프셋 리셋은 변경 이력과 근거를 남기고, 재소비 기간 동안 알림 임계 임시 상향 고려

부록
- compose: docker-compose.monitoring.yml
- rules: cc-webapp/monitoring/kafka_alerts.yml
- 대시보드: cc-webapp/monitoring/grafana_dashboard.json
