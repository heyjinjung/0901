"""
🎰 Casino-Club F2P - 통합 유틸리티 시스템 (Unified Utilities System)
=============================================================================
✅ 게임 확률 계산 (가챠, 스트릭 보너스, 가중 랜덤)
✅ 리워드 처리 (변동 비율 보상, 도파민 트리거)
✅ 감정 피드백 (사용자 상호작용 피드백)
✅ Redis 헬퍼 (캐싱, 세션 관리)
✅ 세그멘테이션 (RFM 분석, 사용자 분류)
✅ 웹훅 및 외부 API 처리

🔧 Features:
- 심리학 기반 게임 확률 알고리즘
- 도파민 루프 최적화 시스템
- 실시간 데이터 캐싱 (Redis + 메모리 fallback)
- 사용자 행동 기반 세그멘테이션
- 외부 API 연동 및 웹훅 처리

🔄 Previous Files Archived:
- emotion_utils.py → archive/emotion_utils.py.bak
- probability.py → archive/probability.py.bak
- redis.py → archive/redis.py.bak
- reward_utils.py → archive/reward_utils.py.bak
- segment_utils.py → archive/segment_utils.py.bak
- webhook.py → archive/webhook.py.bak
"""

import json
import random
import hashlib
import secrets
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
import math

logger = logging.getLogger("unified_utils")

# ===== 확률 계산 유틸리티 =====
class ProbabilityUtils:
    """게임 확률 계산 및 랜덤 시스템"""
    
    @staticmethod
    def calculate_gacha_probability(base_rate: float, pity_count: int, max_pity: int = 90) -> float:
        """
        가챠 확률 계산 (천장 시스템 포함)
        
        Args:
            base_rate: 기본 확률 (0.0-1.0)
            pity_count: 현재 뽑기 실패 횟수
            max_pity: 천장 횟수
        
        Returns:
            최종 확률
        """
        if pity_count >= max_pity:
            return 1.0  # 천장 도달
        
        # 천장 근처에서 확률 상승
        pity_multiplier = 1.0 + (pity_count / max_pity) * 2.0
        final_rate = min(base_rate * pity_multiplier, 0.9)  # 최대 90%
        
        return final_rate
    
    @staticmethod
    def calculate_streak_bonus(streak_count: int, max_bonus: float = 2.0) -> float:
        """
        연속 성공에 따른 보너스 배율 계산
        
        Args:
            streak_count: 연속 성공 횟수
            max_bonus: 최대 보너스 배율
        
        Returns:
            보너스 배율
        """
        if streak_count <= 0:
            return 1.0
        
        # 로그 스케일 보너스 (급격한 상승 방지)
        bonus = 1.0 + (math.log(streak_count + 1) / 5.0)
        return min(bonus, max_bonus)
    
    @staticmethod
    def weighted_random_choice(items: List[Dict[str, Any]], weight_key: str = 'weight') -> Optional[Dict[str, Any]]:
        """
        가중치 기반 랜덤 선택
        
        Args:
            items: 선택할 아이템 리스트 (각 아이템은 weight_key를 포함해야 함)
            weight_key: 가중치 키 이름
        
        Returns:
            선택된 아이템
        """
        if not items:
            return None
        
        total_weight = sum(item.get(weight_key, 1) for item in items)
        if total_weight <= 0:
            return random.choice(items)
        
        pick = random.uniform(0, total_weight)
        current = 0
        
        for item in items:
            current += item.get(weight_key, 1)
            if current >= pick:
                return item
        
        return items[-1]  # fallback
    
    @staticmethod
    def variable_ratio_reward(action_count: int, avg_ratio: int = 5, variance: float = 0.3) -> bool:
        """
        가변 비율 보상 스케줄 (도박성 강화)
        
        Args:
            action_count: 현재 행동 횟수
            avg_ratio: 평균 보상 비율
            variance: 변동성 (0.0-1.0)
        
        Returns:
            보상 여부
        """
        # 기본 확률
        base_prob = 1.0 / avg_ratio
        
        # 변동성 적용
        variance_factor = 1.0 + random.uniform(-variance, variance)
        final_prob = base_prob * variance_factor
        
        # 연속 실패시 보상 확률 증가 (심리적 보상)
        if action_count > avg_ratio * 2:
            final_prob *= 1.5
        
        return random.random() < final_prob


# ===== 리워드 처리 유틸리티 =====
class RewardUtils:
    """리워드 처리 및 도파민 트리거"""
    
    @staticmethod
    def process_reward(
        user_id: int,
        reward_type: str,
        amount: int,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        리워드 처리 및 감정적 피드백 생성
        
        Args:
            user_id: 사용자 ID
            reward_type: 리워드 타입 (cyber_tokens, items, exp 등)
            amount: 리워드 양
            context: 추가 컨텍스트
        
        Returns:
            처리 결과 및 피드백
        """
        try:
            # 리워드 크기에 따른 감정적 반응 생성
            if amount >= 1000:
                emotion = "MEGA_WIN"
                intensity = "extreme"
            elif amount >= 500:
                emotion = "BIG_WIN" 
                intensity = "high"
            elif amount >= 100:
                emotion = "GOOD_WIN"
                intensity = "medium"
            else:
                emotion = "SMALL_WIN"
                intensity = "low"
            
            # 감정적 피드백 생성
            feedback = EmotionUtils.generate_feedback(emotion, intensity)
            
            result = {
                "user_id": user_id,
                "reward_type": reward_type,
                "amount": amount,
                "emotion": emotion,
                "feedback": feedback,
                "timestamp": datetime.utcnow().isoformat(),
                "context": context or {}
            }
            
            logger.info(f"Reward processed: {user_id} received {amount} {reward_type} ({emotion})")
            return result
            
        except Exception as e:
            logger.error(f"Failed to process reward: {str(e)}")
            return {
                "user_id": user_id,
                "reward_type": reward_type,
                "amount": amount,
                "error": str(e)
            }


# ===== 감정 피드백 유틸리티 =====
class EmotionUtils:
    """감정 피드백 및 도파민 트리거"""
    
    # 감정 상태별 피드백 메시지
    EMOTION_RESPONSES = {
        "MEGA_WIN": {
            "messages": [
                "🎉 JACKPOT! 대박 터졌다!",
                "💎 전설급 운이야! 믿을 수 없어!",
                "🚀 우주급 행운! 다시 한 번!",
                "⭐ 신급 결과! 계속 가자!"
            ],
            "colors": ["#FFD700", "#FF1493", "#00CED1"],
            "effects": ["explosion", "fireworks", "rainbow"]
        },
        "BIG_WIN": {
            "messages": [
                "🔥 대박! 엄청난 결과야!",
                "✨ 와! 정말 운이 좋네!",
                "💫 환상적이야! 계속해보자!",
                "🎊 놀라운 행운이야!"
            ],
            "colors": ["#FF6B6B", "#4ECDC4", "#45B7D1"],
            "effects": ["bounce", "glow", "sparkle"]
        },
        "GOOD_WIN": {
            "messages": [
                "👍 좋아! 꽤 괜찮은 결과야!",
                "🎯 적중! 운이 따르네!",
                "⚡ 번쩍! 좋은 흐름이야!",
                "🌟 빛나는 결과!"
            ],
            "colors": ["#98D8C8", "#F7DC6F", "#BB8FCE"],
            "effects": ["pulse", "shine"]
        },
        "SMALL_WIN": {
            "messages": [
                "😊 작지만 소중한 보상!",
                "🍀 운이 조금씩 쌓이고 있어!",
                "📈 꾸준히 좋아지고 있어!",
                "🎈 작은 기쁨도 소중해!"
            ],
            "colors": ["#85C1E9", "#F8C471", "#D5A6BD"],
            "effects": ["gentle_pulse"]
        },
        "NEAR_MISS": {
            "messages": [
                "😅 아쉬워! 거의 다 왔는데!",
                "🤏 조금만 더! 다음엔 분명히!",
                "⏳ 운이 쌓이고 있어! 계속해!",
                "🎯 타이밍이 아쉬웠어!"
            ],
            "colors": ["#F39C12", "#E67E22"],
            "effects": ["shake", "fade"]
        }
    }
    
    @staticmethod
    def generate_feedback(emotion: str, intensity: str = "medium") -> Dict[str, Any]:
        """
        감정 상태에 따른 피드백 생성
        
        Args:
            emotion: 감정 타입
            intensity: 강도 (low, medium, high, extreme)
        
        Returns:
            피드백 데이터
        """
        response_data = EmotionUtils.EMOTION_RESPONSES.get(emotion, EmotionUtils.EMOTION_RESPONSES["SMALL_WIN"])
        
        return {
            "message": random.choice(response_data["messages"]),
            "color": random.choice(response_data["colors"]),
            "effect": random.choice(response_data["effects"]),
            "intensity": intensity,
            "emotion": emotion,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def calculate_addiction_score(
        session_duration: int,
        actions_per_minute: float,
        spending_amount: int,
        consecutive_days: int
    ) -> Dict[str, Any]:
        """
        중독성 점수 계산 (건전한 게임 환경을 위해)
        
        Args:
            session_duration: 세션 시간 (분)
            actions_per_minute: 분당 액션 수
            spending_amount: 지출 금액
            consecutive_days: 연속 접속 일수
        
        Returns:
            중독성 분석 결과
        """
        # 기본 점수 계산
        duration_score = min(session_duration / 60, 10)  # 최대 10점
        intensity_score = min(actions_per_minute, 10)    # 최대 10점
        spending_score = min(spending_amount / 10000, 10) # 최대 10점
        consistency_score = min(consecutive_days / 30, 10) # 최대 10점
        
        total_score = (duration_score + intensity_score + spending_score + consistency_score) / 4
        
        # 위험도 분류
        if total_score >= 8:
            risk_level = "HIGH"
            recommendation = "휴식을 권장합니다. 건전한 게임 환경을 유지해주세요."
        elif total_score >= 6:
            risk_level = "MEDIUM"
            recommendation = "적절한 휴식과 함께 즐겨주세요."
        elif total_score >= 4:
            risk_level = "LOW"
            recommendation = "건전한 게임 패턴을 유지하고 있습니다."
        else:
            risk_level = "MINIMAL"
            recommendation = "매우 건전한 게임 이용 패턴입니다."
        
        return {
            "total_score": total_score,
            "risk_level": risk_level,
            "recommendation": recommendation,
            "breakdown": {
                "session_duration": duration_score,
                "action_intensity": intensity_score,
                "spending": spending_score,
                "consistency": consistency_score
            }
        }


# ===== Redis 유틸리티 =====
class RedisUtils:
    """Redis 캐싱 및 세션 관리"""
    
    @staticmethod
    def get_redis_client():
        """Redis 클라이언트 가져오기 (연결 실패시 None 반환)"""
        try:
            import redis
            client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)
            client.ping()  # 연결 테스트
            return client
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            return None
    
    @staticmethod
    def cache_user_data(user_id: int, data: Dict[str, Any], expire_seconds: int = 3600) -> bool:
        """사용자 데이터 캐싱"""
        try:
            client = RedisUtils.get_redis_client()
            if client:
                key = f"user_cache:{user_id}"
                client.setex(key, expire_seconds, json.dumps(data))
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to cache user data: {e}")
            return False
    
    @staticmethod
    def get_cached_user_data(user_id: int) -> Optional[Dict[str, Any]]:
        """캐시된 사용자 데이터 가져오기"""
        try:
            client = RedisUtils.get_redis_client()
            if client:
                key = f"user_cache:{user_id}"
                data = client.get(key)
                if data:
                    return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Failed to get cached user data: {e}")
            return None
    
    @staticmethod
    def increment_counter(key: str, expire_seconds: int = 3600) -> int:
        """카운터 증가 (스트릭, 액션 카운트 등)"""
        try:
            client = RedisUtils.get_redis_client()
            if client:
                pipe = client.pipeline()
                pipe.incr(key)
                pipe.expire(key, expire_seconds)
                results = pipe.execute()
                return results[0]
            return 1  # fallback
        except Exception as e:
            logger.error(f"Failed to increment counter: {e}")
            return 1


# ===== 세그멘테이션 유틸리티 =====
class SegmentUtils:
    """사용자 세그멘테이션 및 RFM 분석"""
    
    @staticmethod
    def calculate_rfm_score(
        recency_days: int,
        frequency_count: int,
        monetary_amount: int
    ) -> Dict[str, Any]:
        """
        RFM 점수 계산
        
        Args:
            recency_days: 최근 접속일 (일)
            frequency_count: 접속 빈도
            monetary_amount: 지출 금액
        
        Returns:
            RFM 분석 결과
        """
        # R (Recency) 점수 - 최근성 (1-5점)
        if recency_days <= 1:
            r_score = 5
        elif recency_days <= 3:
            r_score = 4
        elif recency_days <= 7:
            r_score = 3
        elif recency_days <= 14:
            r_score = 2
        else:
            r_score = 1
        
        # F (Frequency) 점수 - 빈도 (1-5점)
        if frequency_count >= 30:
            f_score = 5
        elif frequency_count >= 20:
            f_score = 4
        elif frequency_count >= 10:
            f_score = 3
        elif frequency_count >= 5:
            f_score = 2
        else:
            f_score = 1
        
        # M (Monetary) 점수 - 금액 (1-5점)
        if monetary_amount >= 100000:
            m_score = 5
        elif monetary_amount >= 50000:
            m_score = 4
        elif monetary_amount >= 20000:
            m_score = 3
        elif monetary_amount >= 5000:
            m_score = 2
        else:
            m_score = 1
        
        # 전체 점수 및 세그먼트 결정
        total_score = r_score + f_score + m_score
        
        if total_score >= 13:
            segment = "CHAMPIONS"
            tier = "VIP"
        elif total_score >= 10:
            segment = "LOYAL_CUSTOMERS"
            tier = "PREMIUM"
        elif total_score >= 7:
            segment = "POTENTIAL_LOYALISTS"
            tier = "STANDARD"
        elif total_score >= 5:
            segment = "NEW_CUSTOMERS"
            tier = "STANDARD"
        else:
            segment = "AT_RISK"
            tier = "STANDARD"
        
        return {
            "rfm_score": total_score,
            "r_score": r_score,
            "f_score": f_score,
            "m_score": m_score,
            "segment": segment,
            "tier": tier,
            "calculated_at": datetime.utcnow().isoformat()
        }


# ===== 웹훅 유틸리티 =====
class WebhookUtils:
    """웹훅 및 외부 API 처리"""
    
    @staticmethod
    def send_webhook(url: str, data: Dict[str, Any], headers: Dict[str, str] = None) -> bool:
        """
        웹훅 전송
        
        Args:
            url: 웹훅 URL
            data: 전송할 데이터
            headers: 추가 헤더
        
        Returns:
            전송 성공 여부
        """
        try:
            import requests
            
            default_headers = {
                "Content-Type": "application/json",
                "User-Agent": "Casino-Club-Webhook/1.0"
            }
            
            if headers:
                default_headers.update(headers)
            
            response = requests.post(
                url,
                json=data,
                headers=default_headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Webhook sent successfully to {url}")
                return True
            else:
                logger.warning(f"Webhook failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send webhook: {e}")
            return False
    
    @staticmethod
    def generate_webhook_signature(payload: str, secret: str) -> str:
        """웹훅 서명 생성 (보안)"""
        import hmac
        
        signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return f"sha256={signature}"


# ===== 전역 헬퍼 함수 =====
def generate_unique_id(prefix: str = "") -> str:
    """고유 ID 생성"""
    timestamp = int(datetime.utcnow().timestamp() * 1000)
    random_part = secrets.token_hex(4)
    return f"{prefix}{timestamp}_{random_part}" if prefix else f"{timestamp}_{random_part}"

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """안전한 나눗셈 (0으로 나누기 방지)"""
    try:
        if denominator == 0:
            return default
        return numerator / denominator
    except (TypeError, ZeroDivisionError):
        return default

def clamp(value: float, min_value: float, max_value: float) -> float:
    """값을 범위 내로 제한"""
    return max(min_value, min(value, max_value))

def format_currency(amount: int, currency: str = "토큰") -> str:
    """통화 포맷팅"""
    if amount >= 1000000:
        return f"{amount/1000000:.1f}M {currency}"
    elif amount >= 1000:
        return f"{amount/1000:.1f}K {currency}"
    else:
        return f"{amount:,} {currency}"


# ===== __all__ 정의 =====
__all__ = [
    "ProbabilityUtils",
    "RewardUtils", 
    "EmotionUtils",
    "RedisUtils",
    "SegmentUtils",
    "WebhookUtils",
    "generate_unique_id",
    "safe_divide",
    "clamp",
    "format_currency"
]
