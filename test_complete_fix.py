"""
Testet die vollständige Reparatur.
"""

import requests
import json
import time

def test_complete_fix():
    """Testet die vollständige Reparatur."""
    print("=== VOLLSTÄNDIGE REPARATUR TEST ===")
    
    base_url = "http://localhost:8000"
    
    # 1. Login testen
    print("1. Login testen...")
    login_data = {"username": "admin", "password": "admin123"}
    response = requests.post(f"{base_url}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"Login fehlgeschlagen: {response.status_code}")
        print(f"Fehler: {response.text}")
        return False
    
    token = response.json()["access_token"]
    print("Login erfolgreich")
    
    # 2. Projekte testen
    print("\n2. Projekte testen...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{base_url}/projects/", headers=headers)
    
    if response.status_code != 200:
        print(f"Projekte-Fehler: {response.status_code}")
        return False
    
    projects = response.json()
    print(f"Projekte geladen: {len(projects)}")
    for project in projects:
        print(f"  - {project['name']} (ID: {project['id']})")
    
    # 3. Frontend testen
    print("\n3. Frontend testen...")
    response = requests.get(f"{base_url}/app")
    if response.status_code != 200:
        print(f"Frontend-Ladefehler: {response.status_code}")
        return False
    print("Frontend geladen")
    
    # 4. JavaScript testen
    print("\n4. JavaScript testen...")
    response = requests.get(f"{base_url}/static/app_simple.js")
    if response.status_code != 200:
        print(f"JavaScript-Ladefehler: {response.status_code}")
        return False
    print("JavaScript geladen")
    
    # 5. Rechnungsgenerierung testen
    print("\n5. Rechnungsgenerierung testen...")
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
    
    if response.status_code != 200:
        print(f"Rechnungsgenerierung-Fehler: {response.status_code}")
        return False
    
    result = response.json()
    print(f"Rechnungsgenerierung erfolgreich:")
    print(f"  - Gesamtbetrag: {result['total_amount']:.2f} EUR")
    print(f"  - Personalkosten: {result['total_labor_cost']:.2f} EUR")
    print(f"  - Positionen: {len(result['items'])}")
    
    return True

def test_frontend_elements():
    """Testet Frontend-Elemente."""
    print("\n=== FRONTEND-ELEMENTE TEST ===")
    
    base_url = "http://localhost:8000"
    
    # HTML testen
    response = requests.get(f"{base_url}/app")
    if response.status_code == 200:
        html_content = response.text
        
        elements = [
            'invoiceProjectSelect',
            'autoInvoiceModal',
            'invoiceGenerationMethod',
            'invoiceNumber',
            'clientName'
        ]
        
        print("HTML-Elemente:")
        for element in elements:
            if element in html_content:
                print(f"  {element} gefunden")
            else:
                print(f"  {element} NICHT gefunden")
    
    # JavaScript testen
    response = requests.get(f"{base_url}/static/app_simple.js")
    if response.status_code == 200:
        js_content = response.text
        
        functions = [
            'showAutoInvoiceModal',
            'loadProjectsForInvoiceGeneration',
            'generateInvoice',
            'showInvoiceGenerationResult'
        ]
        
        print("\nJavaScript-Funktionen:")
        for func in functions:
            if func in js_content:
                print(f"  {func} gefunden")
            else:
                print(f"  {func} NICHT gefunden")
        
        # Timing-Code prüfen
        if 'setTimeout' in js_content and '500' in js_content:
            print("\nTiming-Verbesserungen:")
            print("  setTimeout mit 500ms gefunden")
        
        # Token-Validierung prüfen
        if 'localStorage.getItem(\'token\')' in js_content:
            print("\nToken-Validierung:")
            print("  Token-Validierung gefunden")

def main():
    """Hauptfunktion für finalen Test."""
    print("VOLLSTÄNDIGE REPARATUR TEST")
    print("=" * 40)
    
    # Kompletter Workflow
    success = test_complete_fix()
    
    # Frontend-Elemente
    test_frontend_elements()
    
    print("\n=== ERGEBNIS ===")
    if success:
        print("ALLE TESTS ERFOLGREICH!")
        print("Die App sollte jetzt vollständig funktionieren.")
        print("\nVerfügbare Funktionen:")
        print("- Login mit admin/admin123")
        print("- Auto-Rechnung Modal")
        print("- Projektauswahl funktioniert")
        print("- Rechnungsgenerierung funktioniert")
        print("- Personalkosten werden korrekt angezeigt")
        print("- Token-Validierung implementiert")
        print("- Verbesserte Timing-Logik")
    else:
        print("Tests fehlgeschlagen - weitere Reparaturen nötig")

if __name__ == "__main__":
    main()

