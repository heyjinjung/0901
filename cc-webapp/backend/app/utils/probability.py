"""
확률 계산 유틸리티
- 가챠 시스템 확률 계산
- 스트릭 보너스 계산
- 가중 랜덤 선택
- 변수비율 강화 보상
"""

import random
import math
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def calculate_gacha_probability(base_probability: float, streak_count: int = 0, 
                               pity_system: bool = True, max_pity: int = 100) -> float:
    """
    가챠 확률 계산 (스트릭 보너스 + 동정 시스템)
    
    Args:
        base_probability: 기본 확률 (0.0-1.0)
        streak_count: 연속 실패 횟수
        pity_system: 동정 시스템 활성화 여부
        max_pity: 최대 동정 카운트
    
    Returns:
        최종 확률 (0.0-1.0)
    """
    try:
        final_probability = base_probability
        
        # 스트릭 보너스 (매 실패마다 0.1% 증가)
        if streak_count > 0:
            streak_bonus = min(streak_count * 0.001, 0.1)  # 최대 10% 보너스
            final_probability += streak_bonus
        
        # 동정 시스템 (최대 카운트에 가까워질수록 확률 급증)
        if pity_system and streak_count > max_pity * 0.7:  # 70% 지점부터 급증
            pity_bonus = ((streak_count - max_pity * 0.7) / (max_pity * 0.3)) * 0.5
            final_probability += pity_bonus
            
        # 100% 보장 (최대 동정)
        if pity_system and streak_count >= max_pity:
            final_probability = 1.0
        
        return min(final_probability, 1.0)
        
    except Exception as e:
        logger.error(f"Failed to calculate gacha probability: {str(e)}")
        return base_probability

def calculate_streak_bonus(streak_count: int, multiplier: float = 1.1, 
                          max_multiplier: float = 3.0) -> float:
    """
    스트릭 보너스 배수 계산
    
    Args:
        streak_count: 연속 성공 횟수
        multiplier: 기본 배수 (매 스트릭마다 적용)
        max_multiplier: 최대 배수 제한
    
    Returns:
        보너스 배수
    """
    try:
        if streak_count <= 0:
            return 1.0
        
        # 로그 함수로 점진적 증가 (급격한 증가 방지)
        bonus = 1.0 + (math.log(streak_count + 1) * (multiplier - 1.0))
        return min(bonus, max_multiplier)
        
    except Exception as e:
        logger.error(f"Failed to calculate streak bonus: {str(e)}")
        return 1.0

def weighted_random_choice(items: List[Dict[str, Any]], weight_key: str = "weight") -> Optional[Dict[str, Any]]:
    """
    가중치 기반 랜덤 선택
    
    Args:
        items: 선택할 아이템 리스트 (각 아이템은 weight_key를 가져야 함)
        weight_key: 가중치 키 이름
    
    Returns:
        선택된 아이템 또는 None
    """
    try:
        if not items:
            return None
        
        # 총 가중치 계산
        total_weight = sum(item.get(weight_key, 0) for item in items)
        if total_weight <= 0:
            return random.choice(items)  # 가중치가 없으면 균등 선택
        
        # 랜덤 값 생성
        random_value = random.uniform(0, total_weight)
        
        # 가중치에 따라 선택
        current_weight = 0
        for item in items:
            current_weight += item.get(weight_key, 0)
            if random_value <= current_weight:
                return item
        
        # 예외 상황 (부동소수점 오차 등)
        return items[-1]
        
    except Exception as e:
        logger.error(f"Failed to make weighted random choice: {str(e)}")
        return random.choice(items) if items else None

def variable_ratio_reward(action_count: int, base_ratio: int = 5, 
                         variance: float = 0.3) -> bool:
    """
    변수비율 강화 보상 시스템 (도파민 루프 최적화)
    
    Args:
        action_count: 현재 액션 수행 횟수
        base_ratio: 기본 보상 비율 (평균적으로 N회당 1회 보상)
        variance: 변동성 (0.0-1.0, 높을수록 예측 불가능)
    
    Returns:
        보상 지급 여부
    """
    try:
        # 변수비율 계산 (정규분포 기반)
        actual_ratio = max(1, int(random.normalvariate(base_ratio, base_ratio * variance)))
        
        # 보상 확률 계산 (액션 수가 비율에 가까워질수록 확률 증가)
        if action_count <= 0:
            return False
        
        # 기본 확률: 1/actual_ratio
        base_chance = 1.0 / actual_ratio
        
        # 액션 수에 따른 확률 증가 (변수비율의 핵심)
        progress_multiplier = min(action_count / actual_ratio, 2.0)  # 최대 2배
        final_chance = base_chance * progress_multiplier
        
        return random.random() < final_chance
        
    except Exception as e:
        logger.error(f"Failed to calculate variable ratio reward: {str(e)}")
        return False

def calculate_drop_rates(user_tier: str, item_rarity: str) -> Dict[str, float]:
    """
    사용자 등급과 아이템 희귀도에 따른 드롭률 계산
    
    Args:
        user_tier: 사용자 등급 (STANDARD, PREMIUM, VIP)
        item_rarity: 아이템 희귀도 (COMMON, RARE, EPIC, LEGENDARY)
    
    Returns:
        등급별 드롭률 정보
    """
    try:
        # 기본 드롭률 설정
        base_rates = {
            "COMMON": 0.50,     # 50%
            "RARE": 0.30,       # 30%
            "EPIC": 0.15,       # 15%
            "LEGENDARY": 0.05   # 5%
        }
        
        # 사용자 등급별 보너스
        tier_bonuses = {
            "STANDARD": {"COMMON": 1.0, "RARE": 1.0, "EPIC": 1.0, "LEGENDARY": 1.0},
            "PREMIUM": {"COMMON": 1.0, "RARE": 1.2, "EPIC": 1.3, "LEGENDARY": 1.5},
            "VIP": {"COMMON": 1.0, "RARE": 1.5, "EPIC": 1.8, "LEGENDARY": 2.0}
        }
        
        # 최종 드롭률 계산
        final_rates = {}
        for rarity, base_rate in base_rates.items():
            bonus = tier_bonuses.get(user_tier, tier_bonuses["STANDARD"]).get(rarity, 1.0)
            final_rates[rarity] = min(base_rate * bonus, 0.95)  # 최대 95% 제한
        
        # 확률 정규화 (총합이 1.0이 되도록)
        total = sum(final_rates.values())
        if total > 1.0:
            for rarity in final_rates:
                final_rates[rarity] /= total
        
        return final_rates
        
    except Exception as e:
        logger.error(f"Failed to calculate drop rates: {str(e)}")
        return base_rates

def simulate_gacha_pull(tier: str = "STANDARD", pull_count: int = 1, 
                       streak_count: int = 0) -> List[Dict[str, Any]]:
    """
    가챠 뽑기 시뮬레이션
    
    Args:
        tier: 사용자 등급
        pull_count: 뽑기 횟수
        streak_count: 연속 실패 횟수
    
    Returns:
        뽑기 결과 리스트
    """
    try:
        results = []
        current_streak = streak_count
        
        for i in range(pull_count):
            # 드롭률 계산
            drop_rates = calculate_drop_rates(tier, "COMMON")  # 임시로 COMMON 사용
            
            # 각 희귀도별 확률로 아이템 결정
            rarities = ["LEGENDARY", "EPIC", "RARE", "COMMON"]
            selected_rarity = None
            
            for rarity in rarities:
                probability = calculate_gacha_probability(
                    drop_rates.get(rarity, 0.05), 
                    current_streak,
                    pity_system=(rarity == "LEGENDARY")
                )
                
                if random.random() < probability:
                    selected_rarity = rarity
                    current_streak = 0 if rarity in ["LEGENDARY", "EPIC"] else current_streak + 1
                    break
            
            if not selected_rarity:
                selected_rarity = "COMMON"
                current_streak += 1
            
            results.append({
                "rarity": selected_rarity,
                "pull_number": i + 1,
                "streak_at_pull": current_streak
            })
        
        return results
        
    except Exception as e:
        logger.error(f"Failed to simulate gacha pull: {str(e)}")
        return []