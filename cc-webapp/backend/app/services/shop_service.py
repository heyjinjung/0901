from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy import inspect
from typing import Dict, Any, List, Optional
from typing import Literal
from datetime import datetime
import uuid
import threading

# 프로세스 단위 인메모리 멱등 잠금 (테스트/단일 인스턴스 환경 보조)
_IDEMP_LOCKS: dict[str, threading.Lock] = {}
_IDEMP_LOCKS_GUARD = threading.Lock()

def _acquire_idemp_lock(key: str) -> threading.Lock:
    with _IDEMP_LOCKS_GUARD:
        lock = _IDEMP_LOCKS.get(key)
        if lock is None:
            lock = threading.Lock()
            _IDEMP_LOCKS[key] = lock
    lock.acquire()
    return lock

from .. import models
from .token_service import TokenService
from .payment_gateway import PaymentGatewayService
import json
from sqlalchemy import text
from ..utils.redis import get_redis  # Redis 선점 멱등 pre-lock
from .settlement_service import SettlementService  # P0: conversion 해시/서명 생성
from ..core.config import settings

class ShopService:
    def __init__(self, db: Session, token_service: TokenService | None = None):
        self.db = db
        self.token_service = token_service or TokenService(db)

    # ----- internal helpers -----
    def _table_exists(self, table_name: str) -> bool:
        try:
            insp = inspect(self.db.get_bind())
            return table_name in insp.get_table_names()
        except Exception:
            return False

    # ----- catalog -----
    def list_active_products(self) -> List[Dict[str, Any]]:
        """Return active products or empty list if table absent."""
        if not self._table_exists('shop_products'):
            return []
        rows = (
            self.db.query(models.ShopProduct)
            .filter(models.ShopProduct.is_active == True)  # noqa: E712
            .filter(models.ShopProduct.deleted_at.is_(None))
            .all()
        )
        return [
            {
                "product_id": r.product_id,
                "name": r.name,
                "description": r.description,
                "price": r.price,
                "extra": getattr(r, 'extra', None),
            }
            for r in rows
        ]

    def _get_product(self, product_id: str) -> Optional[models.ShopProduct]:
        if not self._table_exists('shop_products'):
            return None
        return (
            self.db.query(models.ShopProduct)
            .filter(models.ShopProduct.product_id == product_id)
            .first()
        )

    def _get_active_discounts(self, product_id: str, now: datetime) -> List[models.ShopDiscount]:
        if not self._table_exists('shop_discounts'):
            return []
        q = self.db.query(models.ShopDiscount).filter(
            models.ShopDiscount.product_id == product_id,
            models.ShopDiscount.is_active == True,  # noqa: E712
        )
        # time-window filter if provided
        q = q.filter(
            (models.ShopDiscount.starts_at == None) | (models.ShopDiscount.starts_at <= now)  # noqa: E711
        ).filter(
            (models.ShopDiscount.ends_at == None) | (models.ShopDiscount.ends_at >= now)  # noqa: E711
        )
        return q.all()

    def compute_price(self, product_id: str, now: Optional[datetime] = None) -> Dict[str, Any]:
        """Compute server price using product base price and applicable discounts.

        Returns dict with base_price, final_price, discounts_applied.
        If catalog tables are missing or product not found, raises ValueError.
        """
        now = now or datetime.utcnow()
        product = self._get_product(product_id)
        if not product:
            raise ValueError("상품이 존재하지 않습니다.")
        base = product.price
        final = base
        applied: List[Dict[str, Any]] = []
        for d in self._get_active_discounts(product_id, now):
            if d.discount_type == 'percent':
                cut = int(base * (d.value / 100.0))
                final = max(0, base - cut)
            elif d.discount_type == 'flat':
                final = max(0, base - d.value)
            applied.append({
                "type": d.discount_type,
                "value": d.value,
                "starts_at": d.starts_at.isoformat() if d.starts_at else None,
                "ends_at": d.ends_at.isoformat() if d.ends_at else None,
            })
            # For simplicity, apply first matching discount; extend to stack as needed
            break
        return {"base_price": base, "final_price": final, "discounts_applied": applied}

    def purchase_item(self, user_id: int, item_id: int, item_name: str, price: int, description: str | None, *, product_id: str | None = None) -> Dict[str, Any]:
        """Item purchase using cyber tokens; logs as UserAction and returns counts.

        This method deducts tokens, records a BUY_PACKAGE action with JSON payload,
        and returns the updated token balance and a simple per-product purchase count.
        """
        user = self.db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        current_balance = getattr(user, 'cyber_token_balance', 0) or 0
        if current_balance < price:
            return {
                "success": False,
                "message": "토큰이 부족합니다.",
                "new_balance": current_balance,
                "item_id": product_id or str(item_id),
                "item_name": item_name,
                "new_item_count": 0,
            }

        # Deduct tokens using the service
        new_balance = self.token_service.deduct_tokens(user_id, price)
        if new_balance is None:
            return {
                "success": False,
                "message": "토큰이 부족합니다.",
                "new_balance": current_balance,
                "item_id": product_id or str(item_id),
                "item_name": item_name,
                "new_item_count": 0,
            }

        # Log purchase as UserAction (BUY_PACKAGE)
        payload = {
            "product_id": product_id or str(item_id),
            "item_id": item_id,
            "item_name": item_name,
            "amount": price,
            "description": description,
            "kind": "item",
        }
        ua = models.UserAction(
            user_id=user_id,
            action_type='BUY_PACKAGE',
            action_data=json.dumps(payload, ensure_ascii=False),
        )
        self.db.add(ua)
        self.db.commit()

        # Compute new item count using action logs
        count_query = self.db.query(models.UserAction).filter(
            models.UserAction.user_id == user_id,
            models.UserAction.action_type == 'BUY_PACKAGE',
        )
        # Narrow by product_id when provided
        if product_id:
            count_query = count_query.filter(models.UserAction.action_data.contains(f'"product_id":"{product_id}"'))
        else:
            count_query = count_query.filter(models.UserAction.action_data.contains(f'"item_id": {item_id}'))
        item_count = count_query.count()

        return {
            "success": True,
            "message": f"{item_name} 구매 성공!",
            "new_balance": new_balance,
            "item_id": product_id or str(item_id),
            "item_name": item_name,
            "new_item_count": item_count,
        }

    # ----- transactions/receipts -----
    def record_transaction(self, user_id: int, product_id: str, kind: str, quantity: int, unit_price: int, amount: int, payment_method: str | None, status: str, receipt_code: str, extra: Dict[str, Any] | None = None, failure_reason: Optional[str] = None, idempotency_key: Optional[str] = None, *, raise_on_conflict: bool = False) -> None:
        if not self._table_exists('shop_transactions'):
            return
        try:
            tx = models.ShopTransaction(
                user_id=user_id,
                product_id=product_id,
                kind=kind,
                quantity=quantity,
                unit_price=unit_price,
                amount=amount,
                payment_method=payment_method,
                status=status,
                receipt_code=receipt_code,
                failure_reason=failure_reason,
                idempotency_key=idempotency_key,
                extra=extra or None,
            )
            self.db.add(tx)
            self.db.commit()
        except Exception as e:  # pragma: no cover - conflict path exercised in race test
            self.db.rollback()
            if raise_on_conflict:
                raise e

    def list_transactions(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        if self._table_exists('shop_transactions'):
            rows = (
                self.db.query(models.ShopTransaction)
                .filter(models.ShopTransaction.user_id == user_id)
                .order_by(models.ShopTransaction.id.desc())
                .limit(limit)
                .all()
            )
            return [
                {
                    "product_id": r.product_id,
                    "kind": r.kind,
                    "quantity": r.quantity,
                    "unit_price": r.unit_price,
                    "amount": r.amount,
                    "status": r.status,
                    "payment_method": r.payment_method,
                    "receipt_code": r.receipt_code,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in rows
            ]
        # Fallback: derive from UserAction logs
        logs = (
            self.db.query(models.UserAction)
            .filter(
                models.UserAction.user_id == user_id,
                models.UserAction.action_type.in_(['PURCHASE_GOLD', 'BUY_PACKAGE'])
            )
            .order_by(models.UserAction.id.desc())
            .limit(limit)
            .all()
        )
        out: List[Dict[str, Any]] = []
        for a in logs:
            try:
                data = json.loads(a.action_data or '{}')
            except Exception:
                data = {}
            out.append({
                "product_id": data.get('product_id'),
                "kind": data.get('kind'),
                "quantity": data.get('quantity', 1),
                "unit_price": data.get('amount'),
                "amount": data.get('amount'),
                "status": data.get('status') or "success",
                "payment_method": data.get('payment_method'),
                "receipt_code": data.get('receipt_code'),
                "created_at": None,
            })
        return out

    # ----- admin helpers -----
    def admin_search_transactions(
        self,
        *,
        user_id: Optional[int] = None,
        product_id: Optional[str] = None,
        status: Optional[str] = None,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        receipt_code: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        if not self._table_exists('shop_transactions'):
            return []
        q = self.db.query(models.ShopTransaction)
        if user_id is not None:
            q = q.filter(models.ShopTransaction.user_id == user_id)
        if product_id is not None:
            q = q.filter(models.ShopTransaction.product_id == product_id)
        if status is not None:
            q = q.filter(models.ShopTransaction.status == status)
        if receipt_code is not None:
            q = q.filter(models.ShopTransaction.receipt_code == receipt_code)
        if start is not None:
            q = q.filter(models.ShopTransaction.created_at >= start)
        if end is not None:
            q = q.filter(models.ShopTransaction.created_at <= end)
        rows = q.order_by(models.ShopTransaction.id.desc()).limit(limit).all()
        return [
            {
                "user_id": r.user_id,
                "product_id": r.product_id,
                "kind": r.kind,
                "quantity": r.quantity,
                "unit_price": r.unit_price,
                "amount": r.amount,
                "status": r.status,
                "payment_method": r.payment_method,
                "receipt_code": r.receipt_code,
                "failure_reason": r.failure_reason,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ]

    def refund_transaction(self, *, receipt_code: str, reason: Optional[str] = None) -> Dict[str, Any]:
        if not self._table_exists('shop_transactions'):
            return {"success": False, "message": "Transactions table not found"}
        tx = (
            self.db.query(models.ShopTransaction)
            .filter(models.ShopTransaction.receipt_code == receipt_code)
            .first()
        )
        if not tx:
            return {"success": False, "message": "Transaction not found"}
        if tx.status == 'refunded':
            return {"success": True, "message": "Already refunded"}
        if tx.status != 'success':
            return {"success": False, "message": f"Cannot refund transaction in status {tx.status}"}

        token_svc = TokenService(self.db)
        # gold 충전 트랜잭션(kind='gold') 환불은 사용자 잔액에서 차감
        if tx.kind == 'gold':
            current = token_svc.get_token_balance(tx.user_id)
            if current < tx.amount:
                return {"success": False, "message": "Insufficient user balance to refund"}
            new_balance = token_svc.deduct_tokens(tx.user_id, tx.amount)
            if new_balance is None:
                return {"success": False, "message": "Failed to deduct tokens for refund"}
        else:
            # 아이템 구매(kind='item') 환불은 토큰을 되돌려줌
            token_svc.add_tokens(tx.user_id, tx.amount)

        # Update transaction status
        tx.status = 'refunded'
        tx.failure_reason = (reason or '').strip() or None
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            return {"success": False, "message": "Failed to update transaction"}
        return {"success": True, "message": "Refund completed"}

    # ----- limited packages -----
    def list_limited_available(self, now: Optional[datetime] = None) -> List[Dict[str, Any]]:
        now = now or datetime.utcnow()
        if not self._table_exists('shop_limited_packages'):
            return []
        q = self.db.query(models.ShopLimitedPackage).filter(models.ShopLimitedPackage.is_active == True, models.ShopLimitedPackage.emergency_disabled == False)  # noqa: E712
        q = q.filter((models.ShopLimitedPackage.starts_at == None) | (models.ShopLimitedPackage.starts_at <= now))  # noqa: E711
        q = q.filter((models.ShopLimitedPackage.ends_at == None) | (models.ShopLimitedPackage.ends_at >= now))  # noqa: E711
        out: List[Dict[str, Any]] = []
        for p in q.all():
            out.append({
                "package_id": p.package_id,
                "name": p.name,
                "description": p.description,
                "price": p.price,
                "stock_remaining": p.stock_remaining,
                "per_user_limit": p.per_user_limit,
                "starts_at": p.starts_at.isoformat() if p.starts_at else None,
                "ends_at": p.ends_at.isoformat() if p.ends_at else None,
                "contents": p.contents,
            })
        return out

    def _get_limited(self, package_id: str) -> Optional[models.ShopLimitedPackage]:
        if not self._table_exists('shop_limited_packages'):
            return None
        return self.db.query(models.ShopLimitedPackage).filter(models.ShopLimitedPackage.package_id == package_id).first()

    def _user_purchases_count(self, user_id: int, package_id: str) -> int:
        if not self._table_exists('shop_transactions'):
            return 0
        return self.db.query(models.ShopTransaction).filter(
            models.ShopTransaction.user_id == user_id,
            models.ShopTransaction.product_id == package_id,
            models.ShopTransaction.kind == 'item',
            models.ShopTransaction.status == 'success',
        ).count()

    def _apply_promo(self, price: int, promo_code: Optional[str], package_id: str, now: Optional[datetime] = None) -> int:
        if not promo_code:
            return price
        now = now or datetime.utcnow()
        if not self._table_exists('shop_promo_codes'):
            return price
        pc = self.db.query(models.ShopPromoCode).filter(models.ShopPromoCode.code == promo_code, models.ShopPromoCode.is_active == True).first()  # noqa: E712
        if not pc:
            return price
        if pc.package_id and pc.package_id != package_id:
            return price
        if pc.starts_at and pc.starts_at > now:
            return price
        if pc.ends_at and pc.ends_at < now:
            return price
        # max uses check
        if pc.max_uses is not None and pc.used_count >= pc.max_uses:
            return price
        # apply discount
        if pc.discount_type == 'percent':
            discounted = max(0, int(price * (100 - pc.value) / 100))
        else:
            discounted = max(0, price - pc.value)
        return discounted

    def purchase_limited(self, user_id: int, package_id: str, promo_code: Optional[str] = None) -> Dict[str, Any]:
        now = datetime.utcnow()
        pkg = self._get_limited(package_id)
        if not pkg or not pkg.is_active or pkg.emergency_disabled:
            return {"success": False, "message": "Package unavailable"}
        if pkg.starts_at and now < pkg.starts_at:
            return {"success": False, "message": "Package not started"}
        if pkg.ends_at and now > pkg.ends_at:
            return {"success": False, "message": "Package expired"}
        if pkg.stock_remaining is not None and pkg.stock_remaining <= 0:
            return {"success": False, "message": "Out of stock"}
        if pkg.per_user_limit is not None and self._user_purchases_count(user_id, package_id) >= pkg.per_user_limit:
            return {"success": False, "message": "Per-user limit reached"}

        price = int(pkg.price)
        # Determine if promo is valid and track usage; if promo provided but not applied, treat as invalid
        promo_applied = False
        if promo_code:
            old_price = price
            new_price = self._apply_promo(price, promo_code, package_id, now)
            promo_applied = new_price < old_price
            if not promo_applied:
                return {"success": False, "message": "Invalid or exhausted promo code"}
            price = new_price

        # deduct tokens
        new_balance = TokenService(self.db).deduct_tokens(user_id, price)
        if new_balance is None:
            return {"success": False, "message": "Insufficient tokens"}

        # Decrement stock (원자 감소) - oversell 방지
        if pkg.stock_remaining is not None:
            try:
                updated = self.db.execute(
                    text("""
                        UPDATE shop_limited_packages
                        SET stock_remaining = stock_remaining - 1
                        WHERE package_id = :pid AND stock_remaining > 0
                        RETURNING stock_remaining
                    """), {"pid": package_id}
                ).fetchone()
                if not updated:
                    self.db.rollback()
                    return {"success": False, "message": "Out of stock"}
            except Exception:
                self.db.rollback()
                return {"success": False, "message": "Stock decrement failed"}

        # Record transaction
        tx_code = uuid.uuid4().hex[:12]
        t = models.ShopTransaction(
            user_id=user_id,
            product_id=package_id,
            kind='item',
            quantity=1,
            unit_price=price,
            amount=price,
            payment_method='tokens',
            status='success',
            receipt_code=tx_code,
            extra={"limited": True},
        )
        try:
            self.db.add(t)
            # If promo used, atomic increment with max_uses guard
            if promo_applied and self._table_exists('shop_promo_codes'):
                try:
                    row = self.db.execute(
                        text("""
                            UPDATE shop_promo_codes
                            SET used_count = used_count + 1
                            WHERE code = :code
                              AND is_active = 1
                              AND (max_uses IS NULL OR used_count < max_uses)
                            RETURNING used_count, max_uses
                        """), {"code": promo_code}
                    ).fetchone()
                    if not row:
                        self.db.rollback()
                        return {"success": False, "message": "Invalid or exhausted promo code"}
                except Exception:
                    self.db.rollback()
                    return {"success": False, "message": "Promo update failed"}
            self.db.commit()
        except Exception:
            self.db.rollback()
            return {"success": False, "message": "Failed to record transaction"}

        # Deliver contents (tokens/items)
        granted = {}
        if pkg.contents:
            bonus_tokens = (pkg.contents or {}).get('bonus_tokens')
            if isinstance(bonus_tokens, int) and bonus_tokens > 0:
                new_balance = TokenService(self.db).add_tokens(user_id, bonus_tokens)
                granted['bonus_tokens'] = bonus_tokens

        return {"success": True, "message": "Limited package purchased", "new_balance": new_balance, "receipt_code": tx_code, "granted": granted}

    # ----- unified gold product purchase (conversion/item stub) -----
    def purchase_product(
        self,
        *,
        user_id: int,
        product_id: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """단일화폐(gold) 기반 상점 상품 구매.

        요구사항:
        - MODEL 포인트 전환(conversion): 내부 포인트 차감 없음. extra.source_points / granted_gold 기록 후 gold 증가.
        - 아이템(item) 카테고리: gold 소모 후 stub 트랜잭션 (효과 적용은 외부 시스템). limit_once 상품 재구매 차단.
        - idempotency_key 동일 + 성공 기록 있으면 재구성하여 동일 응답 (멱등).
        - 응답: gold_before, gold_delta(+/-), gold_after, product_id, category(conversion|item), transaction_id, idempotency_key.
        - SoftDelete/비활성 상품 방어.

        extra 스키마 예:
        conversion:
          {"category":"conversion","source_points":330000,"granted_gold":300000,"conversion":true}
        item stub:
          {"category":"item","effect":"COMP_DOUBLE","stub":true,"limit_once":true}
        """
        if not self._table_exists('shop_products'):
            return {"success": False, "message": "상품 테이블이 없습니다."}
        if not self._table_exists('shop_transactions'):
            return {"success": False, "message": "트랜잭션 테이블이 없습니다."}

    # idempotent 재사용 검사 (Redis pre-lock 이전 빠른 조회)
        if idempotency_key:
            existing = (
                self.db.query(models.ShopTransaction)
                .filter(
                    models.ShopTransaction.user_id == user_id,
                    models.ShopTransaction.product_id == product_id,
                    models.ShopTransaction.idempotency_key == idempotency_key,
                    models.ShopTransaction.status == 'success',
                ).first()
            )
            if existing:
                before = None
                extra = existing.extra or {}
                gold_delta = 0
                if extra:
                    gold_delta = extra.get('granted_gold') or extra.get('gold_delta') or 0
                    before = extra.get('gold_before')
                # balance 최신 조회
                user_obj = self.db.query(models.User).filter(models.User.id == user_id).first()
                current_balance = getattr(user_obj, 'gold_balance', 0) if user_obj else None
                gold_after = current_balance
                return {
                    "success": True,
                    "idempotent": True,
                    "product_id": product_id,
                    "category": (extra or {}).get('category'),
                    "gold_before": before,
                    "gold_delta": gold_delta,
                    "gold_after": gold_after,
                    "transaction_id": existing.id,
                    "idempotency_key": idempotency_key,
                }

        # Redis 선점 멱등 pre-lock (멀티 인스턴스) - 실패 시 진행 상태 혹은 재구성
        pre_locked = False
        redis_client = None
        if idempotency_key:
            try:
                redis_client = get_redis()
                if redis_client:
                    prelock_key = f"shop:idemp:{user_id}:{product_id}:{idempotency_key}"
                    # SET NX EX 60
                    set_ok = redis_client.set(prelock_key, "1", nx=True, ex=60)
                    if not set_ok:
                        # 이미 다른 프로세스 진행 중 → DB에 success 있는지 재확인 후 없으면 진행중 응답
                        existing_mid = (
                            self.db.query(models.ShopTransaction)
                            .filter(
                                models.ShopTransaction.user_id == user_id,
                                models.ShopTransaction.product_id == product_id,
                                models.ShopTransaction.idempotency_key == idempotency_key,
                                models.ShopTransaction.status == 'success',
                            ).first()
                        )
                        if existing_mid:
                            ex_extra = existing_mid.extra or {}
                            return {
                                "success": True,
                                "idempotent": True,
                                "product_id": product_id,
                                "category": ex_extra.get('category'),
                                "gold_before": ex_extra.get('gold_before'),
                                "gold_delta": ex_extra.get('gold_delta') or ex_extra.get('granted_gold') or 0,
                                "gold_after": self.db.query(models.User).filter(models.User.id == user_id).first().gold_balance if self.db.query(models.User).filter(models.User.id == user_id).first() else None,
                                "transaction_id": existing_mid.id,
                                "idempotency_key": idempotency_key,
                                "receipt_code": existing_mid.receipt_code,
                            }
                        return {"success": False, "message": "IN_PROGRESS", "idempotency_key": idempotency_key}
                    pre_locked = True
            except Exception:  # pragma: no cover - Redis 실패는 관용 처리
                redis_client = None

        # 멱등 락 (프로세스 메모리, 보조)
        lock: Optional[threading.Lock] = None
        lock_key = None
        if idempotency_key:
            lock_key = f"{user_id}:{product_id}:{idempotency_key}"
            lock = _acquire_idemp_lock(lock_key)
        try:
            product = self._get_product(product_id)
            if not product or not product.is_active or getattr(product, 'deleted_at', None):
                return {"success": False, "message": "유효하지 않은 상품"}

            # (2차) 락 획득 후 멱등 재검사: 동시에 들어온 경쟁 요청 중 선행 성공 건 재활용
            if idempotency_key:
                existing_after_lock = (
                    self.db.query(models.ShopTransaction)
                    .filter(
                        models.ShopTransaction.user_id == user_id,
                        models.ShopTransaction.product_id == product_id,
                        models.ShopTransaction.idempotency_key == idempotency_key,
                        models.ShopTransaction.status == 'success',
                    ).first()
                )
                if existing_after_lock:
                    ex_extra = existing_after_lock.extra or {}
                    return {
                        "success": True,
                        "idempotent": True,
                        "product_id": product_id,
                        "category": ex_extra.get('category'),
                        "gold_before": ex_extra.get('gold_before'),
                        "gold_delta": ex_extra.get('gold_delta') or ex_extra.get('granted_gold') or 0,
                        "gold_after": self.db.query(models.User).filter(models.User.id == user_id).first().gold_balance if self.db.query(models.User).filter(models.User.id == user_id).first() else None,
                        "transaction_id": existing_after_lock.id,
                        "idempotency_key": idempotency_key,
                        "receipt_code": existing_after_lock.receipt_code,
                    }

            p_extra = getattr(product, 'extra', {}) or {}
            category = p_extra.get('category') or 'item'
            limit_once = bool(p_extra.get('limit_once'))

            # limit_once 재구매 차단
            if limit_once:
                prior = (
                    self.db.query(models.ShopTransaction)
                    .filter(
                        models.ShopTransaction.user_id == user_id,
                        models.ShopTransaction.product_id == product_id,
                        models.ShopTransaction.status == 'success',
                    ).first()
                )
                if prior:
                    return {"success": False, "message": "이미 1회 한정 상품을 구매했습니다.", "limit_once": True}

            # 사용자 행 FOR UPDATE (Postgres) - SQLAlchemy ORM 단순 잠금 (raw text 사용 가능)
            user_obj = self.db.query(models.User).filter(models.User.id == user_id).with_for_update(nowait=False).first()
            if not user_obj:
                return {"success": False, "message": "사용자 없음"}
            gold_before = getattr(user_obj, 'gold_balance', 0) or 0

            # 카테고리 분기
            if category == 'conversion':  # EXTERNAL_STUB: 외부 포인트 차감/정산은 외부 시스템 처리. 내부는 granted_gold 증가 기록만.
                granted_gold = int(p_extra.get('gold_out') or product.price)
                # 증가
                user_obj.gold_balance = gold_before + granted_gold
                gold_delta = granted_gold
                tx_extra = {
                    "category": "conversion",
                    "source_points": p_extra.get('source_points'),
                    "granted_gold": granted_gold,
                    "conversion": True,
                    "gold_before": gold_before,
                    "gold_delta": gold_delta,
                }
                kind = 'gold'
                # P0 SettlementService 호출(해시/서명) - 외부 차감은 아직 Stub
                try:
                    secret = getattr(settings, 'PAYMENT_WEBHOOK_SECRET', None) or getattr(settings, 'JWT_SECRET_KEY', 'stub-secret')
                    settle = SettlementService(hmac_secret=secret)
                    settle_res = settle.settle_conversion(
                        user_id=user_id,
                        product_id=product_id,
                        amount=product.price,
                        quantity=1,
                        kind=kind,
                        receipt_code="PENDING",  # 실제 receipt_code 생성 전 프리뷰용(최종 tx 객체에 다시 채움)
                    )
                    tx_extra['settlement_status'] = settle_res.status
                    tx_extra['external_reference'] = settle_res.external_reference
                    # receipt_code 실제 생성 후 integrity_hash 재계산 위해 임시 저장
                    pending_integrity_hash = settle_res.integrity_hash
                    pending_signature = settle_res.receipt_signature
                except Exception:  # pragma: no cover
                    pending_integrity_hash = None
                    pending_signature = None
            else:
                # item: gold 차감 필요 (price 만큼 소모)
                price = int(product.price)
                if gold_before < price:
                    return {"success": False, "message": "GOLD 부족", "required": price, "gold_balance": gold_before}
                user_obj.gold_balance = gold_before - price
                gold_delta = -price
                effect = p_extra.get('effect') or p_extra.get('code') or p_extra.get('effect_code')
                tx_extra = {
                    "category": "item",
                    "effect": effect,
                    "stub": True,
                    "limit_once": limit_once,
                    "gold_before": gold_before,
                    "gold_delta": gold_delta,
                }
                kind = 'item'

            receipt_code = uuid.uuid4().hex[:16]
            tx = models.ShopTransaction(
            user_id=user_id,
            product_id=product_id,
            kind=kind,
            quantity=1,
            unit_price=product.price,
            amount=product.price,
            payment_method='gold',
            status='success',
            receipt_code=receipt_code,
            idempotency_key=idempotency_key,
            extra=tx_extra,
            )
            # conversion 해시/서명 실제 receipt_code 기반 재계산 (임시 단계: P0)
            if category == 'conversion':
                try:
                    secret2 = getattr(settings, 'PAYMENT_WEBHOOK_SECRET', None) or getattr(settings, 'JWT_SECRET_KEY', 'stub-secret')
                    settle2 = SettlementService(hmac_secret=secret2)
                    final_res = settle2.settle_conversion(
                        user_id=user_id,
                        product_id=product_id,
                        amount=product.price,
                        quantity=1,
                        kind=kind,
                        receipt_code=receipt_code,
                    )
                    tx.integrity_hash = final_res.integrity_hash
                    tx.receipt_signature = final_res.receipt_signature
                    tx.extra = {**(tx.extra or {}), "integrity_hash": final_res.integrity_hash, "receipt_signature": final_res.receipt_signature}
                except Exception:  # pragma: no cover
                    pass
            self.db.add(tx)
            action_payload = {
                "product_id": product_id,
                "category": category,
                "gold_before": gold_before,
                "gold_delta": gold_delta,
                "gold_after": user_obj.gold_balance,
                "idempotency_key": idempotency_key,
                "receipt_code": receipt_code,
            }
            ua = models.UserAction(
                user_id=user_id,
                action_type='PURCHASE_GOLD' if category == 'conversion' else 'BUY_PACKAGE',
                action_data=json.dumps(action_payload, ensure_ascii=False),
            )
            self.db.add(ua)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            msg = str(e).lower()
            if idempotency_key and ('uq_shop_tx_user_product_idem' in msg or 'unique constraint' in msg):
                existing = (
                    self.db.query(models.ShopTransaction)
                    .filter(
                        models.ShopTransaction.user_id == user_id,
                        models.ShopTransaction.product_id == product_id,
                        models.ShopTransaction.idempotency_key == idempotency_key,
                        models.ShopTransaction.status == 'success',
                    ).first()
                )
                if existing:
                    ex_extra = existing.extra or {}
                    return {
                        "success": True,
                        "idempotent": True,
                        "product_id": product_id,
                        "category": ex_extra.get('category') or category,
                        "gold_before": ex_extra.get('gold_before'),
                        "gold_delta": ex_extra.get('gold_delta') or ex_extra.get('granted_gold') or 0,
                        "gold_after": self.db.query(models.User).filter(models.User.id == user_id).first().gold_balance if self.db.query(models.User).filter(models.User.id == user_id).first() else None,
                        "transaction_id": existing.id,
                        "idempotency_key": idempotency_key,
                        "receipt_code": existing.receipt_code,
                    }
            return {"success": False, "message": "DB 오류", "detail": str(e)}
        finally:
            if lock:
                lock.release()
            # Redis pre-lock 해제 (명시 삭제; TTL로도 만료되지만 빠른 재시도 허용)
            if idempotency_key and pre_locked and redis_client:
                try:
                    redis_client.delete(f"shop:idemp:{user_id}:{product_id}:{idempotency_key}")
                except Exception:
                    pass

        return {
            "success": True,
            "product_id": product_id,
            "category": category,
            "gold_before": gold_before,
            "gold_delta": gold_delta,
            "gold_after": user_obj.gold_balance,
            "transaction_id": tx.id,
            "idempotency_key": idempotency_key,
            "receipt_code": receipt_code,
        }

    # ----- user settlement/polling -----
    def get_tx_by_receipt_for_user(self, user_id: int, receipt_code: str) -> Optional[models.ShopTransaction]:
        if not self._table_exists('shop_transactions'):
            return None
        try:
            return (
                self.db.query(models.ShopTransaction)
                .filter(
                    models.ShopTransaction.user_id == user_id,
                    models.ShopTransaction.receipt_code == receipt_code,
                )
                .first()
            )
        except Exception as e:
            # Handle SQLite schema drift (missing newly added columns) in ephemeral test DBs
            msg = str(e).lower()
            if 'no such column' in msg or 'has no column named' in msg:
                self._repair_shop_tx_table()
                try:
                    return (
                        self.db.query(models.ShopTransaction)
                        .filter(
                            models.ShopTransaction.user_id == user_id,
                            models.ShopTransaction.receipt_code == receipt_code,
                        )
                        .first()
                    )
                except Exception:
                    return None
            return None

    def _repair_shop_tx_table(self):
        """Attempt to add any missing columns on shop_transactions (SQLite only).

        This is a lenient, test-environment helper so that newly introduced optional
        columns (receipt_signature, integrity_hash, idempotency_key, extra) don't break
        older persisted local DB files when migrations lag behind model definition.
        """
        try:
            if self.db.bind.dialect.name != 'sqlite':
                return
            from sqlalchemy import text
            conn = self.db.connection()
            cols = set()
            try:
                res = conn.execute(text('PRAGMA table_info(shop_transactions)'))
                for row in res.fetchall():
                    cols.add(row[1])  # second column is name
            except Exception:
                return
            needed = {
                'failure_reason': "ALTER TABLE shop_transactions ADD COLUMN failure_reason VARCHAR(500)",
                'integrity_hash': "ALTER TABLE shop_transactions ADD COLUMN integrity_hash VARCHAR(64)",
                'original_tx_id': "ALTER TABLE shop_transactions ADD COLUMN original_tx_id INTEGER",
                'receipt_signature': "ALTER TABLE shop_transactions ADD COLUMN receipt_signature VARCHAR(128)",
                'idempotency_key': "ALTER TABLE shop_transactions ADD COLUMN idempotency_key VARCHAR(80)",
                'extra': "ALTER TABLE shop_transactions ADD COLUMN extra JSON",
                'updated_at': "ALTER TABLE shop_transactions ADD COLUMN updated_at DATETIME",
            }
            for col, ddl in needed.items():
                if col not in cols:
                    try:
                        conn.execute(text(ddl))
                    except Exception:
                        pass
        except Exception:
            pass

    def settle_pending_gold_for_user(self, user_id: int, receipt_code: str, gateway: Optional[PaymentGatewayService] = None) -> Dict[str, Any]:
        tx = self.get_tx_by_receipt_for_user(user_id, receipt_code)
        gateway = gateway or PaymentGatewayService()
        if tx is None:
            # Fallback when transactions table is absent: derive from UserAction log
            a = (
                self.db.query(models.UserAction)
                .filter(
                    models.UserAction.user_id == user_id,
                    models.UserAction.action_type == 'PURCHASE_GOLD',
                    models.UserAction.action_data.contains(f'"receipt_code":"{receipt_code}"'),
                )
                .order_by(models.UserAction.id.desc())
                .first()
            )
            if not a:
                return {"success": False, "message": "Transaction not found"}
            try:
                data = json.loads(a.action_data or '{}')
            except Exception:
                data = {}
            # If already settled
            if data.get('status') == 'success':
                return {"success": True, "status": 'success'}
            gw_ref = data.get('gateway_reference') or receipt_code
            res = gateway.check_status(gw_ref)
            status = res.get('status')
            if status == 'pending':
                return {"success": True, "status": 'pending'}
            elif status == 'failed':
                # Write a follow-up log to indicate failure
                payload = {**data, 'status': 'failed'}
                ua = models.UserAction(user_id=user_id, action_type='PURCHASE_GOLD', action_data=json.dumps(payload, ensure_ascii=False))
                try:
                    self.db.add(ua)
                    self.db.commit()
                except Exception:
                    self.db.rollback()
                return {"success": True, "status": 'failed'}
            else:
                # Credit tokens and write success log
                amount = int(data.get('amount') or 0)
                new_balance = TokenService(self.db).add_tokens(user_id, amount)
                payload = {**data, 'status': 'success'}
                ua = models.UserAction(user_id=user_id, action_type='PURCHASE_GOLD', action_data=json.dumps(payload, ensure_ascii=False))
                try:
                    self.db.add(ua)
                    self.db.commit()
                except Exception:
                    self.db.rollback()
                return {"success": True, "status": 'success', "new_balance": new_balance}
        # Normal path: have transaction row
        if tx.status != 'pending':
            return {"success": True, "status": tx.status}
        if tx.kind != 'gold':
            return {"success": False, "message": "Only gold transactions can be auto-settled"}
        res = gateway.check_status(receipt_code)
        status = res.get('status')
        if status == 'pending':
            return {"success": True, "status": 'pending'}
        elif status == 'failed':
            tx.status = 'failed'
            tx.failure_reason = 'Gateway declined on poll'
            try:
                self.db.commit()
            except Exception:
                self.db.rollback()
            return {"success": True, "status": 'failed'}
        else:
            TokenService(self.db).add_tokens(user_id, tx.amount)
            tx.status = 'success'
            try:
                self.db.commit()
            except Exception:
                self.db.rollback()
                return {"success": False, "message": "Failed to update transaction"}
            new_balance = TokenService(self.db).get_token_balance(user_id)
            return {"success": True, "status": 'success', "new_balance": new_balance}

    # ----- admin force settle -----
    def admin_force_settle(self, receipt_code: str, outcome: Literal['success', 'failed'] = 'success') -> Dict[str, Any]:
        if not self._table_exists('shop_transactions'):
            return {"success": False, "message": "Transactions table not found"}
        tx = self.db.query(models.ShopTransaction).filter(models.ShopTransaction.receipt_code == receipt_code).first()
        if not tx:
            return {"success": False, "message": "Transaction not found"}
        if tx.status != 'pending':
            return {"success": True, "status": tx.status}
        if tx.kind != 'gold':
            return {"success": False, "message": "Only gold transactions can be force-settled"}

        if outcome == 'failed':
            tx.status = 'failed'
            tx.failure_reason = 'Force failed by admin'
            try:
                self.db.commit()
            except Exception:
                self.db.rollback()
                return {"success": False, "message": "DB commit failed"}
            return {"success": True, "status": 'failed'}
        else:
            # success: credit and mark success
            TokenService(self.db).add_tokens(tx.user_id, tx.amount)
            tx.status = 'success'
            try:
                self.db.commit()
            except Exception:
                self.db.rollback()
                return {"success": False, "message": "DB commit failed"}
            new_balance = TokenService(self.db).get_token_balance(tx.user_id)
            return {"success": True, "status": 'success', "new_balance": new_balance}
