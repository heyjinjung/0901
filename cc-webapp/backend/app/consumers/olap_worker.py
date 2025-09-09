import json, time, logging
from typing import Dict, List
from kafka import KafkaConsumer
from app.core.config import settings
from app.olap.clickhouse_client import ClickHouseClient
from app.kafka_client import send_kafka_message

log = logging.getLogger("olap_worker")
# Ensure visible logs when launched as module
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log.setLevel(logging.INFO)

def _parse(msg) -> Dict:
    try:
        return json.loads(msg.value.decode("utf-8"))
    except Exception:
        return {}

def run():
    if not (settings.KAFKA_ENABLED and settings.CLICKHOUSE_ENABLED):
        log.warning("OLAP worker disabled (KAFKA=%s, CH=%s)", settings.KAFKA_ENABLED, settings.CLICKHOUSE_ENABLED)
        return

    client = ClickHouseClient()
    client.init_schema()

    topics = [
        settings.KAFKA_ACTIONS_TOPIC,
        settings.KAFKA_REWARDS_TOPIC,
        getattr(settings, "KAFKA_PURCHASES_TOPIC", "buy_package"),
    ]
    consumer = KafkaConsumer(
        *topics,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS.split(","),
        group_id="cc_olap_worker",
        enable_auto_commit=False,
        # Consume from beginning when no committed offsets exist (useful for dev/smoke)
        auto_offset_reset="earliest",
        consumer_timeout_ms=1000,
        max_poll_records=1000,
        value_deserializer=lambda v: v,
    )
    log.warning("OLAP worker started, topics=%s, bootstrap=%s", topics, settings.KAFKA_BOOTSTRAP_SERVERS)

    buf_actions: List[Dict] = []
    buf_rewards: List[Dict] = []
    buf_purchases: List[Dict] = []
    last_flush = time.time()

    def flush():
        nonlocal buf_actions, buf_rewards, buf_purchases, last_flush
        try:
            if buf_actions:
                client.insert_actions(buf_actions)
                log.info("flushed actions=%d", len(buf_actions))
                buf_actions = []
            if buf_rewards:
                client.insert_rewards(buf_rewards)
                log.info("flushed rewards=%d", len(buf_rewards))
                buf_rewards = []
            if buf_purchases:
                client.insert_purchases(buf_purchases)
                log.info("flushed purchases=%d", len(buf_purchases))
                buf_purchases = []
        except Exception as e:
            # On failure, publish failed buffers to DLQ topic with reason
            try:
                if buf_actions:
                    send_kafka_message(settings.KAFKA_DLQ_TOPIC, {"stream":"user_actions","reason": str(e), "records": buf_actions[:100]})
                if buf_rewards:
                    send_kafka_message(settings.KAFKA_DLQ_TOPIC, {"stream":"rewards","reason": str(e), "records": buf_rewards[:100]})
                if buf_purchases:
                    send_kafka_message(settings.KAFKA_DLQ_TOPIC, {"stream":"purchases","reason": str(e), "records": buf_purchases[:100]})
            except Exception:
                pass
            finally:
                # Drop buffers to avoid stuck loop; continue consumption
                buf_actions = []
                buf_rewards = []
                buf_purchases = []
        finally:
            last_flush = time.time()

    try:
        while True:
            polled = consumer.poll(timeout_ms=500, max_records=500)
            for records in polled.values():
                for m in records:
                    payload = _parse(m)
                    if not payload:
                        continue
                    if m.topic == settings.KAFKA_ACTIONS_TOPIC:
                        buf_actions.append({
                            "user_id": payload.get("user_id"),
                            "action_type": payload.get("action_type"),
                            "client_ts": payload.get("client_ts"),
                            "server_ts": payload.get("server_ts"),
                            "context_json": json.dumps(payload.get("context") or {}),
                        })
                    elif m.topic == settings.KAFKA_REWARDS_TOPIC:
                        buf_rewards.append({
                            "user_id": payload.get("user_id"),
                            "reward_type": payload.get("reward_type"),
                            "reward_value": payload.get("reward_value"),
                            "source": payload.get("source"),
                            "awarded_at": payload.get("awarded_at"),
                        })
                    elif m.topic == getattr(settings, "KAFKA_PURCHASES_TOPIC", "buy_package"):
                        buf_purchases.append({
                            "user_id": payload.get("user_id"),
                            "code": payload.get("code"),
                            "quantity": payload.get("quantity"),
                            "total_price_cents": payload.get("total_price_cents"),
                            "gems_granted": payload.get("gems_granted"),
                            "charge_id": payload.get("charge_id"),
                            "purchased_at": payload.get("server_ts"),
                        })
            if (
                len(buf_actions) + len(buf_rewards) + len(buf_purchases) >= settings.OLAP_BATCH_SIZE
            ) or (time.time() - last_flush >= settings.OLAP_FLUSH_SECONDS):
                flush()
                consumer.commit()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        log.exception("OLAP worker crashed: %s", e)
    finally:
        try:
            flush()
            consumer.commit()
        except Exception:
            pass
        consumer.close()

if __name__ == "__main__":
    run()