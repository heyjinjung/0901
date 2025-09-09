"""Deprecated: use app.realtime.manager instead.

This module remains as a shim to prevent import errors from older paths.
It re-exports the unified real-time manager from app.realtime.
"""

from .realtime import manager  # noqa: F401
