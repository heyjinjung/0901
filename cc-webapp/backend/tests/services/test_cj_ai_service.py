import json
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.services.cj_ai_service import CJAIService, ChatContext

@pytest.fixture
def ai_service():
    mock_websocket = AsyncMock()
    service = CJAIService(websocket_manager=mock_websocket)
    return service

@pytest.mark.asyncio
async def test_analyze_emotion(ai_service):
    """Test emotion analysis method."""
    message = "오늘 게임에서 이겼어요!"
    
    result = await ai_service.analyze_emotion(message)
    
    assert isinstance(result, dict)
    assert "joy" in result
    assert "neutral" in result
    assert "sadness" in result
    assert all(isinstance(score, (int, float)) for score in result.values())

@pytest.mark.asyncio
async def test_process_chat_message(ai_service):
    """Test chat message processing."""
    message = "안녕하세요!"
    
    with patch.object(ai_service, 'token_service') as mock_token_service:
        mock_token_service.deduct_tokens = MagicMock()
        
        response = await ai_service.process_chat_message(message)
        
        assert isinstance(response, str)
        assert "AI processed" in response
        mock_token_service.deduct_tokens.assert_called_once()

@pytest.mark.asyncio
async def test_get_user_emotion_history(ai_service):
    """Test getting user emotion history."""
    user_id = 789
    
    history = await ai_service.get_user_emotion_history(user_id)
    
    assert isinstance(history, list)
    assert len(history) > 0
    assert "timestamp" in history[0]
    assert "emotion" in history[0]
    assert "context" in history[0]

@pytest.mark.asyncio
async def test_get_user_emotion_history_no_redis(ai_service):
    """Test emotion history when no Redis is available."""
    user_id = 123
    result = await ai_service.get_user_emotion_history(user_id)
    
    # Should return a default emotion history entry
    assert isinstance(result, list)
    assert len(result) > 0

@pytest.mark.asyncio
async def test_send_websocket_message(ai_service):
    """Test sending WebSocket messages."""
    user_id = 999
    message = "테스트 메시지"

    result = await ai_service.send_websocket_message(user_id, message)

    assert result is True
    ai_service.websocket_manager.broadcast.assert_called_once()

@pytest.mark.asyncio
async def test_send_websocket_message_no_manager(ai_service):
    """Test WebSocket message sending when no manager is available."""
    ai_service.websocket_manager = None
    result = await ai_service.send_websocket_message(123, "테스트")
    
    assert result is False

def test_cache_emotion_result(ai_service):
    """Test caching emotion results."""
    user_id = 456
    emotion_result = {"joy": 0.8, "neutral": 0.2}
    
    # Should not raise any exceptions
    ai_service.cache_emotion_result(user_id, emotion_result)
    
    # Test with string input
    ai_service.cache_emotion_result(user_id, "happy")

def test_analyze_emotion_sync(ai_service):
    """Test synchronous emotion analysis."""
    message = "게임이 재미있어요!"
    
    result = ai_service.analyze_emotion_sync(message)
    
    assert isinstance(result, dict)
    assert "joy" in result
    assert "neutral" in result

def test_chat_context():
    """Test ChatContext class."""
    user_id = 123
    context = ChatContext(user_id)
    
    assert context.user_id == user_id
    assert context.messages == []
    assert context.context_type == 'default'
    
    # Test adding messages
    message = {"role": "user", "content": "안녕하세요"}
    context.add_message(message)
    
    assert len(context.messages) == 1
    assert context.get_last_message() == message
    
    # Test clearing context
    context.clear_context()
    assert len(context.messages) == 0
    assert context.get_last_message() is None
