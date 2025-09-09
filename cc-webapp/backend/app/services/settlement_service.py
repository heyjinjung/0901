"""Settlement / Receipt Integrity Service (설계 스켈레톤)

역할 (Boundary):
1. 외부 포인트/현금 → GOLD 전환(conversion) 시 외부 시스템(결제 게이트웨이/포인트 플랫폼)에 실제 차감/정산 요청
2. 영수증 무결성(integrity_hash) 생성: sha256(user_id|product_id|amount|quantity|kind|receipt_code|ts)
3. 클라이언트 검증용 receipt_signature 생성(HMAC, 회전 가능 secret) 및 검증
4. 재시도/멱등: 외부 Settlement API 5xx/타임아웃 시 백오프 재시도 + 최종 PENDING 표기 → 후속 settle 작업
5. Fraud/Velocity 훅: 시도 직전 FraudService(pre-authorization) 호출 (추가 예정)

미구현(추가 예정 단계화):
- 실제 외부 API 연동 (HTTPClient 추상화 필요)
- Circuit breaker / exponential backoff
- Secret rotation (active + next secret dual verify)
- 영수증 재생(duplicate) 탐지 캐시

사용 위치:
- 현재 `ShopService.purchase_product` 의 EXTERNAL_STUB 변환 분기에 삽입 예정 (conversion category)

로드맵 단계:
P0: hash/signature 생성 + DB 컬럼 채움 (성공 케이스만)
P1: 실패/재시도 상태 관리 (pending → poll), settlement_jobs 테이블 또는 큐
P2: secret rotation + dual verification + Fraud hook
P3: 감사 로그(Audit) + 메트릭(export: settlement_latency_seconds, settlement_fail_total)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any
import hmac, hashlib, time


@dataclass
class SettlementResult:
    success: bool
    status: str  # success|pending|failed
    external_reference: Optional[str] = None
    failure_reason: Optional[str] = None
    integrity_hash: Optional[str] = None
    receipt_signature: Optional[str] = None


class SettlementService:
    def __init__(self, *, hmac_secret: str, next_hmac_secret: str | None = None):
        self.hmac_secret = hmac_secret.encode()
        self.next_hmac_secret = next_hmac_secret.encode() if next_hmac_secret else None

    # --- Public API ---
    def settle_conversion(
        self,
        *,
        user_id: int,
        product_id: str,
        amount: int,
        quantity: int,
        kind: str,
        receipt_code: str,
        extra: Optional[Dict[str, Any]] = None,
    ) -> SettlementResult:
        """외부 정산 요청 + hash/signature 생성.

        현재는 외부 호출을 STUB 처리하고 즉시 success 처리.
        추후: HTTP POST → 2xx success|202 pending|4xx fail 분기.
        """
        ts = int(time.time())
        integrity_hash = self._compute_integrity_hash(
            user_id=user_id,
            product_id=product_id,
            amount=amount,
            quantity=quantity,
            kind=kind,
            receipt_code=receipt_code,
            ts=ts,
        )
        signature = self._sign_receipt(receipt_code, integrity_hash)
        # 외부 호출 STUB → success
        return SettlementResult(
            success=True,
            status="success",
            external_reference=f"stub-{receipt_code[:8]}",
            integrity_hash=integrity_hash,
            receipt_signature=signature,
        )

    def verify_signature(self, receipt_code: str, integrity_hash: str, signature: str) -> bool:
        base = f"{receipt_code}|{integrity_hash}".encode()
        if hmac.compare_digest(signature, hmac.new(self.hmac_secret, base, hashlib.sha256).hexdigest()):
            return True
        if self.next_hmac_secret and hmac.compare_digest(signature, hmac.new(self.next_hmac_secret, base, hashlib.sha256).hexdigest()):
            return True
        return False

    # --- Internal helpers ---
    def _compute_integrity_hash(self, *, user_id: int, product_id: str, amount: int, quantity: int, kind: str, receipt_code: str, ts: int) -> str:
        raw = f"{user_id}|{product_id}|{amount}|{quantity}|{kind}|{receipt_code}|{ts}".encode()
        return hashlib.sha256(raw).hexdigest()

    def _sign_receipt(self, receipt_code: str, integrity_hash: str) -> str:
        base = f"{receipt_code}|{integrity_hash}".encode()
        return hmac.new(self.hmac_secret, base, hashlib.sha256).hexdigest()


__all__ = [
    "SettlementService",
    "SettlementResult",
]
