from app.services.auth_service import AuthService
import time


def _signup_and_login(client, site_id: str, nickname: str, password: str = "pass1234"):
	# Sign up
	suffix = str(int(time.time() * 1000))[-7:]
	phone = f"010{suffix}0"  # >=10 digits, unique per run
	r = client.post(
		"/api/auth/signup",
		json={
			"site_id": site_id,
			"nickname": nickname,
			"password": password,
			"invite_code": "5858",
			"phone_number": phone,
		},
	)
	assert r.status_code in (200, 409, 400, 422)
	# If signup failed due to duplicate, attempt login
	if r.status_code != 200:
		r = client.post("/api/auth/login", json={"site_id": site_id, "password": password})
		assert r.status_code == 200
	token = r.json().get("access_token")
	if not token:
		# fallback: login to get token
		r = client.post("/api/auth/login", json={"site_id": site_id, "password": password})
		assert r.status_code == 200
		token = r.json()["access_token"]
	return token


def test_admin_only_invite_generate_denied_for_regular_user(client):
	uniq = str(int(time.time()))[-6:]
	token = _signup_and_login(client, site_id=f"user_rbac_{uniq}", nickname=f"user_rbac_{uniq}")
	# Try create invite code (requires admin)
	r = client.post(
		"/api/invite/generate",
		headers={"Authorization": f"Bearer {token}"},
	)
	assert r.status_code in (401, 403)


def test_rank_check_utility():
	# Pure service-level check without HTTP
	assert AuthService.check_rank_access("STANDARD", "STANDARD") is True
	assert AuthService.check_rank_access("PREMIUM", "STANDARD") is True
	assert AuthService.check_rank_access("VIP", "STANDARD") is True
	assert AuthService.check_rank_access("STANDARD", "VIP") is False
	assert AuthService.check_rank_access("PREMIUM", "VIP") is False
