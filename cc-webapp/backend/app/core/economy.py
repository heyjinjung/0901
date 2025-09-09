"""Economy feature flags and helpers.

Provides a minimal is_v2_active(settings) function used by catalog_service
and games routes. If the function was missing (AttributeError in tests),
this file restores expected API.

Activation rules (simple, extend later):
 1. ENV var ECONOMY_V2=1 or =true (case-insensitive)
 2. settings.ECONOMY_V2 (bool/int/str truthy) if present
Defaults to False.
"""
from __future__ import annotations
import os
from typing import Any

_DEF_FALSE = {"0", "false", "off", "no"}
_DEF_TRUE = {"1", "true", "on", "yes"}

def _coerce_bool(val: Any) -> bool:
    if isinstance(val, bool):
        return val
    if val is None:
        return False
    if isinstance(val, (int,)):
        return val != 0
    try:
        s = str(val).strip().lower()
    except Exception:
        return False
    if s in _DEF_TRUE:
        return True
    if s in _DEF_FALSE:
        return False
    return False

def is_v2_active(settings) -> bool:  # settings: app.core.config.settings
    # Order: explicit env var beats settings attribute
    env_val = os.getenv("ECONOMY_V2")
    if env_val is not None:
        return _coerce_bool(env_val)
    attr = getattr(settings, "ECONOMY_V2", None)
    return _coerce_bool(attr)

__all__ = ["is_v2_active"]
