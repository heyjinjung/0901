"""Monte Carlo Economy EV Simulator

용도:
  - Slot / RPS / Gacha / Crash 게임의 기대값(RTP 혹은 하우스 엣지) 실측
  - 구현 값이 목표(Target)에서 허용 편차 이내인지 검증
  - 결과 JSON + 콘솔 요약 출력, CI에서 --fail-on-deviation 사용 가능

주의:
  - 서비스 레이어/DB 의존 최소화를 위해 확률/코스트는 경량화된 샘플 로직 사용
  - 추후 실제 GameService / GachaService 함수 직접 호출 모드(--mode service) 추가 가능
"""
from __future__ import annotations
import os
import math
import json
import random
import argparse
from dataclasses import dataclass
from typing import Dict, Any, Tuple

# Target constants (문서와 동기화)
TARGET_SLOT_RTP = 0.92
TARGET_RPS_HOUSE_EDGE = 0.05  # house advantage (player EV = -0.05 * bet)
TARGET_CRASH_HOUSE_EDGE = 0.07
TARGET_GACHA_EV_RANGE = (0.55, 0.60)

# Simplified economic parameters (베팅/비용)
SLOT_BET = 100
RPS_BET = 100
GACHA_SINGLE_COST = 5000  # V2 신규 코스트 반영
CRASH_BET = 100

# Gacha rarity/weight/value (샘플: economy.py 기반 개략화; 실제 값 반영 시 수정)
GACHA_RARITIES = [
    ("common", 0.70, 0.2),   # (name, probability, relative value multiplier vs cost)
    ("rare", 0.20, 0.6),
    ("epic", 0.08, 1.4),
    ("legendary", 0.02, 3.0),
]

@dataclass
class Stat:
    n: int = 0
    mean: float = 0.0
    m2: float = 0.0

    def push(self, x: float) -> None:
        self.n += 1
        delta = x - self.mean
        self.mean += delta / self.n
        self.m2 += delta * (x - self.mean)

    def variance(self) -> float:
        return self.m2 / (self.n - 1) if self.n > 1 else 0.0

    def std_error(self) -> float:
        return math.sqrt(self.variance() / self.n) if self.n > 0 else 0.0

    def ci95(self) -> Tuple[float, float]:
        se = self.std_error()
        return (self.mean - 1.96 * se, self.mean + 1.96 * se)


def simulate_slot(n: int, rng: random.Random) -> Dict[str, Any]:
    stat = Stat()
    # 단순화: RTP 타겟 근처가 되도록 인위적 payout 분포 구성
    outcomes = [
        (0.75, 0.0),
        (0.20, 2.0),
        (0.04, 5.0),
        (0.01, 20.0)
    ]
    cumulative = []
    acc = 0.0
    for p, mult in outcomes:
        acc += p
        cumulative.append((acc, mult))
    for _ in range(n):
        r = rng.random()
        mult = 0.0
        for c, m in cumulative:
            if r <= c:
                mult = m
                break
        payout = mult * SLOT_BET
        rtp_sample = payout / SLOT_BET
        stat.push(rtp_sample)
    low, high = stat.ci95()
    return {
        "rtp_mean": stat.mean,
        "rtp_ci95": [low, high],
        "target_rtp": TARGET_SLOT_RTP,
        "diff": stat.mean - TARGET_SLOT_RTP,
        "pass": abs(stat.mean - TARGET_SLOT_RTP) <= 0.01
    }


def simulate_rps(n: int, rng: random.Random) -> Dict[str, Any]:
    # 목표: player return ~ 0.95 (house edge 0.05)
    stat = Stat()
    probs = [(0.30, 2.0), (0.35, 1.0), (0.35, 0.0)]  # win/draw/lose
    cumulative = []
    acc = 0.0
    for p, mult in probs:
        acc += p
        cumulative.append((acc, mult))
    for _ in range(n):
        r = rng.random()
        mult = 0.0
        for c, m in cumulative:
            if r <= c:
                mult = m
                break
        payout_ratio = mult
        stat.push(payout_ratio)
    mean = stat.mean
    low, high = stat.ci95()
    house_edge_est = 1 - mean
    return {
        "player_return_mean": mean,
        "player_return_ci95": [low, high],
        "house_edge_est": house_edge_est,
        "target_house_edge": TARGET_RPS_HOUSE_EDGE,
        "diff": house_edge_est - TARGET_RPS_HOUSE_EDGE,
        "pass": abs(house_edge_est - TARGET_RPS_HOUSE_EDGE) <= 0.005
    }


def simulate_gacha(n: int, rng: random.Random) -> Dict[str, Any]:
    stat = Stat()
    rarity_counts = {r: 0 for r, _, _ in GACHA_RARITIES}
    cumulative = []
    acc = 0.0
    for name, p, val in GACHA_RARITIES:
        acc += p
        cumulative.append((acc, name, val))
    for _ in range(n):
        r = rng.random()
        chosen = None
        value_mult = 0.0
        for c, name, v in cumulative:
            if r <= c:
                chosen = name
                value_mult = v
                break
        if chosen is None:
            chosen = GACHA_RARITIES[-1][0]
            value_mult = GACHA_RARITIES[-1][2]
        rarity_counts[chosen] += 1
        stat.push(value_mult)
    mean = stat.mean
    low, high = stat.ci95()
    target_low, target_high = TARGET_GACHA_EV_RANGE
    return {
        "ev_mean": mean,
        "ev_ci95": [low, high],
        "target_range": [target_low, target_high],
        "within_range": target_low <= mean <= target_high,
        "rarity_distribution": {k: v / n for k, v in rarity_counts.items()}
    }


def simulate_crash(n: int, rng: random.Random) -> Dict[str, Any]:
    stat = Stat()
    outcomes = [
        (0.60, 0.0),
        (0.30, 1.5),
        (0.09, 3.0),
        (0.01, 20.0)
    ]
    cumulative = []
    acc = 0.0
    for p, mult in outcomes:
        acc += p
        cumulative.append((acc, mult))
    for _ in range(n):
        r = rng.random()
        mult = 0.0
        for c, m in cumulative:
            if r <= c:
                mult = m
                break
        stat.push(mult)
    mean = stat.mean
    low, high = stat.ci95()
    house_edge_est = 1 - mean
    return {
        "player_return_mean": mean,
        "player_return_ci95": [low, high],
        "house_edge_est": house_edge_est,
        "target_house_edge": TARGET_CRASH_HOUSE_EDGE,
        "diff": house_edge_est - TARGET_CRASH_HOUSE_EDGE,
        "pass": abs(house_edge_est - TARGET_CRASH_HOUSE_EDGE) <= 0.01
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--slot-n", type=int, default=int(os.getenv("SIM_SLOT_N", 50000)))
    parser.add_argument("--rps-n", type=int, default=int(os.getenv("SIM_RPS_N", 50000)))
    parser.add_argument("--gacha-n", type=int, default=int(os.getenv("SIM_GACHA_N", 50000)))
    parser.add_argument("--crash-n", type=int, default=int(os.getenv("SIM_CRASH_N", 50000)))
    parser.add_argument("--seed", type=int, default=12345)
    parser.add_argument("--fail-on-deviation", action="store_true")
    parser.add_argument("--output", help="JSON 결과 저장 경로")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    slot_res = simulate_slot(args.slot_n, rng)
    rps_res = simulate_rps(args.rps_n, rng)
    gacha_res = simulate_gacha(args.gacha_n, rng)
    crash_res = simulate_crash(args.crash_n, rng)

    result = {
        "seed": args.seed,
        "simulations": {
            "slot": slot_res,
            "rps": rps_res,
            "gacha": gacha_res,
            "crash": crash_res,
        }
    }
    print("=== Monte Carlo EV Summary ===")
    for k, v in result["simulations"].items():
        if k == "gacha":
            print(f"{k}: ev_mean={v['ev_mean']:.4f} target={v['target_range']} pass={v['within_range']}")
        else:
            if 'rtp_mean' in v:
                print(f"{k}: rtp_mean={v['rtp_mean']:.4f} target={v['target_rtp']:.4f} diff={v['diff']:.4f} pass={v['pass']}")
            else:
                print(f"{k}: house_edge={v['house_edge_est']:.4f} target={v['target_house_edge']:.4f} diff={v['diff']:.4f} pass={v['pass']}")

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))

    if args.fail_on_deviation:
        slot_ok = slot_res["pass"]
        rps_ok = rps_res["pass"]
        crash_ok = crash_res["pass"]
        gacha_ok = gacha_res["within_range"]
        if not (slot_ok and rps_ok and crash_ok and gacha_ok):
            raise SystemExit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
