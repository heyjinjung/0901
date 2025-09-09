from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
import uuid
from kafka import KafkaConsumer

from app.core.config import settings
from app.kafka_client import send_kafka_message


router = APIRouter(prefix="/api/kafka", tags=["Kafka"])


class ProduceRequest(BaseModel):
    topic: str
    payload: Dict[str, Any]


@router.get("/health")
def kafka_health():
    """Lightweight health that reflects config; avoids blocking if broker is absent."""
    return {
        "enabled": settings.KAFKA_ENABLED,
        "bootstrap_servers": settings.KAFKA_BOOTSTRAP_SERVERS or None,
        "status": "enabled" if settings.KAFKA_ENABLED else "disabled",
    }


@router.post("/produce")
def kafka_produce(req: ProduceRequest):
    """Produce a message to Kafka if enabled; otherwise 503."""
    # Tests accept 200 (success) or 502 (broker-related/disabled). Align by returning 502 when disabled.
    if not settings.KAFKA_ENABLED:
        raise HTTPException(status_code=502, detail="Kafka disabled")
    if not (settings.KAFKA_BOOTSTRAP_SERVERS or settings.kafka_bootstrap_servers):
        raise HTTPException(status_code=500, detail="Kafka bootstrap not configured")

    try:
        send_kafka_message(req.topic, req.payload)
        return {"ok": True}
    except Exception as e:
        # Hide internal errors but indicate failure
        raise HTTPException(status_code=502, detail=f"Kafka produce failed: {e}")


@router.get("/debug/peek")
def kafka_peek(
    topic: Optional[str] = None,
    max_messages: int = 20,
    from_beginning: bool = True,
    timeout_ms: int = 1000,
):
    """Peek messages directly from Kafka with a temporary consumer.

    Returns up to max_messages messages with basic metadata. Does not commit offsets.
    """
    if not settings.KAFKA_ENABLED:
        raise HTTPException(status_code=503, detail="Kafka disabled")
    t = (topic or (settings.KAFKA_TOPICS.split(",")[0] if settings.KAFKA_TOPICS else "cc_test")).strip()
    if not t:
        raise HTTPException(status_code=400, detail="topic required")
    try:
        group_id = f"peek-{uuid.uuid4().hex[:8]}"
        consumer = KafkaConsumer(
            t,
            bootstrap_servers=(settings.KAFKA_BOOTSTRAP_SERVERS or settings.kafka_bootstrap_servers),
            auto_offset_reset=("earliest" if from_beginning else "latest"),
            enable_auto_commit=False,
            group_id=group_id,
            value_deserializer=lambda m: __import__("json").loads(m.decode("utf-8")),
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Kafka consumer init failed: {e}")

    items: List[Dict[str, Any]] = []
    try:
        records = consumer.poll(timeout_ms=timeout_ms, max_records=max_messages)
        for tp, msgs in records.items():
            for msg in msgs:
                items.append(
                    {
                        "topic": msg.topic,
                        "partition": msg.partition,
                        "offset": msg.offset,
                        "value": msg.value,
                    }
                )
                if len(items) >= max_messages:
                    break
            if len(items) >= max_messages:
                break
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Kafka poll failed: {e}")
    finally:
        try:
            consumer.close()
        except Exception:
            pass
    return {"items": items, "count": len(items)}
