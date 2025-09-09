"""
공통 테스트 픽스처 - MCP 최적화
재사용 가능한 픽스처들을 제공하여 테스트 중복 제거
"""

import pytest
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any, List


# 사용자 관련 픽스처
@pytest.fixture
def mock_user():
    """기본 Mock 사용자"""
    return {
        "user_id": 1,
        "nickname": "testuser",
        "email": "testuser@example.com",
        "gems": 1000,
        "coins": 5000,
        "level": 1,
        "exp": 0,
        "created_at": "2024-01-01T00:00:00Z",
        "last_login": "2024-01-01T12:00:00Z"
    }


@pytest.fixture
def mock_users():
    """여러 Mock 사용자들"""
    return [
        {
            "user_id": i,
            "nickname": f"user{i:03d}",
            "email": f"user{i:03d}@example.com",
            "gems": 1000 + i * 100,
            "coins": 5000 + i * 500,
            "level": (i // 10) + 1,
            "exp": i * 50
        }
        for i in range(1, 11)
    ]


# 감정 분석 관련 픽스처
@pytest.fixture
def mock_emotion_analyzer():
    """Mock 감정 분석기"""
    analyzer = Mock()
    analyzer.analyze.return_value = Mock(
        emotion="neutral",
        confidence=0.7,
        language="english"
    )
    return analyzer


@pytest.fixture
def mock_sentiment_analyzer():
    """Mock 감정 분석 서비스"""
    analyzer = AsyncMock()
    analyzer.analyze_text.return_value = {
        "emotion": "neutral",
        "confidence": 0.7,
        "language": "english",
        "timestamp": "2024-01-01T00:00:00Z"
    }
    return analyzer


@pytest.fixture
def sample_emotion_data():
    """샘플 감정 데이터"""
    return {
        "text": "I'm feeling great today!",
        "expected_emotion": "happy",
        "expected_confidence": 0.8,
        "expected_language": "english"
    }


@pytest.fixture
def emotion_test_cases():
    """감정 분석 테스트 케이스들"""
    return [
        {
            "text": "I love this game!",
            "emotion": "happy",
            "confidence": 0.9,
            "language": "english"
        },
        {
            "text": "This is so frustrating!",
            "emotion": "angry",
            "confidence": 0.8,
            "language": "english"
        },
        {
            "text": "정말 좋아요!",
            "emotion": "happy",
            "confidence": 0.85,
            "language": "korean"
        },
        {
            "text": "화나네요...",
            "emotion": "angry",
            "confidence": 0.75,
            "language": "korean"
        },
        {
            "text": "It's okay I guess",
            "emotion": "neutral",
            "confidence": 0.6,
            "language": "english"
        }
    ]


# 가차 서비스 관련 픽스처
@pytest.fixture
def mock_gacha_service():
    """Mock 가차 서비스"""
    service = Mock()
    service.pull.return_value = {
        "item_id": "test_item_001",
        "item_name": "Test Sword",
        "rarity": "common",
        "user_id": 1,
        "quantity": 1,
        "obtained_at": "2024-01-01T00:00:00Z"
    }
    return service


@pytest.fixture
def sample_slot_data():
    """샘플 슬롯 데이터"""
    return {
        "result": "WIN",
        "reward": 100,
        "symbols": ["🍒", "🍒", "🍒"],
        "multiplier": 2.0,
        "user_id": 1,
        "bet_amount": 50
    }


@pytest.fixture
def gacha_items():
    """가차 아이템 목록"""
    return [
        {
            "item_id": "sword_001",
            "item_name": "Iron Sword",
            "rarity": "common",
            "attack": 10,
            "category": "weapon"
        },
        {
            "item_id": "sword_002",
            "item_name": "Steel Sword",
            "rarity": "rare",
            "attack": 25,
            "category": "weapon"
        },
        {
            "item_id": "sword_003",
            "item_name": "Legendary Blade",
            "rarity": "legendary",
            "attack": 100,
            "category": "weapon"
        },
        {
            "item_id": "potion_001",
            "item_name": "Health Potion",
            "rarity": "common",
            "heal": 50,
            "category": "consumable"
        }
    ]


@pytest.fixture
def gacha_rates():
    """가차 확률 설정"""
    return {
        "common": 0.70,    # 70%
        "rare": 0.20,      # 20%
        "epic": 0.08,      # 8%
        "legendary": 0.02  # 2%
    }


# API 관련 픽스처
@pytest.fixture
def mock_api_client():
    """Mock API 클라이언트"""
    client = Mock()
    return client


@pytest.fixture
def api_headers():
    """API 헤더"""
    return {
        "Content-Type": "application/json",
        "Authorization": "Bearer test_token",
        "User-Agent": "TestClient/1.0"
    }


@pytest.fixture
def sample_api_response():
    """샘플 API 응답"""
    return {
        "success": True,
        "data": {
            "message": "Operation successful",
            "timestamp": "2024-01-01T00:00:00Z"
        },
        "metadata": {
            "request_id": "test_request_001",
            "version": "1.0"
        }
    }


# 데이터베이스 관련 픽스처
@pytest.fixture
def mock_database_connection():
    """Mock 데이터베이스 연결"""
    conn = AsyncMock()
    conn.execute.return_value = Mock()
    conn.fetchone.return_value = None
    conn.fetchall.return_value = []
    return conn


@pytest.fixture
def sample_database_rows():
    """샘플 데이터베이스 행들"""
    return [
        {"id": 1, "name": "Item 1", "value": 100},
        {"id": 2, "name": "Item 2", "value": 200},
        {"id": 3, "name": "Item 3", "value": 300}
    ]


# 게임 관련 픽스처
@pytest.fixture
def game_session():
    """게임 세션 데이터"""
    return {
        "session_id": "session_001",
        "user_id": 1,
        "game_type": "slot_machine",
        "start_time": "2024-01-01T10:00:00Z",
        "end_time": None,
        "total_bets": 0,
        "total_wins": 0,
        "current_balance": 1000
    }


@pytest.fixture
def slot_machine_config():
    """슬롯머신 설정"""
    return {
        "symbols": ["🍒", "🍋", "🍊", "🍇", "⭐", "💎"],
        "paylines": 5,
        "min_bet": 10,
        "max_bet": 1000,
        "jackpot_threshold": 10000,
        "rtp": 0.96  # Return to Player 96%
    }


# 성능 테스트 관련 픽스처
@pytest.fixture
def performance_config():
    """성능 테스트 설정"""
    return {
        "max_response_time": 1.0,  # 1초
        "max_concurrent_users": 100,
        "test_duration": 30,  # 30초
        "ramp_up_time": 10    # 10초
    }


@pytest.fixture
def load_test_data():
    """부하 테스트 데이터"""
    return {
        "users": list(range(1, 101)),  # 100명 사용자
        "requests_per_user": 50,
        "total_requests": 5000
    }


# 통합 테스트 관련 픽스처
@pytest.fixture
def integration_test_config():
    """통합 테스트 설정"""
    return {
        "test_database_url": "sqlite:///:memory:",
        "api_base_url": "http://localhost:8000",
        "test_user_count": 10,
        "test_duration": 60
    }


# 모킹 관련 픽스처
@pytest.fixture
def mock_external_api():
    """외부 API Mock"""
    api = Mock()
    api.get.return_value = Mock(
        status_code=200,
        json=lambda: {"status": "success", "data": {}}
    )
    api.post.return_value = Mock(
        status_code=201,
        json=lambda: {"status": "created", "id": 1}
    )
    return api


@pytest.fixture
def mock_cache():
    """캐시 Mock"""
    cache = Mock()
    cache.get.return_value = None
    cache.set.return_value = True
    cache.delete.return_value = True
    cache.exists.return_value = False
    return cache


@pytest.fixture
def mock_logger():
    """로거 Mock"""
    logger = Mock()
    return logger


# 에러 처리 관련 픽스처
@pytest.fixture
def error_scenarios():
    """에러 시나리오들"""
    return [
        {
            "name": "network_error",
            "exception": ConnectionError("Network connection failed"),
            "expected_status": 503
        },
        {
            "name": "timeout_error",
            "exception": TimeoutError("Request timeout"),
            "expected_status": 504
        },
        {
            "name": "validation_error",
            "exception": ValueError("Invalid input data"),
            "expected_status": 400
        },
        {
            "name": "authorization_error",
            "exception": PermissionError("Access denied"),
            "expected_status": 403
        }
    ]


# 시간 관련 픽스처
@pytest.fixture
def fixed_datetime():
    """고정된 날짜/시간"""
    from datetime import datetime
    return datetime(2024, 1, 1, 12, 0, 0)


@pytest.fixture
def time_ranges():
    """시간 범위들"""
    return {
        "daily": ("2024-01-01T00:00:00Z", "2024-01-01T23:59:59Z"),
        "weekly": ("2024-01-01T00:00:00Z", "2024-01-07T23:59:59Z"),
        "monthly": ("2024-01-01T00:00:00Z", "2024-01-31T23:59:59Z")
    }


# 이벤트 관련 픽스처
@pytest.fixture
def game_events():
    """게임 이벤트들"""
    return [
        {
            "event_type": "user_login",
            "user_id": 1,
            "timestamp": "2024-01-01T10:00:00Z",
            "data": {"platform": "web"}
        },
        {
            "event_type": "gacha_pull",
            "user_id": 1,
            "timestamp": "2024-01-01T10:05:00Z",
            "data": {"item_id": "sword_001", "rarity": "common"}
        },
        {
            "event_type": "slot_spin",
            "user_id": 1,
            "timestamp": "2024-01-01T10:10:00Z",
            "data": {"bet_amount": 50, "result": "WIN", "reward": 100}
        }
    ]


# 설정 관련 픽스처
@pytest.fixture
def app_config():
    """애플리케이션 설정"""
    return {
        "database_url": "sqlite:///:memory:",
        "redis_url": "redis://localhost:6379/0",
        "secret_key": "test_secret_key",
        "debug": True,
        "testing": True,
        "api_version": "v1",
        "max_connections": 100
    }