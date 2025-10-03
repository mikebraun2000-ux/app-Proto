"""
PDF-Utilities für die Erstellung von Angeboten.
Verwendet fpdf2 für die PDF-Generierung.
"""

from fpdf import FPDF
from typing import List, Dict, Any, Union
import json
from datetime import datetime

class OfferPDF(FPDF):
    """
    PDF-Klasse für die Erstellung von Angeboten.
    Erweitert FPDF mit spezifischen Formatierungen für Bauangebote.
    """
    
    def __init__(self):
        super().__init__()
        self.add_page()
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        """PDF-Header mit Firmeninformationen."""
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'BAU-DOKUMENTATIONS-APP', 0, 1, 'C')
        self.set_font('Arial', '', 12)
        self.cell(0, 8, 'Angebot', 0, 1, 'C')
        self.ln(10)
        
    def footer(self):
        """PDF-Footer mit Seitenzahl."""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Seite {self.page_no()}', 0, 0, 'C')


def _ensure_text(value: Union[str, bytes, bytearray, None], default: str = '', encoding: str = 'utf-8') -> str:
    """Garantiert, dass ein String zurückgegeben wird."""
    if value is None:
        return default
    if isinstance(value, str):
        return value
    if isinstance(value, (bytes, bytearray)):
        for codec in (encoding, 'latin-1'):
            try:
                return value.decode(codec)
            except Exception:
                continue
        return default
    return str(value)

def create_offer_pdf(offer_data: Dict[str, Any]) -> bytes:
    """
    Erstellt ein PDF-Angebot basierend auf den Angebotsdaten.
    
    Args:
        offer_data: Dictionary mit Angebotsdaten
        
    Returns:
        bytes: PDF-Datei als Bytes
    """
    pdf = OfferPDF()
    
    # Angebotsinformationen
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, _ensure_text(offer_data.get('title', 'Angebot')), 0, 1, 'L')
    pdf.ln(5)
    
    # Kundeninformationen
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Kunde:', 0, 1, 'L')
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 6, _ensure_text(offer_data.get('client_name', '')), 0, 1, 'L')
    
    client_address = offer_data.get('client_address')
    if client_address:
        pdf.cell(0, 6, _ensure_text(client_address), 0, 1, 'L')
    
    pdf.ln(5)
    
    # Angebotsdatum
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 6, f'Angebotsdatum: {datetime.now().strftime("%d.%m.%Y")}', 0, 1, 'L')
    
    if offer_data.get('valid_until'):
        valid_until = datetime.fromisoformat(offer_data['valid_until'].replace('Z', '+00:00'))
        pdf.cell(0, 6, f'Gültig bis: {valid_until.strftime("%d.%m.%Y")}', 0, 1, 'L')
    
    pdf.ln(10)
    
    # Beschreibung
    description = offer_data.get('description')
    if description:
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'Beschreibung:', 0, 1, 'L')
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 6, _ensure_text(description), 0, 'L')
        pdf.ln(5)
    
    # Angebotspositionen
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Angebotspositionen:', 0, 1, 'L')
    pdf.ln(3)
    
    # Tabellen-Header
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(80, 8, 'Beschreibung', 1, 0, 'C')
    pdf.cell(25, 8, 'Menge', 1, 0, 'C')
    pdf.cell(20, 8, 'Einheit', 1, 0, 'C')
    pdf.cell(25, 8, 'Einzelpreis', 1, 0, 'C')
    pdf.cell(30, 8, 'Gesamtpreis', 1, 1, 'C')
    
    # Angebotspositionen hinzufügen
    pdf.set_font('Arial', '', 9)
    items = offer_data.get('items', [])
    
    if isinstance(items, str):
        try:
            items = json.loads(items)
        except json.JSONDecodeError:
            items = []
    
    total_amount = 0
    currency = _ensure_text(offer_data.get('currency', 'EUR'))
    
    for item in items:
        if not isinstance(item, dict):
            continue

        description = _ensure_text(item.get('description', ''))
        quantity = float(item.get('quantity', 0) or 0)
        unit = _ensure_text(item.get('unit', ''))
        unit_price = float(item.get('unit_price', 0) or 0)
        total_price = float(item.get('total_price', 0) or (unit_price * quantity))

        truncated_desc = description[:35] + ('...' if len(description) > 35 else '')
        pdf.cell(80, 8, truncated_desc, 1, 0, 'L')
        pdf.cell(25, 8, f"{quantity:g}", 1, 0, 'C')
        pdf.cell(20, 8, unit, 1, 0, 'C')
        pdf.cell(25, 8, f"{unit_price:.2f} {currency}", 1, 0, 'R')
        pdf.cell(30, 8, f"{total_price:.2f} {currency}", 1, 1, 'R')

        total_amount += total_price
    
    # Gesamtbetrag
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(150, 10, 'Gesamtbetrag:', 0, 0, 'R')
    pdf.cell(30, 10, f"{total_amount:.2f} {_ensure_text(offer_data.get('currency', 'EUR'))}", 0, 1, 'R')
    
    # MwSt. (optional)
    if total_amount > 0:
        vat = total_amount * 0.19  # 19% MwSt.
        total_with_vat = total_amount + vat
        
        pdf.set_font('Arial', '', 10)
        pdf.cell(150, 6, 'zzgl. 19% MwSt.:', 0, 0, 'R')
        pdf.cell(30, 6, f"{vat:.2f} {currency}", 0, 1, 'R')
        
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(150, 8, 'Gesamtbetrag inkl. MwSt.:', 0, 0, 'R')
        pdf.cell(30, 8, f"{total_with_vat:.2f} {currency}", 0, 1, 'R')
    
    # Fußzeile mit Hinweisen
    pdf.ln(15)
    pdf.set_font('Arial', '', 9)
    pdf.multi_cell(0, 5, 
        "Dieses Angebot ist freibleibend und unverbindlich. "
        "Alle Preise verstehen sich zzgl. der gesetzlichen Mehrwertsteuer. "
        "Änderungen und Irrtümer vorbehalten.", 0, 'L')
    
    result = pdf.output(dest='S')
    return bytes(result)

def create_invoice_pdf(invoice_data: Dict[str, Any]) -> bytes:
    """
    Erstellt ein PDF-Rechnung basierend auf den Rechnungsdaten.
    
    Args:
        invoice_data: Dictionary mit Rechnungsdaten
        
    Returns:
        bytes: PDF-Datei als Bytes
    """
    pdf = OfferPDF()  # Verwende die gleiche PDF-Klasse
    
    # Rechnungsinformationen
    pdf.set_font('Arial', 'B', 14)
    company_block = invoice_data.get('company_block')
    if company_block:
        for line in company_block.split('\n'):
            pdf.cell(0, 6, _ensure_text(line), 0, 1, 'L')
    else:
        pdf.cell(0, 6, 'Trockenbau Stuttgart GmbH', 0, 1, 'L')
        pdf.cell(0, 6, 'Musterstraße 123, 70173 Stuttgart', 0, 1, 'L')
        pdf.cell(0, 6, 'Tel: 0711-123456', 0, 1, 'L')
        pdf.cell(0, 6, 'E-Mail: info@trockenbau-stuttgart.de', 0, 1, 'L')

    pdf.ln(5)
    pdf.cell(0, 8, _ensure_text(invoice_data.get('title', 'Rechnung')), 0, 1, 'L')
    pdf.ln(3)

    tax_block = invoice_data.get('tax_block')
    if tax_block:
        pdf.set_font('Arial', '', 10)
        for line in tax_block.split('\n'):
            pdf.cell(0, 6, _ensure_text(line), 0, 1, 'L')
        pdf.ln(3)
        pdf.set_font('Arial', 'B', 12)
    
    # Rechnungsnummer
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, f"Rechnungsnummer: {_ensure_text(invoice_data.get('invoice_number', ''))}", 0, 1, 'L')
    pdf.ln(3)
    
    # Kundeninformationen
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Rechnungsempfänger:', 0, 1, 'L')
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 6, _ensure_text(invoice_data.get('client_name', '')), 0, 1, 'L')
    
    client_address = invoice_data.get('client_address')
    if client_address:
        pdf.cell(0, 6, _ensure_text(client_address), 0, 1, 'L')
    
    pdf.ln(5)
    
    # Rechnungsdatum
    pdf.set_font('Arial', '', 10)
    if invoice_data.get('invoice_date'):
        invoice_date = datetime.fromisoformat(invoice_data['invoice_date'].replace('Z', '+00:00'))
        pdf.cell(0, 6, f'Rechnungsdatum: {invoice_date.strftime("%d.%m.%Y")}', 0, 1, 'L')
    
    if invoice_data.get('due_date'):
        due_date = datetime.fromisoformat(invoice_data['due_date'].replace('Z', '+00:00'))
        pdf.cell(0, 6, f'Fälligkeitsdatum: {due_date.strftime("%d.%m.%Y")}', 0, 1, 'L')
    
    pdf.ln(10)
    
    # Beschreibung
    description = invoice_data.get('description')
    if description:
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'Beschreibung:', 0, 1, 'L')
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 6, _ensure_text(description), 0, 'L')
        pdf.ln(5)
    
    # Rechnungspositionen
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 8, 'Rechnungspositionen:', 0, 1, 'L')
    pdf.ln(3)
    
    # Tabellen-Header
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(80, 8, 'Beschreibung', 1, 0, 'C')
    pdf.cell(25, 8, 'Menge', 1, 0, 'C')
    pdf.cell(20, 8, 'Einheit', 1, 0, 'C')
    pdf.cell(25, 8, 'Einzelpreis', 1, 0, 'C')
    pdf.cell(30, 8, 'Gesamtpreis', 1, 1, 'C')
    
    # Rechnungspositionen hinzufügen
    pdf.set_font('Arial', '', 9)
    items = invoice_data.get('items', [])
    
    if isinstance(items, str):
        try:
            items = json.loads(items)
        except json.JSONDecodeError:
            items = []
    
    total_amount = 0
    currency = _ensure_text(invoice_data.get('currency', 'EUR'))
    
    for item in items:
        if not isinstance(item, dict):
            continue

        description = _ensure_text(item.get('description', ''))
        quantity = float(item.get('quantity', 0) or 0)
        unit = _ensure_text(item.get('unit', ''))
        unit_price = float(item.get('unit_price', 0) or 0)
        total_price = float(item.get('total_price', 0) or (unit_price * quantity))

        truncated_desc = description[:35] + ('...' if len(description) > 35 else '')
        pdf.cell(80, 8, truncated_desc, 1, 0, 'L')
        pdf.cell(25, 8, f"{quantity:g}", 1, 0, 'C')
        pdf.cell(20, 8, unit, 1, 0, 'C')
        pdf.cell(25, 8, f"{unit_price:.2f} {currency}", 1, 0, 'R')
        pdf.cell(30, 8, f"{total_price:.2f} {currency}", 1, 1, 'R')

        total_amount += total_price
    
    # Gesamtbetrag
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(150, 10, 'Gesamtbetrag:', 0, 0, 'R')
    pdf.cell(30, 10, f"{total_amount:.2f} {currency}", 0, 1, 'R')
    
    # MwSt. (optional)
    if total_amount > 0:
        vat = total_amount * 0.19  # 19% MwSt.
        total_with_vat = total_amount + vat
        
        pdf.set_font('Arial', '', 10)
        pdf.cell(150, 6, 'zzgl. 19% MwSt.:', 0, 0, 'R')
        pdf.cell(30, 6, f"{vat:.2f} {currency}", 0, 1, 'R')
        
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(150, 8, 'Gesamtbetrag inkl. MwSt.:', 0, 0, 'R')
        pdf.cell(30, 8, f"{total_with_vat:.2f} {currency}", 0, 1, 'R')
    
    # Fußzeile mit Hinweisen
    pdf.ln(15)
    pdf.set_font('Arial', '', 9)
    pdf.multi_cell(0, 5, 
        "Vielen Dank für Ihren Auftrag. "
        "Bitte überweisen Sie den Rechnungsbetrag bis zum Fälligkeitsdatum. "
        "Bei Fragen stehen wir Ihnen gerne zur Verfügung.", 0, 'L')
    
    result = pdf.output(dest='S')
    return bytes(result)

