"""Quick E2E verification: demo login -> real JWT -> all endpoints."""
import requests, json, sys

BASE = "http://localhost:8000"
PASS = FAIL = 0

def check(label, ok):
    global PASS, FAIL
    tag = "PASS" if ok else "FAIL"
    if ok: PASS += 1
    else: FAIL += 1
    print(f"  [{tag}] {label}")

# 1. Demo farmer login
r = requests.post(f"{BASE}/auth/login", json={"email": "demo-farmer@gramsight.ai", "password": "DemoUser123!"})
check("Farmer login 200", r.status_code == 200)
farmer_token = r.json().get("access_token", "")
check("Farmer got JWT", len(farmer_token) > 20)

# 2. Demo admin login
r = requests.post(f"{BASE}/auth/login", json={"email": "demo-admin@gramsight.ai", "password": "DemoUser123!"})
check("Admin login 200", r.status_code == 200)
admin_token = r.json().get("access_token", "")
check("Admin got JWT", len(admin_token) > 20)

fh = {"Authorization": f"Bearer {farmer_token}"}
ah = {"Authorization": f"Bearer {admin_token}"}

# 3. Farmer: villages
r = requests.get(f"{BASE}/farmer/villages", headers=fh)
check("Farmer villages 200", r.status_code == 200)
villages = r.json()
check("8 villages", len(villages) >= 8)
vid = villages[0]["id"]
vname = villages[0]["name"]
print(f"    First village: {vname} ({vid})")

# 4. Farmer: risk
r = requests.get(f"{BASE}/farmer/{vid}/risk", headers=fh)
check("Farmer risk 200", r.status_code == 200)
risk = r.json().get("risk", {})
score = risk.get("score", risk) if isinstance(risk, dict) else risk
print(f"    Risk score: {score}")
check("Risk score is number", isinstance(score, (int, float)))

# 5. Farmer: weather
r = requests.get(f"{BASE}/farmer/{vid}/weather", headers=fh)
check("Farmer weather 200", r.status_code == 200)
w = r.json()
history = w.get("history", [])
check("Weather has history", len(history) >= 5)
temps = [x.get("temperature") for x in history[:5]]
print(f"    Temps (recent 5): {temps}")

# After frontend reversal these should become [28,31,33,30,27]
reversed_temps = list(reversed(temps[:5]))
check("Weather temps match DEMO", reversed_temps == [28, 31, 33, 30, 27])

# 6. Farmer: market
r = requests.get(f"{BASE}/farmer/{vid}/market", headers=fh)
check("Farmer market 200", r.status_code == 200)
m = r.json()
markets = m.get("markets", [])
check("Market has entries", len(markets) >= 5)
prices = [x.get("modal_price") for x in markets[:5]]
print(f"    Prices (recent 5): {prices}")
check("Market prices match DEMO", prices == [2200, 2180, 2250, 2300, 2280])

# 7. Farmer: soil
r = requests.get(f"{BASE}/farmer/{vid}/soil", headers=fh)
check("Farmer soil 200", r.status_code == 200)
s = r.json()
print(f"    Soil: N={s.get('nitrogen')} P={s.get('phosphorus')} K={s.get('potassium')} M={s.get('moisture')} pH={s.get('ph')}")
check("Soil nitrogen=65", s.get("nitrogen") == 65)
check("Soil phosphorus=42", s.get("phosphorus") == 42)
check("Soil potassium=72", s.get("potassium") == 72)
check("Soil moisture=38", s.get("moisture") == 38)
check("Soil ph=6.5", s.get("ph") == 6.5)

# 8. Farmer: advisory
r = requests.get(f"{BASE}/farmer/{vid}/advisory", headers=fh)
check("Farmer advisory 200", r.status_code == 200)
a = r.json()
items = a.get("items", [])
check("Advisory has 4 items", len(items) == 4)
print(f"    Advisory items: {len(items)}")

# 9. Admin: villages
r = requests.get(f"{BASE}/admin/villages", headers=ah)
check("Admin villages 200", r.status_code == 200)
av = r.json()
check("Admin 8+ villages", len(av) >= 8)

# Check a few risk scores match DEMO_VILLAGES
demo_scores = {"Rajpur": 72, "Devgad": 45, "Malshiras": 83, "Kothrud": 28,
               "Sinhagad": 56, "Baramati": 91, "Pandharpur": 67, "Wai": 34}
for v in av:
    name = v.get("name")
    if name in demo_scores:
        expected = demo_scores[name]
        actual = v.get("risk_score")
        ok = actual == expected
        check(f"Admin {name} risk={actual} (expected {expected})", ok)
        if not ok:
            print(f"      District: {v.get('district')}, Crop: {v.get('crop')}")

# 10. Demo status
r = requests.get(f"{BASE}/demo/status")
check("Demo status 200", r.status_code == 200)
ds = r.json()
check("Demo mode true", ds.get("demo_mode") is True)
check("Data source=database", ds.get("data_source") == "database")

print(f"\n{'='*50}")
print(f"Results: {PASS} PASS, {FAIL} FAIL out of {PASS+FAIL}")
print(f"{'='*50}")
sys.exit(0 if FAIL == 0 else 1)
