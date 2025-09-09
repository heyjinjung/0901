"""
Kafka 메시징 시스템 API
Casino-Club F2P 백엔드 Kafka 통합
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
import json
import asyncio
from datetime import datetime

from ...core.logging import get_logger, log_service_call
from ...core.error_handlers import CasinoClubException

# Kafka 라우터 생성
router = APIRouter(prefix="/kafka", tags=["kafka", "messaging"])

# 로거 초기화
logger = get_logger("kafka")

# Kafka 클라이언트 모의 구현 (실제 환경에서는 kafka-python 사용)
class MockKafkaProducer:
    """Kafka Producer 모의 구현"""
    
    def __init__(self):
        self.sent_messages = []
        self.is_connected = False
    
    async def connect(self):
        """Kafka 연결"""
        self.is_connected = True
        logger.info("Kafka producer connected (mock)")
    
    async def disconnect(self):
        """Kafka 연결 해제"""
        self.is_connected = False
        logger.info("Kafka producer disconnected (mock)")
    
    async def send_message(self, topic: str, message: Dict[str, Any]):
        """메시지 전송"""
        if not self.is_connected:
            raise CasinoClubException("Kafka가 연결되지 않았습니다.", "KAFKA_NOT_CONNECTED")
        
        message_data = {
            "topic": topic,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "partition": 0,
            "offset": len(self.sent_messages)
        }
        
        self.sent_messages.append(message_data)
        logger.info(f"Message sent to topic {topic}: {json.dumps(message, default=str)[:100]}...")
        
        return message_data


class MockKafkaConsumer:
    """Kafka Consumer 모의 구현"""
    
    def __init__(self, topics: List[str]):
        self.topics = topics
        self.consumed_messages = []
        self.is_connected = False
    
    async def connect(self):
        """Kafka 연결"""
        self.is_connected = True
        logger.info(f"Kafka consumer connected to topics: {self.topics} (mock)")
    
    async def disconnect(self):
        """Kafka 연결 해제"""
        self.is_connected = False
        logger.info("Kafka consumer disconnected (mock)")
    
    async def consume_messages(self, max_messages: int = 10):
        """메시지 소비"""
        if not self.is_connected:
            raise CasinoClubException("Kafka가 연결되지 않았습니다.", "KAFKA_NOT_CONNECTED")
        
        # 모의 메시지 생성
        messages = []
        for i in range(min(max_messages, 3)):  # 최대 3개 모의 메시지
            message = {
                "topic": self.topics[0] if self.topics else "default",
                "partition": 0,
                "offset": i,
                "timestamp": datetime.utcnow().isoformat(),
                "key": f"test_key_{i}",
                "value": {
                    "event_type": "user_action",
                    "user_id": 1000 + i,
                    "action": "GACHA_PULL",
                    "data": {"count": 1, "result": "Common"}
                }
            }
            messages.append(message)
            self.consumed_messages.append(message)
        
        logger.info(f"Consumed {len(messages)} messages from topics: {self.topics}")
        return messages


# Kafka 인스턴스 (싱글톤)
kafka_producer = MockKafkaProducer()
kafka_consumer = MockKafkaConsumer(["user_actions", "game_events", "rewards"])


# 의존성 함수
async def get_kafka_producer():
    """Kafka Producer 의존성"""
    if not kafka_producer.is_connected:
        await kafka_producer.connect()
    return kafka_producer


async def get_kafka_consumer():
    """Kafka Consumer 의존성"""
    if not kafka_consumer.is_connected:
        await kafka_consumer.connect()
    return kafka_consumer


# API 엔드포인트
@router.post("/send")
async def send_message(
    topic: str,
    message: Dict[str, Any],
    producer: MockKafkaProducer = Depends(get_kafka_producer)
):
    """
    Kafka 토픽으로 메시지 전송
    
    Args:
        topic: 대상 토픽 이름
        message: 전송할 메시지 데이터
    """
    log_service_call("kafka", "send_message", topic=topic)
    
    try:
        result = await producer.send_message(topic, message)
        return {
            "success": True,
            "message": "메시지가 성공적으로 전송되었습니다.",
            "data": result
        }
    except Exception as e:
        logger.error(f"Failed to send message to topic {topic}: {str(e)}")
        raise HTTPException(status_code=500, detail="메시지 전송 실패")


@router.get("/consume/{topic}")
async def consume_messages(
    topic: str,
    max_messages: int = 10,
    consumer: MockKafkaConsumer = Depends(get_kafka_consumer)
):
    """
    Kafka 토픽에서 메시지 소비
    
    Args:
        topic: 소비할 토픽 이름
        max_messages: 최대 메시지 수
    """
    log_service_call("kafka", "consume_messages", topic=topic, max_messages=max_messages)
    
    try:
        # 토픽이 consumer의 구독 목록에 있는지 확인
        if topic not in consumer.topics:
            consumer.topics.append(topic)
        
        messages = await consumer.consume_messages(max_messages)
        return {
            "success": True,
            "topic": topic,
            "message_count": len(messages),
            "messages": messages
        }
    except Exception as e:
        logger.error(f"Failed to consume messages from topic {topic}: {str(e)}")
        raise HTTPException(status_code=500, detail="메시지 소비 실패")


@router.get("/status")
async def kafka_status():
    """
    Kafka 연결 상태 확인
    """
    log_service_call("kafka", "status")
    
    return {
        "success": True,
        "producer_connected": kafka_producer.is_connected,
        "consumer_connected": kafka_consumer.is_connected,
        "subscribed_topics": kafka_consumer.topics,
        "sent_messages_count": len(kafka_producer.sent_messages),
        "consumed_messages_count": len(kafka_consumer.consumed_messages)
    }


@router.post("/user-action")
async def send_user_action(
    user_id: int,
    action: str,
    data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    producer: MockKafkaProducer = Depends(get_kafka_producer)
):
    """
    사용자 액션 이벤트 전송
    
    Args:
        user_id: 사용자 ID
        action: 액션 타입 (GACHA_PULL, SLOT_SPIN, etc.)
        data: 액션 데이터
    """
    log_service_call("kafka", "send_user_action", user_id=user_id, action=action)
    
    message = {
        "event_type": "user_action",
        "user_id": user_id,
        "action": action,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # 백그라운드에서 메시지 전송
    background_tasks.add_task(producer.send_message, "user_actions", message)
    
    return {
        "success": True,
        "message": "사용자 액션 이벤트가 전송되었습니다.",
        "event": {
            "user_id": user_id,
            "action": action,
            "timestamp": message["timestamp"]
        }
    }


@router.post("/game-event")
async def send_game_event(
    game_type: str,
    event_type: str,
    data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    producer: MockKafkaProducer = Depends(get_kafka_producer)
):
    """
    게임 이벤트 전송
    
    Args:
        game_type: 게임 타입 (gacha, slot, roulette, etc.)
        event_type: 이벤트 타입 (start, end, win, lose, etc.)
        data: 이벤트 데이터
    """
    log_service_call("kafka", "send_game_event", game_type=game_type, event_type=event_type)
    
    message = {
        "event_type": "game_event",
        "game_type": game_type,
        "event": event_type,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # 백그라운드에서 메시지 전송
    background_tasks.add_task(producer.send_message, "game_events", message)
    
    return {
        "success": True,
        "message": "게임 이벤트가 전송되었습니다.",
        "event": {
            "game_type": game_type,
            "event_type": event_type,
            "timestamp": message["timestamp"]
        }
    }


@router.post("/reward-event")
async def send_reward_event(
    user_id: int,
    reward_type: str,
    amount: float,
    background_tasks: BackgroundTasks,
    producer: MockKafkaProducer = Depends(get_kafka_producer),
    data: Optional[Dict[str, Any]] = None
):
    """
    리워드 이벤트 전송
    
    Args:
        user_id: 사용자 ID
        reward_type: 리워드 타입 (tokens, gems, items, etc.)
        amount: 리워드 수량
        data: 추가 데이터
    """
    log_service_call("kafka", "send_reward_event", user_id=user_id, reward_type=reward_type, amount=amount)
    
    message = {
        "event_type": "reward_event",
        "user_id": user_id,
        "reward_type": reward_type,
        "amount": amount,
        "data": data or {},
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # 백그라운드에서 메시지 전송
    background_tasks.add_task(producer.send_message, "rewards", message)
    
    return {
        "success": True,
        "message": "리워드 이벤트가 전송되었습니다.",
        "event": {
            "user_id": user_id,
            "reward_type": reward_type,
            "amount": amount,
            "timestamp": message["timestamp"]
        }
    }


@router.get("/messages/sent")
async def get_sent_messages(limit: int = 50):
    """
    전송된 메시지 목록 조회 (디버깅용)
    """
    log_service_call("kafka", "get_sent_messages", limit=limit)
    
    messages = kafka_producer.sent_messages[-limit:] if kafka_producer.sent_messages else []
    
    return {
        "success": True,
        "total_sent": len(kafka_producer.sent_messages),
        "returned_count": len(messages),
        "messages": messages
    }


@router.get("/messages/consumed")
async def get_consumed_messages(limit: int = 50):
    """
    소비된 메시지 목록 조회 (디버깅용)
    """
    log_service_call("kafka", "get_consumed_messages", limit=limit)
    
    messages = kafka_consumer.consumed_messages[-limit:] if kafka_consumer.consumed_messages else []
    
    return {
        "success": True,
        "total_consumed": len(kafka_consumer.consumed_messages),
        "returned_count": len(messages),
        "messages": messages
    }


@router.delete("/messages/clear")
async def clear_message_history():
    """
    메시지 히스토리 초기화 (테스트용)
    """
    log_service_call("kafka", "clear_message_history")
    
    sent_count = len(kafka_producer.sent_messages)
    consumed_count = len(kafka_consumer.consumed_messages)
    
    kafka_producer.sent_messages.clear()
    kafka_consumer.consumed_messages.clear()
    
    return {
        "success": True,
        "message": "메시지 히스토리가 초기화되었습니다.",
        "cleared": {
            "sent_messages": sent_count,
            "consumed_messages": consumed_count
        }
    }


# 시작/종료 이벤트 핸들러
@router.on_event("startup")
async def startup_kafka():
    """Kafka 서비스 시작"""
    try:
        await kafka_producer.connect()
        await kafka_consumer.connect()
        logger.info("Kafka services started successfully (mock)")
    except Exception as e:
        logger.error(f"Failed to start Kafka services: {str(e)}")


@router.on_event("shutdown")
async def shutdown_kafka():
    """Kafka 서비스 종료"""
    try:
        await kafka_producer.disconnect()
        await kafka_consumer.disconnect()
        logger.info("Kafka services stopped successfully (mock)")
    except Exception as e:
        logger.error(f"Failed to stop Kafka services: {str(e)}")
