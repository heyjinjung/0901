"""CJ AI Service for intelligent chat interactions and emotion analysis."""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union

from sqlalchemy.orm import Session

from app.services.token_service import TokenService
from app.websockets.chat import WebSocketManager

logger = logging.getLogger(__name__)

class ChatContext:
    """
    Represents the context of a chat interaction.
    
    Attributes:
        user_id (int): Unique identifier for the user
        messages (List[Dict[str, str]]): List of messages in the conversation
        context_type (str): Type of context (e.g., 'game', 'support')
    """
    def __init__(
        self, 
        user_id: int, 
        messages: Optional[List[Dict[str, str]]] = None,
        context_type: str = 'default'
    ):
        self.user_id = user_id
        self.messages = messages or []
        self.context_type = context_type

    def add_message(self, message: Dict[str, str]) -> None:
        """
        Add a new message to the chat context.

        Args:
            message (Dict[str, str]): Message to add to the context
        """
        self.messages.append(message)

    def get_last_message(self) -> Optional[Dict[str, str]]:
        """
        Retrieve the last message in the context.

        Returns:
            Optional[Dict[str, str]]: The last message, or None if no messages exist
        """
        return self.messages[-1] if self.messages else None

    def clear_context(self) -> None:
        """
        Clear all messages from the context.
        """
        self.messages = []

__all__ = ["CJAIService", "ChatContext"]

class CJAIService:
    """
    Service for managing AI-driven chat interactions and emotion analysis.

    Handles chat message processing, emotion tracking, and intelligent responses.
    """

    def __init__(
        self, 
        token_service: Optional[TokenService] = None, 
        websocket_manager: Optional[WebSocketManager] = None
    ):
        """
        Initialize CJ AI Service with token and websocket management.

        Args:
            token_service (Optional[TokenService]): Service for managing user tokens
            websocket_manager (Optional[WebSocketManager]): Manager for WebSocket connections
        """
        self.token_service = token_service
        self.websocket_manager = websocket_manager

    async def process_chat_message(self, message: str) -> str:
        """
        Process an incoming chat message and generate an intelligent response.

        Args:
            message (str): Incoming chat message

        Returns:
            str: AI-generated response
        """
        try:
            # Basic AI response generation logic
            # This is a placeholder implementation
            response = f"AI processed: {message}"
            
            # Optional token deduction for chat interaction
            if self.token_service:
                self.token_service.deduct_tokens(1, 1)  # Example user ID and token cost
            
            # Optional WebSocket broadcast
            if self.websocket_manager:
                await self.websocket_manager.broadcast(f"New message: {message}")
            
            return response
        except Exception as exc:
            logger.error(f"Chat message processing error: {exc}")
            return "죄송합니다. 현재 대화를 처리할 수 없습니다."

    async def get_user_emotion_history(self, user_id: int) -> List[Dict]:
        """
        Retrieve emotion history for a specific user.

        Args:
            user_id (int): User's unique identifier

        Returns:
            List[Dict]: List of past emotion interactions
        """
        try:
            # Placeholder implementation for emotion history retrieval
            emotion_history = [
                {
                    "timestamp": datetime.now().isoformat(),
                    "emotion": "neutral",
                    "context": "Chat interaction"
                }
            ]
            return emotion_history
        except Exception as exc:
            logger.error(f"Failed to retrieve emotion history for user {user_id}: {exc}")
            return []

    async def analyze_emotion(self, message: str) -> Dict[str, float]:
        """
        Analyze the emotional tone of a given message.

        Args:
            message (str): Text message to analyze

        Returns:
            Dict[str, float]: Emotion analysis results with confidence scores
        """
        try:
            # Basic emotion analysis logic
            # This is a placeholder implementation
            emotion_analysis = {
                "joy": 0.3,
                "sadness": 0.2,
                "anger": 0.1,
                "fear": 0.1,
                "neutral": 0.3
            }
            return emotion_analysis
        except Exception as exc:
            logger.error(f"Emotion analysis failed: {exc}")
            return {}

    def analyze_emotion_sync(self, message: str) -> Dict[str, float]:
        """
        Synchronous version of emotion analysis for compatibility with tests.

        Args:
            message (str): Text message to analyze

        Returns:
            Dict[str, float]: Emotion analysis results with confidence scores
        """
        try:
            # Basic emotion analysis logic
            # This is a placeholder implementation
            emotion_analysis = {
                "joy": 0.3,
                "sadness": 0.2,
                "anger": 0.1,
                "fear": 0.1,
                "neutral": 0.3
            }
            return emotion_analysis
        except Exception as exc:
            logger.error(f"Emotion analysis failed: {exc}")
            return {}

    def cache_emotion_result(
        self, 
        user_id: int, 
        emotion_result: Union[Dict[str, Union[float, str]], str], 
        *args, 
        **kwargs
    ) -> None:
        """
        Cache emotion analysis results for a user.

        Args:
            user_id (int): User's unique identifier
            emotion_result (Union[Dict[str, Union[float, str]], str]): Emotion analysis results to cache
            *args: Variable positional arguments for compatibility
            **kwargs: Variable keyword arguments for compatibility (e.g., redis_client, sentiment_analyzer)
        """
        try:
            # Convert various input types to a consistent dictionary format
            if isinstance(emotion_result, str):
                emotion_result = {"emotion": emotion_result}
            elif isinstance(emotion_result, dict):
                # Ensure all values are converted to strings if they are not already
                emotion_result = {
                    k: str(v) if not isinstance(v, str) else v 
                    for k, v in emotion_result.items()
                }
            
            # Placeholder implementation for caching emotion results
            logger.info(f"Caching emotion result for user {user_id}: {emotion_result}")
            
            # Optional Redis caching
            redis_client = kwargs.get('redis_client')
            if redis_client is not None:
                redis_key = f"user:{user_id}:emotion"
                redis_client.set(redis_key, json.dumps(emotion_result))
            
            # Optional sentiment analysis
            sentiment_analyzer = kwargs.get('sentiment_analyzer')
            if sentiment_analyzer is not None:
                # Placeholder for sentiment analysis processing
                pass
        except Exception as exc:
            logger.error(f"Failed to cache emotion result for user {user_id}: {exc}")

    async def send_websocket_message(self, user_id: int, message: str) -> bool:
        """
        Send a WebSocket message to a specific user.
        
        Args:
            user_id (int): ID of the user to send message to
            message (str): Message content to send
            
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        try:
            if self.websocket_manager is None:
                logger.warning(f"No WebSocket manager available for user {user_id}")
                return False
                
            # For now, broadcast to all connections since we don't have user-specific connections
            await self.websocket_manager.broadcast(f"[User {user_id}] {message}")
            logger.info(f"Sent WebSocket message for user {user_id}")
            return True
        except Exception as exc:
            logger.error(f"Failed to send WebSocket message for user {user_id}: {exc}")
            return False
