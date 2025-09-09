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

# Signup/login
uid = str(int(time.time()))
phone = f"010{int(uid)%100000000:08d}"
signup = {"invite_code":"5858","nickname":f"verify_{uid}","site_id":f"verify_{uid}","phone_number":phone,"password":"pass1234"}
print('signup', signup)
sc, sb = req('/api/auth/signup','POST', signup)
print('signup', sc)
if sc == 400:
    sc, sb = req('/api/auth/login','POST', {'site_id': signup['site_id'], 'password': signup['password']})
    print('login fallback', sc)
elif sc != 200:
    print('signup failed', sc, sb); sys.exit(2)

sc, sb = req('/api/auth/login','POST', {'site_id': signup['site_id'], 'password': signup['password']})
if sc != 200:
    print('login failed', sc, sb); sys.exit(3)
js = json.loads(sb)
user = js.get('user')
token = js.get('access_token')
headers = {'Authorization': f'Bearer {token}'}
user_id = user.get('id')
print('user id', user_id)

# helper to print balance from responses if present

def parse_balance_from_resp(body):
    try:
        j = json.loads(body)
        if isinstance(j, dict):
            if 'balance' in j:
                b = j['balance']
                if isinstance(b, dict) and 'tokens' in b:
                    return b['tokens']
                if isinstance(b, (int,float)):
                    return b
            if 'currency_balance' in j and isinstance(j['currency_balance'], dict):
                return j['currency_balance'].get('tokens')
    except Exception:
        pass
    return None

# initial stats
sc,sb = req(f'/api/games/stats/{user_id}','GET', None, headers)
print('initial stats', sc)
initial_stats = json.loads(sb) if sc==200 else {}
initial_spins = initial_stats.get('total_spins',0)
print('initial total_spins', initial_spins)

# perform slot spin
sc,sb = req('/api/games/slot/spin','POST', {'bet_amount':1}, headers)
print('slot spin', sc, sb[:300])
slot_balance = parse_balance_from_resp(sb)
print('slot balance', slot_balance)

# perform gacha pull
sc,sb = req('/api/games/gacha/pull','POST', {'pull_count':1}, headers)
print('gacha pull', sc, sb[:300])
gacha_balance = parse_balance_from_resp(sb)
print('gacha balance', gacha_balance)

# perform crash bet
sc,sb = req('/api/games/crash/bet','POST', {'bet_amount':1}, headers)
print('crash bet', sc, sb[:300])
crash_balance = parse_balance_from_resp(sb)
print('crash balance', crash_balance)

# final stats
sc,sb = req(f'/api/games/stats/{user_id}','GET', None, headers)
print('final stats', sc)
final_stats = json.loads(sb) if sc==200 else {}
final_spins = final_stats.get('total_spins',0)
print('final total_spins', final_spins)

# simple validation
played = final_spins - initial_spins
print('spins increased by', played)
if played >= 1:
    print('history appears recorded')
else:
    print('history not recorded or stats aggregation delayed')

# balance deltas
print('balances (slot,gacha,crash):', slot_balance, gacha_balance, crash_balance)

print('done')
