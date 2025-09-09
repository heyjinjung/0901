"""간단 인메모리 WebSocket 브로드캐스터 (MVP)

확장 고려 사항 (미구현/주석):
- Redis Pub/Sub 또는 Kafka로 교체 시 이 모듈의 인터페이스 유지
- backpressure / queue size 제한, disconnect GC 추가 예정
"""
from __future__ import annotations

import asyncio
import time
import os
from typing import Dict, Set, Any
try:  # optional prometheus metrics
    from prometheus_client import Gauge, Counter  # type: ignore
    _REALTIME_ACTIVE_USERS = Gauge("realtime_active_users", "Active users with WS connections")
    _REALTIME_EVENTS_TOTAL = Counter("realtime_events_total", "Total realtime events broadcasted")
except Exception:  # pragma: no cover
    _REALTIME_ACTIVE_USERS = None
    _REALTIME_EVENTS_TOTAL = None

class RealtimeHub:
    def __init__(self) -> None:
        # user_id -> set(WebSocket-like) ; WebSocket은 .send_text(str) 지원 필요
        self._user_channels: Dict[int, Set[Any]] = {}
        # monitor(관리) 채널(전체 세션 관찰)
        self._monitor: Set[Any] = set()
        self._lock = asyncio.Lock()
        # 최근 이벤트 메모리 (간단 sliding window)
        self._recent_events: list[dict[str, Any]] = []
        self._max_recent = 200
        # 퍼유저 스로틀: user_id -> 마지막 전송 epoch(float)
        self._last_emit: Dict[int, float] = {}
        # 최소 인터벌 초 (환경변수 REALTIME_USER_MIN_INTERVAL_MS, 기본 300ms)
        try:
            ms = float(os.getenv("REALTIME_USER_MIN_INTERVAL_MS", "300"))
        except ValueError:
            ms = 300.0
        self._min_interval = ms / 1000.0

    async def register_user(self, user_id: int, ws: Any) -> None:
        async with self._lock:
            self._user_channels.setdefault(user_id, set()).add(ws)
            if _REALTIME_ACTIVE_USERS is not None:
                try:
                    _REALTIME_ACTIVE_USERS.set(len(self._user_channels))
                except Exception:
                    pass

    async def unregister_user(self, user_id: int, ws: Any) -> None:
        async with self._lock:
            bucket = self._user_channels.get(user_id)
            if bucket and ws in bucket:
                bucket.remove(ws)
                if not bucket:
                    self._user_channels.pop(user_id, None)
            if _REALTIME_ACTIVE_USERS is not None:
                try:
                    _REALTIME_ACTIVE_USERS.set(len(self._user_channels))
                except Exception:
                    pass

    async def register_monitor(self, ws: Any) -> None:
        async with self._lock:
            self._monitor.add(ws)

    async def unregister_monitor(self, ws: Any) -> None:
        async with self._lock:
            self._monitor.discard(ws)

    def _remember(self, event: dict[str, Any]) -> None:
        event.setdefault("ts", time.time())
        self._recent_events.append(event)
        if len(self._recent_events) > self._max_recent:
            # 앞부분 트림
            self._recent_events = self._recent_events[-self._max_recent :]

    async def broadcast(self, event: dict[str, Any]) -> None:
        """모니터 + 사용자 타겟 브로드캐스트.
        event 예시: {"type":"game_event","user_id":123,"game_type":"slot", ...}
        """
        self._remember(event)
        if _REALTIME_EVENTS_TOTAL is not None:
            try:
                _REALTIME_EVENTS_TOTAL.inc()
            except Exception:
                pass
        text = None
        try:
            import json
            text = json.dumps(event, default=str)
        except Exception:
            return
        targets: Set[Any] = set()
        async with self._lock:
            uid = event.get("user_id")
            # 스로틀 적용(모니터 채널 제외) - user_id가 있고 type이 balance_update/reward_grant/game_session/game_event 등 빈번 이벤트인 경우
            throttled = False
            if uid in self._user_channels:
                if uid is not None and self._min_interval > 0:
                    now = time.time()
                    last = self._last_emit.get(uid, 0.0)
                    # 이벤트 타입 화이트리스트(스로틀 적용 대상)
                    evt_type = event.get("type")
                    if evt_type in {"reward_grant", "balance_update", "game_session", "game_event"}:
                        if (now - last) < self._min_interval:
                            throttled = True
                        else:
                            self._last_emit[uid] = now
                if not throttled:
                    targets |= self._user_channels[uid]
            targets |= self._monitor
        if not targets:
            return
        coros = []
        for ws in list(targets):
            try:
                coros.append(ws.send_text(text))
            except Exception:
                # 개별 오류 무시
                pass
        if coros:
            await asyncio.gather(*coros, return_exceptions=True)

    async def snapshot_for_monitor(self) -> dict[str, Any]:
        async with self._lock:
            return {
                "type": "monitor_snapshot",
                "active_users": len(self._user_channels),
                "connections": sum(len(v) for v in self._user_channels.values()),
                "recent_events": self._recent_events[-20:],
            }

# 전역 싱글톤 (애플리케이션 기동 시 main에서 import)
hub = RealtimeHub()

async def broadcast_game_session_event(event: dict[str, Any]) -> None:
    # 기존 games.py에서 lazy import로 호출
    await hub.broadcast({"type": "game_session", **event})
