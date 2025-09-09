"""카지노 게임 단일 통화(골드) 관리 서비스

단일 통화 시스템:
- gold_balance: 유일한 게임 내 통화
- 신규 가입 시 1000 골드 기본 지급
- 게임 참여, 관리자 지급으로 골드 획득
- 상점에서 아이템 구매 시 골드 차감
"""
from __future__ import annotations
from typing import Optional, Literal
from sqlalchemy.orm import Session
from sqlalchemy import select, update, text
from sqlalchemy.exc import SQLAlchemyError
from app.models.auth_models import User
import logging

logger = logging.getLogger(__name__)

CurrencyType = Literal['coin','gem','token']  # coin/gem synonym → 단일 token

class InsufficientBalanceError(Exception):
    def __init__(self, currency: str, required: int, current: int):
        super().__init__(f"Insufficient {currency} balance: required={required}, current={current}")
        self.currency = currency
        self.required = required
        self.current = current

class CurrencyService:
    def __init__(self, db: Session):
        self.db = db

    def _get_user_for_update(self, user_id: int) -> Optional[User]:
        # DB-agnostic 방식: ORM refresh with FOR UPDATE (raw SQL)
        try:
            return self.db.execute(
                select(User).where(User.id == user_id).with_for_update()
            ).scalar_one_or_none()
        except Exception as e:
            logger.error(f"Lock user failed user_id={user_id}: {e}")
            return None

    def _apply_delta(self, user: User, currency: CurrencyType, delta: int) -> int:
        # 모든 통화 요청은 gold_balance로 통합
        label = 'gold'
        current = getattr(user, 'gold_balance', 0) or 0
        new_val = current + delta
        if new_val < 0:
            raise InsufficientBalanceError(label, -delta, current)
        user.gold_balance = new_val
        return new_val

    def add(self, user_id: int, amount: int, currency: CurrencyType) -> int:
        if amount < 0:
            raise ValueError('amount must be >=0')
        user = self._get_user_for_update(user_id)
        if not user:
            raise ValueError('user not found')
        new_val = self._apply_delta(user, currency, amount)
        self.db.commit()
        return new_val

    def deduct(self, user_id: int, amount: int, currency: CurrencyType) -> int:
        if amount < 0:
            raise ValueError('amount must be >=0')
        user = self._get_user_for_update(user_id)
        if not user:
            raise ValueError('user not found')
        new_val = self._apply_delta(user, currency, -amount)
        self.db.commit()
        return new_val

    def get_balance(self, user_id: int) -> int:
        """사용자의 골드 잔액 조회"""
        user = self.db.get(User, user_id)
        if not user:
            raise ValueError('user not found')
        return getattr(user, 'gold_balance', 0) or 0

    def get_balances(self, user_id: int) -> dict:
        """하위 호환을 위한 잔액 조회 (모두 골드로 통일)"""
        gold = self.get_balance(user_id)
        return {
            'gold': gold,
            'token': gold,  # alias for backward compatibility
            'coin': gold,   # alias for backward compatibility
            'gem': gold,    # alias for backward compatibility
        }
