import math
import random
import requests

BASE_URL = "http://localhost:8000"
SLOT_SPIN_ENDPOINT = f"{BASE_URL}/api/games/slot/spin"

def approx_ratio(n, total):
    return 0.0 if total == 0 else n / float(total)

def test_slot_distribution_sanity(auth_token):
    """Sanity check: outcomes over many spins are within broad bands and streak bonus increases average win.
    This is a smoke test; not strict, intended to catch regressions.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    spins = 300
    bet = 10

    wins = 0
    total_win_amount = 0
    prev_avg = None

    for i in range(spins):
        resp = requests.post(SLOT_SPIN_ENDPOINT, headers=headers, json={"bet_amount": bet, "lines": 1})
        assert resp.status_code == 200, resp.text
        data = resp.json()
        win_amount = data.get("win_amount", 0)
        total_win_amount += win_amount
        if win_amount > 0:
            wins += 1

        # halfway checkpoint: average win should not decrease at the end (streak bonus trend)
        if i == spins // 2:
            prev_avg = total_win_amount / (i + 1)

    final_avg = total_win_amount / spins
    # Loose checks to avoid flakes: win rate not absurdly low/high, and average not catastrophically off
    win_rate = approx_ratio(wins, spins)
    assert 0.01 <= win_rate <= 0.5
    if prev_avg is not None:
        assert final_avg >= prev_avg * 0.8  # allow noise but expect non-degradation trend
