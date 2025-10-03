#!/usr/bin/env python3
"""
Test-Script für die erweiterten Services:
- InvoiceGenerator
- BeautifulPDFGenerator
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from app.services.invoice_generator import InvoiceGenerator
from app.services.beautiful_pdf_generator import create_beautiful_invoice_pdf, create_offer_pdf
from app.schemas import InvoiceGenerationRequest, InvoiceItem
from app.database import get_session

def test_invoice_generator():
    """Testet den erweiterten InvoiceGenerator."""
    print("🧾 Teste InvoiceGenerator...")
    
    try:
        # Session erstellen
        session = next(get_session())
        generator = InvoiceGenerator(session)
        
        # Test-Daten erstellen
        request = InvoiceGenerationRequest(
            project_id=1,
            generation_method="hybrid",
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now(),
            include_materials=True,
            include_labor=True,
            tax_rate=19.0,
            labor_cost_percentage=0.0
        )
        
        print(f"✅ Rechnungsgenerierungs-Anfrage erstellt: {request.generation_method}")
        
        # Rechnung generieren
        result = generator.generate_invoice(request)
        
        print(f"✅ Rechnung generiert:")
        print(f"   - Gesamtbetrag: {result.total_amount}€")
        print(f"   - Positionen: {len(result.items)}")
        print(f"   - Lohnanteil: {result.labor_percentage}%")
        
        # Rechnungsnummer generieren
        invoice_number = generator.generate_invoice_number(1, "RE")
        print(f"✅ Rechnungsnummer generiert: {invoice_number}")
        
        # Zusammenfassung erstellen
        summary = generator.get_invoice_summary(result)
        print(f"✅ Zusammenfassung erstellt: {summary['summary']['total_items']} Positionen")
        
        # Export testen
        json_export = generator.export_invoice_data(result, "json")
        print(f"✅ JSON-Export: {len(json_export)} Zeichen")
        
        csv_export = generator.export_invoice_data(result, "csv")
        print(f"✅ CSV-Export: {len(csv_export)} Zeichen")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Testen des InvoiceGenerators: {str(e)}")
        return False

def test_pdf_generator():
    """Testet den erweiterten BeautifulPDFGenerator."""
    print("\n📄 Teste BeautifulPDFGenerator...")
    
    try:
        # Test-Rechnungsdaten
        invoice_data = {
            'invoice_number': 'RE-20250101-001-001',
            'title': 'Test-Rechnung',
            'client_name': 'Test-Kunde',
            'client_address': 'Test-Straße 123, 70173 Stuttgart',
            'total_amount': 1000.0,
            'invoice_date': datetime.now().isoformat(),
            'due_date': (datetime.now() + timedelta(days=30)).isoformat(),
            'items': [
                {
                    'description': 'Trockenbauarbeiten',
                    'quantity': 10.0,
                    'unit': 'm²',
                    'unit_price': 50.0,
                    'total_price': 500.0
                },
                {
                    'description': 'Materialkosten',
                    'quantity': 1.0,
                    'unit': 'Stk',
                    'unit_price': 300.0,
                    'total_price': 300.0
                }
            ]
        }
        
        # PDF generieren
        pdf_data = create_beautiful_invoice_pdf(invoice_data)
        print(f"✅ Rechnungs-PDF generiert: {len(pdf_data)} Bytes")
        
        # Test-Angebotsdaten
        offer_data = {
            'offer_number': 'AN-20250101-001',
            'title': 'Test-Angebot',
            'client_name': 'Test-Kunde',
            'client_address': 'Test-Straße 123, 70173 Stuttgart',
            'total_amount': 800.0,
            'offer_date': datetime.now().isoformat(),
            'valid_until': (datetime.now() + timedelta(days=14)).isoformat(),
            'items': [
                {
                    'description': 'Trockenbauarbeiten',
                    'quantity': 8.0,
                    'unit': 'm²',
                    'unit_price': 50.0,
                    'total_price': 400.0
                },
                {
                    'description': 'Materialkosten',
                    'quantity': 1.0,
                    'unit': 'Stk',
                    'unit_price': 200.0,
                    'total_price': 200.0
                }
            ]
        }
        
        # Angebots-PDF generieren
        offer_pdf = create_offer_pdf(offer_data)
        print(f"✅ Angebots-PDF generiert: {len(offer_pdf)} Bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Fehler beim Testen des BeautifulPDFGenerators: {str(e)}")
        return False

def main():
    """Hauptfunktion für alle Tests."""
    print("🚀 Starte Tests der erweiterten Services...\n")
    
    # Tests ausführen
    invoice_test = test_invoice_generator()
    pdf_test = test_pdf_generator()
    
    # Ergebnisse zusammenfassen
    print("\n📊 Test-Ergebnisse:")
    print(f"   InvoiceGenerator: {'✅ BESTANDEN' if invoice_test else '❌ FEHLGESCHLAGEN'}")
    print(f"   BeautifulPDFGenerator: {'✅ BESTANDEN' if pdf_test else '❌ FEHLGESCHLAGEN'}")
    
    if invoice_test and pdf_test:
        print("\n🎉 Alle Tests erfolgreich!")
        return True
    else:
        print("\n⚠️ Einige Tests fehlgeschlagen!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
