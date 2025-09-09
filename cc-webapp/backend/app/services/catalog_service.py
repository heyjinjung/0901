"""Simple in-memory shop catalog and pricing/discount policy."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Iterable
from datetime import datetime, timedelta

from ..core.config import settings
from ..core import economy


@dataclass(frozen=True)
class Product:
    id: int
    sku: str
    name: str
    # Price in minor currency unit (e.g., cents)
    price_cents: int
    # 구매 시 부여되는 골드(기존 gems 제거)
    gold: int
    # Optional discount percent (0-100)
    discount_percent: int = 0
    # Optional discount window
    discount_ends_at: Optional[datetime] = None
    # Optional VIP required rank
    min_rank: Optional[str] = None


class CatalogService:
    """In-memory 카탈로그.

    Stage2 (Economy V2) 목표:
      - 기존 1001~1004 상품은 유지(역호환)
      - Feature Flag 활성 시 2001~2004 신규 패키지 노출 (Starter/Value/Premium/Whale)
      - 추후 단계에서 100x 제품 sunset 예정 (문서에 일정 기재)
    """

    # Legacy (V1) catalog
    _catalog_v1: Dict[int, Product] = {
        1001: Product(id=1001, sku="GOLD_PACK_SMALL", name="Gold x100", price_cents=299, gold=100),
        1002: Product(id=1002, sku="GOLD_PACK_MED", name="Gold x550", price_cents=1299, gold=550, discount_percent=8),
        1003: Product(id=1003, sku="GOLD_PACK_BIG", name="Gold x1200", price_cents=2499, gold=1200, discount_percent=12),
        1004: Product(
            id=1004,
            sku="GOLD_PACK_VIP",
            name="Gold x3000 (VIP)",
            price_cents=5999,
            gold=3000,
            discount_percent=15,
            discount_ends_at=datetime.utcnow() + timedelta(days=7),
            min_rank="VIP",
        ),
    }

    # Economy V2 proposed catalog (under flag). Pricing 전략:
    #  - Starter: 초기가격 효율(First Purchase Conversion 강화)
    #  - Value / Premium: 점진적 단가 절감 (effective gold per $ 상승)
    #  - Whale: 최고 효율 + 한시 할인 윈도우(구매 촉진) – Flag off 시 미노출
    _catalog_v2: Dict[int, Product] = {
        2001: Product(id=2001, sku="GOLD_PACK_STARTER", name="Starter Bundle (2,600 Gold)", price_cents=199, gold=2600, discount_percent=0),
        2002: Product(id=2002, sku="GOLD_PACK_VALUE", name="Value Pack (6,000 Gold)", price_cents=499, gold=6000, discount_percent=5),
        2003: Product(id=2003, sku="GOLD_PACK_PREMIUM", name="Premium Pack (13,500 Gold)", price_cents=1099, gold=13500, discount_percent=10),
        2004: Product(
            id=2004,
            sku="GOLD_PACK_WHALE",
            name="Whale Pack (30,000 Gold)",
            price_cents=2299,
            gold=30000,
            discount_percent=15,
            discount_ends_at=datetime.utcnow() + timedelta(days=14),
        ),
    }

    @classmethod
    def _iter_active_catalog(cls) -> Iterable[Product]:
        # 항상 V1 포함
        for p in cls._catalog_v1.values():
            yield p
        # Flag 켜진 경우 V2 추가 (ID 충돌 회피; 중복되면 V2 우선 아님 - 서로 다른 id 사용)
        if economy.is_v2_active(settings):
            for p in cls._catalog_v2.values():
                yield p

    @classmethod
    def get_product(cls, product_id: int) -> Optional[Product]:
        # Flag 상태 반영 조회
        if economy.is_v2_active(settings):
            p = cls._catalog_v2.get(product_id)
            if p:
                return p
        return cls._catalog_v1.get(product_id)

    @classmethod
    def list_products(cls) -> list[Product]:
        # Flag 순서: V1 먼저 → V2 (프론트 기존 정렬 영향 최소화)
        return list(cls._iter_active_catalog())

    @staticmethod
    def compute_price_cents(product: Product, quantity: int = 1) -> int:
        """Compute discounted total price for the quantity."""
        base = product.price_cents * max(1, quantity)
        disc = product.discount_percent or 0
        if product.discount_ends_at and datetime.utcnow() > product.discount_ends_at:
            disc = 0
        if disc <= 0:
            return base
        # Round down after discount to minor unit
        return int(base * (100 - disc) / 100)
