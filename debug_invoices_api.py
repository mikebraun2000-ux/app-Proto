"""
Debug-Script für Rechnungen-API.
"""

import requests
import json

def debug_invoices_api():
    """Debuggt die Rechnungen-API."""
    print("=== RECHNUNGEN-API DEBUG ===")
    
    base_url = "http://localhost:8000"
    
    # 1. Login
    print("1. Login...")
    login_data = {"username": "admin", "password": "admin123"}
    response = requests.post(f"{base_url}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"Login fehlgeschlagen: {response.status_code}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"Token erhalten: {token[:50]}...")
    
    # 2. Rechnungen abrufen mit detailliertem Debug
    print("\n2. Rechnungen abrufen...")
    try:
        response = requests.get(f"{base_url}/invoices/", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            invoices = response.json()
            print(f"Rechnungen geladen: {len(invoices)}")
            if invoices:
                print(f"Erste Rechnung: {invoices[0]}")
        else:
            print(f"Fehler-Response: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    debug_invoices_api()

