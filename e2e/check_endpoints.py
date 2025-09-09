#!/usr/bin/env python3
import urllib.request
import urllib.error
import json
import sys

ENDPOINTS = [
    ('GET', 'http://localhost:8000/health'),
    ('POST', 'http://localhost:8000/api/games/slot/play'),
    ('POST', 'http://localhost:8000/api/games/gacha/play'),
    ('POST', 'http://localhost:8000/api/games/crash/play'),
    ('GET', 'http://localhost:8000/api/battlepass/status'),
    ('GET', 'http://localhost:8000/api/events/list'),
    ('GET', 'http://localhost:3000/games/slot'),
    ('GET', 'http://localhost:3000/games/gacha'),
    ('GET', 'http://localhost:3000/games/crash'),
    ('GET', 'http://localhost:3000/battlepass'),
    ('GET', 'http://localhost:3000/events'),
]

def fetch(method, url, timeout=10):
    req = urllib.request.Request(url, method=method)
    if method == 'POST':
        req.add_header('Content-Type', 'application/json')
        data = b'{}'
    else:
        data = None
    try:
        with urllib.request.urlopen(req, data=data, timeout=timeout) as resp:
            status = resp.getcode()
            raw = resp.read()
            try:
                text = raw.decode('utf-8', errors='replace')
            except Exception:
                text = str(raw)
            snippet = text[:300] + ("..." if len(text) > 300 else "")
            return status, snippet
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode('utf-8', errors='replace')
            snippet = body[:300] + ("..." if len(body) > 300 else "")
        except Exception:
            snippet = ''
        return e.code, snippet
    except Exception as e:
        return None, str(e)

if __name__ == '__main__':
    results = []
    for method, url in ENDPOINTS:
        status, snippet = fetch(method, url)
        print(f'{method} {url} -> {status}')
        if status == 200 and snippet:
            print('  body:', snippet)
    sys.exit(0)
