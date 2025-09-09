import pytest


def test_signup_action_recent_flow(client, auth_token):
    """Signup → log action → verify in /api/actions/recent/{user_id}.

    - Creates a unique user via auth_token fixture
    - Fetches /api/auth/me to get user_id
    - POST /api/actions with a simple context (no PII)
    - GET /api/actions/recent/{user_id} and assert the action is present
    """
    token = auth_token()
    assert token, "Failed to obtain auth token"
    headers = {"Authorization": f"Bearer {token}"}

    # Resolve current user id
    me = client.get("/api/auth/me", headers=headers)
    assert me.status_code == 200, f"/api/auth/me failed: {me.status_code} {me.text}"
    user = me.json()
    user_id = user.get("id") or user.get("user_id")
    assert isinstance(user_id, int) and user_id > 0

    # Log an action for this user
    body = {
        "user_id": user_id,
        "action_type": "LOGIN",
        "context": {"ip": "127.0.0.1"},  # avoid PII keys to keep assertion simple
    }
    r = client.post("/api/actions", json=body)
    assert r.status_code == 200, r.text

    # Fetch recent actions and verify presence
    recent = client.get(f"/api/actions/recent/{user_id}?limit=20")
    assert recent.status_code == 200, recent.text
    items = recent.json() or []
    # Look for our LOGIN action in the most recent window
    assert any(
        it.get("action_type") == "LOGIN" and (it.get("action_data") or {}).get("context", {}).get("ip") == "127.0.0.1"
        for it in items
    ), f"LOGIN action not found in recent list for user {user_id}"
