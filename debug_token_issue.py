"""
Debuggt das Token-Problem im Frontend.
"""

import requests
import json

def debug_token_issue():
    """Debuggt das Token-Problem."""
    print("=== TOKEN-PROBLEM DEBUG ===")
    
    base_url = "http://localhost:8000"
    
    # 1. Login testen
    print("1. Login testen...")
    login_data = {"username": "admin", "password": "admin123"}
    response = requests.post(f"{base_url}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"Login fehlgeschlagen: {response.status_code}")
        return False
    
    token = response.json()["access_token"]
    print(f"Token erhalten: {token[:50]}...")
    
    # 2. Token-Validierung testen
    print("\n2. Token-Validierung testen...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{base_url}/auth/me", headers=headers)
    
    if response.status_code != 200:
        print(f"Token-Validierung fehlgeschlagen: {response.status_code}")
        return False
    
    user_data = response.json()
    print(f"Benutzer validiert: {user_data['username']}")
    
    # 3. Projekte mit Token testen
    print("\n3. Projekte mit Token testen...")
    response = requests.get(f"{base_url}/projects/", headers=headers)
    
    if response.status_code != 200:
        print(f"Projekte-Fehler: {response.status_code}")
        return False
    
    projects = response.json()
    print(f"Projekte geladen: {len(projects)}")
    
    # 4. Frontend HTML prüfen
    print("\n4. Frontend HTML prüfen...")
    response = requests.get(f"{base_url}/app")
    if response.status_code == 200:
        html_content = response.text
        
        # Prüfe auf Token-Handling im HTML
        if 'localStorage' in html_content:
            print("localStorage wird verwendet")
        else:
            print("WARNUNG: localStorage nicht gefunden")
        
        # Prüfe auf Token-Validierung
        if 'getItem' in html_content:
            print("localStorage.getItem gefunden")
        else:
            print("WARNUNG: localStorage.getItem nicht gefunden")
        
        # Prüfe auf Bearer Token
        if 'Bearer' in html_content:
            print("Bearer Token-Handling gefunden")
        else:
            print("WARNUNG: Bearer Token-Handling nicht gefunden")
    
    # 5. JavaScript prüfen
    print("\n5. JavaScript prüfen...")
    response = requests.get(f"{base_url}/static/app_simple.js")
    if response.status_code == 200:
        js_content = response.text
        
        # Prüfe auf Token-Funktionen
        token_functions = [
            'localStorage.getItem',
            'localStorage.setItem',
            'Bearer',
            'Authorization'
        ]
        
        print("JavaScript Token-Funktionen:")
        for func in token_functions:
            if func in js_content:
                print(f"  {func} gefunden")
            else:
                print(f"  {func} NICHT gefunden")
        
        # Prüfe auf spezifische Token-Handling-Funktionen
        specific_functions = [
            'loadProjectsForInvoiceGeneration',
            'generateInvoice',
            'showAutoInvoiceModal'
        ]
        
        print("\nSpezifische Funktionen:")
        for func in specific_functions:
            if func in js_content:
                print(f"  {func} gefunden")
            else:
                print(f"  {func} NICHT gefunden")
    
    return True

def test_browser_simulation():
    """Simuliert Browser-Verhalten."""
    print("\n=== BROWSER-SIMULATION ===")
    
    base_url = "http://localhost:8000"
    
    # Simuliere Browser-Session
    session = requests.Session()
    
    # 1. Login
    print("1. Browser-Login...")
    login_data = {"username": "admin", "password": "admin123"}
    response = session.post(f"{base_url}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"Login fehlgeschlagen: {response.status_code}")
        return False
    
    token = response.json()["access_token"]
    print(f"Token erhalten: {token[:50]}...")
    
    # 2. Simuliere localStorage
    print("\n2. Simuliere localStorage...")
    # In einem echten Browser würde das so aussehen:
    # localStorage.setItem('token', token)
    print(f"Simuliere: localStorage.setItem('token', '{token[:50]}...')")
    
    # 3. Teste API-Aufrufe mit Token
    print("\n3. Teste API-Aufrufe...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Projekte laden
    response = session.get(f"{base_url}/projects/", headers=headers)
    if response.status_code == 200:
        projects = response.json()
        print(f"Projekte erfolgreich geladen: {len(projects)}")
        
        # Zeige Projekt-Details
        for project in projects[:3]:  # Erste 3 Projekte
            print(f"  - {project['name']} (ID: {project['id']})")
    else:
        print(f"Projekte-Fehler: {response.status_code}")
        return False
    
    # 4. Teste Rechnungsgenerierung
    print("\n4. Teste Rechnungsgenerierung...")
    generation_data = {
        "project_id": 1,
        "generation_method": "hybrid",
        "labor_cost_percentage": 30.0,
        "include_materials": True,
        "include_labor": True,
        "tax_rate": 19.0
    }
    
    response = session.post(f"{base_url}/invoice-generation/generate", 
                           json=generation_data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Rechnungsgenerierung erfolgreich:")
        print(f"  - Gesamtbetrag: {result['total_amount']:.2f} EUR")
        print(f"  - Personalkosten: {result['total_labor_cost']:.2f} EUR")
        print(f"  - Positionen: {len(result['items'])}")
    else:
        print(f"Rechnungsgenerierung-Fehler: {response.status_code}")
        return False
    
    return True

def main():
    """Hauptfunktion für Token-Debug."""
    print("TOKEN-PROBLEM DEBUG")
    print("=" * 30)
    
    # Backend-Tests
    backend_ok = debug_token_issue()
    
    # Browser-Simulation
    browser_ok = test_browser_simulation()
    
    print("\n=== ERGEBNIS ===")
    if backend_ok and browser_ok:
        print("Backend funktioniert korrekt!")
        print("Das Problem liegt im Frontend-Token-Handling.")
        print("\nMögliche Ursachen:")
        print("1. localStorage wird nicht korrekt verwendet")
        print("2. Token wird nicht gespeichert")
        print("3. Token wird nicht korrekt übertragen")
        print("4. Timing-Problem beim Modal-Loading")
    else:
        print("Backend-Problem gefunden!")

if __name__ == "__main__":
    main()

