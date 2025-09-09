"""
Kafka 토픽 정의 및 생성 유틸
- 주요 토픽: user_actions, user_rewards 등
- 토픽 존재 여부 확인 및 생성
"""
from kafka.admin import KafkaAdminClient, NewTopic
import os
from dotenv import load_dotenv

load_dotenv()

KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "localhost:9093")
KAFKA_CLIENT_ID = os.getenv("KAFKA_CLIENT_ID", "cc-backend")

TOPICS = [
    "user_actions",
    "user_rewards"
]

def create_topics():
    admin_client = KafkaAdminClient(
        bootstrap_servers=KAFKA_BROKER_URL,
        client_id=KAFKA_CLIENT_ID
    )
    topic_list = [NewTopic(name=topic, num_partitions=1, replication_factor=1) for topic in TOPICS]
    try:
        admin_client.create_topics(new_topics=topic_list, validate_only=False)
        print(f"[Kafka] 토픽 생성 완료: {TOPICS}")
    except Exception as e:
        print(f"[Kafka] 토픽 생성 오류(이미 존재할 수 있음): {e}")
    finally:
        admin_client.close()

if __name__ == "__main__":
    create_topics()
