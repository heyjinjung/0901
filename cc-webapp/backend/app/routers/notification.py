from fastapi import APIRouter, Header
from typing import Dict, Optional
from jose import jwt, JWTError

# Lightweight stub for frontend to avoid 404 while notification service is small.
# This route allows anonymous access; when an Authorization header with a valid
# Bearer token is present, we try to extract the user id from the token payload.
from ..auth.auth_service import JWT_SECRET_KEY, JWT_ALGORITHM

router = APIRouter(prefix="/api/notification", tags=["Notification Center"])


@router.get("/settings/anon")
def get_notification_settings_anon(authorization: Optional[str] = Header(None)) -> Dict:
    """Return default notification settings; include user_id when available.

    This endpoint intentionally allows anonymous requests and will not trigger
    the global HTTPBearer auto_error behavior.
    """
    default = {
        "email": True,
        "push": True,
        "in_app": True,
        "daily_summary": False,
    }

    user_id = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            user_id = payload.get("sub") or payload.get("user_id")
        except JWTError:
            # ignore invalid tokens for this lightweight stub
            user_id = None

    return {"scope": "anon", "user_id": user_id, "settings": default}
