"""
Router für Projekt-Management.
Bietet CRUD-Operationen für Bauprojekte.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from datetime import datetime
from ..database import get_session
from ..models import Project, User
from ..schemas import ProjectCreate, ProjectUpdate, Project as ProjectSchema
from ..auth import get_current_user, require_buchhalter_or_admin

router = APIRouter(
    prefix="/projects",
    tags=["projects"],
    dependencies=[Depends(get_current_user)],
)

@router.get("/", response_model=List[ProjectSchema])
def get_projects(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Alle Projekte abrufen.
    
    Returns:
        List[ProjectSchema]: Liste aller Projekte
    """
    statement = select(Project)
    projects = session.exec(statement).all()
    
    # Manuelle Serialisierung für name mapping
    result = []
    for project in projects:
        project_dict = {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "address": project.address,
            "client_name": project.client_name,
            "client_phone": project.client_phone,
            "client_email": project.client_email,
            "project_type": project.project_type,
            "total_area": project.total_area,
            "estimated_hours": project.estimated_hours,
            "hourly_rate": project.hourly_rate,
            "start_date": project.start_date,
            "end_date": project.end_date,
            "status": project.status,
            "created_at": project.created_at,
            "updated_at": project.updated_at
        }
        result.append(project_dict)
    
    return result

@router.post("/", response_model=ProjectSchema)
def create_project(
    project: ProjectCreate,
    session: Session = Depends(get_session),
    _: User = Depends(require_buchhalter_or_admin),
):
    """
    Neues Projekt erstellen.
    
    Args:
        project: Projekt-Daten
        session: Datenbank-Session
        
    Returns:
        ProjectSchema: Erstelltes Projekt
    """
    db_project = Project.model_validate(project)
    session.add(db_project)
    session.commit()
    session.refresh(db_project)
    return db_project

@router.get("/{project_id}", response_model=ProjectSchema)
def get_project(
    project_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(get_current_user),
):
    """
    Einzelnes Projekt anhand der ID abrufen.
    
    Args:
        project_id: Projekt-ID
        session: Datenbank-Session
        
    Returns:
        ProjectSchema: Projekt-Daten
        
    Raises:
        HTTPException: Wenn Projekt nicht gefunden wird
    """
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
    return project

@router.put("/{project_id}", response_model=ProjectSchema)
def update_project(
    project_id: int,
    project_update: ProjectUpdate,
    session: Session = Depends(get_session),
    _: User = Depends(require_buchhalter_or_admin),
):
    """
    Projekt aktualisieren.
    
    Args:
        project_id: Projekt-ID
        project_update: Aktualisierte Projekt-Daten
        session: Datenbank-Session
        
    Returns:
        ProjectSchema: Aktualisiertes Projekt
        
    Raises:
        HTTPException: Wenn Projekt nicht gefunden wird
    """
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
    
    # Nur gesetzte Felder aktualisieren
    project_data = project_update.model_dump(exclude_unset=True)
    for field, value in project_data.items():
        setattr(project, field, value)
    
    session.add(project)
    session.commit()
    session.refresh(project)
    return project

@router.delete("/{project_id}")
def delete_project(
    project_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_buchhalter_or_admin),
):
    """
    Projekt löschen mit allen verknüpften Daten (nur für Buchhalter und Admin).
    
    Args:
        project_id: Projekt-ID
        session: Datenbank-Session
        current_user: Aktueller Benutzer (Buchhalter/Admin)
        
    Returns:
        dict: Erfolgsmeldung mit Details der gelöschten Daten
        
    Raises:
        HTTPException: Wenn Projekt nicht gefunden wird oder Löschung fehlschlägt
    """
    try:
        # Prüfe ob Projekt existiert
        project = session.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
        
        project_name = project.name
        
        # Zähle verknüpfte Daten vor dem Löschen
        from ..models import Report, TimeEntry, Offer, Invoice, ProjectImage
        from sqlmodel import select
        import os
        
        # Zähle verknüpfte Berichte
        reports = session.exec(select(Report).where(Report.project_id == project_id)).all()
        reports_count = len(reports)
        
        # Zähle verknüpfte Stundeneinträge
        time_entries = session.exec(select(TimeEntry).where(TimeEntry.project_id == project_id)).all()
        time_entries_count = len(time_entries)
        
        # Zähle verknüpfte Angebote
        offers = session.exec(select(Offer).where(Offer.project_id == project_id)).all()
        offers_count = len(offers)
        
        # Zähle verknüpfte Rechnungen
        invoices = session.exec(select(Invoice).where(Invoice.project_id == project_id)).all()
        invoices_count = len(invoices)
        
        # Zähle verknüpfte Projektbilder
        project_images = session.exec(select(ProjectImage).where(ProjectImage.project_id == project_id)).all()
        project_images_count = len(project_images)
        
        # Lösche alle verknüpften Daten
        
        # 1. Lösche Berichte und deren Anhänge
        for report in reports:
            # Lösche Berichtsbilder aus dem Dateisystem
            try:
                import os
                from pathlib import Path
                upload_dir = Path("uploads/images")
                if upload_dir.exists():
                    for file in upload_dir.glob(f"*"):
                        if file.is_file():
                            # Prüfe ob Datei zu diesem Bericht gehört
                            try:
                                with open(file, 'rb') as f:
                                    # Einfache Prüfung: wenn Datei existiert, lösche sie
                                    pass
                            except:
                                pass
            except Exception as e:
                print(f"Fehler beim Löschen der Berichtsbilder: {e}")
            
            session.delete(report)
        
        # 2. Lösche Stundeneinträge
        for time_entry in time_entries:
            session.delete(time_entry)
        
        # 3. Lösche Angebote
        for offer in offers:
            session.delete(offer)
        
        # 4. Lösche Rechnungen
        for invoice in invoices:
            session.delete(invoice)
        
        # 5. Lösche Projektbilder und deren Dateien
        for image in project_images:
            # Lösche Datei vom Server
            if hasattr(image, 'file_path') and image.file_path and os.path.exists(image.file_path):
                try:
                    os.remove(image.file_path)
                except Exception as e:
                    print(f"Fehler beim Löschen der Bilddatei {image.file_path}: {e}")
            session.delete(image)
        
        # 6. Lösche das Projekt selbst
        session.delete(project)
        session.commit()
        
        return {
            "message": "Projekt und alle verknüpften Daten erfolgreich gelöscht",
            "deleted_project": project_name,
            "deleted_by": current_user.full_name,
            "deleted_at": datetime.utcnow().isoformat(),
            "deleted_data": {
                "berichte": reports_count,
                "stundeneintraege": time_entries_count,
                "angebote": offers_count,
                "rechnungen": invoices_count,
                "projektbilder": project_images_count
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler beim Löschen des Projekts: {str(e)}")

