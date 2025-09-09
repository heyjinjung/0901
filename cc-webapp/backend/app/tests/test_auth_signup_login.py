import os
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings

client = TestClient(app)

import uuid

def test_signup_with_default_invite():
    # 통합 후 /signup 은 Token 스키마 반환 (access_token, user, optional refresh_token)
    code = "5858"  # AuthService.create_user 현재 5858만 허용
    sid = "tester1_" + uuid.uuid4().hex[:6]
    resp = client.post("/api/auth/signup", json={
        "site_id": sid,
        "nickname": sid + "nick",
    "phone_number": "010-" + uuid.uuid4().hex[:4] + "-" + uuid.uuid4().hex[4:8],
        "password": "pass1234",
        "invite_code": code
    })
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["user"]["site_id"] == sid
    assert body["access_token"].startswith("ey")  # JWT 헤더 prefix


def test_login_success():
    # Ensure a user exists by performing signup first (captures dynamic site_id prefix used above)
    code = "5858"
    sid = "tester_login_" + uuid.uuid4().hex[:6]
    s_resp = client.post("/api/auth/signup", json={
        "site_id": sid,
        "nickname": sid + "nick",
        "phone_number": "010-" + uuid.uuid4().hex[:4] + "-" + uuid.uuid4().hex[4:8],
        "password": "pass1234",
        "invite_code": code
    })
    assert s_resp.status_code == 200, s_resp.text
    # login after signup using the same site_id
    resp = client.post("/api/auth/login", json={"site_id": sid, "password": "pass1234"})
    assert resp.status_code == 200, resp.text
    assert resp.json()["access_token"].startswith("ey")


def test_signup_invalid_invite():
    resp = client.post("/api/auth/signup", json={
        "site_id": "tester2",
        "nickname": "tester2nick",
        "phone_number": "010-0000-0002",
        "password": "pass1234",
        "invite_code": "WRONG123"  # 5858 이외 거부
    })
    assert resp.status_code == 400
