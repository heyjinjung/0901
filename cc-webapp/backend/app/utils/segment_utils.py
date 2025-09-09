"""
사용자 세그멘테이션 유틸리티
- RFM (Recency, Frequency, Monetary) 분석
- 사용자 등급 업데이트
- 개인화된 오퍼 생성
"""

import math
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

# RFM 세그먼트 정의
RFM_SEGMENTS = {
    "WHALE": {"min_score": 9, "description": "고액 결제 VIP 고객"},
    "HIGH_ENGAGED": {"min_score": 7, "description": "높은 참여도 우수 고객"}, 
    "MEDIUM": {"min_score": 5, "description": "일반 활성 사용자"},
    "LOW": {"min_score": 3, "description": "저활성 사용자"},
    "AT_RISK": {"min_score": 0, "description": "이탈 위험 사용자"}
}

def calculate_rfm_score(user_id: str, db: Session, 
                       analysis_period_days: int = 30) -> Dict[str, Any]:
    """
    사용자의 RFM 점수 계산
    
    Args:
        user_id: 사용자 ID
        db: 데이터베이스 세션
        analysis_period_days: 분석 기간 (일)
    
    Returns:
        RFM 점수 및 세그먼트 정보
    """
    try:
        # 임시로 더미 데이터 계산 (실제 구현시 DB 쿼리로 교체)
        cutoff_date = datetime.utcnow() - timedelta(days=analysis_period_days)
        
        # R (Recency): 최근 활동일로부터 지난 일수
        # 실제 구현: SELECT MAX(created_at) FROM user_actions WHERE user_id = ?
        last_activity_days = 1  # 임시값
        recency_score = _calculate_recency_score(last_activity_days)
        
        # F (Frequency): 분석 기간 내 활동 빈도
        # 실제 구현: SELECT COUNT(*) FROM user_actions WHERE user_id = ? AND created_at > ?
        activity_count = 15  # 임시값
        frequency_score = _calculate_frequency_score(activity_count, analysis_period_days)
        
        # M (Monetary): 분석 기간 내 지출 금액
        # 실제 구현: SELECT SUM(amount) FROM shop_transactions WHERE user_id = ? AND created_at > ?
        total_spent = 50.0  # 임시값
        monetary_score = _calculate_monetary_score(total_spent)
        
        # 종합 RFM 점수
        rfm_score = (recency_score + frequency_score + monetary_score) / 3
        
        # 세그먼트 결정
        segment = _determine_segment(rfm_score)
        
        return {
            "user_id": user_id,
            "recency_score": recency_score,
            "frequency_score": frequency_score,
            "monetary_score": monetary_score,
            "rfm_score": rfm_score,
            "segment": segment,
            "last_activity_days": last_activity_days,
            "activity_count": activity_count,
            "total_spent": total_spent,
            "analysis_date": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to calculate RFM score: {str(e)}")
        return {
            "user_id": user_id,
            "rfm_score": 5.0,
            "segment": "MEDIUM",
            "error": str(e)
        }

def _calculate_recency_score(days_since_last_activity: int) -> float:
    """최근성 점수 계산 (1-10)"""
    if days_since_last_activity <= 1:
        return 10.0
    elif days_since_last_activity <= 7:
        return 8.0
    elif days_since_last_activity <= 14:
        return 6.0
    elif days_since_last_activity <= 30:
        return 4.0
    elif days_since_last_activity <= 60:
        return 2.0
    else:
        return 1.0

def _calculate_frequency_score(activity_count: int, period_days: int) -> float:
    """빈도 점수 계산 (1-10)"""
    daily_average = activity_count / period_days
    
    if daily_average >= 5:
        return 10.0
    elif daily_average >= 3:
        return 8.0
    elif daily_average >= 1:
        return 6.0
    elif daily_average >= 0.5:
        return 4.0
    elif daily_average >= 0.2:
        return 2.0
    else:
        return 1.0

def _calculate_monetary_score(total_spent: float) -> float:
    """결제 점수 계산 (1-10)"""
    if total_spent >= 200:
        return 10.0
    elif total_spent >= 100:
        return 8.0
    elif total_spent >= 50:
        return 6.0
    elif total_spent >= 20:
        return 4.0
    elif total_spent >= 5:
        return 2.0
    else:
        return 1.0

def _determine_segment(rfm_score: float) -> str:
    """RFM 점수로 세그먼트 결정"""
    for segment, info in RFM_SEGMENTS.items():
        if rfm_score >= info["min_score"]:
            return segment
    return "AT_RISK"

def update_user_segment(user_id: str, db: Session) -> bool:
    """
    사용자 세그먼트 업데이트 (DB에 저장)
    
    Args:
        user_id: 사용자 ID
        db: 데이터베이스 세션
    
    Returns:
        업데이트 성공 여부
    """
    try:
        # RFM 점수 계산
        rfm_data = calculate_rfm_score(user_id, db)
        
        # 실제 구현시 DB 업데이트
        # UPDATE user_segments SET 
        #   rfm_group = ?, ltv_score = ?, last_updated = ?
        # WHERE user_id = ?
        
        logger.info(f"Updated segment for user {user_id}: {rfm_data['segment']}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to update user segment: {str(e)}")
        return False

def get_personalized_offers(user_id: str, segment: str, 
                          user_context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    세그먼트별 개인화된 오퍼 생성
    
    Args:
        user_id: 사용자 ID
        segment: 사용자 세그먼트
        user_context: 사용자 컨텍스트 (등급, 활동 이력 등)
    
    Returns:
        개인화된 오퍼 리스트
    """
    try:
        offers = []
        
        # 세그먼트별 오퍼 전략
        if segment == "WHALE":
            offers.extend([
                {
                    "type": "EXCLUSIVE_PACKAGE",
                    "title": "💎 VIP 전용 프리미엄 패키지",
                    "description": "오직 VIP만을 위한 특별한 혜택",
                    "original_price": 99.99,
                    "discounted_price": 79.99,
                    "discount_percentage": 20,
                    "items": ["레어 젬 10000개", "프리미엄 스킨 5개", "VIP 전용 아바타"],
                    "urgency": "24시간 한정",
                    "rarity": "LEGENDARY"
                },
                {
                    "type": "LOYALTY_BONUS",
                    "title": "🏆 충성 고객 보너스",
                    "description": "항상 이용해주셔서 감사합니다",
                    "bonus_gems": 5000,
                    "bonus_points": 10000,
                    "special_access": "베타 기능 우선 접근",
                    "rarity": "EPIC"
                }
            ])
            
        elif segment == "HIGH_ENGAGED":
            offers.extend([
                {
                    "type": "ENGAGEMENT_REWARD",
                    "title": "⚡ 열정적인 플레이어 보상",
                    "description": "활발한 활동에 대한 특별 보상",
                    "original_price": 29.99,
                    "discounted_price": 19.99,
                    "discount_percentage": 33,
                    "items": ["젬 3000개", "스페셜 부스터 10개"],
                    "urgency": "이번 주 한정",
                    "rarity": "RARE"
                },
                {
                    "type": "STREAK_BONUS",
                    "title": "🔥 연속 플레이 보너스",
                    "description": "꾸준한 플레이에 대한 보상",
                    "bonus_multiplier": 1.5,
                    "duration_hours": 24,
                    "rarity": "EPIC"
                }
            ])
            
        elif segment == "MEDIUM":
            offers.extend([
                {
                    "type": "STARTER_PACK",
                    "title": "🎮 게이머 응원 패키지",
                    "description": "더 즐거운 게임을 위한 도움",
                    "original_price": 14.99,
                    "discounted_price": 9.99,
                    "discount_percentage": 33,
                    "items": ["젬 1500개", "부스터 5개"],
                    "urgency": "72시간 한정",
                    "rarity": "COMMON"
                }
            ])
            
        elif segment in ["LOW", "AT_RISK"]:
            offers.extend([
                {
                    "type": "COMEBACK_OFFER",
                    "title": "🌟 컴백 웰컴 패키지",
                    "description": "다시 돌아온 당신을 환영합니다!",
                    "original_price": 9.99,
                    "discounted_price": 4.99,
                    "discount_percentage": 50,
                    "items": ["젬 1000개", "무료 스핀 10회"],
                    "urgency": "지금만 특가",
                    "rarity": "RARE"
                },
                {
                    "type": "FREE_BONUS",
                    "title": "🎁 무료 선물",
                    "description": "다시 시작하는 당신에게",
                    "bonus_gems": 500,
                    "bonus_points": 1000,
                    "free_spins": 5,
                    "rarity": "COMMON"
                }
            ])
        
        # 사용자 컨텍스트에 따른 추가 개인화
        current_gems = user_context.get("gems", 0)
        if current_gems < 100:  # 젬이 부족한 경우
            offers.append({
                "type": "GEMS_REFILL",
                "title": "💎 젬 충전 특가",
                "description": "지금 젬을 충전하고 보너스까지!",
                "gems_amount": 2000,
                "bonus_percentage": 30,
                "price": 4.99,
                "urgency": "재고 한정",
                "rarity": "COMMON"
            })
        
        # 최대 3개 오퍼로 제한 (선택의 패러독스 방지)
        return offers[:3]
        
    except Exception as e:
        logger.error(f"Failed to get personalized offers: {str(e)}")
        return []

# 기존 RFM 서비스와 호환성을 위한 함수
def compute_rfm_and_update_segments(db: Session):
    """
    Initializes RFMService and runs the segment update process for all users.
    This function is called by the APScheduler job.
    """
    try:
        # 실제 구현: RFMService를 호출하여 모든 사용자 세그먼트 갱신
        from app.services.rfm_service import RFMService
        start_ts = datetime.utcnow()
        logger.info("Starting RFM segment update job…")
        svc = RFMService(db=db)
        svc.update_all_user_segments()
        dur_ms = int((datetime.utcnow() - start_ts).total_seconds() * 1000)
        logger.info("RFM segment update job finished in %d ms", dur_ms)
    except Exception as e:
        logger.error(f"An error occurred during the RFM update job: {e}", exc_info=True)
        pass
