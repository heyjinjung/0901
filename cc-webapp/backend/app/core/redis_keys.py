"""Redis 키 네이밍 전략 표준화 모듈

용도별 Prefix 규칙 (콜론 구분, 상위→하위 스코프):
- idemp: 구매/보상 등 멱등 처리
- limited: 한정 패키지 재고/홀드
- fraud: 결제 Fraud 속도 제어 관련 윈도우 집계
- webhook: 외부 웹훅 재생/이벤트 멱등
- purchase: 일반 구매 프로세스 상태
- streak / gacha / slot 등 게임 도메인 키는 기존 관례 유지

패턴 가이드:
1) idempotency (구매): idemp:purchase:<user_id>:<idem_key>
2) idempotency (reward): idemp:reward:<user_id>:<idem_key>
3) 한정패키지 재고 홀드: limited:hold:<package_id>:<hold_id>
4) 한정패키지 재고 카운터: limited:stock:<package_id>
5) Fraud 속도 (전체 요청 타임스탬프 ZSET): fraud:req:ts:<user_id>
6) Fraud distinct 카드토큰 SET: fraud:cardtokens:<user_id>
7) Webhook timestamp+nonce 재생 방지: webhook:replay:<ts>:<nonce>
8) Webhook event idempotency: webhook:event:<event_id>
9) Pending 결제 폴링 락: purchase:pending:lock:<tx_id>

TTL 권장값 요약:
- 멱등키(idemp:*) : settings.IDEMPOTENCY_TTL_SECONDS (기본 600s)
- 한정패키지 hold: settings.LIMITED_HOLD_TTL_SECONDS (만료 시 재고 반환)
- webhook:replay/* : 5분 (요청 skew 범위) → 300s
- webhook:event:* : 24h (이벤트 중복 방어 충분 기간)
- fraud:* : 5분 롤링 윈도우 (동일 300s)

함수는 호출부에서 문자열 포맷 실수를 줄이고, IDE 검색/리팩토링 용이성을 높인다.
"""
from __future__ import annotations

def idemp_purchase(user_id: int, idem_key: str) -> str:
    return f"idemp:purchase:{user_id}:{idem_key}".lower()

def idemp_reward(user_id: int, idem_key: str) -> str:
    return f"idemp:reward:{user_id}:{idem_key}".lower()

def limited_hold(package_id: str, hold_id: str) -> str:
    return f"limited:hold:{package_id}:{hold_id}".lower()

def limited_stock(package_id: str) -> str:
    return f"limited:stock:{package_id}".lower()

def fraud_req_ts(user_id: int) -> str:
    return f"fraud:req:ts:{user_id}".lower()

def fraud_cardtokens(user_id: int) -> str:
    return f"fraud:cardtokens:{user_id}".lower()

def webhook_replay(ts: int, nonce: str) -> str:
    return f"webhook:replay:{ts}:{nonce}".lower()

def webhook_event(event_id: str) -> str:
    return f"webhook:event:{event_id}".lower()

def purchase_pending_lock(tx_id: str) -> str:
    return f"purchase:pending:lock:{tx_id}".lower()

__all__ = [
    "idemp_purchase","idemp_reward","limited_hold","limited_stock","fraud_req_ts",
    "fraud_cardtokens","webhook_replay","webhook_event","purchase_pending_lock"
]
