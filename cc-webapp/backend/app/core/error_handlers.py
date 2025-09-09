import logging
from typing import Dict, Any
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_422_UNPROCESSABLE_ENTITY
from app.core.exceptions import (
    BaseDomainError,
    ValidationError,
)
from app.core.logging import request_id_ctx

logger = logging.getLogger("errors")

STANDARD_CONTENT_TYPE = "application/json"

def _error_payload(code: str, message: str, *, request_id: str, details: Any = None):
    return {"error": {"code": code, "message": message, "details": details, "request_id": request_id}}


def add_exception_handlers(app):
    """Register global exception handlers on the FastAPI app."""

    @app.exception_handler(BaseDomainError)
    async def domain_error_handler(request: Request, exc: BaseDomainError):  # type: ignore
        rid = request_id_ctx.get()
        logger.warning(f"DomainError {exc.code}: {exc.message}", extra={"request_id": rid, "path": request.url.path})
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(exc.code, exc.message, request_id=rid, details=exc.details),
            media_type=STANDARD_CONTENT_TYPE,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):  # type: ignore
        rid = request_id_ctx.get()
        logger.info("Request validation failed", extra={"request_id": rid, "errors": exc.errors()})
        vexc = ValidationError(details=exc.errors())
        return JSONResponse(
            status_code=vexc.status_code,
            content=_error_payload(vexc.code, vexc.message, request_id=rid, details=vexc.details),
            media_type=STANDARD_CONTENT_TYPE,
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):  # type: ignore
        rid = request_id_ctx.get()
        code = f"HTTP_{exc.status_code}"
        logger.info("HTTPException", extra={"request_id": rid, "status": exc.status_code, "detail": exc.detail})
        # Preserve existing structured 'error' payload while also providing a top-level
        # 'detail' field because some tests and clients expect it.
        payload = _error_payload(code, str(exc.detail), request_id=rid)
        # Add a convenience top-level 'detail' for compatibility
        payload_top = {"detail": str(exc.detail)}
        # Merge: keep both keys
        merged = {**payload_top, **payload}
        return JSONResponse(
            status_code=exc.status_code,
            content=merged,
            media_type=STANDARD_CONTENT_TYPE,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):  # type: ignore
        rid = request_id_ctx.get()
        logger.exception("Unhandled exception", extra={"request_id": rid})
        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_payload("INTERNAL_ERROR", "Internal server error", request_id=rid),
            media_type=STANDARD_CONTENT_TYPE,
        )

__all__ = ["add_exception_handlers"]
