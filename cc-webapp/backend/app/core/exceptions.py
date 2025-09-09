"""Domain exception hierarchy for consistent error handling.

Each exception exposes:
  - code: stable machine-readable error code (SNAKE_CASE)
  - message: human readable message (client safe)
  - status_code: default HTTP status to map

Handlers will translate these into the standard error response schema:
{ "error": {"code": str, "message": str, "details": Optional[Any], "request_id": str } }
"""

from typing import Any, Optional

class BaseDomainError(Exception):
	code = "DOMAIN_ERROR"
	status_code = 400

	def __init__(self, message: Optional[str] = None, *, code: Optional[str] = None, status_code: Optional[int] = None, details: Any = None):
		self.message = message or getattr(self, "default_message", "Domain error")
		if code:
			self.code = code
		if status_code is not None:
			self.status_code = status_code
		self.details = details
		super().__init__(self.message)

	def to_dict(self):
		return {"code": self.code, "message": self.message, "details": self.details}


class ValidationError(BaseDomainError):
	code = "VALIDATION_ERROR"
	status_code = 422
	default_message = "Validation failed"


class AuthError(BaseDomainError):
	code = "AUTH_ERROR"
	status_code = 401
	default_message = "Authentication failed"


class AuthorizationError(BaseDomainError):
	code = "AUTHORIZATION_ERROR"
	status_code = 403
	default_message = "Not authorized"


class NotFoundError(BaseDomainError):
	code = "NOT_FOUND"
	status_code = 404
	default_message = "Resource not found"


class ConflictError(BaseDomainError):
	code = "CONFLICT"
	status_code = 409
	default_message = "Conflict"


class RateLimitError(BaseDomainError):
	code = "RATE_LIMIT"
	status_code = 429
	default_message = "Too many requests"


class ServiceError(BaseDomainError):
	code = "SERVICE_ERROR"
	status_code = 503
	default_message = "Service unavailable"


class GameLogicError(BaseDomainError):
	code = "GAME_LOGIC_ERROR"
	status_code = 400
	default_message = "Invalid game logic state"

class UserServiceException(BaseDomainError):
	code = "USER_SERVICE_ERROR"
	status_code = 400
	default_message = "User service error"


__all__ = [
	"BaseDomainError",
	"ValidationError",
	"AuthError",
	"AuthorizationError",
	"NotFoundError",
	"ConflictError",
	"RateLimitError",
	"ServiceError",
	"GameLogicError",
	"UserServiceException",
]

