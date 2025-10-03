"""
Vollständiger System-Debug-Test.
Testet alle kritischen Komponenten.
"""

import requests
import json
import time

def test_complete_system():
    """Testet das komplette System."""
    print("=== VOLLSTÄNDIGER SYSTEM-DEBUG-TEST ===")
    
    base_url = "http://localhost:8000"
    
    # 1. Server-Status prüfen
    print("1. Server-Status prüfen...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"   Server läuft: {response.status_code}")
    except Exception as e:
        print(f"   Server-Fehler: {e}")
        return False
    
    # 2. Login testen
    print("\n2. Login testen...")
    login_data = {"username": "admin", "password": "admin123"}
    try:
        response = requests.post(f"{base_url}/auth/login", json=login_data, timeout=10)
        if response.status_code == 200:
            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print(f"   Login erfolgreich: {token[:50]}...")
        else:
            print(f"   Login fehlgeschlagen: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   Login-Fehler: {e}")
        return False
    
    # 3. Rechnungen abrufen
    print("\n3. Rechnungen abrufen...")
    try:
        response = requests.get(f"{base_url}/invoices/", headers=headers, timeout=10)
        if response.status_code == 200:
            invoices = response.json()
            print(f"   Rechnungen geladen: {len(invoices)}")
            if invoices:
                test_invoice = invoices[0]
                print(f"   Test-Rechnung: {test_invoice.get('invoice_number', 'N/A')}")
            else:
                print("   Keine Rechnungen vorhanden")
        else:
            print(f"   Fehler beim Laden: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   Rechnungen-Fehler: {e}")
        return False
    
    # 4. Rechnung bearbeiten testen
    print("\n4. Rechnung bearbeiten testen...")
    if invoices:
        test_invoice = invoices[0]
        edit_data = {
            "invoice_number": f"{test_invoice['invoice_number']}-DEBUG",
            "status": "versendet",
            "client_name": "Debug Kunde",
            "total_amount": 123.45,
            "title": "Debug Test",
            "description": "Debug-Beschreibung"
        }
        
        try:
            response = requests.put(f"{base_url}/invoices/{test_invoice['id']}", 
                                  json=edit_data, headers=headers, timeout=10)
            if response.status_code == 200:
                updated_invoice = response.json()
                print(f"   Bearbeitung erfolgreich: {updated_invoice['invoice_number']}")
            else:
                print(f"   Bearbeitung fehlgeschlagen: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"   Bearbeitung-Fehler: {e}")
            return False
    
    # 5. Frontend testen
    print("\n5. Frontend testen...")
    try:
        response = requests.get(f"{base_url}/app", timeout=5)
        if response.status_code == 200:
            print("   Frontend lädt erfolgreich")
        else:
            print(f"   Frontend-Fehler: {response.status_code}")
            return False
    except Exception as e:
        print(f"   Frontend-Fehler: {e}")
        return False
    
    # 6. JavaScript testen
    print("\n6. JavaScript testen...")
    try:
        response = requests.get(f"{base_url}/static/app_simple.js", timeout=5)
        if response.status_code == 200:
            js_content = response.text
            required_functions = ['editInvoice', 'showInvoiceEditModal', 'saveInvoiceEdit']
            missing = [f for f in required_functions if f'function {f}(' not in js_content]
            if not missing:
                print("   JavaScript-Funktionen vorhanden")
            else:
                print(f"   Fehlende Funktionen: {missing}")
                return False
        else:
            print(f"   JavaScript-Fehler: {response.status_code}")
            return False
    except Exception as e:
        print(f"   JavaScript-Fehler: {e}")
        return False
    
    return True

def test_auth_system():
    """Testet das Authentifizierungssystem."""
    print("\n=== AUTH-SYSTEM TEST ===")
    
    base_url = "http://localhost:8000"
    
    # Test verschiedene Benutzer
    test_users = [
        {"username": "admin", "password": "admin123"},
        {"username": "buchhalter", "password": "admin123"},
        {"username": "mitarbeiter1", "password": "admin123"}
    ]
    
    for user in test_users:
        print(f"Teste Login für {user['username']}...")
        try:
            response = requests.post(f"{base_url}/auth/login", json=user, timeout=5)
            if response.status_code == 200:
                print(f"   {user['username']}: ERFOLGREICH")
            else:
                print(f"   {user['username']}: FEHLGESCHLAGEN ({response.status_code})")
        except Exception as e:
            print(f"   {user['username']}: FEHLER - {e}")

def main():
    """Hauptfunktion."""
    print("VOLLSTÄNDIGER SYSTEM-DEBUG")
    print("=" * 50)
    
    # Test 1: Komplettes System
    success = test_complete_system()
    
    # Test 2: Auth-System
    test_auth_system()
    
    print("\n=== ERGEBNIS ===")
    if success:
        print("ALLE TESTS ERFOLGREICH!")
        print("Das System funktioniert vollständig.")
    else:
        print("EINIGE TESTS FEHLGESCHLAGEN!")
        print("Das System hat noch Probleme.")

if __name__ == "__main__":
    main()

