"""
Test-Script für Rechnungsbearbeitung und Vorschau-Funktionalität.
"""

import requests
import json
import time

def test_invoice_edit_and_preview():
    """Testet die Rechnungsbearbeitung und Vorschau-Funktionalität."""
    print("=== RECHNUNGSBEARBEITUNG UND VORSCHAU TEST ===")
    
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
    
    # 2. Rechnungen abrufen
    print("\n2. Rechnungen abrufen...")
    response = requests.get(f"{base_url}/invoices/", headers=headers)
    
    if response.status_code != 200:
        print(f"Fehler beim Abrufen der Rechnungen: {response.status_code}")
        return False
    
    invoices = response.json()
    print(f"Rechnungen gefunden: {len(invoices)}")
    
    if not invoices:
        print("Keine Rechnungen vorhanden - erstelle Test-Rechnung...")
        return create_test_invoice_and_edit(base_url, headers)
    
    # 3. Erste Rechnung bearbeiten
    test_invoice = invoices[0]
    print(f"\n3. Teste Bearbeitung für Rechnung: {test_invoice['invoice_number']}")
    
    # Bearbeitungsdaten (ohne Datum-Felder)
    edit_data = {
        "invoice_number": f"{test_invoice['invoice_number']}-EDITED",
        "status": "versendet",
        "client_name": "Bearbeiteter Kunde",
        "total_amount": 999.99,
        "title": "Bearbeitete Test-Rechnung",
        "description": "Diese Rechnung wurde über die API bearbeitet",
        "client_address": "Bearbeitete Adresse\n12345 Teststadt"
    }
    
    # Rechnung aktualisieren
    response = requests.put(f"{base_url}/invoices/{test_invoice['id']}", 
                          json=edit_data, headers=headers)
    
    if response.status_code != 200:
        print(f"Fehler beim Bearbeiten der Rechnung: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    updated_invoice = response.json()
    print(f"Rechnung erfolgreich bearbeitet:")
    print(f"  - Neue Nummer: {updated_invoice['invoice_number']}")
    print(f"  - Status: {updated_invoice['status']}")
    print(f"  - Kunde: {updated_invoice['client_name']}")
    print(f"  - Betrag: {updated_invoice['total_amount']} EUR")
    
    # 4. Rechnung abrufen und Vorschau testen
    print(f"\n4. Teste Vorschau für Rechnung: {updated_invoice['invoice_number']}")
    
    response = requests.get(f"{base_url}/invoices/{updated_invoice['id']}", headers=headers)
    
    if response.status_code == 200:
        invoice_details = response.json()
    print("Rechnungsdetails abgerufen:")
    print(f"  - ID: {invoice_details['id']}")
    print(f"  - Titel: {invoice_details['title']}")
    print(f"  - Beschreibung: {invoice_details['description']}")
    print(f"  - Adresse: {invoice_details['client_address']}")
    
    # Items prüfen
    if invoice_details.get('items'):
        if isinstance(invoice_details['items'], str):
            try:
                items = json.loads(invoice_details['items'])
            except json.JSONDecodeError:
                print("  - Positionen: Fehler beim Parsen")
                items = []
        else:
            items = invoice_details['items']

        if items:
            print(f"  - Positionen: {len(items)}")
            for i, item in enumerate(items[:3]):
                total_price = item.get('total_price')
                if total_price is None:
                    quantity = item.get('quantity') or 0
                    unit_price = item.get('unit_price') or 0
                    total_price = quantity * unit_price
                print(f"    {i+1}. {item.get('description', 'N/A')} - {total_price:.2f} EUR")

    # PDF testen
    if not test_invoice_pdf_download(base_url, headers, updated_invoice['id']):
        return False

    return True

def create_test_invoice_and_edit(base_url, headers):
    """Erstellt eine Test-Rechnung und bearbeitet sie."""
    print("Erstelle Test-Rechnung...")
    
    # Test-Rechnung erstellen
    test_invoice_data = {
        "invoice_number": f"TEST-{int(time.time())}",
        "title": "Test-Rechnung für Bearbeitung",
        "description": "Automatisch erstellte Test-Rechnung",
        "client_name": "Test Kunde",
        "client_address": "Teststraße 123\n12345 Teststadt",
        "total_amount": 500.00,
        "currency": "EUR",
        "status": "entwurf",
        "items": json.dumps([
            {
                "description": "Test-Position 1",
                "quantity": 1,
                "unit": "Stk",
                "unit_price": 300.00,
                "total_price": 300.00
            },
            {
                "description": "Test-Position 2", 
                "quantity": 2,
                "unit": "Stk",
                "unit_price": 100.00,
                "total_price": 200.00
            }
        ])
    }
    
    response = requests.post(f"{base_url}/invoices/", json=test_invoice_data, headers=headers)
    
    if response.status_code != 200:
        print(f"Fehler beim Erstellen der Test-Rechnung: {response.status_code}")
        return False
    
    created_invoice = response.json()
    print(f"Test-Rechnung erstellt: {created_invoice['invoice_number']}")
    
    # Jetzt bearbeiten
    edit_data = {
        "invoice_number": f"{created_invoice['invoice_number']}-EDITED",
        "status": "versendet",
        "client_name": "Bearbeiteter Test-Kunde",
        "total_amount": 750.00,
        "title": "Bearbeitete Test-Rechnung",
        "description": "Diese Test-Rechnung wurde bearbeitet",
        "client_address": "Bearbeitete Teststraße 456\n54321 Bearbeitetstadt"
    }
    
    response = requests.put(f"{base_url}/invoices/{created_invoice['id']}", 
                          json=edit_data, headers=headers)
    
    if response.status_code != 200:
        print(f"Fehler beim Bearbeiten der Test-Rechnung: {response.status_code}")
        return False
    
    updated_invoice = response.json()
    print(f"Test-Rechnung erfolgreich bearbeitet:")
    print(f"  - Neue Nummer: {updated_invoice['invoice_number']}")
    print(f"  - Status: {updated_invoice['status']}")
    print(f"  - Kunde: {updated_invoice['client_name']}")
    print(f"  - Betrag: {updated_invoice['total_amount']} EUR")
    
    return True

def test_frontend_integration():
    """Testet die Frontend-Integration."""
    print("\n=== FRONTEND-INTEGRATION TEST ===")
    
    base_url = "http://localhost:8000"
    
    # 1. Frontend laden
    print("1. Frontend laden...")
    response = requests.get(f"{base_url}/app")
    
    if response.status_code != 200:
        print(f"Fehler beim Laden des Frontends: {response.status_code}")
        return False
    
    print("Frontend erfolgreich geladen")
    
    # 2. JavaScript laden
    print("2. JavaScript laden...")
    response = requests.get(f"{base_url}/static/app_simple.js")
    
    if response.status_code != 200:
        print(f"Fehler beim Laden des JavaScript: {response.status_code}")
        return False
    
    js_content = response.text
    
    # Prüfe ob die neuen Funktionen vorhanden sind
    required_functions = [
        'editInvoice',
        'showInvoiceEditModal', 
        'saveInvoiceEdit',
        'previewInvoice',
        'showInvoicePreviewModal',
        'downloadInvoicePDF'
    ]
    
    missing_functions = []
    for func in required_functions:
        if f'function {func}(' not in js_content:
            missing_functions.append(func)
    
    if missing_functions:
        print(f"Fehlende JavaScript-Funktionen: {missing_functions}")
        return False
    
    print("Alle erforderlichen JavaScript-Funktionen gefunden")
    
    # 3. HTML-Struktur prüfen
    print("3. HTML-Struktur prüfen...")
    html_content = requests.get(f"{base_url}/app").text
    
    required_elements = [
        'invoices-table',
        'id="invoices-table"'
    ]
    
    missing_elements = []
    for element in required_elements:
        if element not in html_content:
            missing_elements.append(element)
    
    if missing_elements:
        print(f"Fehlende HTML-Elemente: {missing_elements}")
        return False
    
    print("Alle erforderlichen HTML-Elemente gefunden")
    
    return True

def test_invoice_pdf_download(base_url, headers, invoice_id):
    print("5. PDF herunterladen und prüfen...")
    response = requests.get(f"{base_url}/invoices/{invoice_id}/pdf", headers=headers)

    if response.status_code != 200:
        print(f"Fehler beim Herunterladen des PDFs: {response.status_code}")
        try:
            print("Antwort:", response.json())
        except Exception:
            print("Antwort konnte nicht geparst werden.")
        return False

    content_type = response.headers.get('content-type')
    if content_type != 'application/pdf':
        print(f"Unerwarteter Content-Type: {content_type}")
        return False

    content_length = len(response.content)
    print(f"PDF erfolgreich geladen ({content_length} Bytes)")

    return True

def main():
    """Hauptfunktion für den Test."""
    print("RECHNUNGSBEARBEITUNG UND VORSCHAU TEST")
    print("=" * 50)
    
    # Test 1: Backend-Funktionalität
    success1 = test_invoice_edit_and_preview()
    
    # Test 2: Frontend-Integration
    success2 = test_frontend_integration()
    
    print("\n=== ERGEBNIS ===")
    print(f"Backend-Funktionalität: {'ERFOLGREICH' if success1 else 'FEHLGESCHLAGEN'}")
    print(f"Frontend-Integration: {'ERFOLGREICH' if success2 else 'FEHLGESCHLAGEN'}")
    
    if success1 and success2:
        print("\nALLE TESTS ERFOLGREICH!")
        print("Rechnungsbearbeitung und Vorschau sind vollständig implementiert.")
        print("\nVerfügbare Funktionen:")
        print("OK Rechnungen bearbeiten")
        print("OK Rechnungsvorschau anzeigen")
        print("OK PDF-Download")
        print("OK Status-Aenderungen")
        print("OK Kundeninformationen bearbeiten")
    else:
        print("\nX EINIGE TESTS FEHLGESCHLAGEN!")
        if not success1:
            print("- Backend-Funktionalität muss repariert werden")
        if not success2:
            print("- Frontend-Integration muss repariert werden")

if __name__ == "__main__":
    main()
