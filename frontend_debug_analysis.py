"""
Detaillierte Frontend-Debug-Analyse.
Simuliert den Browser-Workflow und identifiziert das Problem.
"""

import requests
import json
import time

def simulate_browser_workflow():
    """Simuliert den kompletten Browser-Workflow."""
    print("=== BROWSER-WORKFLOW-SIMULATION ===")
    
    base_url = "http://localhost:8000"
    session = requests.Session()
    
    # 1. Login simulieren
    print("1. Login simulieren...")
    login_data = {"username": "admin", "password": "admin123"}
    response = session.post(f"{base_url}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"Login fehlgeschlagen: {response.status_code}")
        return None
    
    token = response.json()["access_token"]
    print(f"Login erfolgreich, Token: {token[:20]}...")
    
    # 2. Frontend laden
    print("\n2. Frontend laden...")
    response = session.get(f"{base_url}/app")
    if response.status_code != 200:
        print(f"Frontend-Ladefehler: {response.status_code}")
        return None
    
    print("Frontend geladen")
    
    # 3. JavaScript laden
    print("\n3. JavaScript laden...")
    response = session.get(f"{base_url}/static/app_simple.js")
    if response.status_code != 200:
        print(f"JavaScript-Ladefehler: {response.status_code}")
        return None
    
    print("JavaScript geladen")
    
    # 4. Projekte mit Token laden (wie im Browser)
    print("\n4. Projekte mit Token laden...")
    headers = {"Authorization": f"Bearer {token}"}
    response = session.get(f"{base_url}/projects/", headers=headers)
    
    print(f"Projekte-Response: {response.status_code}")
    if response.status_code == 200:
        projects = response.json()
        print(f"Projekte geladen: {len(projects)}")
        for project in projects:
            print(f"  - {project['name']} (ID: {project['id']})")
    else:
        print(f"Projekte-Fehler: {response.text}")
    
    return token

def test_modal_functionality(token):
    """Testet die Modal-Funktionalität."""
    print("\n=== MODAL-FUNKTIONALITÄT-TEST ===")
    
    base_url = "http://localhost:8000"
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Generierungsmethoden testen
    print("1. Generierungsmethoden testen...")
    response = requests.get(f"{base_url}/invoice-generation/methods", headers=headers)
    print(f"Generierungsmethoden: {response.status_code}")
    
    if response.status_code == 200:
        methods = response.json()
        print(f"Verfügbare Methoden: {list(methods['methods'].keys())}")
    
    # 2. Rechnungsgenerierung testen
    print("\n2. Rechnungsgenerierung testen...")
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
    print(f"Rechnungsgenerierung: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Berechnung erfolgreich:")
        print(f"  - Gesamtbetrag: {result['total_amount']} EUR")
        print(f"  - Lohnanteil: {result['total_labor_cost']} EUR")
        print(f"  - Positionen: {len(result['items'])}")
    else:
        print(f"Rechnungsgenerierung-Fehler: {response.text}")

def analyze_javascript_functions():
    """Analysiert die JavaScript-Funktionen."""
    print("\n=== JAVASCRIPT-FUNKTIONS-ANALYSE ===")
    
    base_url = "http://localhost:8000"
    
    try:
        response = requests.get(f"{base_url}/static/app_simple.js")
        if response.status_code == 200:
            js_content = response.text
            
            # Wichtige Funktionen suchen
            functions = [
                'showAutoInvoiceModal',
                'loadProjectsForInvoiceGeneration', 
                'generateInvoice',
                'showInvoiceGenerationResult',
                'createInvoiceFromResult'
            ]
            
            print("JavaScript-Funktionen:")
            for func in functions:
                if func in js_content:
                    print(f"  ✅ {func} gefunden")
                else:
                    print(f"  ❌ {func} NICHT gefunden")
            
            # Projektauswahl-Code analysieren
            if 'invoiceProjectSelect' in js_content:
                print("\nProjektauswahl-Code gefunden")
                
                # Timing-Code suchen
                if 'setTimeout' in js_content:
                    print("  -> setTimeout für Timing gefunden")
                if '200' in js_content:
                    print("  -> 200ms Verzögerung gefunden")
            
    except Exception as e:
        print(f"JavaScript-Analyse-Fehler: {e}")

def main():
    """Hauptfunktion für Frontend-Debug-Analyse."""
    print("FRONTEND-DEBUG-ANALYSE")
    print("=" * 30)
    
    # 1. Browser-Workflow simulieren
    token = simulate_browser_workflow()
    
    if token:
        # 2. Modal-Funktionalität testen
        test_modal_functionality(token)
    
    # 3. JavaScript-Funktionen analysieren
    analyze_javascript_functions()
    
    print("\n=== DIAGNOSE ===")
    print("Wenn alle Tests erfolgreich sind, liegt das Problem")
    print("wahrscheinlich in der Browser-Konsole oder im")
    print("Frontend-JavaScript-Timing.")

if __name__ == "__main__":
    main()

