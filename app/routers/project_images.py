"""Router für Projektbilder mit Tenant-Scoping."""

from __future__ import annotations

import os
import uuid
from io import BytesIO
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from PIL import Image
from sqlmodel import Session, select

from ..auth import get_current_user
from ..database import get_session
from ..models import Project, ProjectImage
from ..schemas import ProjectImage as ProjectImageSchema
from ..utils.tenant_scoping import add_tenant_filter, ensure_tenant_access, set_tenant_on_model

router = APIRouter(prefix="/project-images", tags=["project-images"])

# Upload-Verzeichnis für Projektbilder
UPLOAD_DIR = "uploads/project_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _ensure_project(session: Session, project_id: int, tenant_id: int) -> Project:
    project = session.get(Project, project_id)
    return ensure_tenant_access(project, tenant_id, not_found_detail="Projekt nicht gefunden")


def _ensure_image(session: Session, image_id: int, tenant_id: int) -> ProjectImage:
    image = session.get(ProjectImage, image_id)
    return ensure_tenant_access(image, tenant_id, not_found_detail="Bild nicht gefunden")


@router.get("/", response_model=List[ProjectImageSchema])
def get_project_images(
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """Alle Projektbilder des aktuellen Mandanten abrufen."""
    statement = add_tenant_filter(select(ProjectImage), ProjectImage, current_user.tenant_id)
    return session.exec(statement).all()


@router.post("/", response_model=ProjectImageSchema)
def create_project_image(
    project_id: int,
    description: Optional[str] = None,
    image_type: str = "progress",
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """Neues Projektbild für den Tenant hochladen."""
    _ensure_project(session, project_id, current_user.tenant_id)

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Nur Bilddateien sind erlaubt")

    content = file.file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Datei ist zu groß (max 10MB)")

    file_extension = os.path.splitext(file.filename or "")[1] or ".jpg"
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        image = Image.open(BytesIO(content))
        image.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        image.save(file_path, "JPEG", quality=85, optimize=True)
    except Exception as exc:  # pragma: no cover - Bildverarbeitung
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Fehler beim Speichern der Datei: {exc}")

    db_image = ProjectImage(
        project_id=project_id,
        filename=unique_filename,
        original_filename=file.filename or "unknown",
        file_path=file_path,
        file_size=os.path.getsize(file_path),
        description=description,
        image_type=image_type,
    )
    set_tenant_on_model(db_image, current_user.tenant_id)

    session.add(db_image)
    session.commit()
    session.refresh(db_image)
    return db_image


@router.get("/{image_id}", response_model=ProjectImageSchema)
def get_project_image(
    image_id: int,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """Einzelnes Projektbild abrufen."""
    return _ensure_image(session, image_id, current_user.tenant_id)


@router.delete("/{image_id}")
def delete_project_image(
    image_id: int,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """Projektbild löschen."""
    image = _ensure_image(session, image_id, current_user.tenant_id)

    if image.file_path and os.path.exists(image.file_path):
        try:
            os.remove(image.file_path)
        except OSError as exc:  # pragma: no cover - Dateisystemfehler
            raise HTTPException(status_code=500, detail=f"Fehler beim Löschen der Datei: {exc}")

    session.delete(image)
    session.commit()
    return {"message": "Bild erfolgreich gelöscht"}


@router.get("/project/{project_id}", response_model=List[ProjectImageSchema])
def get_images_by_project(
    project_id: int,
    session: Session = Depends(get_session),
    current_user=Depends(get_current_user),
):
    """Alle Bilder eines Projekts abrufen."""
    _ensure_project(session, project_id, current_user.tenant_id)
    statement = add_tenant_filter(
        select(ProjectImage).where(ProjectImage.project_id == project_id),
        ProjectImage,
        current_user.tenant_id,
    )
    return session.exec(statement).all()
