"""
😊 Casino-Club F2P - 감정 엔진
============================
감정 감지, 분석, 피드백 생성 엔진
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)


class EmotionEngine:
    """감정 분석 및 피드백 엔진"""
    
    def __init__(self, redis_client=None):
        self.redis = redis_client
        
        # 감정별 키워드와 가중치
        self.emotion_keywords = {
            "joy": {
                "keywords": ["좋아", "기뻐", "행복", "최고", "완벽", "대박", "성공", "승리"],
                "weight": 1.0
            },
            "sad": {
                "keywords": ["슬퍼", "실망", "안타까", "아쉬워", "실패", "패배", "힘들어"],
                "weight": 1.0
            },
            "angry": {
                "keywords": ["화나", "짜증", "분노", "열받", "억울", "불공평"],
                "weight": 1.2
            },
            "neutral": {
                "keywords": ["보통", "그냥", "괜찮", "무난", "평범"],
                "weight": 0.5
            },
            "excited": {
                "keywords": ["신나", "흥미", "재미", "즐거", "놀라", "와우"],
                "weight": 1.1
            },
            "calm": {
                "keywords": ["차분", "평온", "안정", "조용", "평화"],
                "weight": 0.8
            }
        }
        
        # 감정별 피드백 템플릿
        self.feedback_templates = {
            "joy": [
                "🎉 정말 기쁘시겠네요! 이런 기분이 계속되길 바라요",
                "✨ 멋진 성과입니다! 다음엔 더 좋은 일이 있을 거예요",
                "🌟 최고의 순간이네요! 이 에너지로 계속 도전해보세요"
            ],
            "sad": [
                "😔 아쉬운 결과네요. 하지만 다음 기회가 더 좋을 거예요",
                "💙 실망스럽겠지만, 이런 경험이 더 성장하게 만들어요",
                "🤗 괜찮아요! 누구에게나 이런 날이 있어요"
            ],
            "angry": [
                "😤 화가 나시는군요. 잠시 휴식을 취해보시는 건 어떨까요?",
                "🧘‍♂️ 깊게 숨을 쉬어보세요. 더 좋은 기회가 올 거예요",
                "🛡️ 이런 감정도 자연스러워요. 조금 쉬었다가 다시 시작해보세요"
            ],
            "neutral": [
                "🙂 평온한 상태네요. 새로운 도전을 시작하기 좋은 때예요",
                "📈 안정적인 플레이 스타일이네요. 조금씩 도전해보세요",
                "⚖️ 균형잡힌 마음가짐이 좋아요"
            ],
            "excited": [
                "🚀 정말 신나시는군요! 이 에너지로 더 큰 도전을 해보세요",
                "⚡ 흥미진진하네요! 재미있는 게임들이 더 많이 있어요",
                "🎪 이런 즐거움이 계속되길 바라요!"
            ],
            "calm": [
                "🧘 차분한 마음 상태가 좋네요. 집중력이 높아질 거예요",
                "🕯️ 평온한 시간을 보내고 계시는군요",
                "🌿 안정적인 감정 상태는 좋은 결과를 가져다줄 거예요"
            ]
        }
    
    async def detect_emotion_from_text(self, text: str) -> Dict[str, Any]:
        """텍스트에서 감정 감지"""
        try:
            if not text:
                return {"emotion": "neutral", "confidence": 0.0, "sentiment_score": 0.0}
            
            text_lower = text.lower()
            emotion_scores = {}
            
            # 각 감정별 키워드 매칭
            for emotion, data in self.emotion_keywords.items():
                score = 0.0
                keywords_found = []
                
                for keyword in data["keywords"]:
                    if keyword in text_lower:
                        score += data["weight"]
                        keywords_found.append(keyword)
                
                if score > 0:
                    emotion_scores[emotion] = {
                        "score": score,
                        "keywords": keywords_found
                    }
            
            # 최고 점수 감정 결정
            if emotion_scores:
                best_emotion = max(emotion_scores.keys(), key=lambda k: emotion_scores[k]["score"])
                confidence = min(emotion_scores[best_emotion]["score"] / 3.0, 1.0)
                
                # 감정별 감정 점수 계산
                sentiment_mapping = {
                    "joy": 0.8, "excited": 0.7, "calm": 0.3,
                    "neutral": 0.0, "sad": -0.5, "angry": -0.8
                }
                sentiment_score = sentiment_mapping.get(best_emotion, 0.0)
            else:
                best_emotion = "neutral"
                confidence = 0.5
                sentiment_score = 0.0
            
            result = {
                "emotion": best_emotion,
                "confidence": confidence,
                "sentiment_score": sentiment_score,
                "details": emotion_scores
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to detect emotion: {str(e)}")
            return {"emotion": "neutral", "confidence": 0.0, "sentiment_score": 0.0}
    
    async def detect_emotion_from_actions(self, user_actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """사용자 행동에서 감정 감지"""
        try:
            if not user_actions:
                return {"emotion": "neutral", "confidence": 0.0}
            
            emotion_indicators = {
                "joy": 0.0,
                "sad": 0.0,
                "angry": 0.0,
                "excited": 0.0,
                "calm": 0.0,
                "neutral": 0.0
            }
            
            for action in user_actions:
                action_type = action.get("action_type", "")
                metadata = action.get("metadata", {})
                
                # 행동별 감정 점수
                if action_type == "GAME_WIN":
                    emotion_indicators["joy"] += 1.5
                    emotion_indicators["excited"] += 1.0
                elif action_type == "GAME_LOSE":
                    emotion_indicators["sad"] += 1.0
                    if metadata.get("consecutive_losses", 0) > 3:
                        emotion_indicators["angry"] += 0.8
                elif action_type == "EARN_CYBER_TOKENS":
                    tokens = metadata.get("tokens_earned", 0)
                    if tokens > 100:
                        emotion_indicators["joy"] += 0.8
                    elif tokens > 0:
                        emotion_indicators["calm"] += 0.5
                elif action_type == "SPEND_CYBER_TOKENS":
                    tokens = metadata.get("tokens_spent", 0)
                    if tokens > 500:
                        emotion_indicators["excited"] += 0.6
                elif action_type == "COMPLETE_MISSION":
                    emotion_indicators["joy"] += 1.2
                    emotion_indicators["excited"] += 0.8
                elif action_type in ["LOGIN", "VISIT_SHOP"]:
                    emotion_indicators["neutral"] += 0.3
                    emotion_indicators["calm"] += 0.2
            
            # 최고 점수 감정 결정
            best_emotion = max(emotion_indicators.keys(), key=lambda k: emotion_indicators[k])
            max_score = emotion_indicators[best_emotion]
            confidence = min(max_score / 5.0, 1.0) if max_score > 0 else 0.5
            
            return {
                "emotion": best_emotion,
                "confidence": confidence,
                "action_analysis": emotion_indicators,
                "total_actions": len(user_actions)
            }
            
        except Exception as e:
            logger.error(f"Failed to detect emotion from actions: {str(e)}")
            return {"emotion": "neutral", "confidence": 0.0}
    
    async def generate_personalized_feedback(
        self, 
        emotion: str, 
        context: Dict[str, Any] = None
    ) -> str:
        """개인화된 피드백 메시지 생성"""
        try:
            templates = self.feedback_templates.get(emotion, self.feedback_templates["neutral"])
            
            # 컨텍스트 기반 템플릿 선택
            if context:
                # 게임 결과에 따른 맞춤 메시지
                if context.get("game_result") == "win":
                    if emotion in ["joy", "excited"]:
                        return "🎉 대단한 승리네요! 이 기세로 더 큰 도전을 해보세요!"
                    else:
                        return "✨ 좋은 결과입니다! 실력이 늘고 있어요"
                elif context.get("game_result") == "lose":
                    if emotion == "angry":
                        return "😤 아쉽지만, 잠시 휴식을 취하고 마음을 진정시켜보세요"
                    elif emotion == "sad":
                        return "😔 실망스럽겠지만, 다음 기회에는 분명 더 좋은 결과가 있을 거예요"
                    else:
                        return "💪 경험이 실력을 만듭니다. 계속 도전해보세요!"
                
                # 세그먼트별 맞춤 메시지
                segment = context.get("user_segment")
                if segment == "Whale" and emotion == "joy":
                    return "👑 VIP 회원다운 멋진 성과네요! 특별 보상을 확인해보세요"
                elif segment == "At-risk" and emotion in ["sad", "angry"]:
                    return "🤗 힘내세요! 특별 복귀 보상을 준비했어요"
            
            # 기본 템플릿에서 랜덤 선택
            import random
            return random.choice(templates)
            
        except Exception as e:
            logger.error(f"Failed to generate feedback: {str(e)}")
            return "😊 오늘도 즐거운 게임 되세요!"
    
    async def get_user_mood(self, user_id: int) -> str:
        """사용자 현재 기분 조회 (Redis 캐시)"""
        try:
            if not self.redis:
                return "neutral"
            
            mood_key = f"user:{user_id}:current_mood"
            mood = await self.redis.get(mood_key)
            
            return mood.decode() if mood else "neutral"
            
        except Exception as e:
            logger.error(f"Failed to get user mood: {str(e)}")
            return "neutral"
    
    async def update_user_mood(
        self, 
        user_id: int, 
        emotion: str, 
        confidence: float = 0.5,
        duration_hours: int = 2
    ):
        """사용자 기분 업데이트 (Redis 캐시)"""
        try:
            if not self.redis:
                return
            
            mood_key = f"user:{user_id}:current_mood"
            mood_history_key = f"user:{user_id}:mood_history"
            
            # 현재 기분 업데이트
            await self.redis.setex(
                mood_key, 
                duration_hours * 3600, 
                emotion
            )
            
            # 기분 히스토리 추가
            mood_entry = {
                "emotion": emotion,
                "confidence": confidence,
                "timestamp": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(hours=duration_hours)).isoformat()
            }
            
            await self.redis.lpush(mood_history_key, json.dumps(mood_entry))
            await self.redis.ltrim(mood_history_key, 0, 50)  # 최근 50개만 유지
            
        except Exception as e:
            logger.error(f"Failed to update user mood: {str(e)}")
    
    async def generate_quiz_feedback(
        self, 
        user_id: int, 
        quiz_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """퀴즈 결과 기반 감정 피드백 생성"""
        try:
            score = quiz_result.get("total_score", 0)
            max_score = quiz_result.get("max_possible_score", 100)
            percentage = (score / max_score) * 100 if max_score > 0 else 0
            
            # 점수 기반 감정 판단
            if percentage >= 90:
                emotion = "joy"
                message = "🌟 완벽한 점수예요! 정말 대단합니다!"
            elif percentage >= 80:
                emotion = "excited"
                message = "🎉 훌륭한 성과네요! 계속 이런 실력을 보여주세요"
            elif percentage >= 60:
                emotion = "calm"
                message = "👍 좋은 결과입니다. 조금만 더 노력하면 완벽할 거예요"
            elif percentage >= 40:
                emotion = "neutral"
                message = "📚 아직 배울 게 많네요. 계속 도전해보세요"
            else:
                emotion = "sad"
                message = "😔 아쉬운 결과지만, 포기하지 마세요. 다음엔 더 잘할 거예요"
            
            # 사용자 기분 업데이트
            await self.update_user_mood(user_id, emotion, confidence=0.8)
            
            # 추가 격려 메시지
            encouragement = await self.generate_personalized_feedback(
                emotion, 
                {"quiz_score": percentage, "user_id": user_id}
            )
            
            return {
                "emotion": emotion,
                "message": message,
                "encouragement": encouragement,
                "score_percentage": percentage,
                "mood_color": self._get_mood_color(emotion),
                "animation": self._get_mood_animation(emotion)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate quiz feedback: {str(e)}")
            return {
                "emotion": "neutral",
                "message": "퀴즈를 완료해주셔서 감사합니다!",
                "encouragement": "계속 도전해보세요!",
                "score_percentage": 0,
                "mood_color": "#6B7280",
                "animation": "none"
            }
    
    def _get_mood_color(self, emotion: str) -> str:
        """감정별 테마 컬러 반환"""
        mood_colors = {
            "joy": "#FFE066",      # 기쁨 - 밝은 노란색
            "sad": "#3B4A6B",      # 슬픔 - 어두운 파란색
            "angry": "#FF4516",    # 분노 - 빨간색
            "excited": "#F59E0B",  # 흥분 - 오렌지색
            "calm": "#135B79",     # 차분 - 차분한 파란색
            "neutral": "#6B7280",  # 중립 - 회색
            "love": "#FFB6B9"      # 사랑 - 분홍색
        }
        return mood_colors.get(emotion, mood_colors["neutral"])
    
    def _get_mood_animation(self, emotion: str) -> str:
        """감정별 애니메이션 효과"""
        mood_animations = {
            "joy": "bounce",
            "sad": "fadeIn",
            "angry": "shake",
            "excited": "pulse",
            "calm": "slideIn",
            "neutral": "fadeIn",
            "love": "heartbeat"
        }
        return mood_animations.get(emotion, "fadeIn")
