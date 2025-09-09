import threading
import time
import random
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine, SessionLocal
from sqlalchemy import text
from app.tests._testdb import reset_db
from app.models import User
from app.utils.redis import init_redis_manager, get_redis_manager
from app.services.limited_package_service import LimitedPackageService


client = TestClient(app)


def setup_module(module):
    # fresh schema
    reset_db(engine)

    # init fake redis (simple dict) for stock/holds
    class _FakePipeline:
        def __init__(self, store):
            self.store = store
            self._ops = []
        def watch(self, key):
            pass
        def unwatch(self):
            pass
        def get(self, key):
            return self.store.get(key)
        def multi(self):
            pass
        def decrby(self, key, amount):
            self.store[key] = int(self.store.get(key, 0)) - int(amount)
        def execute(self):
            return True
        def reset(self):
            pass
    class _FakeRedis:
        def __init__(self):
            self.store = {}
            self._zsets = {}
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
        def pipeline(self):
            return _FakePipeline(self.store)
        # Sorted set for holds
        def zadd(self, key, mapping):
            z = self._zsets.setdefault(key, {})
            z.update({k: v for k, v in mapping.items()})
        def zrange(self, key, start, end):
            z = self._zsets.get(key, {})
            items = sorted(z.items(), key=lambda x: x[1])
            vals = [k for k, _ in items]
            if end == -1:
                end = len(vals) - 1
            return vals[start:end+1]
        def zrangebyscore(self, key, min_score, max_score):
            z = self._zsets.get(key, {})
            low = float('-inf') if min_score == '-inf' else int(min_score)
            high = int(max_score)
            return [k for k, s in z.items() if s <= high and s >= low]
        def zrem(self, key, member):
            z = self._zsets.get(key, {})
            z.pop(member, None)
        def zremrangebyscore(self, key, min_score, max_score):
            z = self._zsets.get(key, {})
            low = float('-inf') if min_score == '-inf' else int(min_score)
            high = int(max_score)
            for m, s in list(z.items()):
                if s <= high and s >= low:
                    z.pop(m, None)
        def exists(self, key):
            return 1 if key in self.store else 0
    init_redis_manager(_FakeRedis())

    # create a user
    db = SessionLocal()
    try:
        u = User(site_id="con_user", nickname="con_user", phone_number="010", password_hash="x", invite_code="5858")
        db.add(u)
        db.commit()
        db.refresh(u)
        module.user_id = u.id
    finally:
        db.close()


def _stock_key(code: str) -> str:
    return f"limited:{code}:stock"


def test_hold_timeout_sweep_returns_stock():
    # stock=1, reserve & hold with short TTL, let it expire then sweep
    r = get_redis_manager().redis_client
    r.setnx(_stock_key("WEEKEND_STARTER"), 1)
    # reserve
    assert LimitedPackageService.try_reserve("WEEKEND_STARTER", 1) is True
    # add hold with 1-second ttl
    hold_id = LimitedPackageService.add_hold("WEEKEND_STARTER", 1, ttl_seconds=1)
    # don't finalize purchase; wait for expiry
    time.sleep(1.2)
    returned = LimitedPackageService.sweep_expired_holds("WEEKEND_STARTER")
    assert returned >= 1
    assert r.get(_stock_key("WEEKEND_STARTER")) == 1


def test_reservation_contention_only_one_succeeds():
    # stock=1; two threads try to reserve 1 concurrently; only one should succeed
    r = get_redis_manager().redis_client
    r.setnx(_stock_key("WEEKEND_STARTER"), 1)
    results = []
    def worker():
        ok = LimitedPackageService.try_reserve("WEEKEND_STARTER", 1)
        results.append(ok)
    t1 = threading.Thread(target=worker)
    t2 = threading.Thread(target=worker)
    t1.start(); t2.start(); t1.join(); t2.join()
    assert results.count(True) == 1
    assert results.count(False) == 1
