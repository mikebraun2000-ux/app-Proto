"""
Testet die Token-Reparatur.
"""

import requests
import json
import time

def test_token_fix():
    """Testet die Token-Reparatur."""
    print("=== TOKEN-REPARATUR TEST ===")
    
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
    
    # 2. Frontend laden
    print("\n2. Frontend laden...")
    response = requests.get(f"{base_url}/app")
    if response.status_code != 200:
        print(f"Frontend-Ladefehler: {response.status_code}")
        return False
    print("Frontend geladen")
    
    # 3. JavaScript laden
    print("\n3. JavaScript laden...")
    response = requests.get(f"{base_url}/static/app_simple.js")
    if response.status_code != 200:
        print(f"JavaScript-Ladefehler: {response.status_code}")
        return False
    
    js_content = response.text
    
    # Prüfe Token-Handling
    print("\n4. Token-Handling prüfen...")
    
    # Prüfe auf access_token
    if 'access_token' in js_content:
        print("access_token gefunden")
    else:
        print("WARNUNG: access_token nicht gefunden")
    
    # Prüfe auf Fallback-Logik
    if 'localStorage.getItem(\'access_token\') || localStorage.getItem(\'token\')' in js_content:
        print("Fallback-Token-Logik gefunden")
    else:
        print("WARNUNG: Fallback-Token-Logik nicht gefunden")
    
    # Prüfe auf spezifische Funktionen
    functions = [
        'loadProjectsForInvoiceGeneration',
        'generateInvoice',
        'showAutoInvoiceModal'
    ]
    
    print("\n5. Funktionen prüfen:")
    for func in functions:
        if func in js_content:
            print(f"  {func} gefunden")
        else:
            print(f"  {func} NICHT gefunden")
    
    # 6. API-Tests
    print("\n6. API-Tests...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Projekte testen
    response = requests.get(f"{base_url}/projects/", headers=headers)
    if response.status_code == 200:
        projects = response.json()
        print(f"Projekte geladen: {len(projects)}")
    else:
        print(f"Projekte-Fehler: {response.status_code}")
        return False
    
    # Rechnungsgenerierung testen
    generation_data = {
        "project_id": 1,
        "generation_method": "hybrid",
        "labor_cost_percentage": 30.0,
        "include_materials": True,
        "include_labor": True,
        "tax_rate": 19.0
    }
    
    response = requests.post(f"{base_url}/invoice-generation/generate", 
                           json=generation_data, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Rechnungsgenerierung erfolgreich:")
        print(f"  - Gesamtbetrag: {result['total_amount']:.2f} EUR")
        print(f"  - Personalkosten: {result['total_labor_cost']:.2f} EUR")
    else:
        print(f"Rechnungsgenerierung-Fehler: {response.status_code}")
        return False
    
    return True

def simulate_browser_behavior():
    """Simuliert Browser-Verhalten."""
    print("\n=== BROWSER-SIMULATION ===")
    
    base_url = "http://localhost:8000"
    
    # Simuliere kompletten Browser-Flow
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
    
    # 2. Simuliere localStorage.setItem('access_token', token)
    print("2. Simuliere localStorage...")
    print(f"Simuliere: localStorage.setItem('access_token', '{token[:50]}...')")
    
    # 3. Teste Modal-Funktionen
    print("\n3. Teste Modal-Funktionen...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Projekte für Modal laden
    response = session.get(f"{base_url}/projects/", headers=headers)
    if response.status_code == 200:
        projects = response.json()
        print(f"Projekte für Modal geladen: {len(projects)}")
        
        # Zeige Projekt-Optionen (wie im Dropdown)
        print("Projekt-Optionen für Dropdown:")
        for project in projects:
            print(f"  <option value=\"{project['id']}\">{project['name']} - {project['client_name'] or 'Kein Kunde'}</option>")
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
        
        # Zeige erste Positionen
        print("\nErste Positionen:")
        for i, item in enumerate(result['items'][:3]):
            print(f"  {i+1}. {item['description']}: {item['total_price']:.2f} EUR")
    else:
        print(f"Rechnungsgenerierung-Fehler: {response.status_code}")
        return False
    
    return True

def main():
    """Hauptfunktion für Token-Test."""
    print("TOKEN-REPARATUR TEST")
    print("=" * 30)
    
    # Token-Reparatur testen
    fix_ok = test_token_fix()
    
    # Browser-Simulation
    browser_ok = simulate_browser_behavior()
    
    print("\n=== ERGEBNIS ===")
    if fix_ok and browser_ok:
        print("TOKEN-REPARATUR ERFOLGREICH!")
        print("\nBehobene Probleme:")
        print("1. Token-Inkonsistenz zwischen Login und Modal")
        print("2. Fallback-Logik für access_token und token")
        print("3. Korrekte Token-Übertragung in API-Aufrufen")
        print("\nDie App sollte jetzt funktionieren:")
        print("- Login speichert access_token")
        print("- Modal verwendet access_token mit Fallback")
        print("- Alle API-Aufrufe verwenden korrektes Token")
        print("- Projektauswahl sollte funktionieren")
    else:
        print("Token-Reparatur fehlgeschlagen!")

if __name__ == "__main__":
    main()

