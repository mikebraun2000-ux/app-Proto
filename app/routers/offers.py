"""
Router für Angebot-Management.
Bietet CRUD-Operationen für Angebote und PDF-Export.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from typing import List
import json
import tempfile
import os
from ..database import get_session
from ..models import Offer, Project, Invoice
from ..schemas import OfferCreate, OfferUpdate, Offer as OfferSchema, OfferItem, InvoiceCreate, OfferGenerationRequest
from ..utils.pdf_utils import create_offer_pdf
from ..auth import get_current_user, require_buchhalter_or_admin
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter(
    prefix="/offers",
    tags=["offers"],
    dependencies=[Depends(get_current_user)],
)

@router.get("/", response_model=List[OfferSchema])
def get_offers(
    auto_generated: Optional[bool] = None,
    session: Session = Depends(get_session),
    current_user = Depends(require_buchhalter_or_admin)
):
    """
    Alle Angebote abrufen, optional gefiltert nach auto_generated.
    
    Args:
        auto_generated: Optional filter - True=nur automatische, False=nur manuelle, None=alle
    
    Returns:
        List[OfferSchema]: Liste der Angebote
    """
    try:
        statement = select(Offer)
        
        # Filter anwenden falls angegeben
        if auto_generated is not None:
            statement = statement.where(Offer.auto_generated == auto_generated)
        
        offers = session.exec(statement).all()
        
        # Stelle sicher, dass items ein JSON-String ist
        for offer in offers:
            if isinstance(offer.items, list):
                offer.items = json.dumps(offer.items)
            elif offer.items is None:
                offer.items = "[]"
            elif not isinstance(offer.items, str):
                offer.items = "[]"
        
        return offers
    except Exception as e:
        print(f"Error in get_offers: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Laden der Angebote: {str(e)}")

@router.post("/", response_model=OfferSchema)
def create_offer(
    offer: OfferCreate,
    session: Session = Depends(get_session),
    current_user = Depends(require_buchhalter_or_admin),
):
    """
    Neues Angebot erstellen.
    
    Args:
        offer: Angebot-Daten
        session: Datenbank-Session
        
    Returns:
        OfferSchema: Erstelltes Angebot
        
    Raises:
        HTTPException: Wenn zugehöriges Projekt nicht gefunden wird
    """
    try:
        # Prüfen ob das Projekt existiert
        project = session.get(Project, offer.project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
        
        # Items als JSON-String speichern
        items_json = json.dumps(offer.items) if offer.items else "[]"
        
        # Datum konvertieren (nur wenn vorhanden und nicht leer)
        valid_until = None
        if offer.valid_until and offer.valid_until.strip():
            try:
                from datetime import datetime
                # ISO-Format: 2025-09-30 -> 2025-09-30T00:00:00
                if len(offer.valid_until) == 10:  # Nur Datum ohne Zeit
                    valid_until = datetime.fromisoformat(offer.valid_until + 'T00:00:00')
                else:
                    valid_until = datetime.fromisoformat(offer.valid_until)
            except Exception as e:
                print(f"Fehler bei Datum-Konvertierung: {e}")
                valid_until = None
        
        # Angebot direkt erstellen
        db_offer = Offer(
            project_id=offer.project_id,
            title=offer.title,
            description=offer.description,
            client_name=offer.client_name,
            client_address=offer.client_address,
            total_amount=offer.total_amount,
            currency=getattr(offer, 'currency', 'EUR'),
            valid_until=valid_until,
            items=items_json,
            status=getattr(offer, 'status', 'entwurf'),
            auto_generated=getattr(offer, 'auto_generated', False)
        )
        
        session.add(db_offer)
        session.commit()
        session.refresh(db_offer)
        return db_offer
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Fehler bei Angebot-Erstellung: {e}")
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler bei Angebot-Erstellung: {str(e)}")

@router.post("/auto", response_model=OfferSchema)
def create_auto_offer(
    request: OfferGenerationRequest,
    session: Session = Depends(get_session),
    current_user = Depends(require_buchhalter_or_admin)
):
    """
    Erstellt ein automatisches Angebot auf Basis der Projektdaten.
    
    Args:
        request: OfferGenerationRequest mit project_id und optionalen Daten
        session: Datenbank-Session
        current_user: Aktueller Benutzer (Buchhalter oder Admin)
    
    Returns:
        OfferSchema: Erstelltes automatisches Angebot
    """
    try:
        project = session.get(Project, request.project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Projekt nicht gefunden")

        # Gültigkeit: 30 Tage ab heute
        today = datetime.utcnow()
        valid_until = today + timedelta(days=30)

        # Titel und Beschreibung
        base_title = project.name or "Projektangebot"
        auto_title = f"Automatisches Angebot – {base_title}"
        auto_description = (
            f"Automatisch generiertes Angebot für das Projekt '{project.name}'.\n"
            f"Kunde: {project.client_name or request.client_name or '—'}."
        )

        # Items: entweder aus Request oder Default-Items generieren
        if request.items:
            items = request.items
        else:
            # Default-Items basierend auf Projektdaten
            items = []
            if project.total_area and project.hourly_rate:
                items.append(OfferItem(
                    position=1,
                    description=f"Trockenbauarbeiten - {project.project_type or 'Standard'}",
                    quantity=project.total_area,
                    unit="m²",
                    unit_price=50.0,
                    total_price=project.total_area * 50.0
                ))
            if project.estimated_hours and project.hourly_rate:
                items.append(OfferItem(
                    position=2,
                    description="Arbeitsstunden",
                    quantity=project.estimated_hours,
                    unit="Std",
                    unit_price=project.hourly_rate,
                    total_price=project.estimated_hours * project.hourly_rate
                ))
            
            # Falls keine Items generiert werden konnten, Standard-Item hinzufügen
            if not items:
                items.append(OfferItem(
                    position=1,
                    description="Bauleistungen",
                    quantity=1.0,
                    unit="Pauschal",
                    unit_price=5000.0,
                    total_price=5000.0
                ))

        # Gesamtbetrag berechnen
        total_amount = sum(item.total_price for item in items)

        # Angebot erstellen mit auto_generated=True
        db_offer = Offer(
            project_id=project.id,
            title=auto_title,
            description=auto_description,
            client_name=request.client_name or project.client_name or "N.N.",
            client_address=request.client_address or project.address or "",
            total_amount=total_amount,
            currency=request.currency,
            valid_until=valid_until,
            items=json.dumps([item.model_dump() for item in items]),
            status="entwurf",
            auto_generated=True  # ⚠️ WICHTIG: Markiert als automatisch generiert
        )

        session.add(db_offer)
        session.commit()
        session.refresh(db_offer)

        return db_offer
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler beim automatischen Angebot: {str(e)}")

@router.get("/{offer_id}", response_model=OfferSchema)
def get_offer(
    offer_id: int,
    session: Session = Depends(get_session),
    current_user = Depends(require_buchhalter_or_admin),
):
    """
    Einzelnes Angebot anhand der ID abrufen.
    
    Args:
        offer_id: Angebot-ID
        session: Datenbank-Session
        
    Returns:
        OfferSchema: Angebot-Daten
        
    Raises:
        HTTPException: Wenn Angebot nicht gefunden wird
    """
    offer = session.get(Offer, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Angebot nicht gefunden")
    return offer

@router.put("/{offer_id}", response_model=OfferSchema)
def update_offer(
    offer_id: int,
    offer_update: OfferUpdate,
    session: Session = Depends(get_session),
    current_user = Depends(require_buchhalter_or_admin)
):
    """
    Angebot aktualisieren.
    
    Args:
        offer_id: Angebot-ID
        offer_update: Aktualisierte Angebot-Daten
        session: Datenbank-Session
        
    Returns:
        OfferSchema: Aktualisiertes Angebot
        
    Raises:
        HTTPException: Wenn Angebot nicht gefunden wird
    """
    offer = session.get(Offer, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Angebot nicht gefunden")
    
    # Nur gesetzte Felder aktualisieren
    offer_data = offer_update.model_dump(exclude_unset=True)
    
    # Items als JSON-String konvertieren falls vorhanden
    if 'items' in offer_data and offer_data['items'] is not None:
        offer_data['items'] = json.dumps([item.model_dump() for item in offer_data['items']])
    
    for field, value in offer_data.items():
        # Spezielle Behandlung für Datumsfelder
        if field == 'valid_until' and value:
            from datetime import datetime
            # Konvertiere String zu datetime
            if isinstance(value, str):
                try:
                    # Versuche ISO-Format zu parsen
                    if 'T' in value:
                        value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    else:
                        # Nur Datum ohne Zeit
                        value = datetime.strptime(value, '%Y-%m-%d').date()
                except ValueError:
                    # Fallback: versuche andere Formate
                    try:
                        value = datetime.strptime(value, '%Y-%m-%d')
                    except ValueError:
                        pass  # Behalte ursprünglichen Wert
        setattr(offer, field, value)
    
    session.add(offer)
    session.commit()
    session.refresh(offer)
    return offer

@router.delete("/{offer_id}")
def delete_offer(
    offer_id: int,
    session: Session = Depends(get_session),
    current_user = Depends(require_buchhalter_or_admin),
):
    """
    Angebot löschen.
    
    Args:
        offer_id: Angebot-ID
        session: Datenbank-Session
        
    Returns:
        dict: Erfolgsmeldung
        
    Raises:
        HTTPException: Wenn Angebot nicht gefunden wird
    """
    offer = session.get(Offer, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Angebot nicht gefunden")
    
    session.delete(offer)
    session.commit()
    return {"message": "Angebot erfolgreich gelöscht"}

@router.post("/{offer_id}/pdf")
def generate_offer_pdf(
    offer_id: int,
    session: Session = Depends(get_session),
    current_user = Depends(require_buchhalter_or_admin),
):
    """
    PDF-Angebot generieren und als Datei zurückgeben.
    
    Args:
        offer_id: Angebot-ID
        session: Datenbank-Session
        
    Returns:
        FileResponse: PDF-Datei
        
    Raises:
        HTTPException: Wenn Angebot nicht gefunden wird
    """
    offer = session.get(Offer, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Angebot nicht gefunden")
    
    try:
        # Angebotsdaten für PDF vorbereiten
        offer_data = {
            'title': offer.title,
            'description': offer.description,
            'client_name': offer.client_name,
            'client_address': offer.client_address,
            'total_amount': offer.total_amount,
            'currency': offer.currency,
            'valid_until': offer.valid_until.isoformat() if offer.valid_until else None,
            'items': offer.items  # Bereits als JSON-String
        }
        
        # PDF generieren
        pdf_bytes = create_offer_pdf(offer_data)
        
        # Temporäre Datei erstellen
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_bytes)
            tmp_file_path = tmp_file.name
        
        # Dateiname für Download
        filename = f"Angebot_{offer.title.replace(' ', '_')}_{offer_id}.pdf"
        
        return FileResponse(
            path=tmp_file_path,
            filename=filename,
            media_type='application/pdf',
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Generieren des PDFs: {str(e)}")

@router.get("/project/{project_id}", response_model=List[OfferSchema])
def get_offers_by_project(
    project_id: int,
    session: Session = Depends(get_session),
    current_user = Depends(require_buchhalter_or_admin),
):
    """
    Alle Angebote eines Projekts abrufen.
    
    Args:
        project_id: Projekt-ID
        session: Datenbank-Session
        
    Returns:
        List[OfferSchema]: Liste der Angebote des Projekts
        
    Raises:
        HTTPException: Wenn Projekt nicht gefunden wird
    """
    # Prüfen ob das Projekt existiert
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
    
    statement = select(Offer).where(Offer.project_id == project_id)
    offers = session.exec(statement).all()
    return offers

@router.post("/{offer_id}/create-invoice", response_model=dict)
def create_invoice_from_offer(
    offer_id: int,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """
    Erstellt eine Rechnung aus einem Angebot.
    
    Args:
        offer_id: ID des Angebots
        session: Datenbanksession
        current_user: Aktueller Benutzer
        
    Returns:
        dict: Erstellte Rechnung mit Download-URL
        
    Raises:
        HTTPException: Wenn Angebot nicht gefunden wird
    """
    # Angebot abrufen
    offer = session.get(Offer, offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Angebot nicht gefunden")
    
    # Prüfen ob bereits eine Rechnung für dieses Angebot existiert
    existing_invoice = session.exec(
        select(Invoice).where(Invoice.offer_id == offer_id)
    ).first()
    
    if existing_invoice:
        raise HTTPException(
            status_code=400, 
            detail="Für dieses Angebot existiert bereits eine Rechnung"
        )
    
    try:
        # Rechnungsnummer generieren
        from datetime import datetime
        invoice_number = f"RE-{datetime.now().strftime('%Y%m%d')}-{offer.id:03d}"
        
        # Rechnung aus Angebot erstellen
        invoice_data = {
            "project_id": offer.project_id,
            "offer_id": offer.id,
            "invoice_number": invoice_number,
            "title": f"Rechnung für {offer.title}",
            "description": f"Rechnung basierend auf Angebot: {offer.title}",
            "client_name": offer.client_name,
            "client_address": offer.client_address,
            "total_amount": offer.total_amount,
            "currency": offer.currency,
            "items": offer.items,  # Angebotspositionen übernehmen
            "status": "entwurf"
        }
        
        # Rechnung in Datenbank speichern
        db_invoice = Invoice(**invoice_data)
        session.add(db_invoice)
        session.commit()
        session.refresh(db_invoice)
        
        return {
            "message": "Rechnung erfolgreich erstellt",
            "invoice_id": db_invoice.id,
            "download_url": f"/invoices/{db_invoice.id}/pdf"
        }
        
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler beim Erstellen der Rechnung: {str(e)}")

