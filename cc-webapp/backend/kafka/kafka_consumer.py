"""
Kafka Consumer 샘플 (user_actions, user_rewards)
- 메시지 수신, 예외/재시도 처리
"""
from .kafka_config import get_kafka_consumer
import time

def consume_messages(topic):
    consumer = get_kafka_consumer(topic)
    try:
        for msg in consumer:
            print(f"[Kafka] 메시지 수신: {msg.topic} {msg.value}")
    except Exception as e:
        print(f"[Kafka] Consumer 오류: {e}")
        time.sleep(1)
        # 재시도 로직 (간단 예시)
        consume_messages(topic)
    finally:
        consumer.close()

if __name__ == "__main__":
    consume_messages("user_actions")
