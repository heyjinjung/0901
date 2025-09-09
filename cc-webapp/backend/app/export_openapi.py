#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Export current OpenAPI schema to project root for syncing with frontend/docs.
Usage: python -m app.export_openapi

This implementation uses app.openapi() directly to avoid potential incompatibilities
between Starlette's TestClient and the installed HTTP client libraries in runtime.
"""
import json
import os
import sys
from datetime import datetime

# Ensure 'app' package import works when run from different CWDs
HERE = os.path.dirname(os.path.abspath(__file__))
BACKEND_ROOT = os.path.dirname(HERE)
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app.main import app


def main() -> None:
    # Invalidate cached schema so newly added routes are included
    try:
        app.openapi_schema = None  # type: ignore[attr-defined]
    except Exception:
        pass
    schema = app.openapi()
    # Always update canonical file under backend root (cc-webapp/backend/current_openapi.json)
    canonical_path = os.path.join(BACKEND_ROOT, "current_openapi.json")
    with open(canonical_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, ensure_ascii=False, indent=2)

    # Also place a copy under the package directory for legacy/test compatibility
    # Path: cc-webapp/backend/app/current_openapi.json (inside container: /app/app/current_openapi.json)
    app_local_path = os.path.join(HERE, "current_openapi.json")
    try:
        with open(app_local_path, "w", encoding="utf-8") as f:
            json.dump(schema, f, ensure_ascii=False, indent=2)
    except Exception as e:
        # Non-fatal; tests may still rely on canonical
        print(f"[warn] failed to write app-local current_openapi.json: {e}")

    # Timestamped snapshot for change tracking (backend root)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    snapshot_path = os.path.join(BACKEND_ROOT, f"openapi_{ts}.json")
    with open(snapshot_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, ensure_ascii=False, indent=2)

    # Stable snapshot name under app/ to enable simple diff in CI if desired
    app_snapshot_path = os.path.join(HERE, "openapi_snapshot.json")
    try:
        with open(app_snapshot_path, "w", encoding="utf-8") as f:
            json.dump(schema, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[warn] failed to write app-local openapi_snapshot.json: {e}")

    print(
        "✅ Exported OpenAPI:\n"
        f"  - canonical={canonical_path}\n"
        f"  - app_current={app_local_path}\n"
        f"  - snapshot(ts)={snapshot_path}\n"
        f"  - app_snapshot={app_snapshot_path}"
    )


if __name__ == "__main__":
    main()
