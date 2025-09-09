import random
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine, SessionLocal
from sqlalchemy import text
from app.tests._testdb import reset_db
from app.models import User
from app.utils.redis import init_redis_manager, get_redis_manager
from app.services.payment_gateway import PaymentResult
from app.services.limited_package_service import LimitedPackageService


client = TestClient(app)

# set during setup_module
user_id = None


class _FakePipeline:
    def __init__(self, store):
        self.store = store
        self._in_multi = False
        self._ops = []

    def watch(self, key):
        # no-op in fake
        self._watch = key

    def unwatch(self):
        self._watch = None

    def get(self, key):
        return self.store.get(key)

    def multi(self):
        self._in_multi = True

    def decrby(self, key, amount):
        self._ops.append(("decrby", key, amount))

    def execute(self):
        for op, key, amount in self._ops:
            if op == "decrby":
                current = int(self.store.get(key, 0))
                self.store[key] = current - int(amount)
        self._ops.clear()
        self._in_multi = False
        return True

    def reset(self):
        self._ops.clear()
        self._in_multi = False


class _FakeRedis:
    def __init__(self):
        self.store = {}

    def ping(self):
        return True

    def get(self, key):
        return self.store.get(key)

    def setnx(self, key, value):
        if key not in self.store:
            self.store[key] = int(value)
            return True
        return False

    def setex(self, key, expire_seconds, value):
        self.store[key] = value
        return True

    def incrby(self, key, amount):
        self.store[key] = int(self.store.get(key, 0)) + int(amount)
        return self.store[key]

    def decrby(self, key, amount):
        self.store[key] = int(self.store.get(key, 0)) - int(amount)
        return self.store[key]

    def delete(self, key):
        self.store.pop(key, None)

    def expire(self, key, seconds):
        # ignore in fake
        return True

    def exists(self, key):
        # redis-py returns 1 if exists, 0 otherwise; tests expect truthy/falsy
        return 1 if key in self.store else 0

    def pipeline(self):
        return _FakePipeline(self.store)


def setup_module(module):
    # fresh schema
    reset_db(engine)

    # init fake redis so limited package service uses counters/stock
    init_redis_manager(_FakeRedis())

    # create a user
    db = SessionLocal()
    try:
        u = User(site_id="lp_user", nickname="lp_user", phone_number="010", password_hash="x", invite_code="5858")
        db.add(u)
        db.commit()
        db.refresh(u)
        global user_id
        user_id = u.id
    finally:
        db.close()


def _stock_key(code: str) -> str:
    return f"limited:{code}:stock"


def test_limited_catalog_lists_packages():
    resp = client.get("/api/shop/limited/catalog")
    assert resp.status_code == 200
    items = resp.json()
    assert isinstance(items, list) and len(items) >= 1
    codes = {it["code"] for it in items}
    assert "WEEKEND_STARTER" in codes or "VIP_BLITZ" in codes


def test_buy_limited_inactive_or_expired_returns_403():
    # Mark VIP_BLITZ inactive and attempt purchase
    pkg = LimitedPackageService.get("VIP_BLITZ")
    assert pkg is not None
    pkg.is_active = False
    resp = client.post(
        "/api/shop/limited/buy",
        json={"user_id": user_id, "code": "VIP_BLITZ", "quantity": 1},
    )
    assert resp.status_code == 403


def test_buy_limited_with_promo_code_discount():
    # Ensure stock and no prior purchases
    r = get_redis_manager().redis_client
    r.store[_stock_key("WEEKEND_STARTER")] = 5
    purchased_key = f"limited:WEEKEND_STARTER:user:{user_id}:purchased"
    r.store[purchased_key] = 0

    # Register promo code via service (50 cents off per unit)
    LimitedPackageService.set_promo_discount("WEEKEND_STARTER", "AUG50", 50)
    try:
        # Use AUG50 to apply $0.50 discount per unit; base price=499 -> expected=449
        random.seed(7)
        resp = client.post(
            "/api/shop/limited/buy",
            json={"user_id": user_id, "code": "WEEKEND_STARTER", "quantity": 1, "promo_code": "AUG50"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["total_price_cents"] == 449
    finally:
        # Clean up promo to avoid affecting other tests
        LimitedPackageService.clear_promo_discount("WEEKEND_STARTER", "AUG50")


def test_buy_limited_happy_and_per_user_limit():
    # ensure stock is available and per-user limit enforced
    r = get_redis_manager().redis_client
    # set a sane stock
    r.setnx(_stock_key("WEEKEND_STARTER"), 5)
    # reset per-user purchased counter to allow first purchase
    purchased_key = f"limited:WEEKEND_STARTER:user:{user_id}:purchased"
    r.store[purchased_key] = 0

    random.seed(42)
    resp = client.post(
        "/api/shop/limited/buy",
        json={"user_id": user_id, "code": "WEEKEND_STARTER", "quantity": 1},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["gold_granted"] > 0

    # second purchase should hit per-user limit (limit=1)
    resp2 = client.post(
        "/api/shop/limited/buy",
        json={"user_id": user_id, "code": "WEEKEND_STARTER", "quantity": 1},
    )
    assert resp2.status_code == 403


def test_buy_limited_out_of_stock_conflict():
    # Set stock=0; even quantity=1 should 409 (out of stock)
    r = get_redis_manager().redis_client
    r.store[_stock_key("WEEKEND_STARTER")] = 0
    # reset per-user purchased counter
    purchased_key = f"limited:WEEKEND_STARTER:user:{user_id}:purchased"
    r.store[purchased_key] = 0

    resp = client.post(
        "/api/shop/limited/buy",
        json={"user_id": user_id, "code": "WEEKEND_STARTER", "quantity": 1},
    )
    assert resp.status_code == 409


def test_buy_limited_payment_failure_releases_reservation(monkeypatch):
    # Preload stock=1; reset per-user counter; fail payment; stock should remain 1 after attempt
    r = get_redis_manager().redis_client
    r.store[_stock_key("WEEKEND_STARTER")] = 1
    # reset per-user purchased counter to allow attempt
    purchased_key = f"limited:WEEKEND_STARTER:user:{user_id}:purchased"
    r.store[purchased_key] = 0

    from app.services import payment_gateway as pg

    def fake_authorize(amount_cents, currency="USD", card_token=None):
        return PaymentResult(False, "failed", None, "Card declined")

    monkeypatch.setattr(pg.PaymentGateway, "authorize", lambda self, *a, **kw: fake_authorize(*a, **kw))

    resp = client.post(
        "/api/shop/limited/buy",
        json={"user_id": user_id, "code": "WEEKEND_STARTER", "quantity": 1},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is False
    # reservation released back to 1
    assert r.store[_stock_key("WEEKEND_STARTER")] == 1
