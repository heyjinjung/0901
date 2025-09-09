# Kafka 연동 자동화 테스트/샘플 가이드

## 목적
- 운영/테스트(dev/prod) 환경 분리된 Kafka 연동 자동화 테스트 및 샘플 코드 제공
- 주요 체크리스트(연결, 토픽, Producer, Consumer, 오류 처리 등)별 예제 및 실행법 안내

## 파일 구조
```
kafka/
  kafka_config.py      # Kafka 연결/설정 (dev/prod .env 연동)
  kafka_topics.py      # 토픽 정의/생성 유틸
  kafka_producer.py    # Producer 샘플 (user_actions, user_rewards)
  kafka_consumer.py    # Consumer 샘플 (user_actions, user_rewards)
  README_KAFKA.md      # 본 가이드
```
tests/
  test_kafka_integration.py  # pytest 기반 Kafka 통합 자동화 테스트
```

## 환경 변수 예시(.env)
```
KAFKA_BROKER_URL=cc_kafka:9093
KAFKA_CLIENT_ID=cc-backend
KAFKA_GROUP_ID=cc-group
```

## 실행 방법
1. 토픽 생성: 
   ```bash
   python -m kafka.kafka_topics
   ```
2. Producer 메시지 발행:
   ```bash
   python -m kafka.kafka_producer
   ```
3. Consumer 메시지 수신:
   ```bash
   python -m kafka.kafka_consumer
   ```
4. 자동화 테스트:
   ```bash
   pytest tests/test_kafka_integration.py
   ```

## 예외/오류 처리 시나리오
- 브로커 연결 실패, 토픽 미존재, 메시지 발행/수신 오류, 재시도 로직 등 샘플 코드 참고

## 운영/테스트 환경 분리
- .env.dev, .env.prod 파일로 브로커/그룹/클라이언트 ID 등 분리 관리
- docker-compose.dev.yml, docker-compose.yml 참고

## 참고
- kafka-python, pytest, python-dotenv 필요
- 상세 체크리스트 및 단계별 진행상황은 20250729-가이드006.md 참고
