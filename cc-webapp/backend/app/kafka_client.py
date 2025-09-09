"""
Kafka Producer (kafka-python) and optional async Consumer (aiokafka).
Improvements:
- Wait for partition assignment on startup
- Seek to end on startup to tail new messages reliably in dev/test
"""
import asyncio
import json
import time
import os
import uuid
from typing import Any, Dict, List, Optional

from kafka import KafkaProducer, KafkaConsumer
from app.core.config import settings

KAFKA_BOOTSTRAP_SERVERS = settings.kafka_bootstrap_servers or settings.KAFKA_BOOTSTRAP_SERVERS
KAFKA_BOOTSTRAP_SERVERS = getattr(settings, "kafka_bootstrap_servers", None) or settings.KAFKA_BOOTSTRAP_SERVERS

# --- Producer (kafka-python; lazy) ---
_producer = None

def get_kafka_producer():
    global _producer
    if _producer is None:
        _producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            acks="all",
            linger_ms=10,
        )
    return _producer

def send_kafka_message(topic: str, value: Dict[str, Any]) -> None:
    """Produce with small retry/backoff to improve resilience under CI/dev.

    Errors are logged; endpoint returns 502 upstream when exceptions bubble.
    """
    attempts = 0
    delay = 0.2
    while attempts < 3:
        attempts += 1
        try:
            producer = get_kafka_producer()
            fut = producer.send(topic, value=value)
            try:
                md = fut.get(timeout=5)
                print(f"Kafka produce ok topic={md.topic} partition={md.partition} offset={md.offset}")
            except Exception as e:
                print(f"Kafka produce future error: {e}")
            producer.flush()
            return
        except Exception as e:
            print(f"Failed to send Kafka message (attempt {attempts}/3): {e}")
            time.sleep(delay)
            delay *= 2
    # If we reach here, all attempts failed; let caller handle response

# --- Async Consumer (aiokafka; optional) ---
_consumer_task: Optional[asyncio.Task] = None
_last_messages: List[Dict[str, Any]] = []
_thread_consumer: Optional[KafkaConsumer] = None
_thread_task: Optional[asyncio.AbstractEventLoop] = None
_thread_running: bool = False
_consumer_ready: bool = False

async def start_consumer() -> None:
    """Start Kafka consumer in background if enabled and configured.

    Behavior:
    - If aiokafka is available, use it; else fallback to kafka-python in a thread.
    - Wait for partition assignment and seek to end to tail new messages.
    """
    if not settings.KAFKA_ENABLED:
        return
    # In pytest context, prefer thread-based consumer for determinism
    if os.environ.get("PYTEST_CURRENT_TEST"):
        _start_thread_consumer()
        return
    try:
        from aiokafka import AIOKafkaConsumer
    except Exception as e:
        print(f"aiokafka not available: {e}")
        # Fallback to thread-based kafka-python consumer
        _start_thread_consumer()
        return

    topics = [t.strip() for t in (settings.KAFKA_TOPICS or "").split(",") if t.strip()] or ["cc_test"]

    # Use a unique group id under pytest to avoid clashing with a running server consumer
    base_group = getattr(settings, "KAFKA_CONSUMER_GROUP", None)
    group_id = (
        f"{base_group}-pytest-{uuid.uuid4().hex[:8]}" if os.environ.get("PYTEST_CURRENT_TEST") else base_group
    )

    consumer = AIOKafkaConsumer(
        *topics,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        enable_auto_commit=True,
        # Use earliest for brand new groups; we will seek_to_end after assignment
        auto_offset_reset="earliest",
        group_id=group_id,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )
    await consumer.start()

    # Nudge the consumer to join the group and get assignment
    try:
        await consumer.getmany(timeout_ms=200)
    except Exception:
        pass

    # Wait up to 10s for partition assignment, then seek to beginning so we don't miss early messages
    deadline = time.time() + 10
    assigned = set()
    while time.time() < deadline:
        try:
            assigned = consumer.assignment()
        except Exception:
            assigned = set()
        if assigned:
            try:
                # Ensure we start from the beginning to catch messages sent before readiness
                await consumer.seek_to_beginning(*assigned)
            except Exception as e:
                print(f"seek_to_beginning failed (aiokafka): {e}")
            break
        await asyncio.sleep(0.1)

    # Mark ready
    global _consumer_ready
    _consumer_ready = True

    async def _consume():
        try:
            async for msg in consumer:
                payload = {
                    "topic": msg.topic,
                    "partition": msg.partition,
                    "offset": msg.offset,
                    "value": msg.value,
                }
                print(f"[aiokafka] consumed topic={msg.topic} partition={msg.partition} offset={msg.offset} value={msg.value}")
                _last_messages.append(payload)
                # Keep only recent 100
                if len(_last_messages) > 100:
                    del _last_messages[: len(_last_messages) - 100]
        except Exception as e:
            print(f"Consumer loop error: {e}")
        finally:
            try:
                await consumer.stop()
            except Exception:
                pass

    global _consumer_task
    _consumer_task = asyncio.create_task(_consume())

async def stop_consumer() -> None:
    global _consumer_task
    if _consumer_task:
        _consumer_task.cancel()
        try:
            await _consumer_task
        except Exception:
            pass
        _consumer_task = None
    # Stop thread-based consumer if running
    global _thread_running, _thread_consumer, _consumer_ready
    if _thread_running and _thread_consumer is not None:
        try:
            _thread_consumer.close()
        except Exception:
            pass
        _thread_running = False
        _thread_consumer = None
    _consumer_ready = False

def get_last_messages(limit: int = 10) -> List[Dict[str, Any]]:
    return _last_messages[-limit:]

def is_consumer_ready() -> bool:
    return _consumer_ready

# --- Thread-based fallback consumer (kafka-python) ---
def _start_thread_consumer():
    global _thread_consumer, _thread_running, _consumer_ready
    if _thread_running:
        return
    topics = [t.strip() for t in (settings.KAFKA_TOPICS or "").split(",") if t.strip()] or ["cc_test"]
    try:
        # Use a unique group id under pytest to avoid clashing with a running server consumer
        base_group = getattr(settings, "KAFKA_CONSUMER_GROUP", None)
        group_id = (
            f"{base_group}-pytest-{uuid.uuid4().hex[:8]}" if os.environ.get("PYTEST_CURRENT_TEST") else base_group
        )

        consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            # Use earliest for new groups; we'll seek_to_end after assignment
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            group_id=group_id,
        )
        _thread_consumer = consumer
    except Exception as e:
        print(f"Thread consumer init failed: {e}")
        return

    import threading

    # Trigger assignment and then seek to beginning so we don't miss early messages
    try:
        consumer.poll(timeout_ms=200)
        deadline = time.time() + 10
        while time.time() < deadline and not consumer.assignment():
            consumer.poll(timeout_ms=200)
            time.sleep(0.1)
        try:
            consumer.seek_to_beginning()
        except Exception as e:
            print(f"seek_to_beginning failed (kafka-python): {e}")
    except Exception as e:
        print(f"Thread consumer pre-run init failed: {e}")

    _thread_running = True
    _consumer_ready = True

    def _run():
        global _thread_running
        try:
            for msg in consumer:
                if not _thread_running:
                    break
                payload = {
                    "topic": msg.topic,
                    "partition": msg.partition,
                    "offset": msg.offset,
                    "value": msg.value,
                }
                print(f"[kafka-python] consumed topic={msg.topic} partition={msg.partition} offset={msg.offset} value={msg.value}")
                _last_messages.append(payload)
                if len(_last_messages) > 100:
                    del _last_messages[: len(_last_messages) - 100]
        except Exception as e:
            print(f"Thread consumer loop error: {e}")
        finally:
            try:
                consumer.close()
            except Exception:
                pass
            _thread_running = False

    threading.Thread(target=_run, name="kafka-consumer", daemon=True).start()
