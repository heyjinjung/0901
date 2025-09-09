"""GameHistory 로깅 유틸리티

단일 책임:
- 게임 관련 액션(베팅, 승리, 세션 이벤트 등)을 game_history 테이블에 기록
- 추후 이벤트 브로드캐스트(WS/Kafka) 훅 연동 지점 주석 표시
"""
from __future__ import annotations
from typing import Any, Optional, Dict
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from ..models.history_models import GameHistory
from .achievement_service import AchievementService
def _lazy_broadcast_game_history_event():
    try:
        from app import main  # type: ignore
        return getattr(main, "broadcast_game_history_event", None)
    except Exception:  # pragma: no cover
        async def _noop(_):
            return None
        return _noop
import logging

logger = logging.getLogger(__name__)

def log_game_history(
    db: Session,
    *,
    user_id: int,
    game_type: str,
    action_type: str,
    delta_coin: int = 0,
    delta_gem: int = 0,
    session_id: Optional[int] = None,
    result_meta: Optional[Dict[str, Any]] = None,
) -> Optional[GameHistory]:
    """GameHistory 레코드 생성 (오류 시 롤백 후 None 반환).

    Parameters:
        user_id: 사용자 ID
        game_type: 'slot' | 'rps' | 'gacha' | 'crash' 등
        action_type: BET / WIN / LOSE / BONUS / JACKPOT / SESSION_START / SESSION_END 등
        delta_coin: 코인 변화량(증가=양수, 감소=음수)
        delta_gem: 젬 변화량
        session_id: 관련 세션 PK (없으면 None)
        result_meta: 추가 메타(JSON 직렬화 가능한 dict)
    """
    try:
        record = GameHistory(
            user_id=user_id,
            game_type=game_type,
            session_id=session_id,
            action_type=action_type,
            delta_coin=delta_coin,
            delta_gem=delta_gem,
            result_meta=result_meta,
        )
        db.add(record)
        db.commit()
        # 비동기 브로드캐스트 (실패 허용) - 이벤트 최소 페이로드
        try:
            payload = {
                "user_id": user_id,
                "game_type": game_type,
                "action_type": action_type,
                "delta_coin": delta_coin,
                "delta_gem": delta_gem,
                "session_id": session_id,
                "id": record.id,
                "created_at": record.created_at.isoformat() if record.created_at else None,
            }
            # 이벤트 루프 존재 시 create_task, 아니면 무시
            loop = asyncio.get_event_loop()
            if loop.is_running():
                broadcast_game_history_event = _lazy_broadcast_game_history_event()
                loop.create_task(broadcast_game_history_event(payload))
        except Exception as be:  # pragma: no cover
            logger.debug("Broadcast schedule failed: %s", be)
        return record
    except SQLAlchemyError as e:
        db.rollback()
        logger.warning("GameHistory 로그 실패 user=%s action=%s err=%s", user_id, action_type, e)
        return None

    # 업적 평가 비동기 실행 (commit 후)
    try:
        if record:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                def _eval():
                    # 새 세션 열어야 하지만 간단히 동일 세션 재사용 (스레드 안전성 보강 필요 시 SessionLocal())
                    svc = AchievementService(db)
                    svc.evaluate_after_history(record)
                loop.run_in_executor(None, _eval)
    except Exception:  # pragma: no cover
        logger.debug("Achievement evaluation scheduling failed", exc_info=True)
