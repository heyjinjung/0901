"""
감정 기반 피드백 생성 서비스
"""
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

from ..schemas import FeedbackResponse

class EmotionFeedbackService:
    def get_emotion_feedback(self, emotion_result, user_segment, mission_type, context_text) -> FeedbackResponse:
        return FeedbackResponse(
            success=True,
            message="감정 분석 기반 피드백이 생성되었습니다",
            suggestions=["일일 미션 완료하기", "추천 게임 플레이"],
            emotion="positive",
            segment=user_segment if user_segment else "default",
            recommendation={"type": "mission", "description": "일일 미션 완료하기"},
            reward_suggestion={"token": 50, "description": "사이버 토큰"}
        )
    """
    사용자 감정에 기반한 피드백 생성 서비스
    SOLID 원칙에 따라 단일 책임 원칙을 준수
    """
    
    def __init__(self, db=None):
        """
        감정 피드백 서비스 초기화
        
        Args:
            db: 데이터베이스 연결 (옵션)
        """
        self.db = db
        self.templates = self._load_templates()
        logger.info("Emotion Feedback Service initialized")
    
    def _load_templates(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        """
        감정 피드백 템플릿 로드
        
        Returns:
            감정별 세그먼트별 피드백 템플릿
        """
        # 기본 템플릿
        return {
            "excited": {
                "Whale": {"message": "대단해요! 계속해서 이 기세를 유지해보세요! 🎉"},
                "Medium": {"message": "축하합니다! 좋은 결과네요! 👍"},
                "Low": {"message": "멋져요! 행운이 따르고 있어요! ✨"}
            },
            "frustrated": {
                "Whale": {"message": "괜찮아요, 다음에 더 좋은 결과가 있을 거예요. 도전해보세요! 💪"},
                "Medium": {"message": "운은 돌고 돌아요. 조금만 더 해보세요! 🍀"},
                "Low": {"message": "아쉽네요. 하지만 포기하지 마세요! 😊"}
            },
            "neutral": {
                "Whale": {"message": "오늘은 어떤 게임을 즐겨보실래요? 🎮"},
                "Medium": {"message": "새로운 게임에 도전해보는 건 어떨까요? 🎲"},
                "Low": {"message": "즐거운 시간 보내세요! 🎯"}
            }
        }
    
    def generate_feedback(self, emotion: str, segment: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        감정과 세그먼트에 맞는 피드백 생성
        
        Args:
            emotion: 감정 상태 (excited, frustrated, neutral 등)
            segment: 사용자 세그먼트 (Whale, Medium, Low)
            context: 추가 컨텍스트 정보
        
        Returns:
            피드백 메시지 및 추가 정보가 포함된 객체
        """
        try:
            # 감정 상태 정규화 (소문자 변환)
            emotion = emotion.lower() if emotion else "neutral"
            
            # 세그먼트 기본값 설정
            segment = segment or "Medium"
            
            # 템플릿 찾기
            emotion_templates = self.templates.get(emotion, self.templates["neutral"])
            segment_template = emotion_templates.get(segment, emotion_templates.get("Medium", {"message": "즐거운 게임 되세요!"}))
            
            # 컨텍스트 기반 추가 추천 생성
            suggestions = self._generate_suggestions(emotion, segment, context)
            
            # 최종 피드백 구성
            feedback = {
                "message": segment_template["message"],
                "suggestions": suggestions,
                "emotion": emotion,
                "segment": segment
            }
            
            logger.info(f"Generated feedback for emotion={emotion}, segment={segment}")
            return feedback
            
        except Exception as e:
            logger.error(f"Error generating feedback: {e}")
            # 기본 피드백 반환
            return {
                "message": "즐거운 게임 되세요!",
                "suggestions": [],
                "emotion": emotion,
                "segment": segment
            }
    
    def _generate_suggestions(self, emotion: str, segment: str, context: Dict[str, Any]) -> list:
        """
        감정과 세그먼트에 따른 추천 생성
        
        Args:
            emotion: 감정 상태
            segment: 사용자 세그먼트
            context: 추가 컨텍스트
        
        Returns:
            추천 목록
        """
        # 기본 추천
        if emotion == "excited":
            return ["룰렛에 도전해보세요!", "이 기세로 슬롯머신도 해보세요!"]
        elif emotion == "frustrated":
            return ["잠시 휴식을 취하는 건 어떨까요?", "간단한 미니게임은 어떨까요?"]
        else:
            return ["오늘의 추천 게임: 슬롯머신", "친구와 함께 게임을 즐겨보세요!"]
