"""
Router für Projektbilder.
Bietet Upload und Management von Projektbildern.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select
from typing import List
import os
import uuid
from PIL import Image
from ..database import get_session
from ..models import ProjectImage, Project, User
from ..schemas import ProjectImageCreate, ProjectImage as ProjectImageSchema
from ..auth import get_current_user, require_employee_or_admin, require_admin

router = APIRouter(
    prefix="/project-images",
    tags=["project-images"],
    dependencies=[Depends(get_current_user)],
)

# Upload-Verzeichnis für Projektbilder
UPLOAD_DIR = "uploads/project_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/", response_model=List[ProjectImageSchema])
def get_project_images(
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
):
    """
    Alle Projektbilder abrufen.
    
    Returns:
        List[ProjectImageSchema]: Liste aller Projektbilder
    """
    statement = select(ProjectImage)
    images = session.exec(statement).all()
    return images

@router.post("/", response_model=ProjectImageSchema)
def create_project_image(
    project_id: int,
    description: str = None,
    image_type: str = "progress",
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    _: User = Depends(require_employee_or_admin),
):
    """
    Neues Projektbild hochladen.
    
    Args:
        project_id: Projekt-ID
        description: Bildbeschreibung
        image_type: Bildtyp (progress, before, after, issue)
        file: Hochgeladene Bilddatei
        session: Datenbank-Session
        
    Returns:
        ProjectImageSchema: Erstelltes Projektbild
        
    Raises:
        HTTPException: Wenn Projekt nicht gefunden wird oder Datei ungültig ist
    """
    # Prüfen ob das Projekt existiert
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
    
    # Dateityp prüfen
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Nur Bilddateien sind erlaubt")
    
    # Dateigröße prüfen (max 10MB)
    content = file.file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Datei ist zu groß (max 10MB)")
    
    # Eindeutigen Dateinamen generieren
    file_extension = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    try:
        # Bild komprimieren und speichern
        image = Image.open(file.file)
        
        # Bild auf maximal 1920x1080 verkleinern
        image.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
        
        # Als JPEG speichern (bessere Komprimierung)
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
        
        image.save(file_path, "JPEG", quality=85, optimize=True)
        
        # Bilddatenbankeintrag erstellen
        db_image = ProjectImage(
            project_id=project_id,
            filename=unique_filename,
            original_filename=file.filename or "unknown",
            file_path=file_path,
            file_size=os.path.getsize(file_path),
            description=description,
            image_type=image_type
        )
        
        session.add(db_image)
        session.commit()
        session.refresh(db_image)
        
        return db_image
    
    except Exception as e:
        # Datei löschen falls Fehler auftritt
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Fehler beim Speichern der Datei: {str(e)}")

@router.get("/{image_id}", response_model=ProjectImageSchema)
def get_project_image(
    image_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
):
    """
    Einzelnes Projektbild anhand der ID abrufen.
    
    Args:
        image_id: Bild-ID
        session: Datenbank-Session
        
    Returns:
        ProjectImageSchema: Bild-Daten
        
    Raises:
        HTTPException: Wenn Bild nicht gefunden wird
    """
    image = session.get(ProjectImage, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Bild nicht gefunden")
    return image

@router.delete("/{image_id}")
def delete_project_image(
    image_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(require_admin),
):
    """
    Projektbild löschen.
    
    Args:
        image_id: Bild-ID
        session: Datenbank-Session
        
    Returns:
        dict: Erfolgsmeldung
        
    Raises:
        HTTPException: Wenn Bild nicht gefunden wird
    """
    image = session.get(ProjectImage, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Bild nicht gefunden")
    
    # Datei vom Server löschen
    if os.path.exists(image.file_path):
        try:
            os.remove(image.file_path)
        except Exception as e:
            print(f"Fehler beim Löschen der Datei: {e}")
    
    session.delete(image)
    session.commit()
    return {"message": "Bild erfolgreich gelöscht"}

@router.get("/project/{project_id}", response_model=List[ProjectImageSchema])
def get_images_by_project(
    project_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
):
    """
    Alle Bilder eines Projekts abrufen.
    
    Args:
        project_id: Projekt-ID
        session: Datenbank-Session
        
    Returns:
        List[ProjectImageSchema]: Liste der Bilder des Projekts
        
    Raises:
        HTTPException: Wenn Projekt nicht gefunden wird
    """
    # Prüfen ob das Projekt existiert
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
    
    statement = select(ProjectImage).where(ProjectImage.project_id == project_id)
    images = session.exec(statement).all()
    return images

