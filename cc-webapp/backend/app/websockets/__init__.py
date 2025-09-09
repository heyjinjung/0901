"""Deprecated shim: prefer app.realtime.hub

기존 `manager` 명칭을 사용하던 코드가 있을 수 있어 hub 기반의 호환 어댑터를 제공합니다.
가능하면 새로운 허브(app.realtime.hub.hub) API를 직접 사용하세요.
"""
from __future__ import annotations

from typing import Any, Dict

from ..realtime.hub import hub  # 최신 허브
from .chat import WebSocketManager  # 레거시 매니저 클래스 (완전 대체 전까지 유지)


class _CompatManager:
	"""레거시 manager 호환 어댑터.

	- send_personal_message(msg, user_id): hub.broadcast 로 대체 (user_id 타겟팅)
	- broadcast(msg): hub.broadcast 로 브로드캐스트 (user_id 없을 시 모니터 채널만 수신)
	"""

	async def send_personal_message(self, message: Any, user_id: int) -> None:  # noqa: D401
		data: Dict[str, Any]
		if isinstance(message, dict) and "type" in message:
			# 기존 payload 키를 data로 정규화
			if "payload" in message and "data" not in message:
				msg = dict(message)
				payload = msg.pop("payload")
				data = {**msg, "data": payload, "user_id": user_id}
			else:
				data = {**message, "user_id": user_id}
		else:
			data = {"type": "message", "data": message, "user_id": user_id}
		await hub.broadcast(data)

	async def broadcast(self, message: Any) -> None:
		if isinstance(message, dict):
			await hub.broadcast(message)
		else:
			await hub.broadcast({"type": "message", "data": message})


# 호환 alias (과거 import 경로 유지)
manager = _CompatManager()

