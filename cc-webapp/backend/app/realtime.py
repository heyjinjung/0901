import asyncio
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, Set, Deque, Optional, Any

from fastapi import WebSocket


@dataclass
class _WSMeta:
    topics: Set[str] = field(default_factory=set)
    last_seen: float = 0.0


class ConnectionManager:
    """Unified real-time connection manager for WS and SSE.

    Features:
    - Multiple connections per user (multi-tab/multi-device)
    - Topic-based multiplexing (subscriptions per connection)
    - Per-user priority queue with bounded buffer and backfill
    - Basic keepalive/heartbeat helpers
    """

    def __init__(self):
        # WebSocket connections per user
        self.ws_connections: Dict[int, Set[WebSocket]] = defaultdict(set)
        self.ws_meta: Dict[int, Dict[int, _WSMeta]] = defaultdict(dict)  # user_id -> {id(ws): meta}
        # SSE queues per user (each consumer gets its own queue)
        self.sse_queues: Dict[int, Set[asyncio.PriorityQueue]] = defaultdict(set)
        # In-memory backfill buffer per user (latest N)
        self.backfill: Dict[int, Deque[dict]] = defaultdict(lambda: deque(maxlen=200))
        # Simple event id counter per user (for SSE Last-Event-ID)
        self._event_seq: Dict[int, int] = defaultdict(int)
        # Lock for concurrent modifications
        self._lock = asyncio.Lock()

    async def connect_ws(self, websocket: WebSocket, user_id: int, topics: Optional[Set[str]] = None):
        await websocket.accept()
        async with self._lock:
            self.ws_connections[user_id].add(websocket)
            self.ws_meta[user_id][id(websocket)] = _WSMeta(topics=topics or set())

    async def disconnect_ws(self, user_id: int, websocket: WebSocket):
        async with self._lock:
            conns = self.ws_connections.get(user_id)
            if conns and websocket in conns:
                conns.remove(websocket)
            if user_id in self.ws_meta:
                self.ws_meta[user_id].pop(id(websocket), None)

    async def update_ws_topics(self, user_id: int, websocket: WebSocket, topics: Optional[Set[str]]):
        """Update topic subscriptions for a specific WebSocket connection."""
        async with self._lock:
            meta = self.ws_meta[user_id].get(id(websocket))
            if meta is not None:
                meta.topics = topics or set()

    async def touch_ws(self, user_id: int, websocket: WebSocket):
        """Update last_seen timestamp for a specific WebSocket connection."""
        async with self._lock:
            meta = self.ws_meta[user_id].get(id(websocket))
            if meta is not None:
                # Monotonic time preferred, fallback to loop time
                try:
                    meta.last_seen = asyncio.get_running_loop().time()
                except RuntimeError:
                    meta.last_seen = 0.0

    async def register_sse(self, user_id: int) -> asyncio.PriorityQueue:
        """Register an SSE client and return its personal priority queue."""
        q: asyncio.PriorityQueue = asyncio.PriorityQueue(maxsize=500)
        async with self._lock:
            self.sse_queues[user_id].add(q)
        return q

    async def unregister_sse(self, user_id: int, q: asyncio.PriorityQueue):
        async with self._lock:
            if user_id in self.sse_queues and q in self.sse_queues[user_id]:
                self.sse_queues[user_id].remove(q)

    def _next_event_id(self, user_id: int) -> int:
        self._event_seq[user_id] += 1
        return self._event_seq[user_id]

    async def enqueue(self, user_id: int, message: dict, priority: int = 0, topic: Optional[str] = None):
        """Enqueue a message for a user for both WS and SSE clients.

        Lower numeric priority value means higher priority in PriorityQueue.
        """
        payload = {
            "id": self._next_event_id(user_id),
            "topic": topic or "default",
            "priority": priority,
            "data": message,
        }
        # Backfill buffer
        self.backfill[user_id].append(payload)

        # SSE: put into each queue (non-blocking best-effort)
        for q in list(self.sse_queues.get(user_id, [])):
            try:
                q.put_nowait((priority, payload))
            except Exception:
                # Drop if queue full or closed
                pass

        # WS: send immediately to subscribed connections (topic filter)
        for ws in list(self.ws_connections.get(user_id, [])):
            meta = self.ws_meta[user_id].get(id(ws))
            if meta and meta.topics and (payload["topic"] not in meta.topics):
                continue
            try:
                await ws.send_json(payload)
            except Exception:
                # Drop broken connection on send failure
                await self.disconnect_ws(user_id, ws)

    async def broadcast(self, message: dict, priority: int = 5, topic: Optional[str] = None):
        # Broadcast to all users (best-effort)
        user_ids = list(set(list(self.ws_connections.keys()) + list(self.sse_queues.keys())))
        for uid in user_ids:
            await self.enqueue(uid, message, priority=priority, topic=topic)

    def get_backfill(self, user_id: int, last_event_id: Optional[int] = None) -> Deque[dict]:
        if last_event_id is None:
            return self.backfill[user_id]
        # Return items with id greater than last_event_id
        return deque([e for e in self.backfill[user_id] if int(e.get("id", 0)) > int(last_event_id)], maxlen=200)


manager = ConnectionManager()
