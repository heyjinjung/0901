"""Payment gateway adapters for development/testing.

이 모듈은 테스트 환경에서 결제 흐름을 시뮬레이션하기 위한 어댑터를 제공합니다.
다음 심볼들을 노출합니다:
- PaymentResult: 간단한 결과 데이터클래스 (기존 테스트 호환)
- PaymentGateway: authorize/capture를 제공하는 아주 단순한 목(기존 코드 호환)
- PaymentGatewayService: process_payment/check_status/refund 인터페이스를 제공하는 서비스(신규 테스트 호환)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional, Dict, Any
from uuid import uuid4
import os
import random
import time


@dataclass
class PaymentResult:
    success: bool
    status: Literal["authorized", "captured", "failed"]
    charge_id: Optional[str]
    message: str


class PaymentGateway:
    """매우 단순한 authorize/capture 기반 목 게이트웨이 (기존 코드 호환)."""

    def authorize(self, amount_cents: int, currency: str = "USD", *, card_token: str | None = None) -> PaymentResult:
        # 테스트 안정성: TESTING 환경변수 true 이면 항상 성공
        if os.getenv("TESTING", "").lower() in {"1", "true", "yes"}:
            return PaymentResult(True, "authorized", str(uuid4()), "Authorized (test deterministic)")
        # 데모용으로 90% 성공 (prod/dev fuzz)
        if random.random() < 0.9:
            return PaymentResult(True, "authorized", str(uuid4()), "Authorized")
        return PaymentResult(False, "failed", None, "Card declined")

    def capture(self, charge_id: str) -> PaymentResult:
        if os.getenv("TESTING", "").lower() in {"1", "true", "yes"}:
            return PaymentResult(True, "captured", charge_id, "Captured (test deterministic)")
        # authorize 된 건의 99% 캡처 성공 (prod/dev fuzz)
        if random.random() < 0.99:
            return PaymentResult(True, "captured", charge_id, "Captured")
        return PaymentResult(False, "failed", charge_id, "Capture failed")


# ===== 신규 테스트 호환 서비스 어댑터 =====
PaymentStatus = Literal["success", "failed", "pending"]


class PaymentGatewayService:
    """환경변수로 동작 모드를 제어하는 테스트용 결제 게이트웨이 서비스.

    모드(PAYMENT_GATEWAY_MODE):
    - always_success: 항상 즉시 성공
    - always_fail: 항상 실패
    - pending_then_success: 최초 요청은 pending, 이후 폴링 시 성공
    - random: success/failed/pending 무작위 (성공 가중치 높음)
    기본값은 always_success
    """

    def __init__(self, *, mode: Optional[str] = None):
        self.mode = (mode or os.getenv("PAYMENT_GATEWAY_MODE", "always_success")).strip()
        # 인스턴스 간 공유되는 간단한 pending 저장소 (dev only)
        global _PENDING_STORE
        try:
            _PENDING_STORE  # type: ignore[name-defined]
        except NameError:
            _PENDING_STORE = {}
        self._pending = _PENDING_STORE  # type: ignore[assignment]

    def process_payment(self, *, amount: int, method: Optional[str], metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        gateway_ref = uuid4().hex[:18]
        mode = self.mode

        if mode == "always_success":
            status: PaymentStatus = "success"
            message = "Payment approved"
        elif mode == "always_fail":
            status = "failed"
            message = "Payment declined"
        elif mode == "pending_then_success":
            status = "pending"
            message = "Payment pending"
            self._pending[gateway_ref] = time.time()
        elif mode == "random":
            status = random.choices(["success", "failed", "pending"], [0.7, 0.2, 0.1])[0]  # type: ignore
            message = {"success": "Payment approved", "failed": "Payment declined", "pending": "Payment pending"}[status]
            if status == "pending":
                self._pending[gateway_ref] = time.time()
        else:
            status = "success"
            message = "Payment approved"

        return {"status": status, "gateway_reference": gateway_ref, "message": message}

    def check_status(self, gateway_reference: str) -> Dict[str, Any]:
        if gateway_reference in self._pending:
            created = self._pending[gateway_reference]
            # 1초 이후 성공으로 전환 (테스트 안정화)
            if time.time() - created > 1.0:
                del self._pending[gateway_reference]
                return {"status": "success", "gateway_reference": gateway_reference}
            return {"status": "pending", "gateway_reference": gateway_reference}
        # 모르는 참조는 실패 처리
        return {"status": "failed", "gateway_reference": gateway_reference}

    def refund(self, *, gateway_reference: str, amount: int, reason: Optional[str] = None) -> Dict[str, Any]:
        if self.mode == "always_fail":
            return {"success": False, "message": "Gateway refund failed"}
        return {"success": True, "message": "Refund processed"}


# ---- thin retry helpers (minimal invasive) ----
def authorize_with_retry(pg: PaymentGateway, amount_cents: int, currency: str = "USD", *, card_token: Optional[str] = None, attempts: int = 3, base_delay: float = 0.2) -> PaymentResult:
    """Call PaymentGateway.authorize with simple exponential backoff.

    Keeps the signature surface small to avoid invasive changes in callers.
    """
    tries = 0
    delay = float(base_delay)
    last: Optional[PaymentResult] = None
    while tries < max(1, attempts):
        tries += 1
        try:
            res = pg.authorize(amount_cents, currency, card_token=card_token)
            if res.success:
                return res
            last = res
        except Exception:
            # swallow and retry
            last = PaymentResult(False, "failed", None, "Authorize exception")
        time.sleep(delay)
        delay *= 2
    return last or PaymentResult(False, "failed", None, "Authorize failed")


def capture_with_retry(pg: PaymentGateway, charge_id: str, attempts: int = 3, base_delay: float = 0.2) -> PaymentResult:
    """Call PaymentGateway.capture with simple exponential backoff."""
    tries = 0
    delay = float(base_delay)
    last: Optional[PaymentResult] = None
    while tries < max(1, attempts):
        tries += 1
        try:
            res = pg.capture(charge_id)
            if res.success:
                return res
            last = res
        except Exception:
            last = PaymentResult(False, "failed", charge_id, "Capture exception")
        time.sleep(delay)
        delay *= 2
    return last or PaymentResult(False, "failed", charge_id, "Capture failed")


__all__ = [
    "PaymentResult",
    "PaymentGateway",
    "PaymentGatewayService",
]
