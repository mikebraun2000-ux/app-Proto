"""
Debug-Test für Rechnungserstellung mit detaillierter Fehleranalyse.
"""

import requests
import json
import time

def test_invoice_creation_with_auth():
    """Testet die Rechnungserstellung mit Authentifizierung."""
    print("=== RECHNUNGSERSTELLUNG DEBUG TEST ===")
    
    base_url = "http://localhost:8000"
    
    # 1. Login
    print("1. Login...")
    login_data = {"username": "admin", "password": "admin123"}
    response = requests.post(f"{base_url}/auth/login", json=login_data)
    
    if response.status_code != 200:
        print(f"Login fehlgeschlagen: {response.status_code}")
        return False
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"Token erhalten: {token[:50]}...")
    
    # 2. Rechnungsgenerierung
    print("\n2. Rechnungsgenerierung...")
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
        print(f"Rechnungsgenerierung fehlgeschlagen: {response.status_code}")
        return False
    
    calculation_result = response.json()
    print(f"Rechnungsgenerierung erfolgreich:")
    print(f"  - Gesamtbetrag: {calculation_result['total_amount']:.2f} EUR")
    print(f"  - Positionen: {len(calculation_result['items'])}")
    
    # 3. Rechnung erstellen - mit detailliertem Debug
    print("\n3. Rechnung erstellen (mit Debug)...")
    
    create_data = {
        "project_id": 1,
        "calculation": calculation_result,
        "invoice_number": f"R-{int(time.time())}",
        "client_name": "Test Kunde",
        "client_address": None
    }
    
    print(f"Request-Daten:")
    print(f"  - project_id: {create_data['project_id']}")
    print(f"  - invoice_number: {create_data['invoice_number']}")
    print(f"  - client_name: {create_data['client_name']}")
    print(f"  - calculation keys: {list(calculation_result.keys())}")
    
    response = requests.post(f"{base_url}/invoice-generation/create-from-calculation", 
                           json=create_data, headers=headers)
    
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        invoice = response.json()
        print(f"Rechnung erfolgreich erstellt:")
        print(f"  - ID: {invoice.get('id')}")
        print(f"  - Nummer: {invoice.get('invoice_number')}")
        print(f"  - Betrag: {invoice.get('total_amount', 0):.2f} EUR")
        return True
    else:
        print(f"Fehler beim Erstellen der Rechnung:")
        try:
            error_data = response.json()
            print(f"Error JSON: {json.dumps(error_data, indent=2)}")
            
            if 'detail' in error_data:
                if isinstance(error_data['detail'], list):
                    for i, err in enumerate(error_data['detail']):
                        print(f"  Fehler {i+1}: {err.get('loc', [])} - {err.get('msg', '')}")
                else:
                    print(f"  Detail: {error_data['detail']}")
        except:
            print(f"Error Text: {response.text}")
        return False

def test_simple_request():
    """Testet einen einfachen Request ohne komplexe Daten."""
    print("\n=== EINFACHER REQUEST TEST ===")
    
    base_url = "http://localhost:8000"
    
    # Login
    login_data = {"username": "admin", "password": "admin123"}
    response = requests.post(f"{base_url}/auth/login", json=login_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Einfacher Test-Request
    simple_data = {
        "project_id": 1,
        "calculation": {
            "total_amount": 100.0,
            "total_labor_cost": 30.0,
            "total_material_cost": 0.0,
            "total_service_cost": 70.0,
            "subtotal": 100.0,
            "tax_amount": 19.0,
            "labor_percentage": 30.0,
            "items": []
        },
        "invoice_number": f"TEST-{int(time.time())}",
        "client_name": "Test Kunde",
        "client_address": None
    }
    
    print(f"Teste einfachen Request...")
    response = requests.post(f"{base_url}/invoice-generation/create-from-calculation", 
                           json=simple_data, headers=headers)
    
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    else:
        print(f"Success: {response.json()}")
    
    return response.status_code == 200

def main():
    """Hauptfunktion für Debug-Test."""
    print("RECHNUNGSERSTELLUNG DEBUG TEST")
    print("=" * 50)
    
    # Test 1: Vollständiger Test
    success1 = test_invoice_creation_with_auth()
    
    # Test 2: Einfacher Test
    success2 = test_simple_request()
    
    print("\n=== ERGEBNIS ===")
    print(f"Vollständiger Test: {'ERFOLGREICH' if success1 else 'FEHLGESCHLAGEN'}")
    print(f"Einfacher Test: {'ERFOLGREICH' if success2 else 'FEHLGESCHLAGEN'}")
    
    if not success1 and not success2:
        print("\nPROBLEM: Beide Tests fehlgeschlagen!")
        print("Mögliche Ursachen:")
        print("1. Backend-Endpoint funktioniert nicht")
        print("2. Request-Format ist falsch")
        print("3. Authentifizierung funktioniert nicht")
        print("4. Datenbank-Problem")

if __name__ == "__main__":
    main()

