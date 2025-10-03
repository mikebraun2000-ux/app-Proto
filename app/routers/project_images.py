"""Mandantenfähiger Router für Projektbilder."""

from __future__ import annotations

import os
import uuid
from io import BytesIO
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from PIL import Image
from sqlmodel import Session, select

from ..auth import get_current_user, require_employee_or_admin
from ..database import get_session
from ..models import Project, ProjectImage, User
from ..schemas import ProjectImage as ProjectImageSchema

router = APIRouter(
    prefix="/project-images",
    tags=["project-images"],
    dependencies=[Depends(get_current_user)],
)

UPLOAD_DIR = "uploads/project_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _ensure_project_access(session: Session, tenant_id: int, project_id: int) -> Project:
    statement = select(Project).where(Project.id == project_id, Project.tenant_id == tenant_id)
    project = session.exec(statement).first()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projekt nicht gefunden")
    return project


def _get_image_for_tenant(session: Session, tenant_id: int, image_id: int) -> ProjectImage:
    statement = select(ProjectImage).where(
        ProjectImage.id == image_id,
        ProjectImage.tenant_id == tenant_id,
    )
    image = session.exec(statement).first()
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bild nicht gefunden")
    return image


@router.get("/", response_model=List[ProjectImageSchema])
def list_project_images(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_employee_or_admin),
) -> List[ProjectImage]:
    """Listet alle Projektbilder des aktuellen Tenants."""
    statement = select(ProjectImage).where(ProjectImage.tenant_id == current_user.tenant_id)
    return session.exec(statement.order_by(ProjectImage.created_at.desc())).all()


@router.post("/", response_model=ProjectImageSchema, status_code=status.HTTP_201_CREATED)
def upload_project_image(
    project_id: int,
    description: str | None = None,
    image_type: str = "progress",
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(require_employee_or_admin),
) -> ProjectImage:
    """Lädt ein Projektbild hoch und speichert es mandantensicher."""
    _ensure_project_access(session, current_user.tenant_id, project_id)

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nur Bilddateien sind erlaubt")

    content = file.file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Datei ist zu groß (max 10MB)")

    buffer = BytesIO(content)
    unique_filename = f"{uuid.uuid4()}.jpg"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        image = Image.open(buffer)
        image.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        image.save(file_path, "JPEG", quality=85, optimize=True)
    except Exception as exc:  # pragma: no cover - Fehlerpfad
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ungültiges Bild: {exc}")

    db_image = ProjectImage(
        tenant_id=current_user.tenant_id,
        project_id=project_id,
        filename=unique_filename,
        original_filename=file.filename or unique_filename,
        file_path=file_path,
        file_size=os.path.getsize(file_path),
        description=description,
        image_type=image_type,
    )

    session.add(db_image)
    session.commit()
    session.refresh(db_image)
    return db_image


@router.get("/{image_id}", response_model=ProjectImageSchema)
def get_project_image(
    image_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_employee_or_admin),
) -> ProjectImage:
    """Gibt die Metadaten eines Projektbilds zurück."""
    return _get_image_for_tenant(session, current_user.tenant_id, image_id)


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project_image(
    image_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_employee_or_admin),
) -> None:
    """Löscht ein Projektbild inklusive Datei."""
    image = _get_image_for_tenant(session, current_user.tenant_id, image_id)
    if image.file_path and os.path.exists(image.file_path):
        try:
            os.remove(image.file_path)
        except OSError:
            pass
    session.delete(image)
    session.commit()


@router.get("/project/{project_id}", response_model=List[ProjectImageSchema])
def list_images_for_project(
    project_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_employee_or_admin),
) -> List[ProjectImage]:
    """Listet alle Bilder eines bestimmten Projekts des Tenants."""
    _ensure_project_access(session, current_user.tenant_id, project_id)
    statement = select(ProjectImage).where(
        ProjectImage.project_id == project_id,
        ProjectImage.tenant_id == current_user.tenant_id,
    )
    return session.exec(statement.order_by(ProjectImage.created_at.desc())).all()
