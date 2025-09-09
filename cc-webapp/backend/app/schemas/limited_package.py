from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator


class LimitedPackageOut(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra='ignore')
    code: str
    package_id: str = Field(..., description="Legacy alias; always equals code")
    name: str
    description: Optional[str] = None
    price_cents: int
    gold: int = Field(0, description="구매 시 부여되는 골드 양 (이전 gems 필드 대체)")
    start_at: datetime
    end_at: datetime
    is_active: bool
    per_user_limit: int = 1
    remaining_stock: Optional[int] = Field(None, description="None means unlimited")
    user_purchased: int = 0
    user_remaining: Optional[int] = None

    @model_validator(mode="after")
    def _sync_ids(self):  # type: ignore[override]
        # 강제 동기화
        object.__setattr__(self, 'package_id', self.code)
        return self


class LimitedBuyRequest(BaseModel):
    package_id: str = Field(..., description="Limited package id/code")
    quantity: int = Field(1, ge=1, le=10)
    currency: str = Field("USD")
    card_token: Optional[str] = None
    promo_code: Optional[str] = Field(None, description="Optional promotion code for discount")
    # Optional idempotency key to protect from duplicate charges/retries
    idempotency_key: Optional[str] = Field(None, description="Client-provided idempotency key (unique per purchase attempt)")


class LimitedBuyReceipt(BaseModel):
    success: bool
    message: str
    user_id: int | None = None
    code: Optional[str] = None
    quantity: Optional[int] = None
    total_price_cents: Optional[int] = None
    gold_granted: Optional[int] = None
    new_gold_balance: Optional[int] = None
    charge_id: Optional[str] = None
    receipt_code: Optional[str] = None
    reason_code: Optional[str] = Field(None, description="실패 사유 코드 (OUT_OF_STOCK, USER_LIMIT 등)")
