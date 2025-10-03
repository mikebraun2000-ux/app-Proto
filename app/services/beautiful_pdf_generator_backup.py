from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image, KeepTogether
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime, timedelta
import json
import io
import os
import logging
from typing import Optional, Dict, Any, List
from sqlmodel import Session, select
from app.models import CompanyLogo

# Logger konfigurieren
logger = logging.getLogger(__name__)

def create_beautiful_invoice_pdf(invoice_data: Dict[str, Any], session: Session = None, user_id: int = None) -> bytes:
    """
    Erstellt eine schöne PDF-Rechnung mit optionalem Firmenlogo.
    
    Args:
        invoice_data: Rechnungsdaten
        session: Datenbank-Session
        user_id: Benutzer-ID für Logo
        
    Returns:
        bytes: PDF-Daten
    """
    try:
        logger.info("Starte PDF-Generierung für Rechnung")
        
        # Items parsen
        items = []
        if invoice_data.get('items'):
            if isinstance(invoice_data['items'], str):
                items = json.loads(invoice_data['items'])
            else:
                items = invoice_data['items']
        
        logger.info(f"Verarbeite {len(items)} Rechnungspositionen")
        
        # Logo laden (falls verfügbar)
        logo_path = None
        if session and user_id:
            logo = session.exec(
                select(CompanyLogo).where(
                    CompanyLogo.user_id == user_id,
                    CompanyLogo.is_active == True
                )
            ).first()
            
            if logo and os.path.exists(logo.file_path):
                logo_path = logo.file_path
        
        # Berechnungen
        subtotal = sum(item.get('total_price', 0) for item in items)
        vat = subtotal * 0.19
        total = subtotal + vat
    
    # PDF in Memory erstellen
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    # Styles definieren
    styles = getSampleStyleSheet()
    
    # Header Style
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#667eea'),
        alignment=1,  # Center
        spaceAfter=20
    )
    
    # Subheader Style
    subheader_style = ParagraphStyle(
        'CustomSubheader',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=HexColor('#333333'),
        spaceAfter=15
    )
    
    # Normal Style
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor('#333333')
    )
    
    # Logo hinzufügen (falls verfügbar)
    if logo_path:
        try:
            # Logo-Bild laden und skalieren
            logo_img = Image(logo_path, width=4*cm, height=2*cm)
            story.append(logo_img)
            story.append(Spacer(1, 10))
        except Exception as e:
            # Falls Logo nicht geladen werden kann, ignorieren
            pass
    
    # Header
    story.append(Paragraph("RECHNUNG", header_style))
    story.append(Paragraph("Trockenbau Stuttgart - Professionelle Bauarbeiten", subheader_style))
    story.append(Spacer(1, 20))
    
    # Firmeninformationen
    company_data = [
        ['Rechnungssteller', 'Rechnungsempfänger'],
        ['Trockenbau Stuttgart GmbH', invoice_data.get('client_name', 'Kunde')],
        ['Musterstraße 123', invoice_data.get('client_address', 'Adresse nicht angegeben')],
        ['70173 Stuttgart', ''],
        ['Tel: 0711-123456', ''],
        ['E-Mail: info@trockenbau-stuttgart.de', '']
    ]
    
    company_table = Table(company_data, colWidths=[8*cm, 8*cm])
    company_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), white),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dddddd')),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(company_table)
    story.append(Spacer(1, 20))
    
    # Rechnungsdetails
    invoice_details_data = [
        ['Rechnungsnummer:', invoice_data.get('invoice_number', 'N/A')],
        ['Rechnungsdatum:', datetime.fromisoformat(invoice_data['invoice_date']).strftime('%d.%m.%Y') if invoice_data.get('invoice_date') else 'N/A'],
        ['Fälligkeitsdatum:', datetime.fromisoformat(invoice_data['due_date']).strftime('%d.%m.%Y') if invoice_data.get('due_date') else 'N/A'],
        ['Projekt:', invoice_data.get('project_name', 'N/A')]
    ]
    
    invoice_details_table = Table(invoice_details_data, colWidths=[4*cm, 12*cm])
    invoice_details_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(invoice_details_table)
    story.append(Spacer(1, 20))
    
    # Rechnungspositionen
    item_table_data = [['Pos.', 'Beschreibung', 'Menge', 'Einheit', 'Einzelpreis', 'Gesamt']]
    for i, item in enumerate(items):
        item_table_data.append([
            i + 1,
            Paragraph(item.get('description', 'N/A'), normal_style),
            f"{item.get('quantity', 0):.2f}",
            item.get('unit', 'Stk'),
            f"{item.get('unit_price', 0):.2f} €",
            f"{item.get('total_price', 0):.2f} €"
        ])
    
    item_table = Table(item_table_data, colWidths=[1*cm, 7*cm, 2*cm, 2*cm, 2.5*cm, 2.5*cm])
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (-1, -1), 'RIGHT'), # Menge, Einzelpreis, Gesamt rechtsbündig
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), white),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dddddd')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(item_table)
    story.append(Spacer(1, 20))
    
    # Summen
    summary_data = [
        ['Nettobetrag:', f"{subtotal:.2f} €"],
        ['Umsatzsteuer (19%):', f"{vat:.2f} €"],
        ['Gesamtbetrag:', f"{total:.2f} €"]
    ]
    
    summary_table = Table(summary_data, colWidths=[13*cm, 3*cm])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LINEABOVE', (0, -1), (-1, -1), 1, black),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    # Fußzeile
    story.append(Paragraph("Vielen Dank für Ihr Vertrauen!", normal_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Bitte überweisen Sie den Betrag innerhalb von 14 Tagen auf unser Konto.", normal_style))
    
        doc.build(story)
        buffer.seek(0)
        pdf_data = buffer.getvalue()
        
        logger.info("PDF erfolgreich generiert")
        return pdf_data
        
    except Exception as e:
        logger.error(f"Fehler bei der PDF-Generierung: {str(e)}")
        raise


def create_offer_pdf(offer_data: Dict[str, Any], session: Session = None, user_id: int = None) -> bytes:
    """
    Erstellt eine schöne PDF-Angebot mit optionalem Firmenlogo.
    
    Args:
        offer_data: Angebotsdaten
        session: Datenbank-Session
        user_id: Benutzer-ID für Logo
        
    Returns:
        bytes: PDF-Daten
    """
    try:
        logger.info("Starte PDF-Generierung für Angebot")
        
        # Items parsen
        items = []
        if offer_data.get('items'):
            if isinstance(offer_data['items'], str):
                items = json.loads(offer_data['items'])
            else:
                items = offer_data['items']
        
        # Logo laden
        logo_path = _get_company_logo(session, user_id)
        
        # PDF in Memory erstellen
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
        story = []
        
        # Styles definieren
        styles = _get_pdf_styles()
        
        # Logo hinzufügen
        if logo_path:
            _add_logo_to_story(story, logo_path)
        
        # Header
        story.append(Paragraph("ANGEBOT", styles['header']))
        story.append(Paragraph("Trockenbau Stuttgart - Professionelle Bauarbeiten", styles['subheader']))
        story.append(Spacer(1, 20))
        
        # Firmeninformationen
        _add_company_info(story, offer_data, styles)
        
        # Angebotsdetails
        _add_offer_details(story, offer_data, styles)
        
        # Angebotspositionen
        _add_offer_items(story, items, styles)
        
        # Summen
        _add_offer_totals(story, offer_data, styles)
        
        # Fußzeile
        _add_footer(story, "Vielen Dank für Ihr Interesse!", styles)
        
        doc.build(story)
        buffer.seek(0)
        pdf_data = buffer.getvalue()
        
        logger.info("Angebots-PDF erfolgreich generiert")
        return pdf_data
        
    except Exception as e:
        logger.error(f"Fehler bei der Angebots-PDF-Generierung: {str(e)}")
        raise


def _get_company_logo(session: Session, user_id: int) -> Optional[str]:
    """Lädt das Firmenlogo."""
    if not session or not user_id:
        return None
    
    try:
        logo = session.exec(
            select(CompanyLogo).where(
                CompanyLogo.user_id == user_id,
                CompanyLogo.is_active == True
            )
        ).first()
        
        if logo and os.path.exists(logo.file_path):
            return logo.file_path
    except Exception as e:
        logger.warning(f"Fehler beim Laden des Logos: {str(e)}")
    
    return None


def _get_pdf_styles() -> Dict[str, ParagraphStyle]:
    """Definiert die PDF-Styles."""
    styles = getSampleStyleSheet()
    
    # Header Style
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#667eea'),
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    # Subheader Style
    subheader_style = ParagraphStyle(
        'CustomSubheader',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=HexColor('#333333'),
        alignment=TA_CENTER,
        spaceAfter=15
    )
    
    # Normal Style
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor('#333333')
    )
    
    # Bold Style
    bold_style = ParagraphStyle(
        'CustomBold',
        parent=styles['Normal'],
        fontSize=10,
        textColor=HexColor('#333333'),
        fontName='Helvetica-Bold'
    )
    
    return {
        'header': header_style,
        'subheader': subheader_style,
        'normal': normal_style,
        'bold': bold_style
    }


def _add_logo_to_story(story: List, logo_path: str):
    """Fügt das Logo zur Story hinzu."""
    try:
        logo_img = Image(logo_path, width=4*cm, height=2*cm)
        story.append(logo_img)
        story.append(Spacer(1, 10))
    except Exception as e:
        logger.warning(f"Fehler beim Hinzufügen des Logos: {str(e)}")


def _add_company_info(story: List, data: Dict[str, Any], styles: Dict[str, ParagraphStyle]):
    """Fügt Firmeninformationen hinzu."""
    company_data = [
        ['Rechnungssteller', 'Rechnungsempfänger'],
        ['Trockenbau Stuttgart GmbH', data.get('client_name', 'Kunde')],
        ['Musterstraße 123', data.get('client_address', 'Adresse nicht angegeben')],
        ['70173 Stuttgart', ''],
        ['Tel: 0711-123456', ''],
        ['E-Mail: info@trockenbau-stuttgart.de', '']
    ]
    
    company_table = Table(company_data, colWidths=[8*cm, 8*cm])
    company_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), TA_LEFT),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), white),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dddddd')),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(company_table)
    story.append(Spacer(1, 20))


def _add_offer_details(story: List, data: Dict[str, Any], styles: Dict[str, ParagraphStyle]):
    """Fügt Angebotsdetails hinzu."""
    offer_details_data = [
        ['Angebotsnummer:', data.get('offer_number', 'N/A')],
        ['Angebotsdatum:', datetime.fromisoformat(data['offer_date']).strftime('%d.%m.%Y') if data.get('offer_date') else 'N/A'],
        ['Gültigkeitsdatum:', datetime.fromisoformat(data['valid_until']).strftime('%d.%m.%Y') if data.get('valid_until') else 'N/A'],
        ['Projekt:', data.get('project_name', 'N/A')]
    ]
    
    offer_details_table = Table(offer_details_data, colWidths=[4*cm, 12*cm])
    offer_details_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), TA_LEFT),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(offer_details_table)
    story.append(Spacer(1, 20))


def _add_offer_items(story: List, items: List[Dict[str, Any]], styles: Dict[str, ParagraphStyle]):
    """Fügt Angebotspositionen hinzu."""
    if not items:
        return
    
    # Angebotspositionen
    item_table_data = [['Pos.', 'Beschreibung', 'Menge', 'Einheit', 'Einzelpreis', 'Gesamt']]
    for i, item in enumerate(items):
        item_table_data.append([
            i + 1,
            Paragraph(item.get('description', 'N/A'), styles['normal']),
            f"{item.get('quantity', 0):.2f}",
            item.get('unit', 'Stk'),
            f"{item.get('unit_price', 0):.2f} €",
            f"{item.get('total_price', 0):.2f} €"
        ])
    
    item_table = Table(item_table_data, colWidths=[1*cm, 7*cm, 2*cm, 2*cm, 2.5*cm, 2.5*cm])
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('ALIGN', (0, 0), (-1, -1), TA_LEFT),
        ('ALIGN', (2, 0), (-1, -1), TA_RIGHT),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), white),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dddddd')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(item_table)
    story.append(Spacer(1, 20))


def _add_offer_totals(story: List, data: Dict[str, Any], styles: Dict[str, ParagraphStyle]):
    """Fügt Angebotssummen hinzu."""
    # Berechnungen
    items = data.get('items', [])
    if isinstance(items, str):
        items = json.loads(items)
    
    subtotal = sum(item.get('total_price', 0) for item in items)
    vat = subtotal * 0.19
    total = subtotal + vat
    
    # Summen
    summary_data = [
        ['Nettobetrag:', f"{subtotal:.2f} €"],
        ['Umsatzsteuer (19%):', f"{vat:.2f} €"],
        ['Gesamtbetrag:', f"{total:.2f} €"]
    ]
    
    summary_table = Table(summary_data, colWidths=[13*cm, 3*cm])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), TA_RIGHT),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LINEABOVE', (0, -1), (-1, -1), 1, black),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 20))


def _add_footer(story: List, text: str, styles: Dict[str, ParagraphStyle]):
    """Fügt Fußzeile hinzu."""
    story.append(Paragraph(text, styles['normal']))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Bitte überweisen Sie den Betrag innerhalb von 14 Tagen auf unser Konto.", styles['normal']))
