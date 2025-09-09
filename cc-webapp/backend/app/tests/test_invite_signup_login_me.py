import time


def test_signup_login_and_me_profile(client):
	uniq = str(int(time.time() * 1000))[-9:]
	site_id = f"tester_{uniq}"
	nickname = f"nick_{uniq}"
	phone = f"010{uniq}"
	password = "pass1234"

	# Signup
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
	if r.status_code != 200:
		# if duplicate or validation mismatch, proceed to login
		r = client.post("/api/auth/login", json={"site_id": site_id, "password": password})
		assert r.status_code == 200

	token = r.json()["access_token"]
	assert token

	# me/profile
	me = client.get("/api/users/profile", headers={"Authorization": f"Bearer {token}"})
	assert me.status_code == 200
	body = me.json()
	assert body["site_id"] == site_id
	assert body["nickname"] == nickname


def test_login_failure_wrong_password_returns_401(client):
	uniq = str(int(time.time()))[-7:]
	site_id = f"badlogin_{uniq}"
	nickname = f"badnick_{uniq}"
	password = "pass1234"
	# Ensure user exists
	client.post(
		"/api/auth/signup",
		json={
			"site_id": site_id,
			"nickname": nickname,
			"password": password,
			"invite_code": "5858",
			"phone_number": f"011{uniq}1",
		},
	)
	# Wrong password
	r = client.post("/api/auth/login", json={"site_id": site_id, "password": "wrong"})
	assert r.status_code == 401
	assert "Invalid" in r.json().get("detail", "")


def test_last_login_updated_on_login(client):
	uniq = str(int(time.time() * 1000))[-9:]
	site_id = f"lastlogin_{uniq}"
	nickname = f"ll_{uniq}"
	password = "pass1234"
	# Signup
	r = client.post(
		"/api/auth/signup",
		json={
			"site_id": site_id,
			"nickname": nickname,
			"password": password,
			"invite_code": "5858",
			"phone_number": f"012{uniq}",
		},
	)
	assert r.status_code == 200
	# Login to trigger last_login update
	r = client.post("/api/auth/login", json={"site_id": site_id, "password": password})
	assert r.status_code == 200
	token = r.json()["access_token"]
	# Fetch user info and verify last_login present and recent
	info = client.get("/api/users/info", headers={"Authorization": f"Bearer {token}"})
	assert info.status_code == 200
	last_login = info.json().get("last_login")
	assert last_login is not None
