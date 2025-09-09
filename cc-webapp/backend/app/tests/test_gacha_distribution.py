import time
import random
from collections import Counter


def _signup(client, prefix: str = "gd"):
    uniq = str(int(time.time() * 1000))[-7:]
    site_id = f"{prefix}_{uniq}"
    payload = {
        "site_id": site_id,
        "password": "pass1234",
        "nickname": f"{prefix}_{uniq}",
        "invite_code": "5858",
        "phone_number": f"010{uniq}0",
    }
    r = client.post("/api/auth/signup", json=payload)
    if r.status_code != 200:
        r = client.post("/api/auth/login", json={"site_id": site_id, "password": "pass1234"})
        assert r.status_code == 200
    data = r.json()
    return data["access_token"], data["user"]["id"]


def _expected_from_table():
    # Read the service default rarity table and derive expected actual-rarity shares
    from app.services.gacha_service import GachaService

    table = getattr(GachaService, "DEFAULT_RARITY_TABLE", [])
    exp = {"common": 0.0, "rare": 0.0, "epic": 0.0, "legendary": 0.0}
    for name, p in table:
        if name == "Common":
            exp["common"] += p
        elif name == "Rare":
            exp["rare"] += p
        elif name == "Epic":
            exp["epic"] += p
        elif name == "Legendary":
            exp["legendary"] += p
        elif name == "Near_Miss_Epic":
            # Near-miss resolves downward to Rare in current implementation
            exp["rare"] += p
        elif name == "Near_Miss_Legendary":
            # Near-miss Legendary resolves to Epic
            exp["epic"] += p

    s = sum(exp.values())
    if s > 0:
        for k in exp:
            exp[k] = exp[k] / s
    return exp


def test_gacha_distribution_sanity_approx(client):
    """Pull 1000 items via 100x 10-pulls and validate rarity distribution within ±5% of expected.

    Notes:
    - RNG is seeded to ensure determinism across CI runs.
    - Uses the service's DEFAULT_RARITY_TABLE and accounts for near-miss mapping
        (Near_Miss_Epic→Rare, Near_Miss_Legendary→Epic).
    - Pity/discount/history damping can shift probabilities slightly; ±5% absolute band allowed.
    """
    # Tests run large number of pulls; ensure daily count check is bypassed in test
    from app.core.config import settings
    settings.DAILY_GACHA_PULLS = 10000
    settings.VIP_DAILY_GACHA_PULLS = 10000
    # Monkeypatch repository method used by service to count daily actions
    from app.repositories.game_repository import GameRepository
    GameRepository.count_daily_actions = lambda self, db, user_id, action_type: 0

    # Seed RNG for deterministic distribution in CI
    random.seed(42)
    access_token, _ = _signup(client)
    headers = {"Authorization": f"Bearer {access_token}"}

    # Bulk pull 계획: 100 x 10-pull = 1000 pulls total
    batches = 100
    # 필요한 토큰 수를 가챠 서비스 비용에서 계산하여 충분히 충전
    from app.services.gacha_service import GachaService
    cost_ten = GachaService().get_config().get("cost_ten", GachaService.NEW_COST_TEN)
    needed = batches * cost_ten + 1000
    r_add = client.post("/api/users/tokens/add", headers=headers, params={"amount": needed})
    # 디버깅: 토큰 추가가 실패하면 즉시 원인 파악을 위해 본문을 노출하고 실패 처리
    assert r_add.status_code == 200, f"토큰 추가 실패: status={r_add.status_code}, body={r_add.text}"

    counts = Counter({"common": 0, "rare": 0, "epic": 0, "legendary": 0})
    for _ in range(batches):
        r = client.post("/api/games/gacha/pull", headers=headers, json={"pull_count": 10})
        assert r.status_code == 200, r.text
        body = r.json()
        items = body.get("items", [])
        assert len(items) == 10
        for it in items:
            rarity = str(it.get("rarity", "common")).lower()
            if rarity not in counts:
                rarity = "common"
            counts[rarity] += 1

    total = sum(counts.values())
    assert total == 1000

    ratios = {k: counts[k] / total for k in counts}
    exp = _expected_from_table()

    # Validate within ±5% absolute tolerance for the main three categories
    # With RNG seeded, the dynamic adjustments should remain stable.
    for k in ("common", "rare", "epic"):
        low = max(0.0, exp.get(k, 0.0) - 0.05)
        high = min(1.0, exp.get(k, 0.0) + 0.05)
        assert low <= ratios[k] <= high, f"{k} ratio {ratios[k]:.3f} not in [{low:.3f}, {high:.3f}] (exp~{exp.get(k,0):.3f})"
