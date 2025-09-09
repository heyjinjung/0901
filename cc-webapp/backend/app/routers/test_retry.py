from fastapi import APIRouter, HTTPException
from app.core.config import settings
import time

router = APIRouter(prefix="/api/test", tags=["test"], include_in_schema=False)


def _dev_only_guard():
    if settings.ENVIRONMENT not in ("development", "local", "dev", "test"):
        # 운영에서 노출 금지
        raise HTTPException(status_code=403, detail="development only")


@router.get("/retry-429")
async def retry_429(count: int = 1, wait_ms: int = 0):
    """
    테스트 전용: 처음 count-1 회는 429 Too Many Requests를 반환하고, 마지막 1회는 200 OK를 반환합니다.
    쿼리 파라미터 count로 실패 횟수 조정, wait_ms로 인위적 지연을 넣어 백오프 관찰 가능.
    상태는 프로세스 전역 카운터에 저장하지 않고, 단발성 호출로 간단 검증만 지원.
    """
    _dev_only_guard()
    try:
        c = max(1, int(count))
    except Exception:
        c = 2
    # 호출 시도 횟수를 쿼리의 count에 의존하는 단순 모형: c>1이면 429, c==1이면 200
    # 실제 재시도 검증은 클라이언트가 동일 URL을 재호출하며 count를 1씩 감소시키는 방식으로 사용
    if wait_ms > 0:
        try:
            time.sleep(min(2.0, wait_ms / 1000.0))
        except Exception:
            pass
    if c > 1:
        raise HTTPException(status_code=429, detail={"hint": "retry with count-1"})
    return {"ok": True, "detail": "recovered after retries"}


@router.get("/retry-500")
async def retry_500(count: int = 1, wait_ms: int = 0):
    """
    테스트 전용: 처음 count-1 회는 500 Internal Server Error를 반환하고, 마지막 1회는 200 OK 반환.
    클라이언트는 동일 URL을 재호출하며 count를 1씩 감소시키는 방식으로 백오프 재시도 로직을 검증할 수 있음.
    """
    _dev_only_guard()
    try:
        c = max(1, int(count))
    except Exception:
        c = 2
    if wait_ms > 0:
        try:
            time.sleep(min(2.0, wait_ms / 1000.0))
        except Exception:
            pass
    if c > 1:
        raise HTTPException(status_code=500, detail={"hint": "retry with count-1"})
    return {"ok": True, "detail": "recovered after retries"}
