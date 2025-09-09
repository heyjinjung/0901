"""Seed account smoke: login -> RPS play -> optional shop buy.

Run inside backend container:
  docker compose exec backend python -m app.scripts.smoke_seed_activity
"""
from __future__ import annotations

import os
import sys
import json
from typing import Any, Dict

def _print(obj: Any):
    try:
        print(json.dumps(obj, ensure_ascii=False))
    except Exception:
        print(str(obj))

def main():
    import requests
    # Ensure seeds exist (idempotent)
    try:
        from app.scripts import seed_basic_accounts
        seed_basic_accounts.main()
    except Exception as e:
        print(f"seed_basic_accounts skipped: {e}")

    base = os.getenv("SMOKE_BASE_URL", "http://localhost:8000")
    s = requests.Session()
    site_id = os.getenv("SMOKE_SITE_ID", "user001")
    password = os.getenv("SMOKE_PASSWORD", "123455")

    # Signup (best-effort)
    signup_payload: Dict[str, Any] = {
        "site_id": site_id,
        "nickname": "유저01",
        "password": password,
        "invite_code": "5858",
        "phone_number": "01000000001",
    }
    try:
        r = s.post(f"{base}/api/auth/signup", json=signup_payload, timeout=10)
        print(f"signup {r.status_code}")
    except Exception as e:
        print(f"signup error: {e}")

    # Login
    r = s.post(f"{base}/api/auth/login", json={"site_id": site_id, "password": password}, timeout=10)
    print(f"login {r.status_code}")
    if not r.ok:
        print(r.text)
        sys.exit(1)
    token = (r.json() or {}).get("access_token")
    h = {"Authorization": f"Bearer {token}"}

    # RPS play
    rp = s.post(f"{base}/api/games/rps/play", json={"choice": "rock", "bet_amount": 10}, headers=h, timeout=10)
    try:
        j = rp.json()
    except Exception:
        j = {"raw": rp.text}
    print(f"rps {rp.status_code}")
    _print(j)

    # Shop limited purchase (if catalog exists)
    rc = s.get(f"{base}/api/shop/limited-packages", headers=h, timeout=10)
    print(f"catalog {rc.status_code}")
    if rc.ok:
        try:
            data = rc.json()
        except Exception:
            data = None
        items = data.get("items") if isinstance(data, dict) else None
        if items:
            pid = items[0].get("id") or items[0].get("code")
            if pid:
                rb = s.post(f"{base}/api/shop/buy-limited", json={"package_id": pid}, headers=h, timeout=10)
                print(f"buy {rb.status_code}")

if __name__ == "__main__":
    main()
