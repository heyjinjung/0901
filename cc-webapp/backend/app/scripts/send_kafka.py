import os
import uuid
from app.kafka_client import send_kafka_message
from app.core.config import settings


topic = os.getenv("KAFKA_TEST_TOPIC", "cc_test")
marker = os.getenv("MARKER", str(uuid.uuid4()))

print(f"Producing to {settings.KAFKA_BOOTSTRAP_SERVERS} topic={topic} marker={marker}")
send_kafka_message(topic, {"marker": marker, "src": "helper"})
print("Done.")
