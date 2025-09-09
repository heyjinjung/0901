import math
from app.services.reward_service import calculate_streak_daily_reward

# 경계 값: 0,1,3,7,14 에 대해 단조 증가 및 기대 상한 접근 특성 검증
# 식: Gold = 1000 + 800 * (1 - e^{-s/6}), XP = 50 + 40 * (1 - e^{-s/8})

def _expected_gold(s: int) -> int:
    return int(round(1000 + 800 * (1 - math.exp(-s/6))))

def _expected_xp(s: int) -> int:
    return int(round(50 + 40 * (1 - math.exp(-s/8))))

BOUNDARIES = [0,1,3,7,14]

def test_streak_reward_boundaries_monotonic():
    prev_g = -1
    prev_x = -1
    for s in BOUNDARIES:
        g, x = calculate_streak_daily_reward(s)
        assert g == _expected_gold(s)
        assert x == _expected_xp(s)
        assert g > prev_g
        assert x > prev_x
        prev_g, prev_x = g, x


def test_streak_reward_upper_asymptote_progress():
    g7, x7 = calculate_streak_daily_reward(7)
    g14, x14 = calculate_streak_daily_reward(14)
    # 14일이 7일보다 증가하지만 증가폭은 0->7 대비 줄어드는(감쇠) 특성 (두 값 모두 상한 < 2000 / < 100)
    assert g14 > g7
    assert x14 > x7
    assert g14 < 2000
    assert x14 < 100
