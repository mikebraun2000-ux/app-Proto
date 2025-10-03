"""FastAPI-Router für mandantenfähiges Projekt-Management."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, delete, select

from ..auth import get_current_user, require_buchhalter_or_admin
from ..database import get_session
from ..models import Invoice, Offer, Project, ProjectImage, Report, TimeEntry, User
from ..schemas import Project as ProjectSchema
from ..schemas import ProjectCreate, ProjectUpdate

router = APIRouter(
    prefix="/projects",
    tags=["projects"],
    dependencies=[Depends(get_current_user)],
)


def _get_project_for_tenant(
    session: Session, tenant_id: int, project_id: int
) -> Project:
    """Hilfsfunktion, die ein Projekt für den aktuellen Mandanten lädt."""
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


@router.get("/", response_model=List[ProjectSchema])
def list_projects(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> List[Project]:
    """Gibt alle Projekte des aktuellen Tenants zurück."""
    statement = select(Project).where(Project.tenant_id == current_user.tenant_id)
    return session.exec(statement).all()


@router.post("/", response_model=ProjectSchema, status_code=status.HTTP_201_CREATED)
def create_project(
    project: ProjectCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_buchhalter_or_admin),
) -> Project:
    """Erstellt ein neues Projekt und verknüpft es mit dem aktuellen Tenant."""
    db_project = Project.model_validate(project, update={"tenant_id": current_user.tenant_id})
    session.add(db_project)
    session.commit()
    session.refresh(db_project)
    return db_project


@router.get("/{project_id}", response_model=ProjectSchema)
def get_project(
    project_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Project:
    """Liefert die Daten eines Projekts aus dem aktuellen Tenant."""
    return _get_project_for_tenant(session, current_user.tenant_id, project_id)


@router.put("/{project_id}", response_model=ProjectSchema)
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_buchhalter_or_admin),
) -> Project:
    """Aktualisiert ein Projekt des aktuellen Mandanten."""
    project = _get_project_for_tenant(session, current_user.tenant_id, project_id)
    update_data = project_update.model_dump(exclude_unset=True)
    for field_name, value in update_data.items():
        setattr(project, field_name, value)

    session.add(project)
    session.commit()
    session.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_buchhalter_or_admin),
) -> None:
    """Löscht ein Projekt inklusive aller verknüpften Datensätze des Tenants."""
    tenant_id = current_user.tenant_id
    project = _get_project_for_tenant(session, tenant_id, project_id)

    report_ids = [
        report.id
        for report in session.exec(
            select(Report).where(Report.project_id == project_id, Report.tenant_id == tenant_id)
        ).all()
    ]

    image_ids = [
        image.id
        for image in session.exec(
            select(ProjectImage).where(
                ProjectImage.project_id == project_id,
                ProjectImage.tenant_id == tenant_id,
            )
        ).all()
    ]

    time_entry_ids = [
        entry.id
        for entry in session.exec(
            select(TimeEntry).where(
                TimeEntry.project_id == project_id,
                TimeEntry.tenant_id == tenant_id,
            )
        ).all()
    ]

    offer_ids = [
        offer.id
        for offer in session.exec(
            select(Offer).where(Offer.project_id == project_id, Offer.tenant_id == tenant_id)
        ).all()
    ]

    invoice_ids = [
        invoice.id
        for invoice in session.exec(
            select(Invoice).where(
                Invoice.project_id == project_id,
                Invoice.tenant_id == tenant_id,
            )
        ).all()
    ]

    # Dateien der Projektbilder entfernen
    for image in session.exec(
        select(ProjectImage).where(ProjectImage.id.in_(image_ids))
    ):
        if image.file_path:
            try:
                import os

                if os.path.exists(image.file_path):
                    os.remove(image.file_path)
            except OSError:
                pass

    # Datensätze löschen – Reihenfolge beachten wegen FK-Constraints
    for model, ids in (
        (ProjectImage, image_ids),
        (Report, report_ids),
        (TimeEntry, time_entry_ids),
        (Offer, offer_ids),
        (Invoice, invoice_ids),
    ):
        if ids:
            session.exec(delete(model).where(model.id.in_(ids)))

    session.delete(project)
    session.commit()
