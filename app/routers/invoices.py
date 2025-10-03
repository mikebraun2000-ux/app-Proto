"""
Router für Rechnungs-Management.
Bietet CRUD-Operationen für Rechnungen und PDF-Export.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from sqlmodel import Session, select
from typing import List
import json
import tempfile
import os
from datetime import datetime, timedelta
from ..database import get_session
from ..models import Invoice, Project, TimeEntry, MaterialUsage, Employee, TenantSettings
from ..schemas import InvoiceCreate, InvoiceUpdate, Invoice as InvoiceSchema, InvoiceItem, InvoiceGenerationRequest, InvoiceCalculationResult
from ..utils.pdf_utils import create_invoice_pdf
from ..auth import get_current_user, require_buchhalter_or_admin
from ..services.beautiful_pdf_generator import create_beautiful_invoice_pdf
from ..services.invoice_generator import InvoiceGenerator

router = APIRouter(prefix="/invoices", tags=["invoices"])

@router.get("/", response_model=List[InvoiceSchema])
def get_invoices(session: Session = Depends(get_session), current_user = Depends(require_buchhalter_or_admin)):
    """
    Alle Rechnungen abrufen.
    
    Returns:
        List[InvoiceSchema]: Liste aller Rechnungen
    """
    try:
        print("DEBUG: Lade Rechnungen...")
        statement = select(Invoice)
        invoices = session.exec(statement).all()
        print(f"DEBUG: {len(invoices)} Rechnungen gefunden")
        
        # Vereinfachte Items-Behandlung
        for invoice in invoices:
            if invoice.items is None:
                invoice.items = "[]"
            elif not isinstance(invoice.items, str):
                invoice.items = json.dumps(invoice.items) if invoice.items else "[]"
        
        print("DEBUG: Rechnungen erfolgreich geladen")
        return invoices
    except Exception as e:
        print(f"DEBUG: Fehler in get_invoices: {e}")
        import traceback
        traceback.print_exc()
        return []

@router.post("/")
def create_invoice(invoice_data: dict, session: Session = Depends(get_session), current_user = Depends(get_current_user)):
    """
    Neue Rechnung erstellen.
    """
    try:
        # Prüfen ob das Projekt existiert
        project_id = invoice_data.get('project_id')
        project = session.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
        
        items = invoice_data.get('items')
        if not items:
            generated_items, generated_total = _collect_project_items(session, project_id)
            items = generated_items
            invoice_data['total_amount'] = generated_total
        else:
            generated_items, generated_total = _collect_project_items(session, project_id)
            if generated_items:
                items = generated_items + items
                if not invoice_data.get('total_amount'):
                    invoice_data['total_amount'] = generated_total + sum(item.get('total_price', 0) for item in items if item not in generated_items)

        items_json = json.dumps(items or [])
        
        # Rechnung erstellen
        db_invoice = Invoice(
            project_id=project_id,
            invoice_number=invoice_data.get('invoice_number', 'INV-001'),
            title=invoice_data.get('title', 'Neue Rechnung'),
            description=invoice_data.get('description'),
            client_name=invoice_data.get('client_name', 'Kunde'),
            client_address=invoice_data.get('client_address'),
            total_amount=round(float(invoice_data.get('total_amount', 0.0)), 2),
            currency=invoice_data.get('currency', 'EUR'),
            invoice_date=datetime.utcnow(),
            due_date=None,
            items=items_json,
            status=invoice_data.get('status', 'entwurf')
        )
        
        session.add(db_invoice)
        session.commit()
        session.refresh(db_invoice)
        
        return {
            "id": db_invoice.id,
            "project_id": db_invoice.project_id,
            "invoice_number": db_invoice.invoice_number,
            "title": db_invoice.title,
            "description": db_invoice.description,
            "client_name": db_invoice.client_name,
            "client_address": db_invoice.client_address,
            "total_amount": db_invoice.total_amount,
            "currency": db_invoice.currency,
            "invoice_date": db_invoice.invoice_date,
            "due_date": db_invoice.due_date,
            "items": json.loads(db_invoice.items) if db_invoice.items else [],
            "status": db_invoice.status,
            "created_at": db_invoice.created_at,
            "updated_at": db_invoice.updated_at
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Fehler bei Rechnung-Erstellung: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler bei Rechnung-Erstellung: {str(e)}")

# ENTFERNT - verschoben nach spezifischen Endpoints

@router.put("/{invoice_id}", response_model=InvoiceSchema)
def update_invoice(
    invoice_id: int, 
    invoice_update: dict, 
    session: Session = Depends(get_session),
    current_user = Depends(require_buchhalter_or_admin)
):
    """
    Rechnung aktualisieren.
    
    Args:
        invoice_id: Rechnungs-ID
        invoice_update: Aktualisierte Rechnungs-Daten als dict
        session: Datenbank-Session
        current_user: Aktueller Benutzer
        
    Returns:
        InvoiceSchema: Aktualisierte Rechnung
        
    Raises:
        HTTPException: Wenn Rechnung nicht gefunden wird
    """
    try:
        print(f"DEBUG: Update Rechnung {invoice_id} mit Daten: {invoice_update}")
        
        invoice = session.get(Invoice, invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="Rechnung nicht gefunden")
        
        # Nur sichere Felder aktualisieren
        safe_fields = ['invoice_number', 'status', 'client_name', 'total_amount', 'title', 'description', 'client_address']
        
        for field in safe_fields:
            if field in invoice_update and invoice_update[field] is not None:
                value = invoice_update[field]
                # Runde Beträge auf 2 Dezimalstellen
                if field == 'total_amount':
                    value = round(float(value), 2)
                setattr(invoice, field, value)
                print(f"DEBUG: Feld {field} auf {value} gesetzt")
        
        # Items als JSON-String konvertieren falls vorhanden
        if 'items' in invoice_update and invoice_update['items'] is not None:
            if isinstance(invoice_update['items'], list):
                invoice.items = json.dumps(invoice_update['items'])
            else:
                invoice.items = json.dumps(invoice_update['items'])
        
        # Änderungen speichern
        session.add(invoice)
        session.commit()
        session.refresh(invoice)
        
        print(f"DEBUG: Rechnung erfolgreich aktualisiert: {invoice.id}")
        
        # Items als JSON-String konvertieren für Response
        if isinstance(invoice.items, str):
            pass  # Bereits JSON-String
        elif isinstance(invoice.items, list):
            invoice.items = json.dumps(invoice.items)
        else:
            invoice.items = json.dumps([])
        
        return invoice
        
    except Exception as e:
        print(f"DEBUG: Fehler beim Aktualisieren der Rechnung: {str(e)}")
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler beim Aktualisieren der Rechnung: {str(e)}")

@router.delete("/{invoice_id}")
def delete_invoice(invoice_id: int, session: Session = Depends(get_session)):
    """
    Rechnung löschen.
    
    Args:
        invoice_id: Rechnungs-ID
        session: Datenbank-Session
        
    Returns:
        dict: Erfolgsmeldung
        
    Raises:
        HTTPException: Wenn Rechnung nicht gefunden wird
    """
    invoice = session.get(Invoice, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Rechnung nicht gefunden")
    
    session.delete(invoice)
    session.commit()
    return {"message": "Rechnung erfolgreich gelöscht"}

@router.get("/{invoice_id}", response_model=InvoiceSchema)
def get_invoice(invoice_id: int, session: Session = Depends(get_session), current_user = Depends(require_buchhalter_or_admin)):
    invoice = session.get(Invoice, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Rechnung nicht gefunden")
    return invoice


@router.get("/{invoice_id}/pdf")
def generate_invoice_pdf(
    invoice_id: int,
    session: Session = Depends(get_session),
    current_user = Depends(require_buchhalter_or_admin)
):
    """
    PDF-Rechnung generieren und als Datei zurückgeben.
    
    Args:
        invoice_id: Rechnungs-ID
        session: Datenbank-Session
        
    Returns:
        FileResponse: PDF-Datei
        
    Raises:
        HTTPException: Wenn Rechnung nicht gefunden wird
    """
    invoice = session.get(Invoice, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Rechnung nicht gefunden")
    
    try:
        # Rechnungsdaten für PDF vorbereiten
        tenant_settings = session.exec(
            select(TenantSettings).where(TenantSettings.tenant_id == current_user.tenant_id)
        ).first()

        company_block = None
        tax_block = None
        if tenant_settings:
            company_lines = [
                tenant_settings.company_name or 'Trockenbau Stuttgart GmbH',
                (tenant_settings.company_address or 'Musterstraße 123, 70173 Stuttgart')
            ]
            contact_line = []
            if tenant_settings.company_phone:
                contact_line.append(f"Tel: {tenant_settings.company_phone}")
            if tenant_settings.company_fax:
                contact_line.append(f"Fax: {tenant_settings.company_fax}")
            if contact_line:
                company_lines.append(' • '.join(contact_line))
            if tenant_settings.company_email:
                company_lines.append(f"E-Mail: {tenant_settings.company_email}")
            company_block = '\n'.join(filter(None, company_lines))

            tax_lines = []
            if tenant_settings.tax_number:
                tax_lines.append(f"Steuernummer: {tenant_settings.tax_number}")
            if tenant_settings.vat_id:
                tax_lines.append(f"USt-IdNr.: {tenant_settings.vat_id}")
            if tenant_settings.bank_iban:
                tax_lines.append(f"IBAN: {tenant_settings.bank_iban}")
            if tenant_settings.bank_bic:
                tax_lines.append(f"BIC: {tenant_settings.bank_bic}")
            if tenant_settings.bank_name:
                tax_lines.append(f"Bank: {tenant_settings.bank_name}")
            tax_block = '\n'.join(tax_lines)

        invoice_data = {
            'invoice_number': invoice.invoice_number,
            'title': invoice.title,
            'description': invoice.description,
            'client_name': invoice.client_name,
            'client_address': invoice.client_address,
            'total_amount': invoice.total_amount,
            'currency': invoice.currency,
            'invoice_date': invoice.invoice_date.isoformat() if invoice.invoice_date else None,
            'due_date': invoice.due_date.isoformat() if invoice.due_date else None,
            'items': invoice.items,
            'company_block': company_block,
            'tax_block': tax_block
        }
        
        # PDF generieren
        if hasattr(current_user, "id"):
            pdf_bytes = create_beautiful_invoice_pdf(invoice_data, session, current_user.id)
        else:
            pdf_bytes = create_invoice_pdf(invoice_data)
        
        # Temporäre Datei erstellen
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_bytes)
            tmp_file_path = tmp_file.name
        
        # Dateiname für Download
        filename = f"Rechnung_{invoice.invoice_number}_{invoice_id}.pdf"

        cleanup_task = BackgroundTask(
            lambda: os.path.exists(tmp_file_path) and os.unlink(tmp_file_path)
        )

        return FileResponse(
            path=tmp_file_path,
            filename=filename,
            media_type='application/pdf',
            headers={"Content-Disposition": f"attachment; filename={filename}"},
            background=cleanup_task
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Generieren des PDFs: {str(e)}")

@router.get("/project/{project_id}", response_model=List[InvoiceSchema])
def get_invoices_by_project(project_id: int, session: Session = Depends(get_session)):
    """
    Alle Rechnungen eines Projekts abrufen.
    
    Args:
        project_id: Projekt-ID
        session: Datenbank-Session
        
    Returns:
        List[InvoiceSchema]: Liste der Rechnungen des Projekts
        
    Raises:
        HTTPException: Wenn Projekt nicht gefunden wird
    """
    # Prüfen ob das Projekt existiert
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
    
    statement = select(Invoice).where(Invoice.project_id == project_id)
    invoices = session.exec(statement).all()
    return invoices

@router.post("/from-offer/{offer_id}")
def create_invoice_from_offer(offer_id: int, session: Session = Depends(get_session)):
    """
    Rechnung aus einem Angebot erstellen.
    
    Args:
        offer_id: Angebots-ID
        session: Datenbank-Session
        
    Returns:
        InvoiceSchema: Erstellte Rechnung
        
    Raises:
        HTTPException: Wenn Angebot nicht gefunden wird
    """
    from ..models import Offer
    
    # Angebot abrufen
    offer = session.get(Offer, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Angebot nicht gefunden")
    
    # Rechnungsnummer generieren
    invoice_number = f"R-{datetime.now().strftime('%Y%m%d')}-{offer_id:04d}"
    
    # Fälligkeitsdatum (30 Tage nach Rechnungsdatum)
    due_date = datetime.now() + timedelta(days=30)
    
    # Rechnung aus Angebot erstellen
    invoice_data = {
        'project_id': offer.project_id,
        'invoice_number': invoice_number,
        'title': f"Rechnung - {offer.title}",
        'description': offer.description,
        'client_name': offer.client_name,
        'client_address': offer.client_address,
        'total_amount': round(float(offer.total_amount), 2),
        'currency': offer.currency,
        'invoice_date': datetime.now(),
        'due_date': due_date,
        'items': offer.items,  # Items vom Angebot übernehmen
        'status': 'entwurf'
    }
    
    db_invoice = Invoice.model_validate(invoice_data)
    session.add(db_invoice)
    session.commit()
    session.refresh(db_invoice)
    
    # Angebot als "abgerechnet" markieren
    offer.status = "abgerechnet"
    session.add(offer)
    session.commit()
    
    return db_invoice

def _calculate_personnel_costs(session: Session, project_id: int):
    time_entries = session.exec(select(TimeEntry).where(TimeEntry.project_id == project_id)).all()
    total_hours = 0.0
    total_cost = 0.0

    for entry in time_entries:
        hours = entry.hours_worked or 0.0
        total_hours += hours

        if entry.hourly_rate is not None:
            rate = entry.hourly_rate
        else:
            employee = session.exec(select(Employee).where(Employee.id == entry.employee_id)).first()
            rate = employee.hourly_rate if employee and employee.hourly_rate else 0.0

        total_cost += hours * rate

    return total_hours, total_cost

def _collect_project_items(session: Session, project_id: int):
    items = []

    hours, personnel_cost = _calculate_personnel_costs(session, project_id)
    if hours > 0 and personnel_cost > 0:
        avg_rate = personnel_cost / hours if hours else 0
        items.append({
            'description': 'Personalkosten',
            'quantity': round(hours, 2),
            'unit': 'Stunden',
            'unit_price': round(avg_rate, 2),
            'total_price': round(personnel_cost, 2),
            'item_type': 'labor'
        })

    material_usages = session.exec(select(MaterialUsage).where(MaterialUsage.project_id == project_id)).all()
    material_total = 0.0
    for material in material_usages:
        cost = material.total_cost
        if cost is None and material.unit_price is not None:
            cost = material.unit_price * material.quantity

        if cost:
            items.append({
                'description': f"Material: {material.material_name}",
                'quantity': material.quantity,
                'unit': material.unit,
                'unit_price': material.unit_price or 0,
                'total_price': round(cost, 2),
                'item_type': 'material'
            })
            material_total += cost

    total_amount = round(personnel_cost + material_total, 2)
    return items, total_amount

@router.post("/auto-generate/{project_id}")
def auto_generate_invoice(project_id: int, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projekt nicht gefunden")

    items, total_amount = _collect_project_items(session, project_id)
    if not items:
        raise HTTPException(status_code=400, detail="Keine abrechenbaren Positionen gefunden")

    invoice_number = f"R-{datetime.now().strftime('%Y%m%d')}-{project_id:04d}"
    due_date = datetime.now() + timedelta(days=30)

    invoice_data = {
        'project_id': project_id,
        'invoice_number': invoice_number,
        'title': f"Rechnung - {project.name}",
        'description': f"Rechnung für Projekt: {project.name}",
        'client_name': project.client_name or "Kunde",
        'client_address': project.address,
        'total_amount': round(total_amount, 2),
        'currency': 'EUR',
        'invoice_date': datetime.now(),
        'due_date': due_date,
        'items': json.dumps(items),
        'status': 'entwurf'
    }

    db_invoice = Invoice.model_validate(invoice_data)
    session.add(db_invoice)
    session.commit()
    session.refresh(db_invoice)

    return db_invoice

# Automatische Rechnungsgenerierung Endpoints (MÜSSEN VOR {invoice_id} stehen!)
@router.get("/generation-methods")
def get_generation_methods(current_user = Depends(get_current_user)):
    """
    Gibt verfügbare Rechnungsgenerierungs-Methoden zurück.
    
    Returns:
        dict: Verfügbare Methoden und deren Beschreibungen
    """
    return {
        "methods": {
            "time_entries": {
                "name": "Stundeneinträge",
                "description": "Generiert Rechnung basierend auf Arbeitsstunden und Stundensätzen",
                "features": ["Lohnanteil-Berechnung", "Mitarbeiter-spezifische Abrechnung"]
            },
            "reports": {
                "name": "Berichte",
                "description": "Generiert Rechnung basierend auf erstellten Berichten",
                "features": ["Leistungsnachweis", "Arbeitsart-spezifische Abrechnung"]
            },
            "offers": {
                "name": "Angebote",
                "description": "Generiert Rechnung basierend auf akzeptierten Angeboten",
                "features": ["Angebotspositionen", "Vordefinierte Preise"]
            },
            "hybrid": {
                "name": "Hybrid (Empfohlen)",
                "description": "Kombiniert alle Datenquellen für umfassende Rechnungsgenerierung",
                "features": ["Stundeneinträge", "Materialverbrauch", "Berichte", "Lohnanteil"]
            }
        },
        "ustg_requirements": {
            "section_14": "UStG §14 konforme Rechnungsstellung",
            "labor_cost_display": "Lohnanteil gesondert ausweisen",
            "tax_calculation": "Automatische USt-Berechnung",
            "invoice_numbering": "Fortlaufende Rechnungsnummerierung"
        }
    }

@router.post("/generate", response_model=InvoiceCalculationResult)
def generate_invoice_calculation(
    request: InvoiceGenerationRequest, 
    session: Session = Depends(get_session), 
    current_user = Depends(require_buchhalter_or_admin)
):
    """
    Generiert eine Rechnungsberechnung basierend auf verschiedenen Datenquellen.
    
    Args:
        request: Rechnungsgenerierungs-Anfrage
        
    Returns:
        InvoiceCalculationResult: Berechnungsergebnis
    """
    try:
        generator = InvoiceGenerator(session)
        result = generator.generate_invoice(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler bei der Rechnungsgenerierung: {str(e)}")

@router.post("/create-from-calculation")
def create_invoice_from_calculation(
    project_id: int,
    calculation: InvoiceCalculationResult,
    invoice_number: str,
    client_name: str,
    client_address: str = None,
    session: Session = Depends(get_session),
    current_user = Depends(require_buchhalter_or_admin)
):
    """
    Erstellt eine tatsächliche Rechnung aus einem Berechnungsergebnis.
    
    Args:
        project_id: Projekt-ID
        calculation: Berechnungsergebnis
        invoice_number: Rechnungsnummer
        client_name: Kundenname
        client_address: Kundenadresse (optional)
        
    Returns:
        Invoice: Erstellte Rechnung
    """
    try:
        generator = InvoiceGenerator(session)
        invoice = generator.create_invoice_from_calculation(
            project_id, calculation, invoice_number, client_name, client_address
        )
        return invoice
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Erstellen der Rechnung: {str(e)}")

# SPEZIFISCHE ENDPOINTS (müssen vor {invoice_id} stehen)
@router.get("/total-revenue")
def get_total_revenue(session: Session = Depends(get_session), current_user = Depends(get_current_user)):
    """
    Berechnet den Gesamtumsatz aus allen bezahlten Rechnungen.
    
    Returns:
        dict: Gesamtumsatz und Anzahl der Rechnungen
    """
    try:
        # Alle bezahlten Rechnungen abrufen
        statement = select(Invoice).where(Invoice.status == 'bezahlt')
        paid_invoices = session.exec(statement).all()
        
        total_revenue = sum(invoice.total_amount for invoice in paid_invoices)
        invoice_count = len(paid_invoices)
        
        return {
            "total_revenue": round(total_revenue, 2),
            "invoice_count": invoice_count,
            "currency": "EUR"
        }
    except Exception as e:
        print(f"Fehler bei Gesamtumsatz-Berechnung: {e}")
        return {
            "total_revenue": 0.0,
            "invoice_count": 0,
            "currency": "EUR"
        }

@router.get("/{invoice_id}", response_model=InvoiceSchema)
def get_invoice(invoice_id: int, session: Session = Depends(get_session)):
    """
    Eine spezifische Rechnung abrufen.
    
    Args:
        invoice_id: ID der Rechnung
        
    Returns:
        InvoiceSchema: Rechnungsdaten
    """
    try:
        statement = select(Invoice).where(Invoice.id == invoice_id)
        invoice = session.exec(statement).first()
        
        if not invoice:
            raise HTTPException(status_code=404, detail="Rechnung nicht gefunden")
        
        # Konvertiere items von JSON-String zu Liste falls nötig
        if isinstance(invoice.items, str):
            try:
                invoice.items = json.loads(invoice.items)
            except:
                invoice.items = []
        elif invoice.items is None:
            invoice.items = []
        
        return invoice
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Rechnung: {str(e)}")

