"""
Kafka 연결 및 환경별 설정 모듈
- dev/prod 환경 분리 (.env 연동)
- 예외 처리 및 로깅 포함
"""
import os
from kafka import KafkaProducer, KafkaConsumer
from dotenv import load_dotenv

load_dotenv()

KAFKA_BROKER_URL = os.getenv("KAFKA_BROKER_URL", "localhost:9093")
KAFKA_CLIENT_ID = os.getenv("KAFKA_CLIENT_ID", "cc-backend")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "cc-group")


def get_kafka_producer():
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER_URL,
            client_id=KAFKA_CLIENT_ID,
            value_serializer=lambda v: v.encode('utf-8'),
            retries=3
        )
        return producer
    except Exception as e:
        print(f"[Kafka] Producer 연결 실패: {e}")
        raise

def get_kafka_consumer(topic):
    try:
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=KAFKA_BROKER_URL,
            group_id=KAFKA_GROUP_ID,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            value_deserializer=lambda v: v.decode('utf-8'),
        )
        return consumer
    except Exception as e:
        print(f"[Kafka] Consumer 연결 실패: {e}")
        raise
