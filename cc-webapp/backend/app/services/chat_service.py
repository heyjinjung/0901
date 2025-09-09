"""
💬 Casino-Club F2P - Chat Service
===============================
실시간 채팅 및 AI 대화 시스템
"""

import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from .. import models
from ..schemas.chat_schemas import ChatMessageCreate, ChatRoomCreate
from ..utils.emotion_engine import EmotionEngine

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self, db: Session, redis=None):
        self.db = db
        self.redis = redis
        self.emotion_engine = EmotionEngine()

    async def create_chat_room(
        self, 
        user_id: int, 
        room_data: ChatRoomCreate
    ) -> models.ChatRoom:
        """채팅방 생성"""
        try:
            room = models.ChatRoom(
                room_name=room_data.room_name,
                room_type=room_data.room_type,
                description=room_data.description,
                created_by=user_id,
                is_active=True,
                max_participants=room_data.max_participants or 50,
                is_ai_enabled=room_data.is_ai_enabled or False
            )
            
            self.db.add(room)
            self.db.commit()
            self.db.refresh(room)
            
            # 생성자를 참가자로 추가
            await self.join_chat_room(user_id, room.id)
            
            return room
            
        except Exception as e:
            logger.error(f"Failed to create chat room: {str(e)}")
            self.db.rollback()
            raise

    async def join_chat_room(self, user_id: int, room_id: int) -> bool:
        """채팅방 참가"""
        try:
            # 이미 참가했는지 확인
            existing = self.db.query(models.ChatParticipant).filter(
                and_(
                    models.ChatParticipant.user_id == user_id,
                    models.ChatParticipant.room_id == room_id,
                    models.ChatParticipant.is_active == True
                )
            ).first()
            
            if existing:
                return True
            
            # 참가자 추가
            participant = models.ChatParticipant(
                user_id=user_id,
                room_id=room_id,
                joined_at=datetime.utcnow(),
                is_active=True
            )
            
            self.db.add(participant)
            self.db.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to join chat room: {str(e)}")
            self.db.rollback()
            return False

    async def send_message(
        self, 
        user_id: int, 
        room_id: int, 
        message_data: ChatMessageCreate
    ) -> models.ChatMessage:
        """메시지 전송"""
        try:
            # 채팅방 참가 확인
            participant = self.db.query(models.ChatParticipant).filter(
                and_(
                    models.ChatParticipant.user_id == user_id,
                    models.ChatParticipant.room_id == room_id,
                    models.ChatParticipant.is_active == True
                )
            ).first()
            
            if not participant:
                raise ValueError("User is not a participant of this room")
            
            # 메시지 생성
            message = models.ChatMessage(
                room_id=room_id,
                sender_id=user_id,
                content=message_data.content,
                message_type=message_data.message_type,
                sent_at=datetime.utcnow(),
                metadata=message_data.metadata or {}
            )
            
            self.db.add(message)
            self.db.commit()
            self.db.refresh(message)
            
            # 감정 분석 (비동기)
            if message_data.content:
                emotion_result = await self.emotion_engine.detect_emotion_from_text(
                    message_data.content
                )
                
                # 감정 결과를 메타데이터에 저장
                if emotion_result:
                    message.metadata = {
                        **message.metadata,
                        "emotion": emotion_result
                    }
                    self.db.commit()
            
            # Redis에 실시간 알림 (있는 경우)
            if self.redis:
                await self._notify_room_participants(room_id, message)
            
            return message
            
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            self.db.rollback()
            raise

    async def get_room_messages(
        self,
        room_id: int,
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> List[models.ChatMessage]:
        """채팅방 메시지 조회"""
        try:
            # 참가 권한 확인
            participant = self.db.query(models.ChatParticipant).filter(
                and_(
                    models.ChatParticipant.user_id == user_id,
                    models.ChatParticipant.room_id == room_id
                )
            ).first()
            
            if not participant:
                raise ValueError("User is not authorized to view this room")
            
            # 메시지 조회 (참가 시점 이후)
            query = self.db.query(models.ChatMessage).filter(
                models.ChatMessage.room_id == room_id
            )
            
            if participant.joined_at:
                query = query.filter(
                    models.ChatMessage.sent_at >= participant.joined_at
                )
            
            messages = query.order_by(
                desc(models.ChatMessage.sent_at)
            ).offset(offset).limit(limit).all()
            
            return list(reversed(messages))  # 시간순 정렬
            
        except Exception as e:
            logger.error(f"Failed to get room messages: {str(e)}")
            return []

    async def create_ai_conversation(
        self,
        user_id: int,
        assistant_type: str = "general"
    ) -> models.AIConversation:
        """AI 대화 생성"""
        try:
            # AI 어시스턴트 조회
            assistant = self.db.query(models.AIAssistant).filter(
                models.AIAssistant.assistant_type == assistant_type,
                models.AIAssistant.is_active == True
            ).first()
            
            if not assistant:
                # 기본 어시스턴트 생성
                assistant = models.AIAssistant(
                    name="General Assistant",
                    assistant_type="general",
                    description="General purpose AI assistant",
                    personality_config={
                        "tone": "friendly",
                        "expertise": "general",
                        "response_style": "helpful"
                    },
                    is_active=True
                )
                self.db.add(assistant)
                self.db.commit()
                self.db.refresh(assistant)
            
            # 대화 생성
            conversation = models.AIConversation(
                user_id=user_id,
                assistant_id=assistant.id,
                started_at=datetime.utcnow(),
                context_data={
                    "user_preferences": await self._get_user_context(user_id),
                    "conversation_type": assistant_type
                }
            )
            
            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)
            
            return conversation
            
        except Exception as e:
            logger.error(f"Failed to create AI conversation: {str(e)}")
            self.db.rollback()
            raise

    async def send_ai_message(
        self,
        conversation_id: int,
        user_id: int,
        user_message: str
    ) -> Dict[str, Any]:
        """AI와 메시지 교환"""
        try:
            # 대화 확인
            conversation = self.db.query(models.AIConversation).filter(
                models.AIConversation.id == conversation_id,
                models.AIConversation.user_id == user_id
            ).first()
            
            if not conversation:
                raise ValueError("Conversation not found")
            
            # 사용자 메시지 저장
            user_msg = models.ChatMessage(
                conversation_id=conversation_id,
                sender_id=user_id,
                content=user_message,
                message_type="text",
                sent_at=datetime.utcnow(),
                is_ai_message=False
            )
            
            self.db.add(user_msg)
            
            # AI 응답 생성
            ai_response = await self._generate_ai_response(
                conversation, 
                user_message
            )
            
            # AI 메시지 저장
            ai_msg = models.ChatMessage(
                conversation_id=conversation_id,
                sender_id=None,  # AI는 sender_id가 None
                content=ai_response["content"],
                message_type="text",
                sent_at=datetime.utcnow(),
                is_ai_message=True,
                metadata={
                    "confidence": ai_response.get("confidence", 0.8),
                    "model_used": ai_response.get("model", "default")
                }
            )
            
            self.db.add(ai_msg)
            self.db.commit()
            
            return {
                "user_message": user_msg,
                "ai_response": ai_msg,
                "conversation_updated": True
            }
            
        except Exception as e:
            logger.error(f"Failed to send AI message: {str(e)}")
            self.db.rollback()
            raise

    async def get_user_conversations(self, user_id: int) -> List[models.AIConversation]:
        """사용자 AI 대화 목록"""
        try:
            conversations = self.db.query(models.AIConversation).filter(
                models.AIConversation.user_id == user_id
            ).order_by(desc(models.AIConversation.started_at)).all()
            
            return conversations
            
        except Exception as e:
            logger.error(f"Failed to get user conversations: {str(e)}")
            return []

    async def _get_user_context(self, user_id: int) -> Dict[str, Any]:
        """사용자 컨텍스트 수집"""
        try:
            # 사용자 기본 정보
            user = self.db.query(models.User).filter(models.User.id == user_id).first()
            if not user:
                return {}
            
            # 퀴즈 히스토리
            quiz_attempts = self.db.query(models.UserQuizAttempt).filter(
                models.UserQuizAttempt.user_id == user_id
            ).count()
            
            # 감정 프로필
            emotion_profile = self.db.query(models.EmotionProfile).filter(
                models.EmotionProfile.user_id == user_id
            ).first()
            
            return {
                "username": user.username,
                "quiz_attempts": quiz_attempts,
                "emotion_state": emotion_profile.current_mood if emotion_profile else "neutral",
                "join_date": user.created_at.isoformat() if hasattr(user, 'created_at') else None
            }
            
        except Exception as e:
            logger.error(f"Failed to get user context: {str(e)}")
            return {}

    async def _generate_ai_response(
        self, 
        conversation: models.AIConversation, 
        user_message: str
    ) -> Dict[str, Any]:
        """AI 응답 생성"""
        try:
            # 어시스턴트 설정 로드
            assistant = conversation.assistant
            personality = assistant.personality_config or {}
            
            # 간단한 규칙 기반 응답 (실제로는 OpenAI API 등 사용)
            response_templates = {
                "greeting": [
                    "안녕하세요! 카지노클럽에 오신 것을 환영합니다! 🎰",
                    "반가워요! 오늘 어떤 게임을 도전해볼까요? 🎲",
                    "환영합니다! 궁금한 것이 있으시면 언제든 물어보세요! 😊"
                ],
                "quiz": [
                    "퀴즈를 풀어보시는군요! 어떤 분야가 관심있으신가요? 🧠",
                    "리스크 평가 퀴즈를 추천드려요. 게임 성향을 알아보는 재미있는 테스트예요! 📊",
                    "퀴즈 결과를 바탕으로 맞춤형 게임을 추천해드릴 수 있어요! 🎯"
                ],
                "help": [
                    "도움이 필요하시군요! 구체적으로 어떤 부분이 궁금하신가요? 🤔",
                    "게임 규칙, 전략, 또는 플랫폼 사용법 중 어떤 것을 도와드릴까요? 💡",
                    "자세한 가이드나 튜토리얼이 필요하시면 말씀해주세요! 📚"
                ],
                "default": [
                    "흥미로운 말씀이네요! 더 자세히 이야기해주세요. 🎪",
                    "그렇군요! 카지노클럽에서 어떤 경험을 원하시나요? 🎨",
                    "좋은 질문이에요! 어떻게 도움을 드릴까요? ✨"
                ]
            }
            
            # 메시지 분류
            message_lower = user_message.lower()
            
            if any(word in message_lower for word in ["안녕", "hello", "hi", "처음"]):
                category = "greeting"
            elif any(word in message_lower for word in ["퀴즈", "quiz", "테스트", "평가"]):
                category = "quiz"
            elif any(word in message_lower for word in ["도움", "help", "모르겠", "어떻게"]):
                category = "help"
            else:
                category = "default"
            
            # 응답 선택
            import random
            response = random.choice(response_templates[category])
            
            return {
                "content": response,
                "confidence": 0.85,
                "model": "rule_based_v1",
                "category": category
            }
            
        except Exception as e:
            logger.error(f"Failed to generate AI response: {str(e)}")
            return {
                "content": "죄송해요, 잠시 문제가 있었어요. 다시 말씀해주시겠어요? 😅",
                "confidence": 0.1,
                "model": "fallback",
                "category": "error"
            }

    async def _notify_room_participants(
        self, 
        room_id: int, 
        message: models.ChatMessage
    ):
        """실시간 알림 전송 (Redis)"""
        try:
            if not self.redis:
                return
            
            # 채팅방 참가자 목록
            participants = self.db.query(models.ChatParticipant).filter(
                and_(
                    models.ChatParticipant.room_id == room_id,
                    models.ChatParticipant.is_active == True
                )
            ).all()
            
            notification = {
                "type": "new_message",
                "room_id": room_id,
                "message_id": message.id,
                "sender_id": message.sender_id,
                "content": message.content,
                "timestamp": message.sent_at.isoformat()
            }
            
            # 각 참가자에게 알림
            for participant in participants:
                if participant.user_id != message.sender_id:  # 본인 제외
                    await self.redis.publish(
                        f"user_{participant.user_id}_chat",
                        json.dumps(notification)
                    )
                    
        except Exception as e:
            logger.error(f"Failed to notify participants: {str(e)}")

    async def update_emotion_profile(
        self,
        user_id: int,
        emotion_data: Dict[str, Any]
    ) -> models.EmotionProfile:
        """감정 프로필 업데이트"""
        try:
            profile = self.db.query(models.EmotionProfile).filter(
                models.EmotionProfile.user_id == user_id
            ).first()
            
            if not profile:
                profile = models.EmotionProfile(
                    user_id=user_id,
                    current_mood="neutral",
                    emotion_history={},
                    mood_patterns={},
                    last_analysis=datetime.utcnow()
                )
                self.db.add(profile)
            
            # 감정 데이터 업데이트
            profile.current_mood = emotion_data.get("mood", profile.current_mood)
            profile.last_analysis = datetime.utcnow()
            
            # 히스토리 업데이트
            if not profile.emotion_history:
                profile.emotion_history = {}
            
            today = datetime.utcnow().date().isoformat()
            profile.emotion_history[today] = emotion_data
            
            self.db.commit()
            self.db.refresh(profile)
            
            return profile
            
        except Exception as e:
            logger.error(f"Failed to update emotion profile: {str(e)}")
            self.db.rollback()
            raise
