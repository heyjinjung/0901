"""Reward / 간단 가챠 유틸.

테스트에서 patch('app.utils.reward_utils.models') 형태로 models 심볼을 주입하므로
여기서 models 를 import 후 노출한다.
현재 구현은 최소 스텁; 실제 로직 확장 시 확률표/아이템 풀/토큰 차감/로그 기록 추가.
"""

from app import models  # 테스트 patch 대상
import random

_BASIC_GACHA_POOL = [
    {"item_type": "COIN", "details": {"min_amount": 10, "max_amount": 50}, "weight": 400},
    {"item_type": "COIN", "details": {"min_amount": 50, "max_amount": 150}, "weight": 80},
]

def spin_gacha(user_id: int, db):
    pool = _BASIC_GACHA_POOL
    weights = [i["weight"] for i in pool]
    item = random.choices(pool, weights=weights, k=1)[0]
    if item["item_type"] == "COIN":
        amt = random.randint(item["details"]["min_amount"], item["details"]["max_amount"])
        return {"type": "COIN", "amount": amt, "message": "코인 보상"}
    return {"type": "NONE"}
