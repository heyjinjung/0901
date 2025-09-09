"""
Routers package initialization.

Keep this file minimal to avoid circular imports and import-time side effects.
FastAPI app imports submodules directly (e.g., `from app.routers import auth`).
Python will auto-import `app.routers.<name>` when referenced, so we don't import
submodules here.
"""

# Optionally define the public submodules for linters/type-checkers. This list
# intentionally includes only stable routers known to exist in this codebase.
__all__ = [
    "auth",
    "users",
    "admin",
    "actions",
    "rewards",
    "shop",
    "missions",
    "quiz",
    "dashboard",
    "rps",
    "notifications",
    "doc_titles",
    "feedback",
    "games",
    "invite_router",
    "rbac_demo",
    "analyze",
    "segments",
    "tracking",
    "unlock",
    "ai_router",
    "chat",
    "events",
    "notification",
]