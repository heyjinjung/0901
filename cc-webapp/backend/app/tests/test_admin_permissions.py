import pytest
from fastapi.testclient import TestClient

# ...existing fixtures and app import assumed available in test environment
# This is a lightweight smoke test to validate admin vs normal token access to an admin-only endpoint


def test_admin_can_access_user_list(auth_token, client: TestClient):
    # auth_token fixture supports roles; assume auth_token('admin') returns token for admin
    admin_token = auth_token(role='admin')
    headers = {"Authorization": f"Bearer {admin_token}"}

    resp = client.get("/api/admin/users", headers=headers)
    assert resp.status_code in (200, 204)


def test_regular_user_cannot_access_user_list(auth_token, client: TestClient):
    user_token = auth_token(role='standard')
    headers = {"Authorization": f"Bearer {user_token}"}

    resp = client.get("/api/admin/users", headers=headers)
    assert resp.status_code in (401, 403)
