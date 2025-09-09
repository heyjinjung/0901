"""
Backend smoke script: signup -> log action -> distribute reward -> list rewards -> push WS notify.

Run inside the backend container:
  docker exec cc_backend_local python app/scripts/smoke_agent.py
"""

import json
import os
import random
from datetime import datetime, timezone

import requests

API = os.environ.get("SMOKE_API", "http://localhost:8000")


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def rnd_user(prefix: str = "agent") -> str:
    return f"{prefix}{random.randint(10000, 99999)}"


def main() -> int:
    # 1) Signup (resilient with retries); if user exists, login
    password = "1234"
    attempts = 0
    max_attempts = 3
    access_token = None
    uid = None
    site_id = None
    last_err = None
    while attempts < max_attempts and access_token is None:
        attempts += 1
        site_id = rnd_user()
        nickname = f"Agent_{site_id[-4:]}"
        phone = f"010{random.randint(10000000, 99999999)}"
        signup_body = {
            "site_id": site_id,
            "nickname": nickname,
            "phone_number": phone,
            "invite_code": "5858",
            "password": password,
        }
        r = requests.post(f"{API}/api/auth/signup", json=signup_body, timeout=15)
        if r.status_code == 200:
            tok = r.json()
            access_token = tok.get("access_token")
            user = tok.get("user") or {}
            uid = user.get("id")
            print("SIGNED_UP:", json.dumps({"user_id": uid, "site_id": site_id}))
            break
        else:
            last_err = (r.status_code, r.text)
            # If user likely exists (400 duplicate), try to login with this site_id
            if r.status_code in (400, 409):
                try:
                    lr = requests.post(
                        f"{API}/api/auth/login",
                        json={"site_id": site_id, "password": password},
                        timeout=15,
                    )
                    if lr.status_code == 200:
                        body = lr.json()
                        access_token = body.get("access_token")
                        print("LOGIN_OK_FOR_EXISTING_USER")
                        break
                except Exception as _:
                    pass
            # Otherwise retry with fresh credentials
            print(f"SIGNUP_ATTEMPT_{attempts}_FAILED:", r.status_code)
    if access_token is None:
        raise SystemExit(f"Signup/login failed after {attempts} attempts: {last_err}")

    # Ensure we have user info; fetch profile when user not returned in auth response
    if uid is None:
        headers = {"Authorization": f"Bearer {access_token}"} if access_token else {}
        prof = requests.get(f"{API}/api/users/profile", headers=headers, timeout=15)
        prof.raise_for_status()
        p = prof.json()
        uid = p.get("id")
        site_id = p.get("site_id", site_id)
        print("PROFILE:", json.dumps({"user_id": uid, "site_id": site_id}))

    # 2) Log action
    act_body = {
        "user_id": uid,
        "action_type": "SLOT_SPIN",
        "context": {"bet": 10, "result": "LOSE"},
        "client_ts": iso_now(),
    }
    r = requests.post(f"{API}/api/actions", json=act_body, timeout=15)
    r.raise_for_status()
    print("ACTION_LOGGED:", json.dumps(r.json(), default=str))

    # 3) Distribute reward
    idemp = f"smoke-{site_id}"
    rw_body = {
        "user_id": uid,
        "reward_type": "TOKEN",
        "amount": 50,
        "source_description": "smoke:test",
        "idempotency_key": idemp,
    }
    r = requests.post(f"{API}/api/rewards/distribute", json=rw_body, timeout=15)
    r.raise_for_status()
    print("REWARD_GRANTED:", json.dumps(r.json(), default=str))

    # 4) List rewards
    r = requests.get(f"{API}/api/rewards/users/{uid}/rewards", params={"page": 1, "page_size": 5}, timeout=15)
    r.raise_for_status()
    print("REWARDS_LIST:", json.dumps(r.json(), default=str))

    # 5) Push WS notification (will buffer if user not connected)
    r = requests.post(f"{API}/ws/notify/{uid}", params={"message": "Hello from smoke"}, timeout=15)
    r.raise_for_status()
    print("WS_NOTIFY:", json.dumps(r.json(), default=str))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
