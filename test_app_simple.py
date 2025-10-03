"""
Einfacher Test der App-Funktionalität.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_basic_functionality():
    """Teste grundlegende App-Funktionalität."""
    print("Teste grundlegende App-Funktionalitaet...")
    
    # 1. Login testen
    print("1. Teste Login...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Login Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"Login fehlgeschlagen: {response.text}")
        return False
    
    token = response.json()["access_token"]
    print("Login erfolgreich")
    
    # 2. Projekte testen
    print("\n2. Teste Projekte...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/projects/", headers=headers)
    print(f"Projekte Status: {response.status_code}")
    
    if response.status_code == 200:
        projects = response.json()
        print(f"Projekte gefunden: {len(projects)}")
    else:
        print(f"Projekte-Fehler: {response.text}")
    
    # 3. Rechnungen testen
    print("\n3. Teste Rechnungen...")
    response = requests.get(f"{BASE_URL}/invoices/", headers=headers)
    print(f"Rechnungen Status: {response.status_code}")
    
    if response.status_code == 200:
        invoices = response.json()
        print(f"Rechnungen gefunden: {len(invoices)}")
    else:
        print(f"Rechnungen-Fehler: {response.text}")
    
    # 4. Generierungsmethoden testen
    print("\n4. Teste Generierungsmethoden...")
    response = requests.get(f"{BASE_URL}/invoice-generation/methods", headers=headers)
    print(f"Generierungsmethoden Status: {response.status_code}")
    
    if response.status_code == 200:
        methods = response.json()
        print("Generierungsmethoden verfuegbar:")
        for method_id, method_info in methods["methods"].items():
            print(f"  - {method_info['name']}")
    else:
        print(f"Generierungsmethoden-Fehler: {response.text}")
    
    return True

if __name__ == "__main__":
    test_basic_functionality()
