"""Router für Firmenlogo-Verwaltung."""

import os
import shutil
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from ..auth import require_admin, get_current_user
from ..database import get_session
from ..models import CompanyLogo, User
from ..schemas import CompanyLogo as CompanyLogoSchema

UPLOAD_DIR = os.path.join("uploads", "logos")
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(
    prefix="/company-logo",
    tags=["company-logo"],
    dependencies=[Depends(get_current_user)],
)


def _tenant_id(user: User) -> int:
    return getattr(user, "tenant_id", None) or 1


def _tenant_logo_query(session: Session, tenant_id: int):
    return select(CompanyLogo).where(CompanyLogo.tenant_id == tenant_id)


def _save_upload_file(destination: str, upload_file: UploadFile) -> None:
    with open(destination, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)


@router.get("/current", response_model=CompanyLogoSchema)
async def get_current_logo(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    tenant_id = _tenant_id(current_user)
    logo = session.exec(
        _tenant_logo_query(session, tenant_id).where(CompanyLogo.is_active == True)  # noqa: E712
    ).first()
    if not logo:
        raise HTTPException(status_code=404, detail="Kein Logo vorhanden")
    return logo


@router.get("/history", response_model=List[CompanyLogoSchema])
async def get_logo_history(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin)
):
    tenant_id = _tenant_id(current_user)
    history = session.exec(
        _tenant_logo_query(session, tenant_id).order_by(CompanyLogo.created_at.desc())
    ).all()
    return history


@router.post("/upload", response_model=CompanyLogoSchema)
async def upload_logo(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin)
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Nur Bilddateien sind erlaubt")

    tenant_id = _tenant_id(current_user)
    extension = os.path.splitext(file.filename or "")[1].lower()
    if extension not in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}:
        raise HTTPException(status_code=400, detail="Unterstützte Formate: PNG, JPG, JPEG, WEBP, GIF, SVG")

    tenant_dir = os.path.join(UPLOAD_DIR, f"tenant_{tenant_id}")
    os.makedirs(tenant_dir, exist_ok=True)

    unique_name = f"{uuid.uuid4().hex}{extension}"
    file_path = os.path.join(tenant_dir, unique_name)

    try:
        _save_upload_file(file_path, file)
    except Exception as exc:  # pragma: no cover - Dateisystemfehler
        raise HTTPException(status_code=500, detail=f"Logo konnte nicht gespeichert werden: {exc}")
    finally:
        file.file.close()

    # Bisheriges aktives Logo deaktivieren
    existing_active = session.exec(
        _tenant_logo_query(session, tenant_id).where(CompanyLogo.is_active == True)  # noqa: E712
    ).all()
    for entry in existing_active:
        entry.is_active = False
        session.add(entry)

    new_logo = CompanyLogo(
        tenant_id=tenant_id,
        user_id=current_user.id,
        filename=unique_name,
        original_filename=file.filename or unique_name,
        file_path=file_path,
        file_size=os.path.getsize(file_path),
        is_active=True,
    )
    session.add(new_logo)
    session.commit()
    session.refresh(new_logo)
    return new_logo


@router.delete("/current")
async def delete_current_logo(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin)
):
    tenant_id = _tenant_id(current_user)
    logo = session.exec(
        _tenant_logo_query(session, tenant_id).where(CompanyLogo.is_active == True)  # noqa: E712
    ).first()
    if not logo:
        raise HTTPException(status_code=404, detail="Kein aktives Logo zum Löschen gefunden")

    logo.is_active = False
    session.add(logo)
    session.commit()
    return {"detail": "Logo deaktiviert"}


@router.delete("/{logo_id}")
async def delete_logo(
    logo_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin)
):
    tenant_id = _tenant_id(current_user)
    logo = session.get(CompanyLogo, logo_id)
    if not logo or logo.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Logo nicht gefunden")

    if logo.is_active:
        raise HTTPException(status_code=400, detail="Aktives Logo kann nicht gelöscht werden. Bitte zuerst ein anderes Logo aktivieren.")

    if logo.file_path and os.path.exists(logo.file_path):
        try:
            os.remove(logo.file_path)
        except OSError as exc:  # pragma: no cover - Dateisystemfehler
            raise HTTPException(status_code=500, detail=f"Datei konnte nicht gelöscht werden: {exc}")

    session.delete(logo)
    session.commit()
    return {"detail": "Logo gelöscht"}


@router.get("/view")
async def view_logo(
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
    logo_id: Optional[int] = None
):
    query = select(CompanyLogo).where(CompanyLogo.is_active == True)  # noqa: E712
    if logo_id is not None:
        query = select(CompanyLogo).where(CompanyLogo.id == logo_id)
    logo = session.exec(query.order_by(CompanyLogo.created_at.desc())).first()
    if not logo or not os.path.exists(logo.file_path):
        raise HTTPException(status_code=404, detail="Logo nicht gefunden")

    media_type = "image/png"
    if logo.original_filename.lower().endswith(".jpg") or logo.original_filename.lower().endswith(".jpeg"):
        media_type = "image/jpeg"
    elif logo.original_filename.lower().endswith(".webp"):
        media_type = "image/webp"
    elif logo.original_filename.lower().endswith(".gif"):
        media_type = "image/gif"
    elif logo.original_filename.lower().endswith(".svg"):
        media_type = "image/svg+xml"

    return FileResponse(path=logo.file_path, media_type=media_type, filename=logo.original_filename)
