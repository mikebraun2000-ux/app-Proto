"""Mandantenfähige Rechnungsverwaltung für die FastAPI-Anwendung."""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime, timedelta
from typing import Iterable, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlmodel import Session, select
from starlette.background import BackgroundTask

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
    User,
)
from ..schemas import Invoice as InvoiceSchema
from ..schemas import (
    InvoiceCalculationResult,
    InvoiceCreate,
    InvoiceGenerationRequest,
    InvoiceItem,
    InvoiceUpdate,
)
from ..services.beautiful_pdf_generator import create_beautiful_invoice_pdf
from ..services.invoice_generator import InvoiceGenerator
from ..utils.pdf_utils import create_invoice_pdf

router = APIRouter(
    prefix="/invoices",
    tags=["invoices"],
    dependencies=[Depends(get_current_user)],
)


def _ensure_project_access(session: Session, tenant_id: int, project_id: int) -> Project:
    statement = select(Project).where(
        Project.id == project_id,
        Project.tenant_id == tenant_id,
    )
    project = session.exec(statement).first()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projekt nicht gefunden")
    return project


def _ensure_offer_access(session: Session, tenant_id: int, offer_id: int) -> Offer:
    statement = select(Offer).where(Offer.id == offer_id, Offer.tenant_id == tenant_id)
    offer = session.exec(statement).first()
    if offer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Angebot nicht gefunden")
    return offer


def _get_invoice_for_tenant(session: Session, tenant_id: int, invoice_id: int) -> Invoice:
    statement = select(Invoice).where(Invoice.id == invoice_id, Invoice.tenant_id == tenant_id)
    invoice = session.exec(statement).first()
    if invoice is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rechnung nicht gefunden")
    return invoice


def _normalize_items(items: Iterable[InvoiceItem]) -> List[InvoiceItem]:
    normalized: List[InvoiceItem] = []
    for raw_item in items:
        item = raw_item if isinstance(raw_item, InvoiceItem) else InvoiceItem(**raw_item)
        if item.total_price is None:
            item.total_price = round(item.quantity * item.unit_price, 2)
        normalized.append(item)
    return normalized


def _serialize_items(items: Iterable[InvoiceItem]) -> str:
    normalized = _normalize_items(items)
    return json.dumps([item.model_dump() for item in normalized])


@router.get("/", response_model=List[InvoiceSchema])
def list_invoices(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_buchhalter_or_admin),
) -> List[Invoice]:
    """Listet alle Rechnungen des aktuellen Tenants."""
    statement = select(Invoice).where(Invoice.tenant_id == current_user.tenant_id)
    invoices = session.exec(statement.order_by(Invoice.created_at.desc())).all()
    for invoice in invoices:
        if invoice.items is None:
            invoice.items = "[]"
        elif not isinstance(invoice.items, str):
            invoice.items = json.dumps(invoice.items)
    return invoices


@router.post("/", response_model=InvoiceSchema, status_code=status.HTTP_201_CREATED)
def create_invoice(
    invoice: InvoiceCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_buchhalter_or_admin),
) -> Invoice:
    """Erstellt eine neue Rechnung für ein Projekt des aktuellen Mandanten."""
    project = _ensure_project_access(session, current_user.tenant_id, invoice.project_id)
    offer = None
    if invoice.offer_id is not None:
        offer = _ensure_offer_access(session, current_user.tenant_id, invoice.offer_id)
        if offer.project_id != project.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Angebot gehört nicht zum angegebenen Projekt",
            )

    items_json = _serialize_items(invoice.items)
    db_invoice = Invoice(
        tenant_id=current_user.tenant_id,
        project_id=project.id,
        offer_id=offer.id if offer else None,
        invoice_number=invoice.invoice_number,
        title=invoice.title,
        description=invoice.description,
        client_name=invoice.client_name,
        client_address=invoice.client_address,
        total_amount=round(invoice.total_amount, 2),
        currency=invoice.currency,
        invoice_date=invoice.invoice_date or datetime.utcnow(),
        due_date=invoice.due_date,
        items=items_json,
        status=invoice.status,
    )
    session.add(db_invoice)
    session.commit()
    session.refresh(db_invoice)
    return db_invoice


@router.get("/{invoice_id}", response_model=InvoiceSchema)
def get_invoice(
    invoice_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_buchhalter_or_admin),
) -> Invoice:
    """Gibt eine Rechnung des aktuellen Mandanten zurück."""
    invoice = _get_invoice_for_tenant(session, current_user.tenant_id, invoice_id)
    if invoice.items is None:
        invoice.items = "[]"
    elif not isinstance(invoice.items, str):
        invoice.items = json.dumps(invoice.items)
    return invoice


@router.put("/{invoice_id}", response_model=InvoiceSchema)
def update_invoice(
    invoice_id: int,
    invoice_update: InvoiceUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_buchhalter_or_admin),
) -> Invoice:
    """Aktualisiert eine vorhandene Rechnung."""
    invoice = _get_invoice_for_tenant(session, current_user.tenant_id, invoice_id)
    update_data = invoice_update.model_dump(exclude_unset=True)

    if "items" in update_data and update_data["items"] is not None:
        update_data["items"] = _serialize_items(update_data["items"])
    if "project_id" in update_data:
        project_id = update_data["project_id"]
        _ensure_project_access(session, current_user.tenant_id, project_id)
        invoice.project_id = project_id
        update_data.pop("project_id")
    if "offer_id" in update_data and update_data["offer_id"] is not None:
        offer = _ensure_offer_access(session, current_user.tenant_id, update_data["offer_id"])
        if offer.project_id != invoice.project_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Angebot gehört nicht zum Projekt der Rechnung",
            )

    for field_name, value in update_data.items():
        setattr(invoice, field_name, value)

    session.add(invoice)
    session.commit()
    session.refresh(invoice)
    if invoice.items is None:
        invoice.items = "[]"
    return invoice


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice(
    invoice_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_buchhalter_or_admin),
) -> None:
    """Löscht eine Rechnung des aktuellen Mandanten."""
    invoice = _get_invoice_for_tenant(session, current_user.tenant_id, invoice_id)
    session.delete(invoice)
    session.commit()


def _build_invoice_pdf_bytes(
    session: Session, current_user: User, invoice: Invoice
) -> bytes:
    tenant_settings = session.exec(
        select(TenantSettings).where(TenantSettings.tenant_id == current_user.tenant_id)
    ).first()

    invoice_payload = {
        "invoice_number": invoice.invoice_number,
        "title": invoice.title,
        "description": invoice.description,
        "client_name": invoice.client_name,
        "client_address": invoice.client_address,
        "total_amount": invoice.total_amount,
        "currency": invoice.currency,
        "invoice_date": invoice.invoice_date.isoformat() if invoice.invoice_date else None,
        "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
        "items": json.loads(invoice.items) if isinstance(invoice.items, str) else invoice.items or [],
    }

    if tenant_settings:
        invoice_payload["company_block"] = "\n".join(
            filter(
                None,
                [
                    tenant_settings.company_name,
                    tenant_settings.company_address,
                    " • ".join(
                        filter(
                            None,
                            [
                                f"Tel: {tenant_settings.company_phone}" if tenant_settings.company_phone else None,
                                f"Fax: {tenant_settings.company_fax}" if tenant_settings.company_fax else None,
                            ],
                        )
                    ),
                    f"E-Mail: {tenant_settings.company_email}" if tenant_settings.company_email else None,
                ],
            )
        )
        invoice_payload["tax_block"] = "\n".join(
            filter(
                None,
                [
                    f"Steuernummer: {tenant_settings.tax_number}" if tenant_settings.tax_number else None,
                    f"USt-IdNr.: {tenant_settings.vat_id}" if tenant_settings.vat_id else None,
                    f"IBAN: {tenant_settings.bank_iban}" if tenant_settings.bank_iban else None,
                    f"BIC: {tenant_settings.bank_bic}" if tenant_settings.bank_bic else None,
                    f"Bank: {tenant_settings.bank_name}" if tenant_settings.bank_name else None,
                ],
            )
        )

    if hasattr(current_user, "id"):
        return create_beautiful_invoice_pdf(invoice_payload, session, current_user.id)
    return create_invoice_pdf(invoice_payload)


@router.get("/{invoice_id}/pdf")
def download_invoice_pdf(
    invoice_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_buchhalter_or_admin),
) -> FileResponse:
    """Erzeugt ein PDF für eine Rechnung des aktuellen Mandanten."""
    invoice = _get_invoice_for_tenant(session, current_user.tenant_id, invoice_id)
    pdf_bytes = _build_invoice_pdf_bytes(session, current_user, invoice)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(pdf_bytes)
        file_path = tmp_file.name

    filename = f"Rechnung_{invoice.invoice_number}_{invoice_id}.pdf"
    cleanup_task = BackgroundTask(lambda: os.path.exists(file_path) and os.unlink(file_path))

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
        background=cleanup_task,
    )


@router.get("/project/{project_id}", response_model=List[InvoiceSchema])
def list_invoices_by_project(
    project_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_buchhalter_or_admin),
) -> List[Invoice]:
    """Listet alle Rechnungen eines Projekts innerhalb des Tenants."""
    _ensure_project_access(session, current_user.tenant_id, project_id)
    statement = select(Invoice).where(
        Invoice.project_id == project_id,
        Invoice.tenant_id == current_user.tenant_id,
    )
    invoices = session.exec(statement.order_by(Invoice.created_at.desc())).all()
    for invoice in invoices:
        if invoice.items is None:
            invoice.items = "[]"
    return invoices


@router.post("/from-offer/{offer_id}", response_model=InvoiceSchema, status_code=status.HTTP_201_CREATED)
def create_invoice_from_offer(
    offer_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_buchhalter_or_admin),
) -> Invoice:
    """Erstellt eine Rechnung auf Basis eines bestehenden Angebots."""
    offer = _ensure_offer_access(session, current_user.tenant_id, offer_id)
    project = _ensure_project_access(session, current_user.tenant_id, offer.project_id)

    invoice_number = f"R-{datetime.utcnow():%Y%m%d}-{offer_id:04d}"
    due_date = datetime.utcnow() + timedelta(days=30)

    items = _normalize_items(json.loads(offer.items) if isinstance(offer.items, str) else offer.items or [])

    db_invoice = Invoice(
        tenant_id=current_user.tenant_id,
        project_id=project.id,
        offer_id=offer.id,
        invoice_number=invoice_number,
        title=f"Rechnung – {offer.title}",
        description=offer.description,
        client_name=offer.client_name,
        client_address=offer.client_address,
        total_amount=round(offer.total_amount, 2),
        currency=offer.currency,
        invoice_date=datetime.utcnow(),
        due_date=due_date,
        items=json.dumps([item.model_dump() for item in items]),
        status="entwurf",
    )

    session.add(db_invoice)
    offer.status = "abgerechnet"
    session.add(offer)
    session.commit()
    session.refresh(db_invoice)
    return db_invoice


def _collect_project_items(session: Session, tenant_id: int, project_id: int) -> tuple[List[dict], float]:
    items: List[dict] = []

    time_entries = session.exec(
        select(TimeEntry).where(
            TimeEntry.project_id == project_id,
            TimeEntry.tenant_id == tenant_id,
        )
    ).all()

    total_hours = sum(entry.hours_worked or 0 for entry in time_entries)
    total_personnel_cost = 0.0
    for entry in time_entries:
        hourly_rate = entry.hourly_rate
        if hourly_rate is None:
            employee = session.exec(
                select(Employee).where(Employee.id == entry.employee_id, Employee.tenant_id == tenant_id)
            ).first()
            hourly_rate = employee.hourly_rate if employee and employee.hourly_rate else 0
        total_personnel_cost += (entry.hours_worked or 0) * (hourly_rate or 0)

    if total_hours and total_personnel_cost:
        items.append(
            {
                "description": "Personalkosten",
                "quantity": round(total_hours, 2),
                "unit": "Std",
                "unit_price": round(total_personnel_cost / total_hours, 2),
                "total_price": round(total_personnel_cost, 2),
                "item_type": "labor",
            }
        )

    material_usages = session.exec(
        select(MaterialUsage).where(
            MaterialUsage.project_id == project_id,
            MaterialUsage.tenant_id == tenant_id,
        )
    ).all()

    material_total = 0.0
    for usage in material_usages:
        cost = usage.total_cost
        if cost is None and usage.unit_price is not None:
            cost = usage.unit_price * (usage.quantity or 0)
        if cost:
            items.append(
                {
                    "description": f"Material: {usage.material_name}",
                    "quantity": usage.quantity,
                    "unit": usage.unit,
                    "unit_price": usage.unit_price or 0,
                    "total_price": round(cost, 2),
                    "item_type": "material",
                }
            )
            material_total += cost

    total_amount = round(total_personnel_cost + material_total, 2)
    return items, total_amount


@router.post("/auto-generate/{project_id}", response_model=InvoiceSchema, status_code=status.HTTP_201_CREATED)
def auto_generate_invoice(
    project_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_buchhalter_or_admin),
) -> Invoice:
    """Erzeugt eine Entwurfsrechnung aus vorhandenen Projekt- und Zeitdaten."""
    project = _ensure_project_access(session, current_user.tenant_id, project_id)
    items, total_amount = _collect_project_items(session, current_user.tenant_id, project_id)
    if not items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Keine abrechenbaren Positionen gefunden")

    invoice_number = f"R-{datetime.utcnow():%Y%m%d}-{project_id:04d}"
    due_date = datetime.utcnow() + timedelta(days=30)

    db_invoice = Invoice(
        tenant_id=current_user.tenant_id,
        project_id=project.id,
        invoice_number=invoice_number,
        title=f"Rechnung – {project.name}",
        description=f"Automatisch generierte Rechnung für Projekt {project.name}",
        client_name=project.client_name or "Kunde",
        client_address=project.address,
        total_amount=total_amount,
        currency="EUR",
        invoice_date=datetime.utcnow(),
        due_date=due_date,
        items=json.dumps(items),
        status="entwurf",
    )

    session.add(db_invoice)
    session.commit()
    session.refresh(db_invoice)
    return db_invoice


@router.post("/generate", response_model=InvoiceCalculationResult)
def generate_invoice_calculation(
    request: InvoiceGenerationRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_buchhalter_or_admin),
) -> InvoiceCalculationResult:
    """Erstellt eine Rechnungskalkulation über den Service-Layer."""
    _ensure_project_access(session, current_user.tenant_id, request.project_id)
    generator = InvoiceGenerator(session)
    return generator.generate_invoice(request)


@router.post("/create-from-calculation", response_model=InvoiceSchema, status_code=status.HTTP_201_CREATED)
def create_invoice_from_calculation(
    project_id: int,
    calculation: InvoiceCalculationResult,
    invoice_number: str,
    client_name: str,
    client_address: str | None = None,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_buchhalter_or_admin),
) -> Invoice:
    """Persistiert eine kalkulierte Rechnung."""
    project = _ensure_project_access(session, current_user.tenant_id, project_id)
    generator = InvoiceGenerator(session)
    invoice = generator.create_invoice_from_calculation(
        project_id,
        calculation,
        invoice_number,
        client_name,
        client_address,
    )
    invoice.tenant_id = current_user.tenant_id
    invoice.project_id = project.id
    session.add(invoice)
    session.commit()
    session.refresh(invoice)
    return invoice


@router.get("/total-revenue")
def get_total_revenue(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_buchhalter_or_admin),
) -> dict:
    """Aggregiert den Umsatz bezahlter Rechnungen für den aktuellen Tenant."""
    paid_invoices = session.exec(
        select(Invoice).where(
            Invoice.tenant_id == current_user.tenant_id,
            Invoice.status == "bezahlt",
        )
    ).all()

    total_revenue = sum(invoice.total_amount for invoice in paid_invoices)
    return {
        "total_revenue": round(total_revenue, 2),
        "invoice_count": len(paid_invoices),
        "currency": "EUR",
    }
