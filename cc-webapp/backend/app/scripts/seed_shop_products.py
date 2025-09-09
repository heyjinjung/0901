"""상점 기본 GOLD 전환 상품 및 기능성 아이템 시드 스크립트.

요구 사양 (사용자 입력 기반):
MODEL 포인트 → GOLD 전환 상품
  - MODEL 30,000 포인트  -> 30,000 GOLD
  - MODEL 105,000 포인트 -> 100,000 GOLD
  - MODEL 330,000 포인트 -> 300,000 GOLD
  - MODEL 1,150,000 포인트 -> 1,000,000 GOLD

MODEL 아이템 (효과성 아이템)
  - 한폴방지        30,000 GOLD
  - 충전30%         50,000 GOLD
  - 조기등업        500,000 GOLD (1회만 구매 가능 - extra.limit_once)
  - 출석연결        20,000 GOLD
  - 하루동안 콤프 2배 50,000 GOLD

추가 정책:
 - 1,000,000 GOLD 충전 시 20,000 GOLD 지급 (보너스 정책은 여기서는 설명만, 추후 구매 로직에서 처리 필요)
 - 멱등: product_id 기준 존재 시 업데이트(가격/설명/extra) 하고 is_active 다시 True.
 - 알림/로그는 stdout.

주의: DB 테이블이 존재하지 않으면 조용히 종료.
"""

from datetime import datetime
from typing import List, Dict, Any
import sys

from ..database import SessionLocal, engine
from sqlalchemy import text
from .. import models


GOLD_PRODUCTS: List[Dict[str, Any]] = [
    {
        "product_id": "MODEL_POINTS_30000",
        "name": "MODEL 30,000 포인트 → 30,000 GOLD",
        "price": 30000,
        "description": "포인트 전환: 30,000 GOLD 지급",
        "extra": {"category": "conversion", "gold_out": 30000},
    },
    {
        "product_id": "MODEL_POINTS_105000",
        "name": "MODEL 105,000 포인트 → 100,000 GOLD",
        "price": 100000,
        "description": "포인트 전환: 100,000 GOLD 지급 (할인 적용)",
        "extra": {"category": "conversion", "gold_out": 100000, "source_points": 105000},
    },
    {
        "product_id": "MODEL_POINTS_330000",
        "name": "MODEL 330,000 포인트 → 300,000 GOLD",
        "price": 300000,
        "description": "포인트 전환: 300,000 GOLD 지급 (볼륨 보너스)",
        "extra": {"category": "conversion", "gold_out": 300000, "source_points": 330000},
    },
    {
        "product_id": "MODEL_POINTS_1150000",
        "name": "MODEL 1,150,000 포인트 → 1,000,000 GOLD",
        "price": 1000000,
        "description": "포인트 전환: 1,000,000 GOLD 지급 (대량 전환)",
        "extra": {"category": "conversion", "gold_out": 1000000, "source_points": 1150000},
    },
]

ITEM_PRODUCTS: List[Dict[str, Any]] = [
    {
        "product_id": "ITEM_ANTI_SINGLE_FAIL",
        "name": "한폴방지",
        "price": 30000,
        "description": "한 폴더 실패 보호 아이템",
        "extra": {"category": "item", "effect": "anti_single_fail", "duration": None},
    },
    {
        "product_id": "ITEM_CHARGE_30pct",
        "name": "충전 30%",
        "price": 50000,
        "description": "즉시 GOLD 30% 추가 충전 보너스 트리거",
        "extra": {"category": "item", "effect": "charge_bonus", "bonus_pct": 30},
    },
    {
        "product_id": "ITEM_EARLY_RANKUP",
        "name": "조기 등업",
        "price": 500000,
        "description": "즉시 VIP 등급 한 단계 상승 (1회 구매 제한)",
        "extra": {"category": "item", "effect": "early_rankup", "limit_once": True},
    },
    {
        "product_id": "ITEM_ATTEND_LINK",
        "name": "출석 연결",
        "price": 20000,
        "description": "출석 연속 유지/복구",
        "extra": {"category": "item", "effect": "attendance_link"},
    },
    {
        "product_id": "ITEM_COMP_DOUBLE_1DAY",
        "name": "하루동안 콤프 2배",
        "price": 50000,
        "description": "24시간 동안 보상/콤프 2배",
        "extra": {"category": "item", "effect": "comp_double", "duration_hours": 24},
    },
]


def table_exists(db, name: str) -> bool:
    try:
        db.execute(text(f"SELECT 1 FROM {name} LIMIT 1"))
        return True
    except Exception:
        db.rollback()
        return False


def upsert_product(db, data: Dict[str, Any]):
    row = (
        db.query(models.ShopProduct)
        .filter(models.ShopProduct.product_id == data["product_id"])
        .first()
    )
    if row:
        changed = False
        for field in ["name", "price", "description"]:
            new_val = data.get(field)
            if getattr(row, field) != new_val:
                setattr(row, field, new_val)
                changed = True
        # extra merge/replace
        new_extra = data.get("extra")
        if new_extra and new_extra != getattr(row, "extra", None):
            row.extra = new_extra
            changed = True
        if row.is_active is False:
            row.is_active = True
            changed = True
        row.updated_at = datetime.utcnow()
        if changed:
            print(f"[UPDATE] {data['product_id']}")
        else:
            print(f"[SKIP] {data['product_id']} (no change)")
    else:
        row = models.ShopProduct(
            product_id=data["product_id"],
            name=data["name"],
            price=data["price"],
            description=data.get("description"),
            extra=data.get("extra"),
            is_active=True,
        )
        db.add(row)
        print(f"[INSERT] {data['product_id']}")


def main():  # pragma: no cover - 수동 실행
    db = SessionLocal()
    try:
        if not table_exists(db, 'shop_products'):
            print("shop_products 테이블이 없어 시드 중단")
            return
        all_defs = GOLD_PRODUCTS + ITEM_PRODUCTS
        for d in all_defs:
            upsert_product(db, d)
        db.commit()
        total = db.query(models.ShopProduct).count()
        print({"ok": True, "total_products": total})
    except Exception as e:
        db.rollback()
        print({"ok": False, "error": str(e)})
        raise
    finally:
        db.close()


if __name__ == "__main__":  # pragma: no cover
    main()
