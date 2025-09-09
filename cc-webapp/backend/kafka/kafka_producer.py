"""
Kafka Producer 샘플 (user_actions, user_rewards)
- 메시지 발행, 예외/재시도 처리
"""
from .kafka_config import get_kafka_producer
import json
import time

def send_message(topic, message: dict):
    producer = get_kafka_producer()
    try:
        producer.send(topic, json.dumps(message))
        producer.flush()
        print(f"[Kafka] 메시지 발행: {topic} {message}")
    except Exception as e:
        print(f"[Kafka] 메시지 발행 실패: {e}")
        # 재시도 로직 (간단 예시)
        time.sleep(1)
        try:
            producer.send(topic, json.dumps(message))
            producer.flush()
            print(f"[Kafka] 재시도 성공: {topic} {message}")
        except Exception as e2:
            print(f"[Kafka] 재시도 실패: {e2}")
    finally:
        producer.close()

if __name__ == "__main__":
    send_message("user_actions", {"user_id": 1, "action": "SLOT_SPIN", "ts": time.time()})
