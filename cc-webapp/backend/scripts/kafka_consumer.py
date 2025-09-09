import os
import json
from confluent_kafka import Consumer, KafkaException, KafkaError

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
TOPIC_USER_ACTIONS = "topic_user_actions"
GROUP_ID = "user_actions_consumer_group" # Example group ID

conf = {
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': GROUP_ID,
    'auto.offset.reset': 'earliest' # Start reading at the earliest message if no offset is stored
}

consumer = Consumer(conf)

try:
    consumer.subscribe([TOPIC_USER_ACTIONS])
    print(f"Subscribed to topic: {TOPIC_USER_ACTIONS} with group ID: {GROUP_ID}")
    print(f"Broker: {KAFKA_BROKER}")
    print("Waiting for messages... (Ctrl+C to exit)")

    while True:
        msg = consumer.poll(timeout=1.0) # Poll for messages with a 1-second timeout

        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition event
                print(f'{msg.topic()} [{msg.partition()}] reached end at offset {msg.offset()}')
            elif msg.error():
                print(f"Kafka error: {msg.error()}") # More direct error printing
                # raise KafkaException(msg.error()) # Raising might stop the consumer prematurely for some errors
            else:
                print(f"Unknown Kafka error: {msg.error()}")
        else:
            # Message is normal
            try:
                payload = json.loads(msg.value().decode('utf-8'))
                print(f"Received message from {msg.topic()} [{msg.partition()}] at offset {msg.offset()}:")
                print(json.dumps(payload, indent=2))
            except json.JSONDecodeError:
                print(f"Error decoding JSON: {msg.value().decode('utf-8')}")
            except Exception as e:
                print(f"An error occurred while processing message: {e}")
except KeyboardInterrupt:
    print("Aborted by user")
except KafkaException as ke:
    print(f"A KafkaException occurred: {ke}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    # Close down consumer to commit final offsets.
    consumer.close()
    print("Consumer closed.")
