"""Mandantenfähiger FastAPI-Router für Angebotsverwaltung."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from starlette.background import BackgroundTask

from ..auth import get_current_user, require_buchhalter_or_admin
from ..database import get_session
from ..models import Offer, Project, User
from ..schemas import Offer as OfferSchema
from ..schemas import OfferCreate, OfferGenerationRequest, OfferItem, OfferUpdate
from ..utils.pdf_utils import create_offer_pdf

router = APIRouter(
    prefix="/offers",
    tags=["offers"],
    dependencies=[Depends(get_current_user)],
)


def _ensure_project_access(session: Session, tenant_id: int, project_id: int) -> Project:
    """Stellt sicher, dass das referenzierte Projekt dem aktuellen Tenant gehört."""
    statement = select(Project).where(
        Project.id == project_id,
        Project.tenant_id == tenant_id,
    )
    project = session.exec(statement).first()
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Projekt nicht gefunden",
        )
    return project


def _serialize_items(items: Optional[List[OfferItem]]) -> str:
    """Serialisiert Angebotspositionen stabil als JSON-String."""
    if not items:
        return "[]"
    return json.dumps([item.model_dump() if hasattr(item, "model_dump") else item for item in items])


@router.get("/", response_model=List[OfferSchema])
def list_offers(
    auto_generated: Optional[bool] = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_buchhalter_or_admin),
) -> List[Offer]:
    """Listet alle Angebote des aktuellen Tenants, optional gefiltert nach Generierungsart."""
    statement = select(Offer).where(Offer.tenant_id == current_user.tenant_id)
    if auto_generated is not None:
        statement = statement.where(Offer.auto_generated == auto_generated)
    offers = session.exec(statement.order_by(Offer.created_at.desc())).all()
    for offer in offers:
        if offer.items is None:
            offer.items = "[]"
        elif not isinstance(offer.items, str):
            offer.items = json.dumps(offer.items)
    return offers


@router.post("/", response_model=OfferSchema, status_code=status.HTTP_201_CREATED)
def create_offer(
    offer: OfferCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_buchhalter_or_admin),
) -> Offer:
    """Erstellt ein Angebot für ein Projekt des aktuellen Tenants."""
    _ensure_project_access(session, current_user.tenant_id, offer.project_id)
    items_json = _serialize_items(offer.items)

    db_offer = Offer.model_validate(
        offer,
        update={
            "tenant_id": current_user.tenant_id,
            "items": items_json,
        },
    )
    session.add(db_offer)
    session.commit()
    session.refresh(db_offer)
    return db_offer


@router.put("/{offer_id}", response_model=OfferSchema)
def update_offer(
    offer_id: int,
    offer_update: OfferUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_buchhalter_or_admin),
) -> Offer:
    """Aktualisiert ein bestehendes Angebot des Tenants."""
    statement = select(Offer).where(
        Offer.id == offer_id,
        Offer.tenant_id == current_user.tenant_id,
    )
    db_offer = session.exec(statement).first()
    if db_offer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Angebot nicht gefunden")

    update_data = offer_update.model_dump(exclude_unset=True)
    if "items" in update_data:
        update_data["items"] = _serialize_items(update_data["items"])
    if "project_id" in update_data:
        _ensure_project_access(session, current_user.tenant_id, update_data["project_id"])

    for field_name, value in update_data.items():
        setattr(db_offer, field_name, value)

    session.add(db_offer)
    session.commit()
    session.refresh(db_offer)
    return db_offer


@router.get("/{offer_id}", response_model=OfferSchema)
def get_offer(
    offer_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_buchhalter_or_admin),
) -> Offer:
    """Gibt ein einzelnes Angebot des Tenants zurück."""
    statement = select(Offer).where(
        Offer.id == offer_id,
        Offer.tenant_id == current_user.tenant_id,
    )
    db_offer = session.exec(statement).first()
    if db_offer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Angebot nicht gefunden")
    if db_offer.items is None:
        db_offer.items = "[]"
    elif not isinstance(db_offer.items, str):
        db_offer.items = json.dumps(db_offer.items)
    return db_offer


@router.delete("/{offer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_offer(
    offer_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_buchhalter_or_admin),
) -> None:
    """Löscht ein Angebot des aktuellen Mandanten."""
    statement = select(Offer).where(
        Offer.id == offer_id,
        Offer.tenant_id == current_user.tenant_id,
    )
    db_offer = session.exec(statement).first()
    if db_offer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Angebot nicht gefunden")
    session.delete(db_offer)
    session.commit()



@router.post("/auto", response_model=OfferSchema, status_code=status.HTTP_201_CREATED)
def create_auto_offer(
    request: OfferGenerationRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_buchhalter_or_admin),
) -> Offer:
    """Erzeugt ein automatisches Angebot auf Basis der Projektdaten."""
    project = _ensure_project_access(session, current_user.tenant_id, request.project_id)

    valid_until = datetime.utcnow() + timedelta(days=30)
    requested_items = request.items or []
    items: List[OfferItem] = [
        item if isinstance(item, OfferItem) else OfferItem(**item)
        for item in requested_items
    ]
    if not items:
        if project.total_area and project.total_area > 0:
            items.append(
                OfferItem(
                    position=1,
                    description=f"Leistungen – {project.project_type or 'Standard'}",
                    quantity=project.total_area,
                    unit="m²",
                    unit_price=50.0,
                    total_price=project.total_area * 50.0,
                )
            )
        if project.estimated_hours and project.hourly_rate:
            items.append(
                OfferItem(
                    position=len(items) + 1,
                    description="Arbeitsstunden",
                    quantity=project.estimated_hours,
                    unit="Std",
                    unit_price=project.hourly_rate,
                    total_price=project.estimated_hours * project.hourly_rate,
                )
            )
        if not items:
            items.append(
                OfferItem(
                    position=1,
                    description="Bauleistungen pauschal",
                    quantity=1.0,
                    unit="Pauschal",
                    unit_price=5000.0,
                    total_price=5000.0,
                )
            )

    total_amount = sum(item.total_price for item in items)
    title = getattr(request, "title", None) or f"Automatisches Angebot – {project.name}"
    description = getattr(request, "description", None) or (
        f"Automatisch generiertes Angebot für das Projekt '{project.name}'."
    )
    status_value = getattr(request, "status", "entwurf")

    db_offer = Offer(
        tenant_id=current_user.tenant_id,
        project_id=project.id,
        title=title,
        description=description,
        client_name=request.client_name or project.client_name,
        client_address=request.client_address or project.address,
        total_amount=total_amount,
        currency=request.currency or "EUR",
        valid_until=valid_until,
        items=_serialize_items(items),
        status=status_value,
        auto_generated=True,
    )

    session.add(db_offer)
    session.commit()
    session.refresh(db_offer)
    return db_offer

@router.get("/{offer_id}/pdf")
def download_offer_pdf(
    offer_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_buchhalter_or_admin),
) -> FileResponse:
    """Erzeugt ein PDF für ein Angebot des aktuellen Tenants."""
    offer = get_offer(offer_id, session=session, current_user=current_user)

    pdf_bytes = create_offer_pdf(
        {
            "offer_number": offer.id,
            "title": offer.title,
            "description": offer.description,
            "client_name": offer.client_name,
            "client_address": offer.client_address,
            "total_amount": offer.total_amount,
            "currency": offer.currency,
            "valid_until": offer.valid_until.isoformat() if offer.valid_until else None,
            "items": json.loads(offer.items) if isinstance(offer.items, str) else offer.items or [],
        }
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(pdf_bytes)
        file_path = tmp_file.name

    filename = f"Angebot_{offer.id}.pdf"
    cleanup_task = BackgroundTask(lambda: os.path.exists(file_path) and os.unlink(file_path))

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=filename,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
        background=cleanup_task,
    )
