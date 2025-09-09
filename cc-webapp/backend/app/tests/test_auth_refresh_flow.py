import base64
import json
import uuid
from typing import Any, Dict

from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings

client = TestClient(app)


def _decode_payload(token: str) -> Dict[str, Any]:
	parts = token.split('.')
	assert len(parts) == 3, "invalid jwt format"
	payload_b64 = parts[1]
	padded = payload_b64 + '=' * ((4 - len(payload_b64) % 4) % 4)
	data = base64.urlsafe_b64decode(padded.encode('utf-8')).decode('utf-8')
	return json.loads(data)


def _signup_and_login(site_id: str, password: str):
	"""After consolidation /signup already returns Token, no second login needed."""
	invite_code = settings.UNLIMITED_INVITE_CODE or "5858"
	phone_number = "010-" + uuid.uuid4().hex[:4] + "-" + uuid.uuid4().hex[4:8]
	resp = client.post(
		"/api/auth/signup",
		json={
			"site_id": site_id,
			"nickname": f"{site_id}nick",
			"phone_number": phone_number,
			"password": password,
			"invite_code": invite_code,
		},
	)
	assert resp.status_code == 200, f"signup failed: {resp.status_code} {resp.text}"
	body = resp.json()
	user_obj = body.get("user") or {}
	return body.get("access_token"), body.get("refresh_token"), user_obj.get("id")


def test_refresh_flow_rotates_access_token_and_jti():
	site_id = "refreshuser1_" + uuid.uuid4().hex[:8]
	password = "pass1234"
	original_access, refresh_token, _ = _signup_and_login(site_id, password)
	orig_payload = _decode_payload(original_access)
	orig_jti = orig_payload.get("jti")
	assert orig_jti

	# Prefer providing refresh_token if available
	if refresh_token:
		r1 = client.post(
			"/api/auth/refresh",
			json={"refresh_token": refresh_token},
			headers={"Authorization": f"Bearer {original_access}"},
		)
	else:
		r1 = client.post(
			"/api/auth/refresh",
			headers={"Authorization": f"Bearer {original_access}"},
		)
	assert r1.status_code == 200, r1.text
	new_access_1 = r1.json()["access_token"]
	assert new_access_1 != original_access
	new_payload_1 = _decode_payload(new_access_1)
	assert new_payload_1.get("jti") and new_payload_1.get("jti") != orig_jti

	r2 = client.post(
		"/api/auth/refresh",
		headers={"Authorization": f"Bearer {new_access_1}"},
	)
	assert r2.status_code == 200, r2.text
	new_access_2 = r2.json()["access_token"]
	assert new_access_2 != new_access_1
	new_payload_2 = _decode_payload(new_access_2)
	assert new_payload_2.get("jti") and new_payload_2.get("jti") != new_payload_1.get("jti")
	assert new_payload_2.get("sub") == orig_payload.get("sub")

