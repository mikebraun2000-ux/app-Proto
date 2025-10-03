import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

sys.path.append(str(Path(__file__).resolve().parents[2]))
os.environ.setdefault("SECRET_KEY", "test-secret")

from app.models import Tenant, Project, Offer, Invoice, ProjectImage  # noqa: E402
from app.routers.projects import create_project, get_projects, get_project  # noqa: E402
from app.routers.offers import create_offer  # noqa: E402
from app.routers.invoices import create_invoice, get_invoices  # noqa: E402
from app.routers.project_images import get_project_images  # noqa: E402
from app.schemas import ProjectCreate, OfferCreate, InvoiceCreate, InvoiceItem  # noqa: E402
from fastapi import HTTPException  # noqa: E402


@pytest.fixture()
def session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture()
def tenants(session):
    first = Tenant(id=1, name="Tenant A")
    second = Tenant(id=2, name="Tenant B")
    session.add(first)
    session.add(second)
    session.commit()
    return first, second


def make_user(tenant_id: int, role: str = "admin") -> SimpleNamespace:
    return SimpleNamespace(
        id=tenant_id * 10,
        tenant_id=tenant_id,
        role=role,
        username=f"user_{tenant_id}",
        full_name=f"User {tenant_id}",
    )


def test_create_project_assigns_current_tenant(session, tenants):
    tenant_a, _ = tenants
    project_input = ProjectCreate(name="Scoped Project")
    user = make_user(tenant_a.id)

    project = create_project(project_input, session=session, current_user=user)

    assert project.tenant_id == tenant_a.id


def test_get_projects_filters_to_current_tenant(session, tenants):
    tenant_a, tenant_b = tenants
    user_a = make_user(tenant_a.id)
    user_b = make_user(tenant_b.id)

    session.add(Project(name="A", tenant_id=tenant_a.id))
    session.add(Project(name="B", tenant_id=tenant_b.id))
    session.commit()

    projects_a = get_projects(session=session, current_user=user_a)
    projects_b = get_projects(session=session, current_user=user_b)

    assert {project["name"] for project in projects_a} == {"A"}
    assert {project["name"] for project in projects_b} == {"B"}


def test_get_project_raises_for_foreign_tenant(session, tenants):
    tenant_a, tenant_b = tenants
    user_a = make_user(tenant_a.id)
    user_b = make_user(tenant_b.id)

    project = Project(name="Shared", tenant_id=tenant_a.id)
    session.add(project)
    session.commit()

    fetched = get_project(project_id=project.id, session=session, current_user=user_a)
    assert fetched.id == project.id

    with pytest.raises(HTTPException):
        get_project(project_id=project.id, session=session, current_user=user_b)


def test_create_offer_respects_project_tenant(session, tenants):
    tenant_a, tenant_b = tenants
    user_a = make_user(tenant_a.id)
    user_b = make_user(tenant_b.id)

    project_a = Project(name="Project A", tenant_id=tenant_a.id)
    foreign_project = Project(name="Foreign", tenant_id=tenant_b.id)
    session.add(project_a)
    session.add(foreign_project)
    session.commit()

    offer_payload = OfferCreate(
        project_id=project_a.id,
        title="Offer",
        description="",
        client_name="Client",
        client_address="",
        total_amount=1000.0,
        currency="EUR",
        valid_until=None,
        items=[],
        status="entwurf",
        auto_generated=False,
    )

    offer = create_offer(offer_payload, session=session, current_user=user_a)
    assert offer.tenant_id == tenant_a.id

    foreign_payload = offer_payload.model_copy(update={"project_id": foreign_project.id})
    with pytest.raises(HTTPException):
        create_offer(foreign_payload, session=session, current_user=user_a)
    with pytest.raises(HTTPException):
        create_offer(offer_payload, session=session, current_user=user_b)

    stored_offer = session.get(Offer, offer.id)
    assert stored_offer.tenant_id == tenant_a.id


def test_invoice_creation_and_listing_respects_tenant(session, tenants):
    tenant_a, tenant_b = tenants
    user_a = make_user(tenant_a.id)
    user_b = make_user(tenant_b.id)

    project_a = Project(name="Project A", tenant_id=tenant_a.id)
    project_b = Project(name="Project B", tenant_id=tenant_b.id)
    session.add(project_a)
    session.add(project_b)
    session.commit()

    invoice_payload = InvoiceCreate(
        project_id=project_a.id,
        offer_id=None,
        invoice_number="INV-A",
        title="Invoice A",
        description=None,
        client_name="Client A",
        client_address=None,
        total_amount=100.0,
        currency="EUR",
        invoice_date=None,
        due_date=None,
        items=[InvoiceItem(description="Service", quantity=1, unit_price=100.0, total_price=100.0)],
        status="entwurf",
    )

    invoice = create_invoice(invoice_payload, session=session, current_user=user_a)
    assert invoice.tenant_id == tenant_a.id

    foreign_invoice = Invoice(
        project_id=project_b.id,
        tenant_id=tenant_b.id,
        invoice_number="INV-B",
        title="Invoice B",
        client_name="Client B",
        client_address=None,
        total_amount=200.0,
        currency="EUR",
        items="[]",
        status="entwurf",
    )
    session.add(foreign_invoice)
    session.commit()

    invoices_a = get_invoices(session=session, current_user=user_a)
    invoices_b = get_invoices(session=session, current_user=user_b)

    assert {inv.invoice_number for inv in invoices_a} == {"INV-A"}
    assert {inv.invoice_number for inv in invoices_b} == {"INV-B"}


def test_project_images_listing_filtered_by_tenant(session, tenants):
    tenant_a, tenant_b = tenants
    user_a = make_user(tenant_a.id)
    user_b = make_user(tenant_b.id)

    project_a = Project(name="Project A", tenant_id=tenant_a.id)
    project_b = Project(name="Project B", tenant_id=tenant_b.id)
    session.add(project_a)
    session.add(project_b)
    session.commit()

    image_a = ProjectImage(
        project_id=project_a.id,
        tenant_id=tenant_a.id,
        filename="a.jpg",
        original_filename="a.jpg",
        file_path="/tmp/a.jpg",
    )
    image_b = ProjectImage(
        project_id=project_b.id,
        tenant_id=tenant_b.id,
        filename="b.jpg",
        original_filename="b.jpg",
        file_path="/tmp/b.jpg",
    )
    session.add(image_a)
    session.add(image_b)
    session.commit()

    images_a = get_project_images(session=session, current_user=user_a)
    images_b = get_project_images(session=session, current_user=user_b)

    assert [img.filename for img in images_a] == ["a.jpg"]
    assert [img.filename for img in images_b] == ["b.jpg"]
