from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, List, Dict

from ..core.config import settings
from ..utils.redis import get_redis_manager


@dataclass
class LimitedPackage:
    code: str
    name: str
    description: str
    price_cents: int
    gold: int
    start_at: datetime
    end_at: datetime
    per_user_limit: int = 1
    initial_stock: Optional[int] = None  # None => unlimited
    is_active: bool = True


class LimitedPackageService:
    """
    In-memory limited packages catalog with Redis-backed stock and per-user counters.
    This avoids DB migrations for now while providing realistic behavior.
    """

    # Demo catalog; can be replaced by DB/admin later.
    _catalog: Dict[str, LimitedPackage] = {}
    _promo_discounts: Dict[str, Dict[str, int]] = {}  # {code: {PROMO: cents_off_per_unit}}
    # In-memory usage mirrors
    _user_purchases: Dict[str, Dict[int, int]] = {}
    _promo_max_uses: Dict[str, int] = {}
    _promo_used_count: Dict[str, int] = {}
    # In-memory stock fallback when Redis is unavailable
    _stock_counts: Dict[str, int] = {}
    # In-memory hold fallback when Redis is unavailable
    _holds_mem: Dict[str, List[tuple]] = {}

    @classmethod
    def _seed_catalog(cls):
        if cls._catalog:
            return
        now = datetime.now(timezone.utc)
        cls._catalog = {
            "WEEKEND_STARTER": LimitedPackage(
                code="WEEKEND_STARTER",
                name="Weekend Starter Pack",
                description="Limited-time pack with bonus gold",
                price_cents=499,
                gold=600,
                start_at=now,
                end_at=now.replace(hour=23, minute=59) ,
                per_user_limit=1,
                initial_stock=1000,
                is_active=True,
            ),
            "VIP_BLITZ": LimitedPackage(
                code="VIP_BLITZ",
                name="VIP Blitz Pack",
                description="High value pack for VIPs",
                price_cents=1999,
                gold=2600,
                start_at=now,
                end_at=now.replace(hour=23, minute=59),
                per_user_limit=2,
                initial_stock=None,  # unlimited
                is_active=True,
            ),
        }

    @classmethod
    def list_active(cls) -> List[LimitedPackage]:
        cls._seed_catalog()
        now = datetime.now(timezone.utc)
        return [p for p in cls._catalog.values() if p.is_active and p.start_at <= now <= p.end_at]

    @classmethod
    def get(cls, code: str) -> Optional[LimitedPackage]:
        cls._seed_catalog()
        return cls._catalog.get(code)

    # --- Admin mutators (MVP; in-memory only) ---
    @classmethod
    def set_active(cls, code: str, active: bool) -> bool:
        pkg = cls.get(code)
        if not pkg:
            return False
        pkg.is_active = bool(active)
        return True

    @classmethod
    def set_period(cls, code: str, start_at: datetime, end_at: datetime) -> bool:
        pkg = cls.get(code)
        if not pkg:
            return False
        pkg.start_at = start_at
        pkg.end_at = end_at
        return True

    @classmethod
    def set_per_user_limit(cls, code: str, per_user_limit: int) -> bool:
        pkg = cls.get(code)
        if not pkg:
            return False
        pkg.per_user_limit = int(per_user_limit)
        return True

    @classmethod
    def set_initial_stock(cls, code: str, initial_stock: Optional[int]) -> bool:
        pkg = cls.get(code)
        if not pkg:
            return False
        pkg.initial_stock = initial_stock
        # also seed redis key to new stock if provided
        if initial_stock is not None:
            r = get_redis_manager()
            if r.redis_client:
                r.redis_client.setnx(cls._stock_key(code), int(initial_stock))
            else:
                # fallback initialize in-memory stock counter
                cls._stock_counts[code] = int(initial_stock)
        return True

    # --- Promo codes (absolute cents discount per unit) ---
    @classmethod
    def set_promo_discount(cls, code: str, promo_code: str, cents_off: int) -> None:
        cls._promo_discounts.setdefault(code, {})[promo_code.upper()] = max(int(cents_off), 0)

    @classmethod
    def clear_promo_discount(cls, code: str, promo_code: str) -> None:
        mp = cls._promo_discounts.get(code) or {}
        mp.pop(promo_code.upper(), None)

    @classmethod
    def list_promos(cls, code: str) -> Dict[str, int]:
        return dict(cls._promo_discounts.get(code) or {})

    @classmethod
    def get_promo_discount(cls, code: str, promo_code: Optional[str]) -> int:
        if not promo_code:
            return 0
        return int((cls._promo_discounts.get(code) or {}).get(promo_code.upper(), 0))

    @staticmethod
    def _stock_key(code: str) -> str:
        return f"limited:{code}:stock"

    @staticmethod
    def _purchased_key(code: str, user_id: int) -> str:
        return f"limited:{code}:user:{user_id}:purchased"

    @staticmethod
    def _holds_key(code: str) -> str:
        return f"limited:{code}:holds"

    @classmethod
    def get_stock(cls, code: str) -> Optional[int]:
        pkg = cls.get(code)
        if not pkg:
            return None
        if pkg.initial_stock is None:
            return None  # unlimited
        r = get_redis_manager()
        key = cls._stock_key(code)
        if r.redis_client:
            # Initialize if not set
            current = r.redis_client.get(key)
            if current is None:
                r.redis_client.setnx(key, pkg.initial_stock)
                return pkg.initial_stock
            try:
                return int(current)
            except Exception:
                return pkg.initial_stock
        # Fallback to in-memory stock counter
        return int(cls._stock_counts.get(code, pkg.initial_stock))

    @classmethod
    def get_user_purchased(cls, code: str, user_id: int) -> int:
        r = get_redis_manager()
        key = cls._purchased_key(code, user_id)
        val = r.redis_client.get(key) if r.redis_client else None
        if val is not None:
            try:
                return int(val)
            except Exception:
                pass
        return int(cls._user_purchases.get(code, {}).get(int(user_id), 0))

    @classmethod
    def try_reserve(cls, code: str, quantity: int) -> bool:
        pkg = cls.get(code)
        if not pkg:
            return False
        if pkg.initial_stock is None:
            return True  # unlimited
        r = get_redis_manager()
        if not r.redis_client:
            # Fallback: manage stock in-memory
            if pkg.initial_stock is None:
                return True
            current = int(cls._stock_counts.get(code, pkg.initial_stock))
            if current < quantity:
                return False
            cls._stock_counts[code] = current - int(quantity)
            return True
        key = cls._stock_key(code)
        pipe = r.redis_client.pipeline()
        while True:
            try:
                pipe.watch(key)
                current = pipe.get(key)
                current = int(current) if current is not None else pkg.initial_stock
                if current < quantity:
                    pipe.unwatch()
                    return False
                pipe.multi()
                pipe.decrby(key, quantity)
                pipe.execute()
                return True
            except Exception:
                # Retry a couple times on contention
                try:
                    pipe.reset()
                except Exception:
                    pass
                return False

    @classmethod
    def finalize_user_purchase(cls, code: str, user_id: int, quantity: int) -> None:
        r = get_redis_manager()
        if r.redis_client:
            r.redis_client.incrby(cls._purchased_key(code, user_id), quantity)
        # Always update in-memory mirror so behavior is correct even without Redis
        mp = cls._user_purchases.setdefault(code, {})
        mp[int(user_id)] = int(mp.get(int(user_id), 0)) + int(quantity)

    # ---- Hold tracking for timeout release ----
    @classmethod
    def add_hold(cls, code: str, quantity: int, ttl_seconds: int = 120) -> str:
        """Record a hold with TTL in a Redis sorted set; fallback to memory.

        Note: Stock is already decremented by try_reserve; this marker allows
        sweeping back to stock if purchase doesn't finalize in time.

        TTL is configurable via settings.LIMITED_HOLD_TTL_SECONDS; the explicit
        ttl_seconds argument takes precedence when provided by callers.
        """
        import time, uuid
        hold_id = uuid.uuid4().hex[:16]
        # Allow central configuration override
        effective_ttl = int(ttl_seconds if ttl_seconds is not None else settings.LIMITED_HOLD_TTL_SECONDS)
        expires = int(time.time()) + int(effective_ttl)
        r = get_redis_manager()
        member = f"{hold_id}:{int(quantity)}"
        if r.redis_client:
            try:
                r.redis_client.zadd(cls._holds_key(code), {member: expires})
            except Exception:
                pass
        else:
            lst = cls._holds_mem.setdefault(code, [])
            lst.append((expires, member))
        return hold_id

    @classmethod
    def remove_hold(cls, code: str, hold_id: str) -> None:
        r = get_redis_manager()
        key = cls._holds_key(code)
        if r.redis_client:
            try:
                # Need to find exact member to remove (member includes qty)
                members = r.redis_client.zrange(key, 0, -1)
                for m in members or []:
                    if isinstance(m, bytes):
                        m = m.decode('utf-8')
                    if m.startswith(f"{hold_id}:"):
                        r.redis_client.zrem(key, m)
                        break
            except Exception:
                pass
        else:
            lst = cls._holds_mem.get(code, [])
            cls._holds_mem[code] = [(exp, mem) for (exp, mem) in lst if not mem.startswith(f"{hold_id}:")]

    @classmethod
    def sweep_expired_holds(cls, code: str) -> int:
        """Return expired holds to stock. Returns number of units returned."""
        import time
        now = int(time.time())
        r = get_redis_manager()
        key = cls._holds_key(code)
        returned = 0
        if r.redis_client:
            try:
                expired = r.redis_client.zrangebyscore(key, '-inf', now)
                if expired:
                    # Sum quantities
                    for m in expired:
                        if isinstance(m, bytes):
                            m = m.decode('utf-8')
                        try:
                            _, qty_s = m.split(":", 1)
                            returned += int(qty_s)
                        except Exception:
                            pass
                    # Remove expired members
                    r.redis_client.zremrangebyscore(key, '-inf', now)
                    if returned > 0:
                        r.redis_client.incrby(cls._stock_key(code), returned)
            except Exception:
                return 0
        else:
            lst = cls._holds_mem.get(code, [])
            keep: List[tuple] = []
            for exp, mem in lst:
                if exp <= now:
                    try:
                        _, qty_s = mem.split(":", 1)
                        returned += int(qty_s)
                    except Exception:
                        pass
                else:
                    keep.append((exp, mem))
            cls._holds_mem[code] = keep
            if returned > 0:
                pkg = cls.get(code)
                if pkg and pkg.initial_stock is not None:
                    cls._stock_counts[code] = int(cls._stock_counts.get(code, pkg.initial_stock)) + returned
        return int(returned)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
    

    @classmethod
    def release_reservation(cls, code: str, quantity: int) -> None:
        pkg = cls.get(code)
        if not pkg or pkg.initial_stock is None:
            return
        r = get_redis_manager()
        if r.redis_client:
            r.redis_client.incrby(cls._stock_key(code), quantity)
        else:
            # Fallback: adjust in-memory stock
            cls._stock_counts[code] = int(cls._stock_counts.get(code, pkg.initial_stock)) + int(quantity)

    # ---- Promo usage helpers ----
    @classmethod
    def set_promo_max_uses(cls, promo_code: str, max_uses: Optional[int]) -> None:
        if max_uses is None:
            cls._promo_max_uses.pop(promo_code.upper(), None)
        else:
            cls._promo_max_uses[promo_code.upper()] = int(max_uses)

    @classmethod
    def can_use_promo(cls, promo_code: Optional[str]) -> bool:
        if not promo_code:
            return True
        code = promo_code.upper()
        max_uses = cls._promo_max_uses.get(code)
        if max_uses is None:
            return True
        used = int(cls._promo_used_count.get(code, 0))
        return used < max_uses

    @classmethod
    def record_promo_use(cls, promo_code: Optional[str]) -> None:
        if not promo_code:
            return
        code = promo_code.upper()
        cls._promo_used_count[code] = int(cls._promo_used_count.get(code, 0)) + 1
