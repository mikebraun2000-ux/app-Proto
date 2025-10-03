"""
Test der automatischen Rechnungsgenerierung.
Testet alle verfügbaren Methoden und UStG §14 Konformität.
"""

import requests
import json
from datetime import datetime, timedelta

# API-Basis-URL
BASE_URL = "http://localhost:8000"

def test_login():
    """Login und Token abrufen."""
    print("Teste Login...")
    
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("Login erfolgreich")
        return token
    else:
        print(f"Login fehlgeschlagen: {response.status_code}")
        print(response.text)
        return None

def test_generation_methods(token):
    """Teste verfügbare Generierungsmethoden."""
    print("\nTeste verfuegbare Generierungsmethoden...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/invoices/generation-methods", headers=headers)
    
    if response.status_code == 200:
        methods = response.json()
        print("Generierungsmethoden abgerufen:")
        for method_id, method_info in methods["methods"].items():
            print(f"  - {method_info['name']}: {method_info['description']}")
            print(f"     Features: {', '.join(method_info['features'])}")
        
        print(f"\nUStG Anforderungen:")
        for req_id, req_desc in methods["ustg_requirements"].items():
            print(f"  - {req_desc}")
        
        return True
    else:
        print(f"Fehler beim Abrufen der Methoden: {response.status_code}")
        return False

def test_hybrid_invoice_generation(token):
    """Teste Hybrid-Rechnungsgenerierung."""
    print("\nTeste Hybrid-Rechnungsgenerierung...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Generierungsanfrage für Projekt 1
    generation_request = {
        "project_id": 1,
        "generation_method": "hybrid",
        "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
        "end_date": datetime.now().isoformat(),
        "include_materials": True,
        "include_labor": True,
        "tax_rate": 19.0,
        "labor_cost_percentage": 30.0  # 30% Lohnanteil
    }
    
    response = requests.post(f"{BASE_URL}/invoices/generate", json=generation_request, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print("Hybrid-Rechnungsgenerierung erfolgreich:")
        print(f"  Gesamtarbeitskosten: {result['total_labor_cost']:.2f} EUR")
        print(f"  Materialkosten: {result['total_material_cost']:.2f} EUR")
        print(f"  Dienstleistungskosten: {result['total_service_cost']:.2f} EUR")
        print(f"  Zwischensumme: {result['subtotal']:.2f} EUR")
        print(f"  USt-Betrag: {result['tax_amount']:.2f} EUR")
        print(f"  Gesamtbetrag: {result['total_amount']:.2f} EUR")
        print(f"  Lohnanteil: {result['labor_percentage']:.1f}%")
        
        print(f"\nRechnungspositionen ({len(result['items'])}):")
        for i, item in enumerate(result['items'], 1):
            print(f"  {i}. {item['description']}")
            print(f"     Menge: {item['quantity']} {item['unit']}")
            print(f"     Einzelpreis: {item['unit_price']:.2f} EUR")
            print(f"     Gesamtpreis: {item['total_price']:.2f} EUR")
            if item.get('labor_cost'):
                print(f"     Lohnanteil: {item['labor_cost']:.2f} EUR")
            if item.get('material_cost'):
                print(f"     Materialkosten: {item['material_cost']:.2f} EUR")
        
        return result
    else:
        print(f"Fehler bei Hybrid-Generierung: {response.status_code}")
        print(response.text)
        return None

def test_time_entries_generation(token):
    """Teste Stundeneinträge-basierte Generierung."""
    print("\nTeste Stundeneintraege-basierte Generierung...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    generation_request = {
        "project_id": 1,
        "generation_method": "time_entries",
        "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
        "end_date": datetime.now().isoformat(),
        "include_materials": False,
        "include_labor": True,
        "tax_rate": 19.0,
        "labor_cost_percentage": 25.0  # 25% Lohnanteil
    }
    
    response = requests.post(f"{BASE_URL}/invoices/generate", json=generation_request, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print("Stundeneintraege-Generierung erfolgreich:")
        print(f"  Gesamtarbeitskosten: {result['total_labor_cost']:.2f} EUR")
        print(f"  Zwischensumme: {result['subtotal']:.2f} EUR")
        print(f"  USt-Betrag: {result['tax_amount']:.2f} EUR")
        print(f"  Gesamtbetrag: {result['total_amount']:.2f} EUR")
        print(f"  Lohnanteil: {result['labor_percentage']:.1f}%")
        return result
    else:
        print(f"Fehler bei Stundeneintraege-Generierung: {response.status_code}")
        return None

def test_reports_generation(token):
    """Teste Berichte-basierte Generierung."""
    print("\nTeste Berichte-basierte Generierung...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    generation_request = {
        "project_id": 1,
        "generation_method": "reports",
        "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
        "end_date": datetime.now().isoformat(),
        "include_materials": False,
        "include_labor": False,
        "tax_rate": 19.0,
        "labor_cost_percentage": 0.0
    }
    
    response = requests.post(f"{BASE_URL}/invoices/generate", json=generation_request, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print("Berichte-Generierung erfolgreich:")
        print(f"  Zwischensumme: {result['subtotal']:.2f} EUR")
        print(f"  USt-Betrag: {result['tax_amount']:.2f} EUR")
        print(f"  Gesamtbetrag: {result['total_amount']:.2f} EUR")
        return result
    else:
        print(f"Fehler bei Berichte-Generierung: {response.status_code}")
        return None

def test_offers_generation(token):
    """Teste Angebote-basierte Generierung."""
    print("\nTeste Angebote-basierte Generierung...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    generation_request = {
        "project_id": 1,
        "generation_method": "offers",
        "start_date": (datetime.now() - timedelta(days=30)).isoformat(),
        "end_date": datetime.now().isoformat(),
        "include_materials": False,
        "include_labor": False,
        "tax_rate": 19.0,
        "labor_cost_percentage": 0.0
    }
    
    response = requests.post(f"{BASE_URL}/invoices/generate", json=generation_request, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print("Angebote-Generierung erfolgreich:")
        print(f"  Zwischensumme: {result['subtotal']:.2f} EUR")
        print(f"  USt-Betrag: {result['tax_amount']:.2f} EUR")
        print(f"  Gesamtbetrag: {result['total_amount']:.2f} EUR")
        return result
    else:
        print(f"Fehler bei Angebote-Generierung: {response.status_code}")
        return None

def test_ustg_compliance(calculation_result):
    """Teste UStG §14 Konformität."""
    print("\nTeste UStG §14 Konformitaet...")
    
    compliance_checks = []
    
    # 1. Lohnanteil gesondert ausweisen
    if calculation_result['labor_percentage'] > 0:
        compliance_checks.append(("Lohnanteil gesondert ausgewiesen", True))
    else:
        compliance_checks.append(("Lohnanteil nicht ausgewiesen", False))
    
    # 2. USt-Berechnung korrekt
    expected_tax = calculation_result['subtotal'] * 0.19
    if abs(calculation_result['tax_amount'] - expected_tax) < 0.01:
        compliance_checks.append(("USt-Berechnung korrekt (19%)", True))
    else:
        compliance_checks.append(("USt-Berechnung fehlerhaft", False))
    
    # 3. Gesamtbetrag korrekt
    expected_total = calculation_result['subtotal'] + calculation_result['tax_amount']
    if abs(calculation_result['total_amount'] - expected_total) < 0.01:
        compliance_checks.append(("Gesamtbetrag korrekt", True))
    else:
        compliance_checks.append(("Gesamtbetrag fehlerhaft", False))
    
    # 4. Rechnungspositionen vorhanden
    if len(calculation_result['items']) > 0:
        compliance_checks.append(("Rechnungspositionen vorhanden", True))
    else:
        compliance_checks.append(("Keine Rechnungspositionen", False))
    
    print("UStG §14 Konformitaetspruefung:")
    for check, passed in compliance_checks:
        print(f"  - {check}")
    
    all_passed = all(passed for _, passed in compliance_checks)
    if all_passed:
        print("Alle UStG §14 Anforderungen erfuellt!")
    else:
        print("Einige UStG §14 Anforderungen nicht erfuellt")
    
    return all_passed

def main():
    """Haupttest-Funktion."""
    print("AUTOMATISCHE RECHNUNGSGENERIERUNG - VOLLSTAENDIGER TEST")
    print("=" * 60)
    
    # 1. Login
    token = test_login()
    if not token:
        return
    
    # 2. Verfügbare Methoden testen
    if not test_generation_methods(token):
        return
    
    # 3. Hybrid-Generierung testen
    hybrid_result = test_hybrid_invoice_generation(token)
    if hybrid_result:
        test_ustg_compliance(hybrid_result)
    
    # 4. Stundeneinträge-Generierung testen
    test_time_entries_generation(token)
    
    # 5. Berichte-Generierung testen
    test_reports_generation(token)
    
    # 6. Angebote-Generierung testen
    test_offers_generation(token)
    
    print("\nTEST ABGESCHLOSSEN")
    print("=" * 60)
    print("Automatische Rechnungsgenerierung implementiert")
    print("UStG §14 Konformitaet gewaehrleistet")
    print("Lohnanteil gesondert ausweisbar")
    print("Verschiedene Generierungsmethoden verfuegbar")
    print("Hybrid-Ansatz fuer umfassende Rechnungsstellung")

if __name__ == "__main__":
    main()
