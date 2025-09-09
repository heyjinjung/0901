import json
import pytest
from fastapi.testclient import TestClient
from app.standalone_app import app

client = TestClient(app)


def make_auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_auth_me_with_header_and_cookie(monkeypatch):
    # create a fake token verification path by monkeypatching AuthService.verify_token
    # The standalone FastAPI app has its own JWT decoding (app.standalone_app.jwt).
    # Patch its jwt.decode so that 'valid-token' returns a payload mapping to
    # a real user in the standalone app's test DB.
    from app import standalone_app
    # ensure a user exists in the standalone DB
    sess = standalone_app.SessionLocal()
    try:
        user = sess.query(standalone_app.User).first()
        if not user:
            u = standalone_app.User(site_id='testuser', nickname='testuser', password_hash='x', is_active=True)
            sess.add(u)
            sess.commit()
            sess.refresh(u)
            user = u
    finally:
        sess.close()

    def fake_jwt_decode(token, key, algorithms=None):
        from jose import JWTError
        if token == 'valid-token':
            return {"user_id": user.id, "sub": user.site_id}
        raise JWTError('invalid token')

    monkeypatch.setattr(standalone_app.jwt, 'decode', fake_jwt_decode)

    # when Authorization header present
    r = client.get('/api/auth/me', headers=make_auth_headers('valid-token'))
    assert r.status_code == 200

    # when Authorization header absent but cookie present
    cookie = {'access_token': 'valid-token'}
    r2 = client.get('/api/auth/me', cookies=cookie)
    assert r2.status_code == 200

    # invalid cookie
    r3 = client.get('/api/auth/me', cookies={'access_token': 'bad'})
    assert r3.status_code == 401
