"""Comprehensive endpoint test suite for GramSight backend."""
import httpx
import json
import sys

BASE = 'http://localhost:8000'
VILLAGE_ID = None
results = []


def test(method, path, expected_status, token=None, body=None, name=None, params=None):
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    try:
        if method == 'GET':
            r = httpx.get(f'{BASE}{path}', headers=headers, params=params, timeout=15)
        else:
            r = httpx.post(f'{BASE}{path}', headers=headers, json=body, params=params, timeout=15)
        ok = r.status_code == expected_status
        results.append((name or path, r.status_code, expected_status, ok, r.text[:300]))
        return r
    except Exception as e:
        results.append((name or path, 'ERR', expected_status, False, str(e)[:300]))
        return None


# --- Discover village ID ---
from backend_service.database import SessionLocal
from backend_service.models import Village
db = SessionLocal()
village = db.query(Village).first()
if village:
    VILLAGE_ID = str(village.id)
    print(f"Using village: {village.name} ({VILLAGE_ID})")
else:
    print("ERROR: No village found in DB")
    sys.exit(1)
db.close()

# 1. Health
test('GET', '/health', 200, name='GET /health')

# 2. Login
r = httpx.post(f'{BASE}/auth/login', json={'email': 'admin@gramsight.in', 'password': 'Admin123!'}, timeout=10)
token = r.json().get('access_token', '')
results.append(('POST /auth/login', r.status_code, 200, r.status_code == 200, r.text[:300]))

# 3. /auth/me
test('GET', '/auth/me', 200, token=token, name='GET /auth/me')

# 4. /auth/me without token (should 401 or 403)
r4 = test('GET', '/auth/me', 401, name='GET /auth/me (no auth)')

# 5. Weather fetch
test('POST', f'/weather/fetch?city=Mumbai', 200, token=token, name='POST /weather/fetch')

# 6. Weather fetch without auth (should 401)
test('POST', f'/weather/fetch?city=Mumbai', 401, name='POST /weather/fetch (no auth)')

# 7. Weather ingest (query params: village_id, lat, lon)
test('POST', '/weather/ingest', 200, token=token,
     params={'village_id': VILLAGE_ID, 'lat': 19.076, 'lon': 72.877},
     name='POST /weather/ingest')

# 8. Market fetch (requires MarketCreate body with modal_price)
test('POST', '/market/fetch', 200, token=token, body={
    'commodity': 'Wheat',
    'modal_price': 2200.0,
    'market_name': 'TestMarket'
}, name='POST /market/fetch')

# 9. Market ingest (query params: village_id, state, district, commodity)
test('POST', '/market/ingest', 200, token=token,
     params={'village_id': VILLAGE_ID, 'state': 'Maharashtra', 'district': 'Mumbai', 'commodity': 'Wheat'},
     name='POST /market/ingest')

# 10. Analytics summary
test('GET', '/analytics/summary', 200, token=token, name='GET /analytics/summary')

# 11. Analytics without auth
test('GET', '/analytics/summary', 401, name='GET /analytics/summary (no auth)')

# 12. Orchestrator refresh (village_id as query param)
test('POST', '/orchestrator/refresh', 200, token=token,
     params={'village_id': VILLAGE_ID, 'lat': 19.076, 'lon': 72.877, 'state': 'Maharashtra', 'district': 'Mumbai'},
     name='POST /orchestrator/refresh')

# 13. Orchestrator without auth
test('POST', '/orchestrator/refresh', 401,
     params={'village_id': VILLAGE_ID},
     name='POST /orchestrator/refresh (no auth)')

# 14. Risk calculate
test('POST', f'/internal/calculate-risk/{VILLAGE_ID}', 200, token=token,
     name='POST /internal/calculate-risk')

# 15. Risk get
test('GET', f'/admin/risk/{VILLAGE_ID}', 200, token=token,
     name='GET /admin/risk')

# --- Summary ---
print()
print('=' * 80)
title = "ENDPOINT TEST RESULTS"
print(f'{title:^80}')
print('=' * 80)
passed = 0
failed = 0
for name, status, expected, ok, body in results:
    icon = 'PASS' if ok else 'FAIL'
    if ok:
        passed += 1
    else:
        failed += 1
    print(f'[{icon}] {name:45s} status={status} expected={expected}')
    if not ok:
        print(f'       Response: {body[:200]}')
print('=' * 80)
print(f'TOTAL: {passed} passed, {failed} failed out of {len(results)}')
