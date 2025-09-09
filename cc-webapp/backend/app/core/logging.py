import logging
import json
import sys
import time
import uuid
from datetime import datetime
from contextvars import ContextVar
from typing import Dict, Any, Optional

# Context variables propagated across the request lifecycle
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")
path_ctx: ContextVar[str] = ContextVar("path", default="-")
method_ctx: ContextVar[str] = ContextVar("method", default="-")
user_id_ctx: ContextVar[Optional[str]] = ContextVar("user_id", default=None)
client_ip_ctx: ContextVar[str] = ContextVar("client_ip", default="-")
status_code_ctx: ContextVar[int] = ContextVar("status_code", default=0)
latency_ms_ctx: ContextVar[float] = ContextVar("latency_ms", default=0.0)

def get_logger(name: str):
    return logging.getLogger(name)

def log_error(exc: Exception, context: Dict[str, Any] = None):
    logger = get_logger("error")
    logger.error(f"Error: {str(exc)}", extra=context or {})

def log_service_call(service_name: str, operation: str, duration: float = None, status: str = "success", extra: Dict[str, Any] = None):
    """서비스 호출 로깅 함수"""
    logger = get_logger("service_calls")
    log_data = {
        "service": service_name,
        "operation": operation,
        "status": status,
        "timestamp": datetime.utcnow().isoformat(),
        **(extra or {})
    }
    
    if duration is not None:
        log_data["duration_ms"] = round(duration * 1000, 2)
    
    logger.info(f"Service call: {service_name}.{operation} - {status}", extra=log_data)

class JSONLogFormatter(logging.Formatter):
    """Lightweight JSON formatter adding contextvars and standard fields."""

    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        base = {
            "ts": datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": request_id_ctx.get(),
            "path": path_ctx.get(),
            "method": method_ctx.get(),
            "user_id": user_id_ctx.get(),
            "client_ip": client_ip_ctx.get(),
            "status_code": status_code_ctx.get() or None,
            "latency_ms": round(latency_ms_ctx.get(), 2) or None,
        }
        # Include extra attributes that aren't standard
        for k, v in record.__dict__.items():
            if k.startswith('_'):
                continue
            if k in base or k in ('msg', 'args', 'levelname', 'levelno', 'pathname', 'filename', 'module', 'exc_info', 'exc_text', 'stack_info', 'lineno', 'funcName', 'created', 'msecs', 'relativeCreated', 'thread', 'threadName', 'processName', 'process'):
                continue
            base[k] = v
        if record.exc_info:
            base["exc_type"] = record.exc_info[0].__name__ if record.exc_info[0] else None
        return json.dumps(base, ensure_ascii=False)


def setup_logging(level: str = "INFO", json_logs: bool = True):
    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    # Clear existing handlers (idempotent setup)
    if root.handlers:
        for h in list(root.handlers):
            root.removeHandler(h)
    handler = logging.StreamHandler(sys.stdout)
    if json_logs:
        handler.setFormatter(JSONLogFormatter())
    else:
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    root.addHandler(handler)
    logging.getLogger("uvicorn.access").propagate = False  # reduce duplicate access logs

class LoggingContextMiddleware:
    """ASGI middleware injecting request scoped context into contextvars for structured logs."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http":
            return await self.app(scope, receive, send)
        start = time.time()
        req_id = uuid.uuid4().hex[:12]
        request_id_ctx.set(req_id)
        path_ctx.set(scope.get("path") or "-")
        method_ctx.set(scope.get("method") or "-")
        client = "-"
        if scope.get("client"):
            client = f"{scope['client'][0]}:{scope['client'][1]}"
        client_ip_ctx.set(client)

        # Capture status code from send events
        async def send_wrapper(message):
            if message.get('type') == 'http.response.start':
                status_code_ctx.set(message.get('status'))
            return await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            latency_ms_ctx.set((time.time() - start) * 1000.0)
            # Emit a single access log line (INFO) at request end
            logging.getLogger("access").info(
                "request complete",
                extra={
                    "event": "request_end",
                }
            )
