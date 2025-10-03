import requests

API_BASE = "http://127.0.0.1:8000"

# Login
login_response = requests.post(
    f"{API_BASE}/auth/login",
    json={"username": "admin", "password": "admin123"}
)

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    print("[OK] Login erfolgreich")
    
    # Test Billing Status
    billing_response = requests.get(
        f"{API_BASE}/billing/status",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    print(f"\nBilling-Status: {billing_response.status_code}")
    if billing_response.status_code == 200:
        print("[OK] Billing-Daten:")
        import json
        print(json.dumps(billing_response.json(), indent=2))
    else:
        print(f"[ERR] Fehler: {billing_response.text}")
else:
    print(f"[ERR] Login fehlgeschlagen: {login_response.status_code}")

