from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from datetime import datetime, timedelta
import tempfile
import os
import json
from sqlmodel import Session, select
from fastapi import HTTPException
from app.models import CompanyLogo, TenantSettings, User

def create_beautiful_invoice_pdf(invoice_data, session: Session, user_id: int):
    """
    Erstellt eine professionelle PDF-Rechnung mit Logo-Integration.
    """
    print(f"PDF-Generierung für Benutzer {user_id} gestartet")
    
    # Temporäre PDF-Datei erstellen
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file_path = tmp_file.name
    
    # PDF-Dokument erstellen
    doc = SimpleDocTemplate(tmp_file_path, pagesize=A4, 
                           rightMargin=2*cm, leftMargin=2*cm, 
                           topMargin=2*cm, bottomMargin=2*cm)
    
    # Story für PDF-Inhalte
    story = []

    # Items parsen (String -> Liste)
    items = invoice_data.get('items') or []
    if isinstance(items, str):
        try:
            items = json.loads(items)
        except json.JSONDecodeError:
            items = []

    # Summen berechnen
    total_amount = float(invoice_data.get('total_amount') or 0)
    net_amount = total_amount / 1.19 if total_amount else 0
    vat_amount = total_amount - net_amount
    
    # Stile definieren
    styles = getSampleStyleSheet()
    black = HexColor('#000000')
    
    # Logo aus Datenbank laden
    logo_path = None
    if session is not None and user_id is not None:
        try:
            logo = session.exec(
                select(CompanyLogo)
                .where(CompanyLogo.user_id == user_id)
                .where(CompanyLogo.is_active == True)
            ).first()

            if logo and logo.file_path and os.path.exists(logo.file_path):
                logo_path = logo.file_path
        except Exception as e:
            print(f"Fehler beim Laden des Logos: {e}")
    
    # PROFESSIONELLES LAYOUT - Genau wie in der Vorschau
    
    # Header - genau wie in der Vorschau mit Firmeninfo links und Logo rechts
    company_name_style = ParagraphStyle(
        'CompanyName', parent=styles['Normal'], fontSize=16, leading=18,
        textColor=black, fontName='Helvetica-Bold', spaceAfter=4
    )
    company_info_style = ParagraphStyle(
        'CompanyInfoBlock', parent=styles['Normal'], fontSize=10, leading=13,
        textColor=black, fontName='Helvetica'
    )
    company_secondary_style = ParagraphStyle(
        'CompanyInfoSecondary', parent=styles['Normal'], fontSize=10, leading=13,
        textColor=black, fontName='Helvetica', alignment=0, spaceBefore=4
    )

    # Logo vorbereiten
    if logo_path:
        try:
            logo_cell = Image(logo_path, width=5.5 * cm, height=2.8 * cm)
        except Exception as e:
            print(f"Fehler beim Laden des Logos in PDF: {e}")
            logo_cell = Paragraph("Firmenlogo", ParagraphStyle('LogoPlaceholder', parent=styles['Normal'], fontSize=10, textColor=black, fontName='Helvetica'))
    else:
        logo_cell = Paragraph("Firmenlogo", ParagraphStyle('LogoPlaceholder', parent=styles['Normal'], fontSize=10, textColor=black, fontName='Helvetica'))

    # Kopfbereich: Firmeninfos, Logo und Steuerblock untereinander, Logo rechts ausgerichtet
    company_name = "Trockenbau Stuttgart GmbH"
    company_address = "Musterstraße 123<br/>70173 Stuttgart"
    company_contact = "Tel: 0711-123456"
    company_email = "info@trockenbau-stuttgart.de"
    tax_number = "12/345/67890"
    vat_id = "DE123456789"
    bank_iban = "DE12 3456 7890 1234 5678 90"
    bank_bic = "GENODEF1S02"
    bank_name = "Musterbank Stuttgart"

    if session is not None and user_id is not None:
        try:
            user = session.get(User, user_id)
            tenant_settings = None
            if user:
                tenant_settings = session.exec(
                    select(TenantSettings).where(TenantSettings.tenant_id == user.tenant_id)
                ).first()

            if tenant_settings:
                company_name = tenant_settings.company_name or company_name
                company_address = (tenant_settings.company_address or "Musterstraße 123, 70173 Stuttgart").replace(", ", "<br/>")
                phone = tenant_settings.company_phone or "0711-123456"
                fax = tenant_settings.company_fax
                company_contact = f"Tel: {phone}" + (f" • Fax: {fax}" if fax else "")
                company_email = tenant_settings.company_email or company_email
                tax_number = tenant_settings.tax_number or tax_number
                vat_id = tenant_settings.vat_id or vat_id
                bank_iban = tenant_settings.bank_iban or bank_iban
                bank_bic = tenant_settings.bank_bic or bank_bic
                bank_name = tenant_settings.bank_name or bank_name
        except Exception as e:
            print(f"Fehler beim Laden der Tenant Settings: {e}")

    info_lines = [company_address]
    if company_contact:
        info_lines.append(company_contact)
    if company_email:
        info_lines.append(f"E-Mail: {company_email}")

    left_block = Table([
        [Paragraph(company_name, company_name_style)],
        [Paragraph(
            "<br/>".join(info_lines),
            company_info_style
        )]
    ], colWidths=[9 * cm])
    left_block.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    right_block = Table([[logo_cell]], colWidths=[8 * cm])
    right_block.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    header_table = Table([[left_block, right_block]], colWidths=[9 * cm, 8 * cm])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    header_table.hAlign = 'LEFT'

    story.append(header_table)
    story.append(Spacer(1, 18))

    secondary_lines = []
    if tax_number:
        secondary_lines.append(f"Steuernummer: {tax_number}")
    if bank_iban:
        secondary_lines.append(f"IBAN: {bank_iban}")
    if bank_bic:
        secondary_lines.append(f"BIC: {bank_bic}")
    if vat_id:
        secondary_lines.append(f"USt-IdNr.: {vat_id}")
    if bank_name:
        secondary_lines.append(f"Bank: {bank_name}")

    if secondary_lines:
        story.append(Paragraph(
            "<br/>".join(secondary_lines),
            company_secondary_style
        ))
    story.append(Spacer(1, 12))

    # Rechnungstitel
    story.append(Paragraph("RECHNUNG", ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        textColor=black,
        fontName='Helvetica-Bold',
        alignment=0,
        spaceAfter=6
    )))

    # Rechnungsempfänger und Rechnungsdetails - genau wie in der Vorschau
    client_name = invoice_data.get('client_name', 'Kunde')
    client_address = invoice_data.get('client_address', 'Adresse nicht angegeben')

    # Rechnungsdetails
    invoice_date = invoice_data.get('invoice_date', datetime.now().isoformat())
    due_date = invoice_data.get('due_date', (datetime.now() + timedelta(days=30)).isoformat())

    # Zwei-spaltige Layout wie in der Vorschau
    main_data = [
        ['Rechnungsempfänger:', 'Rechnungsdetails:'],
        [client_name, f"Rechnungs-Nr: {invoice_data.get('invoice_number', 'R-2025-001')}"],
        [client_address, f"Kunden-Nr: 00000001"],
        ['', f"Rechnungsdatum: {datetime.fromisoformat(invoice_date.replace('Z', '+00:00')).strftime('%d.%m.%Y') if invoice_date else datetime.now().strftime('%d.%m.%Y')}"],
        ['', f"Fälligkeitsdatum: {datetime.fromisoformat(due_date.replace('Z', '+00:00')).strftime('%d.%m.%Y') if due_date else (datetime.now() + timedelta(days=30)).strftime('%d.%m.%Y')}"],
        ['', 'Seite: 1/1']
    ]

    main_table = Table(main_data, colWidths=[9.4 * cm, 7.6 * cm])
    main_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTNAME', (1, 1), (1, -1), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (1, 0), (1, -1), 0),
        ('LEFTPADDING', (1, 0), (1, -1), 0),
    ]))
    main_table.hAlign = 'LEFT'

    story.append(main_table)
    story.append(Spacer(1, 18))

    # 4. Items Tabelle - genau wie in der professionellen Vorlage
    table_data = [['Pos.', 'Bezeichnung', 'Menge', 'Einh.', 'E-Preis €', 'G-Preis €']]

    for i, item in enumerate(items, 1):
        table_data.append([
            f"{i:05d}",  # Ordnungszahl mit führenden Nullen
            item.get('description', 'N/A'),
            str(item.get('quantity', 0)),
            item.get('unit', 'Stk'),
            f"{item.get('unit_price', 0):.2f}",
            f"{item.get('total_price', 0):.2f}"
        ])

    # Tabelle erstellen
    items_table = Table(table_data, colWidths=[1.6 * cm, 7.6 * cm, 1.6 * cm, 1.6 * cm, 2.4 * cm, 2.2 * cm])
    
    # Professioneller Tabellenstil
    items_table.setStyle(TableStyle([
        # Header-Styling
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#1f2937')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        
        # Daten-Styling
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Pos. zentriert
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),   # Bezeichnung links
        ('ALIGN', (2, 1), (3, -1), 'CENTER'), # Menge und Einheit zentriert
        ('ALIGN', (4, 1), (-1, -1), 'RIGHT'), # Preise rechts
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        
        # Rahmen
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#d1d5db')),
        ('LINEBELOW', (0, 0), (-1, 0), 2, black),
        
        # Abstände
        ('PADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    items_table.hAlign = 'LEFT'

    story.append(items_table)
    story.append(Spacer(1, 18))

    # 5. Summen-Tabelle - genau wie in der professionellen Vorlage
    total_amount = invoice_data.get('total_amount', 0)
    net_amount = total_amount / 1.19  # Netto-Betrag
    vat_amount = total_amount - net_amount  # MwSt-Betrag

    summary_table = Table([
        ['', 'Zwischensumme', f"{net_amount:,.2f} €"],
        ['', 'USt (19 %)', f"{vat_amount:,.2f} €"],
        ['', 'Gesamtbetrag', f"{total_amount:,.2f} €"],
    ], colWidths=[9.4 * cm, 3.6 * cm, 4.0 * cm])

    summary_table.setStyle(TableStyle([
        ('FONTNAME', (1, 0), (1, -2), 'Helvetica'),
        ('FONTNAME', (2, 0), (2, -2), 'Helvetica'),
        ('FONTNAME', (1, -1), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (1, -1), (2, -1), HexColor('#111827')),
        ('TEXTCOLOR', (1, -1), (2, -1), colors.white),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('SPAN', (0, 0), (0, -1)),
        ('LINEABOVE', (0, 0), (-1, 0), 0.5, HexColor('#d1d5db')),
        ('LINEABOVE', (0, -1), (-1, -1), 0.5, HexColor('#d1d5db')),
    ]))
    summary_table.hAlign = 'LEFT'

    story.append(summary_table)
    story.append(Spacer(1, 26))

    # 6. Footer
    footer_text = "<br/>".join([
        f"{company_name} • {company_address.replace('<br/>', ' • ')}",
        f"{company_contact} • E-Mail: {company_email}"
    ])
    story.append(Paragraph(footer_text, ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=HexColor('#6b7280'),
        alignment=1,  # Center
        spaceBefore=20
    )))

    # PDF erstellen
    doc.build(story)
    
    # PDF-Bytes lesen
    with open(tmp_file_path, 'rb') as f:
        pdf_bytes = f.read()
    
    # Temporäre Datei löschen
    os.unlink(tmp_file_path)
    
    print(f"PDF erfolgreich generiert: {len(pdf_bytes)} Bytes")
    return pdf_bytes