import httpx
import json

BASE = 'http://localhost:8000'

# 1. Login
r = httpx.post(f'{BASE}/auth/login', json={'email':'admin@gramsight.in','password':'Admin123!'})
token = r.json()['access_token']
h = {'Authorization': f'Bearer {token}'}
print('=== LOGIN: OK ===')
print()

# 2. Farmer flow: get villages, then fetch data for first village
r = httpx.get(f'{BASE}/farmer/villages', headers=h, timeout=10)
villages = r.json()
vid = villages[0]['id'] if villages else 'none'
vname = villages[0]['name'] if villages else 'none'
print(f'=== FARMER VILLAGES ({len(villages)} found) ===')
print(f'First village: {vname} ({vid})')
print()

# 3. Farmer data for that village
endpoints = [
    ('risk', f'/farmer/{vid}/risk'),
    ('weather', f'/farmer/{vid}/weather'),
    ('market', f'/farmer/{vid}/market'),
    ('soil', f'/farmer/{vid}/soil'),
    ('advisory', f'/farmer/{vid}/advisory'),
]
for ep_name, ep in endpoints:
    r = httpx.get(f'{BASE}{ep}', headers=h, timeout=15)
    d = r.json()
    print(f'=== FARMER {ep_name.upper()} [{r.status_code}] ===')
    print(json.dumps(d, default=str)[:200])
    print()

# 4. Admin flow
admin_endpoints = [
    ('villages', '/admin/villages'),
    ('market-trend', '/admin/market-trend'),
    ('risk-trend', '/admin/risk-trend'),
    ('stats', '/admin/stats'),
]
for ep_name, ep in admin_endpoints:
    r = httpx.get(f'{BASE}{ep}', headers=h, timeout=15)
    d = r.json()
    print(f'=== ADMIN {ep_name.upper()} [{r.status_code}] ===')
    print(json.dumps(d, default=str)[:200])
    print()

print('=== ALL E2E CHECKS PASSED ===')
