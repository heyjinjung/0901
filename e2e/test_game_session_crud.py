#!/usr/bin/env python3
import urllib.request, urllib.error, json, time, sys
BASE='http://localhost:8000'

def req(path, method='GET', data=None, headers=None):
    url = BASE + path
    data_b = None
    if data is not None:
        data_b = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=data_b, method=method)
    req.add_header('Content-Type','application/json')
    if headers:
        for k,v in headers.items():
            req.add_header(k,v)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.getcode(), r.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode('utf-8')
        except Exception:
            body = ''
        return e.code, body
    except Exception as e:
        return None, str(e)

# Signup unique user
uid = str(int(time.time()))
phone = f"010{int(uid)%100000000:08d}"
signup = {"invite_code":"5858","nickname":f"crud_{uid}","site_id":f"crud_{uid}","phone_number":phone,"password":"pass1234"}
print('signup', signup)
sc, sb = req('/api/auth/signup','POST', signup)
print('signup', sc, sb[:400])
if sc == 400:
    # try login fallback
    sc, sb = req('/api/auth/login','POST', {'site_id': signup['site_id'], 'password': signup['password']})
    print('login fallback', sc, sb[:400])
elif sc != 200:
    print('signup failed, abort')
    sys.exit(2)

# login
sc, sb = req('/api/auth/login','POST', {'site_id': signup['site_id'], 'password': signup['password']})
print('login', sc, sb[:400])
if sc != 200:
    print('login failed', sc)
    sys.exit(3)

data = json.loads(sb)
token = data.get('access_token')
user = data.get('user')
headers = {'Authorization': f'Bearer {token}'}

# Start session
payload = {'game_type':'slot','bet_amount':5}
sc,sb = req('/api/games/session/start','POST', payload, headers)
print('start session', sc, sb[:500])
if sc != 200:
    print('start failed'); sys.exit(4)
js = json.loads(sb)
sid = js.get('session_id')

# Get active session
sc,sb = req('/api/games/session/active?game_type=slot','GET', None, headers)
print('get active', sc, sb[:500])
if sc != 200:
    print('get active failed'); sys.exit(5)

# End session
end_payload = {'session_id': sid, 'rounds_played': 3, 'total_bet': 5, 'total_win': 10, 'duration': 60}
sc,sb = req('/api/games/session/end','POST', end_payload, headers)
print('end session', sc, sb[:500])
if sc != 200:
    print('end failed'); sys.exit(6)

# Ensure no active session
sc,sb = req('/api/games/session/active?game_type=slot','GET', None, headers)
print('get active after end', sc, sb[:400])
if sc == 200:
    print('still active? test failed')
    sys.exit(7)

print('session CRUD passed')
sys.exit(0)
