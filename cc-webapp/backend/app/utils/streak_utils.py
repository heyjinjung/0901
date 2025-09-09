"""Streak 공통 유틸 함수.

선형 보상 시스템으로 간소화됨.
Epic/Rare Chest 시스템 제거, 단순한 골드/XP 선형 증가 적용.
"""
from __future__ import annotations

def calculate_streak_reward(streak_count: int) -> dict:
    """streak_count에 대한 골드와 XP 보상 계산.
    
    새로운 선형 공식:
    - Gold = 800 + (streak_count * 200)
    - XP = 25 + (streak_count * 25)
    
    Args:
        streak_count: 현재 연속일 수 (1일부터 시작)
    
    Returns:
        dict: {'gold': int, 'xp': int}
    """
    gold = 800 + (streak_count * 200)
    xp = 25 + (streak_count * 25)
    
    # 최대 보상 제한 (10일차)
    max_gold = 2800
    max_xp = 275
    
    return {
        'gold': min(gold, max_gold),
        'xp': min(xp, max_xp)
    }

# 레거시 함수 - 더 이상 사용하지 않음 (하위 호환용으로만 유지)
def calc_next_streak_reward(next_count: int) -> str:
    """DEPRECATED: Epic/Rare Chest 시스템 제거됨.
    
    하위 호환성을 위해 유지하지만 더 이상 사용하지 않음.
    대신 calculate_streak_reward 사용.
    """
    return "Daily Reward"  # 단순화된 응답

__all__ = ["calculate_streak_reward", "calc_next_streak_reward"]
