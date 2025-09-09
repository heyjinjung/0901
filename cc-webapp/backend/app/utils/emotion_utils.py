"""
감정 피드백 및 도파민 트리거 유틸리티
- 사용자 행동에 따른 감정적 피드백 생성
- 도파민 루프 최적화
- 중독성 점수 계산
"""

import random
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# 감정 상태별 피드백 메시지 매트릭스
EMOTION_MATRIX = {
    "EXCITEMENT": {
        "messages": [
            "🎉 대박! 놀라운 결과야!",
            "✨ 와! 정말 운이 좋네!",
            "🚀 환상적이야! 계속 해보자!",
            "💫 믿을 수 없어! 다시 한 번!",
            "🔥 열정이 불타오른다!"
        ],
        "animations": ["pulse", "bounce", "glow", "sparkle"],
        "colors": ["#FFD700", "#FF6B6B", "#4ECDC4", "#45B7D1"]
    },
    "DISAPPOINTMENT": {
        "messages": [
            "😔 아쉽지만 다음에는 더 좋을 거야!",
            "💪 포기하지 마! 운이 곧 올 거야!",
            "🎯 계속 도전해! 성공이 가까워!",
            "⭐ 이런 때가 있어야 더 큰 기쁨이!",
            "🌟 다음 기회를 노려보자!"
        ],
        "animations": ["shake", "fade", "gentle_bounce"],
        "colors": ["#95A5A6", "#BDC3C7", "#7F8C8D"]
    },
    "ANTICIPATION": {
        "messages": [
            "🎲 무엇이 나올까? 두근두근!",
            "⏰ 곧 놀라운 일이 일어날 거야!",
            "🔮 운명의 순간이 다가온다!",
            "⚡ 준비됐어? 시작해보자!",
            "🌈 기대해도 좋을 것 같은데?"
        ],
        "animations": ["heartbeat", "glow_pulse", "anticipation_shake"],
        "colors": ["#9B59B6", "#8E44AD", "#E67E22"]
    },
    "CELEBRATION": {
        "messages": [
            "🎊 축하해! 대단한 성과야!",
            "🏆 챔피언의 기분이야!",
            "🎈 파티 시간이다!",
            "🌟 별처럼 빛나고 있어!",
            "💎 진짜 보석을 찾았네!"
        ],
        "animations": ["celebration", "confetti", "golden_glow", "victory_dance"],
        "colors": ["#F39C12", "#E74C3C", "#2ECC71", "#3498DB"]
    },
    "ENCOURAGEMENT": {
        "messages": [
            "💪 힘내! 넌 할 수 있어!",
            "🚀 다음 도전을 준비해!",
            "⭐ 포기하지 않는 네가 멋져!",
            "🔥 열정을 잃지 마!",
            "💫 꿈을 향해 달려가자!"
        ],
        "animations": ["encourage_glow", "power_up", "motivational_pulse"],
        "colors": ["#2ECC71", "#27AE60", "#16A085"]
    }
}

def get_feedback_message(emotion: str, user_tier: str = "STANDARD", 
                        streak_count: int = 0) -> Dict[str, Any]:
    """
    감정 상태에 따른 피드백 메시지 생성
    
    Args:
        emotion: 감정 상태 (EXCITEMENT, DISAPPOINTMENT, etc.)
        user_tier: 사용자 등급 (메시지 차별화)
        streak_count: 연속 횟수 (메시지 강도 조절)
    
    Returns:
        피드백 메시지 정보
    """
    try:
        emotion_data = EMOTION_MATRIX.get(emotion.upper(), EMOTION_MATRIX["ENCOURAGEMENT"])
        
        # 사용자 등급에 따른 메시지 강화
        tier_bonus = {
            "VIP": " (VIP 특별 혜택!)",
            "PREMIUM": " (프리미엄 보너스!)",
            "STANDARD": ""
        }
        
        # 스트릭에 따른 메시지 강화
        streak_bonus = ""
        if streak_count > 10:
            streak_bonus = f" 🔥 {streak_count}연속!"
        elif streak_count > 5:
            streak_bonus = f" ⚡ {streak_count}연속!"
        
        message = random.choice(emotion_data["messages"])
        animation = random.choice(emotion_data["animations"])
        color = random.choice(emotion_data["colors"])
        
        return {
            "message": message + tier_bonus.get(user_tier, "") + streak_bonus,
            "animation": animation,
            "color": color,
            "emotion": emotion,
            "intensity": min(1.0 + (streak_count * 0.1), 3.0)  # 최대 3배 강도
        }
        
    except Exception as e:
        logger.error(f"Failed to get feedback message: {str(e)}")
        return {
            "message": "🎯 계속 도전해보자!",
            "animation": "gentle_bounce",
            "color": "#95A5A6",
            "emotion": "ENCOURAGEMENT",
            "intensity": 1.0
        }

def generate_dopamine_trigger(action_type: str, result: Dict[str, Any], 
                            user_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    도파민 트리거 생성 (중독성 강화)
    
    Args:
        action_type: 액션 타입 (SLOT_SPIN, GACHA_PULL 등)
        result: 액션 결과
        user_context: 사용자 컨텍스트 (등급, 스트릭 등)
    
    Returns:
        도파민 트리거 정보
    """
    try:
        trigger_data = {
            "trigger_type": "STANDARD",
            "intensity": 1.0,
            "duration": 2000,  # milliseconds
            "effects": [],
            "next_action_hint": None
        }
        
        # 결과에 따른 트리거 타입 결정
        if result.get("success", False):
            if result.get("rarity") == "LEGENDARY":
                trigger_data.update({
                    "trigger_type": "JACKPOT",
                    "intensity": 3.0,
                    "duration": 5000,
                    "effects": ["screen_flash", "celebration_sound", "particle_explosion"],
                    "next_action_hint": "🎰 지금이 기회! 한 번 더!"
                })
            elif result.get("rarity") == "EPIC":
                trigger_data.update({
                    "trigger_type": "BIG_WIN",
                    "intensity": 2.0,
                    "duration": 3000,
                    "effects": ["glow_effect", "victory_sound", "sparkle_animation"],
                    "next_action_hint": "✨ 운이 따르고 있어! 계속해!"
                })
            else:
                trigger_data.update({
                    "trigger_type": "SMALL_WIN",
                    "intensity": 1.5,
                    "duration": 2000,
                    "effects": ["gentle_glow", "success_sound"],
                    "next_action_hint": "🎯 좋아! 다시 한 번!"
                })
        else:
            # 실패시에도 긍정적 트리거 (계속 플레이 유도)
            near_miss = result.get("near_miss", False)
            if near_miss:
                trigger_data.update({
                    "trigger_type": "NEAR_MISS",
                    "intensity": 1.8,
                    "duration": 2500,
                    "effects": ["anticipation_glow", "tension_sound"],
                    "next_action_hint": "🔥 아쉬워! 다음엔 성공할 거야!"
                })
            else:
                trigger_data.update({
                    "trigger_type": "MISS",
                    "intensity": 0.8,
                    "duration": 1500,
                    "effects": ["fade_out"],
                    "next_action_hint": "💪 포기하지 마! 운이 곧 올 거야!"
                })
        
        # 사용자 컨텍스트에 따른 조정
        streak_count = user_context.get("streak_count", 0)
        if streak_count > 0:
            trigger_data["intensity"] *= (1 + min(streak_count * 0.1, 1.0))
        
        user_tier = user_context.get("tier", "STANDARD")
        if user_tier == "VIP":
            trigger_data["intensity"] *= 1.2
            trigger_data["effects"].append("vip_sparkle")
        
        return trigger_data
        
    except Exception as e:
        logger.error(f"Failed to generate dopamine trigger: {str(e)}")
        return {
            "trigger_type": "STANDARD",
            "intensity": 1.0,
            "duration": 2000,
            "effects": ["gentle_glow"],
            "next_action_hint": "🎮 계속 플레이해보자!"
        }

def calculate_addiction_score(user_actions: List[Dict[str, Any]], 
                            time_window_hours: int = 24) -> float:
    """
    사용자의 중독성 점수 계산 (책임감 있는 게이밍을 위한 모니터링)
    
    Args:
        user_actions: 사용자 액션 히스토리
        time_window_hours: 분석 시간 창 (시간)
    
    Returns:
        중독성 점수 (0.0-10.0, 높을수록 위험)
    """
    try:
        if not user_actions:
            return 0.0
        
        # 최근 시간 창 내의 액션만 분석
        cutoff_time = datetime.utcnow().timestamp() - (time_window_hours * 3600)
        recent_actions = [
            action for action in user_actions
            if action.get("timestamp", 0) > cutoff_time
        ]
        
        if not recent_actions:
            return 0.0
        
        # 여러 지표로 중독성 점수 계산
        score = 0.0
        
        # 1. 액션 빈도 (시간당 액션 수)
        action_frequency = len(recent_actions) / time_window_hours
        if action_frequency > 20:  # 시간당 20회 이상
            score += 3.0
        elif action_frequency > 10:
            score += 2.0
        elif action_frequency > 5:
            score += 1.0
        
        # 2. 연속 플레이 시간
        action_times = sorted([action.get("timestamp", 0) for action in recent_actions])
        max_session_duration = 0
        current_session_start = action_times[0] if action_times else 0
        
        for i in range(1, len(action_times)):
            time_gap = action_times[i] - action_times[i-1]
            if time_gap > 1800:  # 30분 이상 간격이면 새 세션
                session_duration = action_times[i-1] - current_session_start
                max_session_duration = max(max_session_duration, session_duration)
                current_session_start = action_times[i]
        
        # 마지막 세션 처리
        if action_times:
            last_session_duration = action_times[-1] - current_session_start
            max_session_duration = max(max_session_duration, last_session_duration)
        
        session_hours = max_session_duration / 3600
        if session_hours > 6:  # 6시간 이상 연속
            score += 4.0
        elif session_hours > 4:
            score += 3.0
        elif session_hours > 2:
            score += 2.0
        elif session_hours > 1:
            score += 1.0
        
        # 3. 실패 후 즉시 재시도 패턴
        immediate_retry_count = 0
        for i in range(1, len(recent_actions)):
            prev_action = recent_actions[i-1]
            curr_action = recent_actions[i]
            
            time_gap = curr_action.get("timestamp", 0) - prev_action.get("timestamp", 0)
            if (time_gap < 10 and  # 10초 이내
                not prev_action.get("success", False)):  # 이전 액션이 실패
                immediate_retry_count += 1
        
        retry_ratio = immediate_retry_count / len(recent_actions) if recent_actions else 0
        if retry_ratio > 0.7:  # 70% 이상이 즉시 재시도
            score += 2.0
        elif retry_ratio > 0.5:
            score += 1.0
        
        # 4. 지출 패턴 (실제 돈 사용)
        total_spent = sum(action.get("amount_spent", 0) for action in recent_actions)
        if total_spent > 100:  # 하루에 100달러 이상
            score += 1.0
        
        return min(score, 10.0)  # 최대 10점
        
    except Exception as e:
        logger.error(f"Failed to calculate addiction score: {str(e)}")
        return 0.0

def get_responsible_gaming_message(addiction_score: float) -> Optional[Dict[str, Any]]:
    """
    중독성 점수에 따른 책임감 있는 게이밍 메시지
    
    Args:
        addiction_score: 중독성 점수 (0.0-10.0)
    
    Returns:
        경고 메시지 정보 또는 None
    """
    try:
        if addiction_score < 5.0:
            return None  # 정상 범위
        
        if addiction_score >= 8.0:
            return {
                "level": "HIGH_RISK",
                "message": "⚠️ 잠깐! 휴식을 취하는 것은 어떨까요? 건강한 게이밍을 위해 잠시 쉬어가세요.",
                "suggestion": "30분 후에 다시 오시는 건 어떨까요?",
                "color": "#E74C3C",
                "mandatory_break": True,
                "break_duration": 1800  # 30분
            }
        elif addiction_score >= 6.0:
            return {
                "level": "MEDIUM_RISK",
                "message": "💡 오늘 정말 열심히 하셨네요! 잠깐 휴식하면서 물 한 잔 드시는 건 어떨까요?",
                "suggestion": "10분 정도 휴식을 권장합니다.",
                "color": "#F39C12",
                "mandatory_break": False,
                "break_duration": 600  # 10분
            }
        else:  # 5.0-6.0
            return {
                "level": "LOW_RISK",
                "message": "🌟 재미있게 즐기고 계시는군요! 적당한 휴식도 잊지 마세요.",
                "suggestion": "건강한 게이밍을 계속 유지해보세요!",
                "color": "#3498DB",
                "mandatory_break": False,
                "break_duration": 0
            }
        
    except Exception as e:
        logger.error(f"Failed to get responsible gaming message: {str(e)}")
        return None

def create_achievement_feedback(achievement: Dict[str, Any], 
                              user_tier: str = "STANDARD") -> Dict[str, Any]:
    """
    업적 달성시 특별한 피드백 생성
    
    Args:
        achievement: 업적 정보
        user_tier: 사용자 등급
    
    Returns:
        업적 피드백 정보
    """
    try:
        achievement_type = achievement.get("type", "GENERAL")
        rarity = achievement.get("rarity", "COMMON")
        
        # 업적 타입별 메시지
        messages = {
            "FIRST_WIN": "🏆 첫 승리를 축하합니다!",
            "STREAK_MASTER": f"🔥 {achievement.get('count', 1)}연승 달성!",
            "BIG_SPENDER": "💎 VIP 고객님을 환영합니다!",
            "LUCKY_STAR": "⭐ 운의 별이 당신을 비추고 있어요!",
            "COLLECTOR": "📚 수집가의 면모를 보여주셨네요!",
            "GENERAL": "🎉 새로운 업적을 달성했습니다!"
        }
        
        # 희귀도별 효과
        effects = {
            "COMMON": ["gentle_glow", "success_sound"],
            "RARE": ["blue_sparkle", "achievement_chime", "glow_pulse"],
            "EPIC": ["purple_explosion", "epic_fanfare", "screen_shake"],
            "LEGENDARY": ["golden_fireworks", "legendary_anthem", "screen_flash", "confetti_rain"]
        }
        
        return {
            "message": messages.get(achievement_type, messages["GENERAL"]),
            "title": achievement.get("title", "업적 달성!"),
            "description": achievement.get("description", "새로운 업적을 달성했습니다!"),
            "effects": effects.get(rarity, effects["COMMON"]),
            "points_awarded": achievement.get("points", 100),
            "tier_bonus": user_tier == "VIP",
            "display_duration": 5000 if rarity in ["EPIC", "LEGENDARY"] else 3000
        }
        
    except Exception as e:
        logger.error(f"Failed to create achievement feedback: {str(e)}")
        return {
            "message": "🎉 업적 달성!",
            "title": "축하합니다!",
            "description": "새로운 업적을 달성했습니다!",
            "effects": ["gentle_glow"],
            "points_awarded": 100,
            "tier_bonus": False,
            "display_duration": 3000
        }