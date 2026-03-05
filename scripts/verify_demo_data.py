"""Comprehensive E2E verification of seeded demo data against DEMO_* constants."""
import httpx
import json
import sys

BASE = 'http://localhost:8000'
PASS_COUNT = 0
FAIL_COUNT = 0


def check(name, condition, detail=""):
    global PASS_COUNT, FAIL_COUNT
    if condition:
        PASS_COUNT += 1
        print(f"  PASS  {name}")
    else:
        FAIL_COUNT += 1
        print(f"  FAIL  {name} — {detail}")


# 1. Login as demo-farmer
r = httpx.post(f'{BASE}/auth/login', json={'email': 'demo-farmer@gramsight.ai', 'password': 'DemoUser123!'})
check("Demo farmer login", r.status_code == 200, f"status={r.status_code}")
farmer_token = r.json().get('access_token', '')
farmer_h = {'Authorization': f'Bearer {farmer_token}'}

# 2. Login as demo-admin
r = httpx.post(f'{BASE}/auth/login', json={'email': 'demo-admin@gramsight.ai', 'password': 'DemoUser123!'})
check("Demo admin login", r.status_code == 200, f"status={r.status_code}")
admin_token = r.json().get('access_token', '')
admin_h = {'Authorization': f'Bearer {admin_token}'}

# 3. Farmer villages
r = httpx.get(f'{BASE}/farmer/villages', headers=farmer_h)
villages = r.json()
check("Farmer villages count", len(villages) >= 8, f"got {len(villages)}")
# Get first village (alphabetical) — should be Baramati
vnames = [v['name'] for v in villages]
check("Villages contain all 8", all(n in vnames for n in ['Rajpur', 'Devgad', 'Malshiras', 'Kothrud', 'Sinhagad', 'Baramati', 'Pandharpur', 'Wai']),
      f"got {vnames}")

# Pick Rajpur for farmer tests
rajpur = next((v for v in villages if v['name'] == 'Rajpur'), villages[0])
vid = rajpur['id']
print(f"\n  Testing farmer endpoints for {rajpur['name']} ({vid})")

# 4. Farmer risk
r = httpx.get(f'{BASE}/farmer/{vid}/risk', headers=farmer_h)
risk = r.json().get('risk', {})
check("Risk score = 72 (Rajpur)", risk.get('score') == 72, f"got {risk.get('score')}")
check("Risk level = High", risk.get('risk_level') == 'High', f"got {risk.get('risk_level')}")

# 5. Farmer weather
r = httpx.get(f'{BASE}/farmer/{vid}/weather', headers=farmer_h)
wd = r.json()
history = wd.get('history', [])
check("Weather has 5 records", len(history) == 5, f"got {len(history)}")
# After frontend reverse: should give temp=[28,31,33,30,27]
temps_reversed = [round(h['temperature']) for h in reversed(history)]
check("Weather temp matches DEMO", temps_reversed == [28, 31, 33, 30, 27], f"got {temps_reversed}")
rain_reversed = [round(h['rainfall']) for h in reversed(history)]
check("Weather rain matches DEMO", rain_reversed == [5, 12, 2, 0, 8], f"got {rain_reversed}")
hum_reversed = [round(h['humidity']) for h in reversed(history)]
check("Weather humidity matches DEMO", hum_reversed == [65, 72, 58, 54, 68], f"got {hum_reversed}")

# 6. Farmer market
r = httpx.get(f'{BASE}/farmer/{vid}/market', headers=farmer_h)
md = r.json()
markets = md.get('markets', [])
check("Market has 5+ records", len(markets) >= 5, f"got {len(markets)}")
# Top 5 most recent (already DESC)
top5_prices = [round(m['modal_price']) for m in markets[:5]]
check("Market prices match DEMO", top5_prices == [2200, 2180, 2250, 2300, 2280], f"got {top5_prices}")
check("Market commodity = Rice", markets[0]['commodity'] == 'Rice', f"got {markets[0].get('commodity')}")

# 7. Farmer soil
r = httpx.get(f'{BASE}/farmer/{vid}/soil', headers=farmer_h)
soil = r.json()
check("Soil nitrogen = 65", soil.get('nitrogen') == 65, f"got {soil.get('nitrogen')}")
check("Soil phosphorus = 42", soil.get('phosphorus') == 42, f"got {soil.get('phosphorus')}")
check("Soil potassium = 72", soil.get('potassium') == 72, f"got {soil.get('potassium')}")
check("Soil moisture = 38", soil.get('moisture') == 38, f"got {soil.get('moisture')}")
check("Soil pH = 6.5", soil.get('ph') == 6.5, f"got {soil.get('ph')}")

# 8. Farmer advisory
r = httpx.get(f'{BASE}/farmer/{vid}/advisory', headers=farmer_h)
adv = r.json()
items = adv.get('items', [])
check("Advisory has 4 items", len(items) == 4, f"got {len(items)}")
check("Advisory first item matches", 'watering frequency' in (items[0] if items else ''), f"got {items[0][:50] if items else 'empty'}")

# 9. Admin villages
print(f"\n  Testing admin endpoints...")
r = httpx.get(f'{BASE}/admin/villages', headers=admin_h)
admin_villages = r.json()
check("Admin villages count >= 8", len(admin_villages) >= 8, f"got {len(admin_villages)}")
# Find Baramati — should have score 91
baramati = next((v for v in admin_villages if v['name'] == 'Baramati'), None)
check("Baramati risk_score = 91", baramati and baramati.get('risk_score') == 91,
      f"got {baramati.get('risk_score') if baramati else 'NOT FOUND'}")
check("Baramati district = Pune", baramati and baramati.get('district') == 'Pune',
      f"got {baramati.get('district') if baramati else 'NOT FOUND'}")
check("Baramati crop = Sugarcane", baramati and baramati.get('crop') == 'Sugarcane',
      f"got {baramati.get('crop') if baramati else 'NOT FOUND'}")

# Check all 8 village risk scores
expected_scores = {'Rajpur': 72, 'Devgad': 45, 'Malshiras': 83, 'Kothrud': 28,
                   'Sinhagad': 56, 'Baramati': 91, 'Pandharpur': 67, 'Wai': 34}
for av in admin_villages:
    if av['name'] in expected_scores:
        check(f"  {av['name']} score={expected_scores[av['name']]}",
              av.get('risk_score') == expected_scores[av['name']],
              f"got {av.get('risk_score')}")

# 10. Admin market trend
r = httpx.get(f'{BASE}/admin/market-trend', headers=admin_h)
mt = r.json()
check("Market trend has labels", len(mt.get('labels', [])) >= 3, f"got {mt.get('labels')}")
check("Market trend has prices", len(mt.get('prices', [])) >= 3, f"got {mt.get('prices')}")
print(f"  INFO  Market trend: labels={mt.get('labels')}, prices={mt.get('prices')}")

# 11. Admin risk trend
r = httpx.get(f'{BASE}/admin/risk-trend', headers=admin_h)
rt = r.json()
check("Risk trend has labels", len(rt.get('labels', [])) >= 3, f"got {rt.get('labels')}")
check("Risk trend has scores", len(rt.get('scores', [])) >= 3, f"got {rt.get('scores')}")
print(f"  INFO  Risk trend: labels={rt.get('labels')}, scores={rt.get('scores')}")

# 12. Admin stats
r = httpx.get(f'{BASE}/admin/stats', headers=admin_h)
stats = r.json()
check("Farmer count >= 1", stats.get('farmer_count', 0) >= 1, f"got {stats.get('farmer_count')}")

# 13. Demo status endpoint
r = httpx.get(f'{BASE}/demo/status')
ds = r.json()
check("Demo status accessible", r.status_code == 200, f"status={r.status_code}")
check("Demo data_source = database", ds.get('data_source') == 'database', f"got {ds.get('data_source')}")
check("Demo villages >= 8", ds.get('seeded_records', {}).get('villages', 0) >= 8,
      f"got {ds.get('seeded_records', {}).get('villages')}")
print(f"\n  Demo status: {json.dumps(ds, indent=2)}")

# Summary
print(f"\n{'='*60}")
print(f"  VERIFICATION: {PASS_COUNT} PASS / {FAIL_COUNT} FAIL")
print(f"  Data Match Status: {'PASS' if FAIL_COUNT == 0 else 'PARTIAL'}")
print(f"{'='*60}")

sys.exit(0 if FAIL_COUNT == 0 else 1)
