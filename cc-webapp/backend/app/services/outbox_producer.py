import json
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from .event_service import logger  # reuse existing logger

# 간단한 Outbox enqueue 유틸 (Phase B 초안)

def enqueue_outbox(
    db: Session,
    event_type: str,
    payload: Dict[str, Any],
    schema_version: int = 1,
    dedupe_key: Optional[str] = None,
):
    """event_outbox 테이블에 이벤트 행 삽입.
    트랜잭션 내부에서 호출하여 도메인 변경과 원자적으로 기록.
    published_at NULL 행은 후속 publisher 가 처리.
    """
    # 느슨한 검증
    if not isinstance(payload, dict):
        raise ValueError("payload must be dict")
    record = {
        'event_type': event_type,
        'payload': payload,
        'schema_version': schema_version,
        'dedupe_key': dedupe_key,
        'created_at': datetime.utcnow(),
    }
    db.execute(
        """
        INSERT INTO event_outbox (event_type, payload, schema_version, dedupe_key, created_at)
        VALUES (:event_type, CAST(:payload AS JSONB), :schema_version, :dedupe_key, :created_at)
        """,
        {
            'event_type': event_type,
            'payload': json.dumps(payload),
            'schema_version': schema_version,
            'dedupe_key': dedupe_key,
            'created_at': record['created_at']
        }
    )
    logger.debug("enqueue_outbox", extra={"event_type": event_type, "dedupe_key": dedupe_key})
