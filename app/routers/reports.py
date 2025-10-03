"""Mandantenfähiger Router für Bauberichte und deren Anhänge."""

from __future__ import annotations

import os
import uuid
from datetime import datetime
from io import BytesIO
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from PIL import Image
from sqlmodel import Session, delete, select

from ..auth import get_current_user, require_buchhalter_or_admin, require_employee_or_admin
from ..database import get_session
from ..models import Project, Report, ReportImage, User
from ..schemas import Report as ReportSchema
from ..schemas import ReportCreate, ReportImage as ReportImageSchema, ReportUpdate

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    dependencies=[Depends(get_current_user)],
)

UPLOAD_DIR = "uploads/images"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _ensure_project_access(session: Session, tenant_id: int, project_id: int) -> Project:
    statement = select(Project).where(Project.id == project_id, Project.tenant_id == tenant_id)
    project = session.exec(statement).first()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projekt nicht gefunden")
    return project


def _get_report_for_tenant(session: Session, tenant_id: int, report_id: int) -> Report:
    statement = select(Report).where(Report.id == report_id, Report.tenant_id == tenant_id)
    report = session.exec(statement).first()
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bericht nicht gefunden")
    return report


def _list_report_attachments(session: Session, tenant_id: int, report_id: int) -> List[ReportImageSchema]:
    statement = select(ReportImage).where(
        ReportImage.report_id == report_id,
        ReportImage.tenant_id == tenant_id,
    )
    images = session.exec(statement.order_by(ReportImage.created_at.desc())).all()
    return [
        ReportImageSchema(
            id=image.id,
            report_id=image.report_id,
            filename=image.filename,
            original_filename=image.original_filename,
            file_path=image.file_path,
            file_size=image.file_size,
            description=image.description,
            image_type=image.image_type,
            created_at=image.created_at,
        )
        for image in images
    ]


@router.get("/", response_model=List[ReportSchema])
def list_reports(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_employee_or_admin),
) -> List[ReportSchema]:
    """Listet alle Berichte des aktuellen Mandanten inklusive Anhängen."""
    statement = select(Report).where(Report.tenant_id == current_user.tenant_id)
    reports = session.exec(statement.order_by(Report.report_date.desc(), Report.id.desc())).all()

    result: List[ReportSchema] = []
    for report in reports:
        attachments = _list_report_attachments(session, current_user.tenant_id, report.id)
        result.append(
            {
                "id": report.id,
                "project_id": report.project_id,
                "title": report.title,
                "content": report.content,
                "report_date": report.report_date,
                "work_type": report.work_type,
                "status": report.status,
                "area_completed": report.area_completed,
                "materials_used": report.materials_used,
                "quality_check": report.quality_check,
                "issues_encountered": report.issues_encountered,
                "next_steps": report.next_steps,
                "progress_percentage": report.progress_percentage,
                "attachments": [image.model_dump() for image in attachments],
                "created_at": report.created_at,
                "updated_at": report.updated_at,
            }
        )
    return result


@router.post("/", response_model=ReportSchema, status_code=status.HTTP_201_CREATED)
def create_report(
    report: ReportCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_employee_or_admin),
) -> ReportSchema:
    """Erstellt einen neuen Bericht für ein Projekt des Mandanten."""
    project = _ensure_project_access(session, current_user.tenant_id, report.project_id)

    report_date: datetime | None = None
    if report.report_date:
        try:
            report_date = datetime.fromisoformat(report.report_date)
        except ValueError:
            report_date = datetime.fromisoformat(f"{report.report_date}T00:00:00")

    db_report = Report(
        tenant_id=current_user.tenant_id,
        project_id=project.id,
        title=report.title,
        content=report.content,
        report_date=report_date,
        work_type=report.work_type,
        status=report.status,
        area_completed=report.area_completed,
        materials_used=report.materials_used,
        quality_check=report.quality_check,
        issues_encountered=report.issues_encountered,
        next_steps=report.next_steps,
        progress_percentage=report.progress_percentage,
    )

    session.add(db_report)
    session.commit()
    session.refresh(db_report)

    return ReportSchema.from_orm(db_report)


@router.get("/{report_id}", response_model=ReportSchema)
def get_report(
    report_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_employee_or_admin),
) -> ReportSchema:
    """Gibt einen einzelnen Bericht inklusive Anhängen zurück."""
    report = _get_report_for_tenant(session, current_user.tenant_id, report_id)
    attachments = _list_report_attachments(session, current_user.tenant_id, report.id)
    return {
        "id": report.id,
        "project_id": report.project_id,
        "title": report.title,
        "content": report.content,
        "report_date": report.report_date,
        "work_type": report.work_type,
        "status": report.status,
        "area_completed": report.area_completed,
        "materials_used": report.materials_used,
        "quality_check": report.quality_check,
        "issues_encountered": report.issues_encountered,
        "next_steps": report.next_steps,
        "progress_percentage": report.progress_percentage,
        "attachments": [image.model_dump() for image in attachments],
        "created_at": report.created_at,
        "updated_at": report.updated_at,
    }


@router.put("/{report_id}", response_model=ReportSchema)
def update_report(
    report_id: int,
    report_update: ReportUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_employee_or_admin),
) -> ReportSchema:
    """Aktualisiert einen bestehenden Bericht des Mandanten."""
    report = _get_report_for_tenant(session, current_user.tenant_id, report_id)
    update_data = report_update.model_dump(exclude_unset=True)
    if "report_date" in update_data and update_data["report_date"]:
        value = update_data["report_date"]
        try:
            update_data["report_date"] = datetime.fromisoformat(value)
        except ValueError:
            update_data["report_date"] = datetime.fromisoformat(f"{value}T00:00:00")

    for field_name, value in update_data.items():
        setattr(report, field_name, value)

    session.add(report)
    session.commit()
    session.refresh(report)

    attachments = _list_report_attachments(session, current_user.tenant_id, report.id)
    return {
        "id": report.id,
        "project_id": report.project_id,
        "title": report.title,
        "content": report.content,
        "report_date": report.report_date,
        "work_type": report.work_type,
        "status": report.status,
        "area_completed": report.area_completed,
        "materials_used": report.materials_used,
        "quality_check": report.quality_check,
        "issues_encountered": report.issues_encountered,
        "next_steps": report.next_steps,
        "progress_percentage": report.progress_percentage,
        "attachments": [image.model_dump() for image in attachments],
        "created_at": report.created_at,
        "updated_at": report.updated_at,
    }


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(
    report_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_buchhalter_or_admin),
) -> None:
    """Löscht einen Bericht und alle verknüpften Anhänge."""
    report = _get_report_for_tenant(session, current_user.tenant_id, report_id)
    attachments = _list_report_attachments(session, current_user.tenant_id, report.id)
    for attachment in attachments:
        if attachment.file_path and os.path.exists(attachment.file_path):
            try:
                os.remove(attachment.file_path)
            except OSError:
                pass
        session.exec(delete(ReportImage).where(ReportImage.id == attachment.id))
    session.delete(report)
    session.commit()


@router.post("/{report_id}/images", response_model=ReportImageSchema, status_code=status.HTTP_201_CREATED)
def upload_report_image(
    report_id: int,
    file: UploadFile = File(...),
    description: str | None = None,
    image_type: str = "progress",
    session: Session = Depends(get_session),
    current_user: User = Depends(require_employee_or_admin),
) -> ReportImage:
    """Hängt einem Bericht ein Bild an."""
    report = _get_report_for_tenant(session, current_user.tenant_id, report_id)

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nur Bilddateien sind erlaubt")

    content = file.file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Datei ist zu groß (max 10MB)")

    buffer = BytesIO(content)
    filename = f"{uuid.uuid4()}.jpg"
    file_path = os.path.join(UPLOAD_DIR, filename)

    try:
        image = Image.open(buffer)
        image.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        image.save(file_path, "JPEG", quality=85, optimize=True)
    except Exception as exc:  # pragma: no cover
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ungültiges Bild: {exc}")

    report_image = ReportImage(
        tenant_id=current_user.tenant_id,
        report_id=report.id,
        filename=filename,
        original_filename=file.filename or filename,
        file_path=file_path,
        file_size=os.path.getsize(file_path),
        description=description,
        image_type=image_type,
    )

    session.add(report_image)
    session.commit()
    session.refresh(report_image)
    return report_image


@router.get("/project/{project_id}", response_model=List[ReportSchema])
def list_reports_for_project(
    project_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_employee_or_admin),
) -> List[ReportSchema]:
    """Listet alle Berichte eines Projekts."""
    _ensure_project_access(session, current_user.tenant_id, project_id)
    statement = select(Report).where(
        Report.project_id == project_id,
        Report.tenant_id == current_user.tenant_id,
    )
    reports = session.exec(statement.order_by(Report.report_date.desc(), Report.id.desc())).all()
    return [
        ReportSchema.from_orm(report)
        for report in reports
    ]
