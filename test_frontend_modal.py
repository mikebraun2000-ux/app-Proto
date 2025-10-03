"""
Test der Frontend-Modal-Funktionalität.
"""

import requests
import time

BASE_URL = "http://localhost:8000"

def test_frontend_modal():
    """Teste die Frontend-Modal-Funktionalität."""
    print("Teste Frontend-Modal-Funktionalität...")
    
    # 1. Login
    print("1. Login...")
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
    
    # 2. Teste Projekte-API direkt
    print("\n2. Teste Projekte-API...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/projects/", headers=headers)
    print(f"Projekte Status: {response.status_code}")
    
    if response.status_code == 200:
        projects = response.json()
        print(f"Projekte gefunden: {len(projects)}")
        for project in projects:
            print(f"  - {project['name']} (ID: {project['id']})")
    else:
        print(f"Projekte-Fehler: {response.text}")
        return False
    
    # 3. Teste HTML-Seite
    print("\n3. Teste HTML-Seite...")
    response = requests.get(f"{BASE_URL}/app")
    print(f"HTML Status: {response.status_code}")
    
    if response.status_code == 200:
        html_content = response.text
        if 'invoiceProjectSelect' in html_content:
            print("OK: invoiceProjectSelect Element gefunden")
        else:
            print("FEHLER: invoiceProjectSelect Element NICHT gefunden")
            
        if 'autoInvoiceModal' in html_content:
            print("OK: autoInvoiceModal Element gefunden")
        else:
            print("FEHLER: autoInvoiceModal Element NICHT gefunden")
    else:
        print(f"HTML-Fehler: {response.text}")
        return False
    
    # 4. Teste JavaScript
    print("\n4. Teste JavaScript...")
    response = requests.get(f"{BASE_URL}/static/app_simple.js")
    print(f"JavaScript Status: {response.status_code}")
    
    if response.status_code == 200:
        js_content = response.text
        if 'showAutoInvoiceModal' in js_content:
            print("OK: showAutoInvoiceModal Funktion gefunden")
        else:
            print("FEHLER: showAutoInvoiceModal Funktion NICHT gefunden")
            
        if 'loadProjectsForInvoiceGeneration' in js_content:
            print("OK: loadProjectsForInvoiceGeneration Funktion gefunden")
        else:
            print("FEHLER: loadProjectsForInvoiceGeneration Funktion NICHT gefunden")
    else:
        print(f"JavaScript-Fehler: {response.text}")
        return False
    
    return True

if __name__ == "__main__":
    test_frontend_modal()
