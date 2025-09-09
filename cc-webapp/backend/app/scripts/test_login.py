"""Quick login test script.

Usage inside container:
  docker compose exec backend python -m app.scripts.test_login <site_id> <password>

Defaults to admin / 123456 if not provided.
"""
from __future__ import annotations
import sys, json
import httpx

SITE = sys.argv[1] if len(sys.argv) > 1 else 'admin'
PW = sys.argv[2] if len(sys.argv) > 2 else '123456'
URL = 'http://localhost:8000/api/auth/login'

def main():  # pragma: no cover
    try:
        r = httpx.post(URL, json={'site_id': SITE, 'password': PW}, timeout=10.0)
    except Exception as e:
        print('REQUEST_ERROR', e)
        return 2
    print('status', r.status_code)
    if r.headers.get('content-type','').startswith('application/json'):
        try:
            data = r.json()
        except Exception:
            data = {'raw': r.text[:400]}
    else:
        data = {'raw': r.text[:400]}
    # redact token body
    if isinstance(data, dict) and 'access_token' in data:
        data['access_token_preview'] = data['access_token'][:32] + '...'
        data.pop('access_token', None)
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0 if r.status_code == 200 else 1

if __name__ == '__main__':  # pragma: no cover
    raise SystemExit(main())
