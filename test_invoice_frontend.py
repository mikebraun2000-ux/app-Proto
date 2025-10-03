"""
Test der Frontend-Funktionalität für automatische Rechnungsgenerierung.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_invoice_generation_frontend():
    """Teste die Frontend-Funktionalität für Rechnungsgenerierung."""
    print("Teste Frontend-Funktionalität für Rechnungsgenerierung...")
    
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
    
    # 2. Projekte laden
    print("\n2. Lade Projekte...")
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
    
    # 3. Rechnungsgenerierung testen
    print("\n3. Teste Rechnungsgenerierung...")
    request_data = {
        "project_id": projects[0]["id"] if projects else 1,
        "generation_method": "hybrid",
        "labor_cost_percentage": 30.0,
        "include_materials": True,
        "include_labor": True,
        "tax_rate": 19.0
    }
    
    response = requests.post(f"{BASE_URL}/invoice-generation/generate", 
                           json=request_data, headers=headers)
    print(f"Rechnungsgenerierung Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("Rechnungsgenerierung erfolgreich:")
        print(f"  Gesamtbetrag: {result['total_amount']:.2f} EUR")
        print(f"  Lohnanteil: {result['total_labor_cost']:.2f} EUR")
        print(f"  Materialkosten: {result['total_material_cost']:.2f} EUR")
        print(f"  USt-Betrag: {result['tax_amount']:.2f} EUR")
        print(f"  Anzahl Positionen: {len(result['items'])}")
        
        # Zeige erste Positionen
        print("\nErste Rechnungspositionen:")
        for i, item in enumerate(result['items'][:3]):
            print(f"  {i+1}. {item['description']}")
            print(f"     Menge: {item['quantity']} {item['unit']}")
            print(f"     Einzelpreis: {item['unit_price']:.2f} EUR")
            print(f"     Gesamtpreis: {item['total_price']:.2f} EUR")
            if item.get('labor_cost'):
                print(f"     Lohnanteil: {item['labor_cost']:.2f} EUR")
    else:
        print(f"Rechnungsgenerierung-Fehler: {response.text}")
        return False
    
    return True

if __name__ == "__main__":
    test_invoice_generation_frontend()

