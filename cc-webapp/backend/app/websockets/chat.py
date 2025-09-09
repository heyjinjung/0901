"""WebSocket connection and message management with per-user sessions."""

import logging
from collections import defaultdict, deque
from typing import Any, Deque, Dict, Set

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Manages WebSocket connections per user with support for:
    - Multiple concurrent connections per user (tabs/devices)
    - Personal messaging and broadcast
    - Offline in-memory buffering and flush on reconnect
    - Simple disconnect handling
    """

    def __init__(self) -> None:
        # user_id -> set of active sockets
        self._connections: Dict[int, Set[WebSocket]] = defaultdict(set)
        # user_id -> fifo queue of pending messages (JSON-serializable)
        self._offline_queue: Dict[int, Deque[Any]] = defaultdict(deque)

    async def connect(self, websocket: WebSocket, user_id: int) -> None:
        await websocket.accept()
        self._connections[user_id].add(websocket)
        # best-effort flush queued messages
        await self.flush_offline(user_id)

    def disconnect(self, user_id: int, websocket: WebSocket | None = None) -> None:
        if websocket is None:
            # remove all sockets for the user
            if user_id in self._connections:
                self._connections.pop(user_id, None)
            return
        try:
            conns = self._connections.get(user_id)
            if conns and websocket in conns:
                conns.remove(websocket)
                if not conns:
                    self._connections.pop(user_id, None)
        except Exception:
            logger.warning("Error during websocket disconnect cleanup", exc_info=True)

    async def broadcast(self, message: Any) -> None:
        # send to every connected socket
        dead: list[tuple[int, WebSocket]] = []
        for uid, conns in list(self._connections.items()):
            for ws in list(conns):
                try:
                    await ws.send_json(message)
                except Exception:
                    dead.append((uid, ws))
        for uid, ws in dead:
            self.disconnect(uid, ws)

    async def send_personal_message(self, message: Any, user_id: int) -> None:
        conns = self._connections.get(user_id)
        if not conns:
            # buffer offline
            self._offline_queue[user_id].append(message)
            return
        dead: list[WebSocket] = []
        for ws in list(conns):
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(user_id, ws)

    async def flush_offline(self, user_id: int) -> None:
        if user_id not in self._offline_queue:
            return
        while self._offline_queue[user_id]:
            msg = self._offline_queue[user_id].popleft()
            await self.send_personal_message(msg, user_id)
        # cleanup empty
        if not self._offline_queue[user_id]:
            self._offline_queue.pop(user_id, None)

    async def send_bulk(self, user_id: int, messages: list[Any]) -> None:
        for m in messages:
            await self.send_personal_message(m, user_id)
