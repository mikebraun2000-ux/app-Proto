"""Router für Rechnungs-Management mit konsequentem Tenant-Scoping."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timedelta
from typing import Iterable, List, Tuple

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from sqlmodel import Session, select, func

from ..auth import get_current_user, require_buchhalter_or_admin
from ..database import get_session
from ..models import (
    Employee,
    Invoice,
    MaterialUsage,
    Offer,
    Project,
    TenantSettings,
    TimeEntry,
)
from ..schemas import (
    Invoice as InvoiceSchema,
    InvoiceCalculationResult,
    InvoiceCreate,
    InvoiceGenerationRequest,
    InvoiceItem,
    InvoiceUpdate,
)
from ..services.beautiful_pdf_generator import create_beautiful_invoice_pdf
from ..services.invoice_generator import InvoiceGenerator
from ..utils.pdf_utils import create_invoice_pdf
from ..utils.tenant_scoping import add_tenant_filter, ensure_tenant_access, set_tenant_on_model

router = APIRouter(prefix="/invoices", tags=["invoices"])


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def _serialize_items(items: Iterable[InvoiceItem] | None) -> str:
    """Serialize InvoiceItem-Instanzen in einen JSON-String."""
    if not items:
        return "[]"
    return json.dumps([item.model_dump() for item in items])


def _ensure_project(session: Session, project_id: int, tenant_id: int) -> Project:
    """Projekt laden und auf Tenant-Zugehörigkeit prüfen."""
    project = session.get(Project, project_id)
    return ensure_tenant_access(project, tenant_id, not_found_detail="Projekt nicht gefunden")


def _ensure_invoice(session: Session, invoice_id: int, tenant_id: int) -> Invoice:
    """Rechnung laden und Tenant-Zugehörigkeit prüfen."""
    invoice = session.get(Invoice, invoice_id)
    return ensure_tenant_access(invoice, tenant_id, not_found_detail="Rechnung nicht gefunden")


def _ensure_offer(session: Session, offer_id: int, tenant_id: int) -> Offer:
    """Angebot laden und Tenant-Zugehörigkeit prüfen."""
    offer = session.get(Offer, offer_id)
    return ensure_tenant_access(offer, tenant_id, not_found_detail="Angebot nicht gefunden")


def _calculate_personnel_costs(session: Session, project_id: int, tenant_id: int) -> Tuple[float, float]:
    """Summiere Stunden und Kosten aller Stundeneinträge eines Projekts."""
    entry_statement = add_tenant_filter(
        select(TimeEntry).where(TimeEntry.project_id == project_id),
        TimeEntry,
        tenant_id,
    )
    time_entries = session.exec(entry_statement).all()

    total_hours = 0.0
    total_cost = 0.0
    for entry in time_entries:
        hours = entry.hours_worked or 0.0
        total_hours += hours

        rate = entry.hourly_rate
        if rate is None:
            employee_statement = add_tenant_filter(
                select(Employee).where(Employee.id == entry.employee_id),
                Employee,
                tenant_id,
            )
            employee = session.exec(employee_statement).first()
            rate = employee.hourly_rate if employee and employee.hourly_rate else 0.0

        total_cost += hours * (rate or 0.0)

    return total_hours, total_cost


def _collect_project_items(session: Session, project_id: int, tenant_id: int) -> Tuple[List[InvoiceItem], float]:
    """Generiere Standard-Rechnungspositionen aus Projektressourcen."""
    items: List[InvoiceItem] = []

    hours, personnel_cost = _calculate_personnel_costs(session, project_id, tenant_id)
    if hours > 0 and personnel_cost > 0:
        average_rate = personnel_cost / hours if hours else 0.0
        items.append(
            InvoiceItem(
                description="Personalkosten",
                quantity=round(hours, 2),
                unit="Std",
                unit_price=round(average_rate, 2),
                total_price=round(personnel_cost, 2),
                item_type="labor",
                labor_cost=round(personnel_cost, 2),
                service_cost=0.0,
            )
        )

    material_statement = add_tenant_filter(
        select(MaterialUsage).where(MaterialUsage.project_id == project_id),
        MaterialUsage,
        tenant_id,
    )
    materials = session.exec(material_statement).all()

    material_total = 0.0
    for material in materials:
        total_price = material.total_cost
        if total_price is None and material.unit_price is not None:
            total_price = (material.unit_price or 0.0) * (material.quantity or 0.0)
        total_price = round(total_price or 0.0, 2)
        material_total += total_price

        items.append(
            InvoiceItem(
                description=f"Material: {material.material_name}",
                quantity=round(material.quantity or 0.0, 2),
                unit=material.unit or "Stk",
                unit_price=round(material.unit_price or 0.0, 2),
                total_price=total_price,
                item_type="material",
                material_cost=total_price,
            )
        )

    total_amount = round(sum(item.total_price or 0.0 for item in items), 2)
    return items, total_amount


def _combine_items(
    provided_items: List[InvoiceItem] | None,
    generated_items: List[InvoiceItem],
    provided_total: float | None,
) -> Tuple[List[InvoiceItem], float]:
    """Füge generierte Positionen zu vorhandenen hinzu und berechne Gesamtsumme."""
    if not provided_items:
        total = provided_total if provided_total is not None else sum(
            item.total_price or 0.0 for item in generated_items
        )
        return generated_items, round(total, 2)

    items = list(generated_items) + list(provided_items)
    if provided_total is not None:
        return items, round(float(provided_total), 2)

    calculated_total = 0.0
    for item in items:
        if item.total_price is not None:
            calculated_total += item.total_price
        else:
            calculated_total += item.quantity * item.unit_price
    return items, round(calculated_total, 2)


# ---------------------------------------------------------------------------
# CRUD-Endpoints
# ---------------------------------------------------------------------------

@router.get("/", response_model=List[InvoiceSchema])
def get_invoices(
    session: Session = Depends(get_session),
    current_user=Depends(require_buchhalter_or_admin),
):
    """Alle Rechnungen des aktuellen Mandanten abrufen."""
    statement = add_tenant_filter(select(Invoice).order_by(Invoice.created_at.desc()), Invoice, current_user.tenant_id)
    invoices = session.exec(statement).all()

    for invoice in invoices:
        if invoice.items is None:
            invoice.items = "[]"
        elif not isinstance(invoice.items, str):
            invoice.items = json.dumps(invoice.items)
    return invoices


@router.post("/", response_model=InvoiceSchema)
def create_invoice(
    invoice_data: InvoiceCreate,
    session: Session = Depends(get_session),
    current_user=Depends(require_buchhalter_or_admin),
):
    """Neue Rechnung erstellen und dem Mandanten zuordnen."""
    project = _ensure_project(session, invoice_data.project_id, current_user.tenant_id)

    generated_items, generated_total = _collect_project_items(session, project.id, current_user.tenant_id)
    items, total_amount = _combine_items(invoice_data.items, generated_items, invoice_data.total_amount)

    payload = invoice_data.model_dump(exclude={"items", "total_amount", "invoice_date", "due_date"})
    payload["total_amount"] = total_amount
    payload["invoice_date"] = invoice_data.invoice_date or datetime.utcnow()
    payload["due_date"] = invoice_data.due_date
    payload["items"] = _serialize_items(items)

    db_invoice = Invoice(**payload)
    set_tenant_on_model(db_invoice, current_user.tenant_id)

    session.add(db_invoice)
    session.commit()
    session.refresh(db_invoice)
    return db_invoice


@router.put("/{invoice_id}", response_model=InvoiceSchema)
def update_invoice(
    invoice_id: int,
    invoice_update: InvoiceUpdate,
    session: Session = Depends(get_session),
    current_user=Depends(require_buchhalter_or_admin),
):
    """Bestehende Rechnung aktualisieren."""
    invoice = _ensure_invoice(session, invoice_id, current_user.tenant_id)

    update_data = invoice_update.model_dump(exclude_unset=True)

    if "items" in update_data:
        items = update_data.pop("items")
        invoice.items = _serialize_items(items)

    for field, value in update_data.items():
        if field == "total_amount" and value is not None:
            value = round(float(value), 2)
        setattr(invoice, field, value)

    session.add(invoice)
    session.commit()
    session.refresh(invoice)
    return invoice


@router.delete("/{invoice_id}")
def delete_invoice(
    invoice_id: int,
    session: Session = Depends(get_session),
    current_user=Depends(require_buchhalter_or_admin),
):
    """Rechnung löschen."""
    invoice = _ensure_invoice(session, invoice_id, current_user.tenant_id)

    session.delete(invoice)
    session.commit()
    return {"message": "Rechnung erfolgreich gelöscht"}


@router.get("/{invoice_id}", response_model=InvoiceSchema)
def get_invoice(
    invoice_id: int,
    session: Session = Depends(get_session),
    current_user=Depends(require_buchhalter_or_admin),
):
    """Einzelne Rechnung abrufen."""
    invoice = _ensure_invoice(session, invoice_id, current_user.tenant_id)
    if isinstance(invoice.items, list):
        invoice.items = json.dumps(invoice.items)
    elif invoice.items is None:
        invoice.items = "[]"
    return invoice


# ---------------------------------------------------------------------------
# PDF / Zusatzfunktionen
# ---------------------------------------------------------------------------

@router.get("/{invoice_id}/pdf")
def generate_invoice_pdf(
    invoice_id: int,
    session: Session = Depends(get_session),
    current_user=Depends(require_buchhalter_or_admin),
):
    """PDF einer Rechnung erzeugen und zum Download bereitstellen."""
    invoice = _ensure_invoice(session, invoice_id, current_user.tenant_id)

    tenant_settings = session.exec(
        select(TenantSettings).where(TenantSettings.tenant_id == current_user.tenant_id)
    ).first()

    company_block = None
    tax_block = None
    if tenant_settings:
        company_lines = [
            tenant_settings.company_name or "Trockenbau Stuttgart GmbH",
            tenant_settings.company_address or "Musterstraße 123, 70173 Stuttgart",
        ]
        contact_line = []
        if tenant_settings.company_phone:
            contact_line.append(f"Tel: {tenant_settings.company_phone}")
        if tenant_settings.company_fax:
            contact_line.append(f"Fax: {tenant_settings.company_fax}")
        if contact_line:
            company_lines.append(" • ".join(contact_line))
        if tenant_settings.company_email:
            company_lines.append(f"E-Mail: {tenant_settings.company_email}")
        company_block = "\n".join(filter(None, company_lines))

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
        tax_block = "\n".join(tax_lines)

    invoice_data = {
        "invoice_number": invoice.invoice_number,
        "title": invoice.title,
        "description": invoice.description,
        "client_name": invoice.client_name,
        "client_address": invoice.client_address,
        "total_amount": invoice.total_amount,
        "currency": invoice.currency,
        "invoice_date": invoice.invoice_date.isoformat() if invoice.invoice_date else None,
        "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
        "items": invoice.items,
        "company_block": company_block,
        "tax_block": tax_block,
    }

    if hasattr(current_user, "id"):
        pdf_bytes = create_beautiful_invoice_pdf(invoice_data, session, current_user.id)
    else:  # pragma: no cover - Fallback für Service-Aufrufe ohne User
        pdf_bytes = create_invoice_pdf(invoice_data)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(pdf_bytes)
        tmp_file_path = tmp_file.name

    filename = f"Rechnung_{invoice.invoice_number}_{invoice_id}.pdf"

    cleanup_task = BackgroundTask(lambda: os.path.exists(tmp_file_path) and os.unlink(tmp_file_path))

    return FileResponse(
        path=tmp_file_path,
        filename=filename,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
        background=cleanup_task,
    )


@router.get("/project/{project_id}", response_model=List[InvoiceSchema])
def get_invoices_by_project(
    project_id: int,
    session: Session = Depends(get_session),
    current_user=Depends(require_buchhalter_or_admin),
):
    """Alle Rechnungen eines Projekts abrufen."""
    _ensure_project(session, project_id, current_user.tenant_id)
    statement = add_tenant_filter(
        select(Invoice).where(Invoice.project_id == project_id),
        Invoice,
        current_user.tenant_id,
    )
    invoices = session.exec(statement).all()
    for invoice in invoices:
        if invoice.items is None:
            invoice.items = "[]"
    return invoices


@router.post("/{offer_id}/create-invoice", response_model=dict)
def create_invoice_from_offer(
    offer_id: int,
    session: Session = Depends(get_session),
    current_user=Depends(require_buchhalter_or_admin),
):
    """Aus einem Angebot eine Rechnung erzeugen."""
    offer = _ensure_offer(session, offer_id, current_user.tenant_id)
    _ensure_project(session, offer.project_id, current_user.tenant_id)

    existing_invoice = session.exec(
        add_tenant_filter(select(Invoice).where(Invoice.offer_id == offer_id), Invoice, current_user.tenant_id)
    ).first()
    if existing_invoice:
        raise HTTPException(status_code=400, detail="Für dieses Angebot existiert bereits eine Rechnung")

    invoice_number = f"RE-{datetime.now().strftime('%Y%m%d')}-{offer.id:03d}"
    invoice_payload = Invoice(
        project_id=offer.project_id,
        offer_id=offer.id,
        invoice_number=invoice_number,
        title=f"Rechnung für {offer.title}",
        description=f"Rechnung basierend auf Angebot: {offer.title}",
        client_name=offer.client_name,
        client_address=offer.client_address,
        total_amount=round(float(offer.total_amount), 2),
        currency=offer.currency,
        invoice_date=datetime.utcnow(),
        due_date=None,
        items=offer.items or "[]",
        status="entwurf",
    )
    set_tenant_on_model(invoice_payload, current_user.tenant_id)

    session.add(invoice_payload)
    session.commit()
    session.refresh(invoice_payload)

    return {
        "message": "Rechnung erfolgreich erstellt",
        "invoice_id": invoice_payload.id,
        "download_url": f"/invoices/{invoice_payload.id}/pdf",
    }


@router.post("/auto-generate/{project_id}", response_model=InvoiceSchema)
def auto_generate_invoice(
    project_id: int,
    session: Session = Depends(get_session),
    current_user=Depends(require_buchhalter_or_admin),
):
    """Rechnung automatisch aus Projektressourcen generieren."""
    project = _ensure_project(session, project_id, current_user.tenant_id)
    items, total_amount = _collect_project_items(session, project.id, current_user.tenant_id)
    if not items:
        raise HTTPException(status_code=400, detail="Keine abrechenbaren Positionen gefunden")

    invoice_number = f"RE-{datetime.utcnow().strftime('%Y%m%d')}-{project_id:04d}"
    invoice = Invoice(
        project_id=project.id,
        invoice_number=invoice_number,
        title=f"Rechnung - {project.name}",
        description=f"Rechnung für Projekt: {project.name}",
        client_name=project.client_name or "Kunde",
        client_address=project.address,
        total_amount=total_amount,
        currency="EUR",
        invoice_date=datetime.utcnow(),
        due_date=datetime.utcnow() + timedelta(days=30),
        items=_serialize_items(items),
        status="entwurf",
    )
    set_tenant_on_model(invoice, current_user.tenant_id)

    session.add(invoice)
    session.commit()
    session.refresh(invoice)
    return invoice


# ---------------------------------------------------------------------------
# Analyse- und Service-Endpunkte
# ---------------------------------------------------------------------------

@router.get("/total-revenue")
def get_total_revenue(
    session: Session = Depends(get_session),
    current_user=Depends(require_buchhalter_or_admin),
):
    """Gesamtumsatz (bezahlt) des aktuellen Mandanten ermitteln."""
    statement = add_tenant_filter(select(Invoice).where(Invoice.status == "bezahlt"), Invoice, current_user.tenant_id)
    paid_invoices = session.exec(statement).all()

    total_revenue = sum(invoice.total_amount for invoice in paid_invoices)
    return {
        "total_revenue": round(total_revenue, 2),
        "invoice_count": len(paid_invoices),
        "currency": "EUR",
    }


@router.post("/generate", response_model=InvoiceCalculationResult)
def generate_invoice_calculation(
    request: InvoiceGenerationRequest,
    session: Session = Depends(get_session),
    current_user=Depends(require_buchhalter_or_admin),
):
    """Berechnung für Rechnungsentwurf durchführen."""
    generator = InvoiceGenerator(session, current_user.tenant_id)
    return generator.generate_invoice(request)


@router.post("/create-from-calculation", response_model=InvoiceSchema)
def create_invoice_from_calculation(
    request_data: dict,
    session: Session = Depends(get_session),
    current_user=Depends(require_buchhalter_or_admin),
):
    """Rechnung basierend auf einer vorherigen Berechnung anlegen."""
    project_id = request_data.get("project_id")
    calculation = request_data.get("calculation")
    invoice_number = request_data.get("invoice_number")
    client_name = request_data.get("client_name")
    client_address = request_data.get("client_address")

    missing = [
        field
        for field, value in {
            "project_id": project_id,
            "calculation": calculation,
            "invoice_number": invoice_number,
            "client_name": client_name,
        }.items()
        if not value
    ]
    if missing:
        raise HTTPException(status_code=400, detail=f"Fehlende erforderliche Parameter: {missing}")

    _ensure_project(session, project_id, current_user.tenant_id)

    generator = InvoiceGenerator(session, current_user.tenant_id)
    invoice = generator.create_invoice_from_calculation(
        project_id=project_id,
        calculation=calculation,
        invoice_number=invoice_number,
        client_name=client_name,
        client_address=client_address,
    )
    return invoice


@router.get("/stats/summary")
def get_invoice_summary(
    session: Session = Depends(get_session),
    current_user=Depends(require_buchhalter_or_admin),
):
    """Aggregierte Kennzahlen für Rechnungen liefern."""
    tenant_id = current_user.tenant_id

    total_invoices = session.exec(
        select(func.count(Invoice.id)).where(Invoice.tenant_id == tenant_id)
    ).one()
    paid_total = session.exec(
        select(func.sum(Invoice.total_amount)).where(
            Invoice.tenant_id == tenant_id, Invoice.status == "bezahlt"
        )
    ).one()

    return {
        "total_invoices": total_invoices or 0,
        "paid_revenue": float(paid_total or 0.0),
    }
