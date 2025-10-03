"""
Router für Bericht-Management.
Bietet CRUD-Operationen für Bauberichte und Bild-Uploads.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select
from typing import List
import os
import uuid
from datetime import datetime
from ..database import get_session
from ..models import Report, Project, ReportImage
from ..schemas import ReportCreate, ReportUpdate, Report as ReportSchema, ReportImage as ReportImageSchema
from ..auth import get_current_user, require_buchhalter_or_admin

router = APIRouter(prefix="/reports", tags=["reports"])

# Upload-Verzeichnis für Bilder
UPLOAD_DIR = "uploads/images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def _get_report_attachments(session: Session, report_id: int) -> list:
    attachments = []
    statement = select(ReportImage).where(ReportImage.report_id == report_id)
    report_images = session.exec(statement).all()

    for img in report_images:
        attachments.append({
            "filename": img.filename,
            "original_filename": img.original_filename,
            "size": img.file_size,
            "description": getattr(img, 'description', None),
            "image_type": getattr(img, 'image_type', None)
        })
    return attachments

@router.get("/", response_model=List[ReportSchema])
def get_reports(session: Session = Depends(get_session), current_user = Depends(get_current_user)):
    """
    Alle Berichte abrufen.
    
    Returns:
        List[ReportSchema]: Liste aller Berichte
    """
    try:
        # Verwende die übergebene Session
        statement = select(Report).order_by(Report.id.desc())
        reports = session.exec(statement).all()
        print(f"DEBUG: {len(reports)} Berichte gefunden")
        
        # Konvertiere zu Liste für JSON-Serialisierung und füge Projekt-Namen hinzu
        result = []
        for report in reports:
            # Projekt-Informationen abrufen
            project = session.get(Project, report.project_id)
            project_name = project.name if project else "Unbekannt"
            
            # Anhänge für diesen Bericht abrufen (nur die Bilder dieses Berichts!)
            attachments = _get_report_attachments(session, report.id)
            print(f"DEBUG: Bericht {report.id} - {len(attachments)} Anhänge aus Datenbank")
            
            # Debug-Ausgabe
            print(f"DEBUG: Bericht {report.id} - Finale Anhänge: {len(attachments)}")
            if len(attachments) > 0:
                print(f"DEBUG: Anhänge für Bericht {report.id}: {[a['filename'] for a in attachments]}")
            
            # Bericht-Daten mit Projekt-Namen und Anhängen erweitern
            report_dict = {
                "id": report.id,
                "project_id": report.project_id,
                "project_name": project_name,
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
                "attachments": attachments,
                "created_at": report.created_at,
                "updated_at": report.updated_at
            }
            result.append(report_dict)
        
        print(f"DEBUG: {len(result)} Berichte zurückgegeben")
        return result
    except Exception as e:
        print(f"Error in get_reports: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Fehler beim Laden der Berichte: {str(e)}")

@router.post("/", response_model=ReportSchema)
def create_report(report: ReportCreate, session: Session = Depends(get_session), current_user = Depends(get_current_user)):
    """
    Neuen Bericht erstellen.
    
    Args:
        report: Bericht-Daten
        session: Datenbank-Session
        
    Returns:
        ReportSchema: Erstellter Bericht
        
    Raises:
        HTTPException: Wenn zugehöriges Projekt nicht gefunden wird
    """
    try:
        # Prüfen ob das Projekt existiert
        project = session.get(Project, report.project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
        
        # Datum konvertieren (nur wenn vorhanden und nicht leer)
        report_date = None
        if report.report_date and report.report_date.strip():
            try:
                from datetime import datetime
                # ISO-Format: 2025-09-30 -> 2025-09-30T00:00:00
                if len(report.report_date) == 10:  # Nur Datum ohne Zeit
                    report_date = datetime.fromisoformat(report.report_date + 'T00:00:00')
                else:
                    report_date = datetime.fromisoformat(report.report_date)
            except Exception as e:
                print(f"Fehler bei Datum-Konvertierung: {e}")
                report_date = None
        
        # Bericht direkt erstellen
        db_report = Report(
            project_id=report.project_id,
            title=report.title,
            content=report.content,
            report_date=report_date,
            work_type=report.work_type,
            area_completed=report.area_completed,
            materials_used=report.materials_used,
            quality_check=report.quality_check,
            issues_encountered=report.issues_encountered,
            next_steps=report.next_steps,
            progress_percentage=report.progress_percentage
        )
        
        session.add(db_report)
        session.commit()
        session.refresh(db_report)
        return db_report
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Fehler bei Bericht-Erstellung: {e}")
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Fehler bei Bericht-Erstellung: {str(e)}")

@router.get("/{report_id}", response_model=ReportSchema)
def get_report(report_id: int, session: Session = Depends(get_session)):
    """
    Einzelnen Bericht anhand der ID abrufen.
    
    Args:
        report_id: Bericht-ID
        session: Datenbank-Session
        
    Returns:
        ReportSchema: Bericht-Daten
        
    Raises:
        HTTPException: Wenn Bericht nicht gefunden wird
    """
    report = session.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Bericht nicht gefunden")
    
    # Projekt-Informationen abrufen
    project = session.get(Project, report.project_id)
    project_name = project.name if project else "Unbekannt"
    
    # Anhänge für diesen Bericht abrufen (vereinfachte Lösung)
    attachments = _get_report_attachments(session, report.id)
    print(f"DEBUG: Einzelner Bericht {report.id} - {len(attachments)} Anhänge aus Datenbank")
    
    # Bericht-Daten mit Projekt-Namen und Anhängen erweitern
    report_dict = {
        "id": report.id,
        "project_id": report.project_id,
        "project_name": project_name,
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
        "attachments": attachments,
        "created_at": report.created_at,
        "updated_at": report.updated_at
    }
    
    return report_dict

@router.put("/{report_id}", response_model=ReportSchema)
def update_report(
    report_id: int, 
    report_update: ReportUpdate, 
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """
    Bericht aktualisieren.
    
    Args:
        report_id: Bericht-ID
        report_update: Aktualisierte Bericht-Daten
        session: Datenbank-Session
        
    Returns:
        ReportSchema: Aktualisierter Bericht
        
    Raises:
        HTTPException: Wenn Bericht nicht gefunden wird
    """
    report = session.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Bericht nicht gefunden")
    
    # Nur gesetzte Felder aktualisieren
    report_data = report_update.model_dump(exclude_unset=True)
    for field, value in report_data.items():
        # Spezielle Behandlung für Datumsfelder
        if field == 'report_date':
            if value and value != '' and value is not None:
                from datetime import datetime
                # Konvertiere String zu datetime
                if isinstance(value, str) and value.strip():
                    try:
                        # Versuche ISO-Format zu parsen
                        if 'T' in value:
                            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        else:
                            # Nur Datum ohne Zeit
                            value = datetime.strptime(value, '%Y-%m-%d').date()
                    except ValueError:
                        # Fallback: versuche andere Formate
                        try:
                            value = datetime.strptime(value, '%Y-%m-%d')
                        except ValueError:
                            pass  # Behalte ursprünglichen Wert
                    setattr(report, field, value)
            # Leere Strings oder None-Werte werden ignoriert
        else:
            setattr(report, field, value)
    
    session.add(report)
    session.commit()
    session.refresh(report)
    return report

@router.delete("/{report_id}")
def delete_report(report_id: int, session: Session = Depends(get_session)):
    """
    Bericht löschen.
    
    Args:
        report_id: Bericht-ID
        session: Datenbank-Session
        
    Returns:
        dict: Erfolgsmeldung
        
    Raises:
        HTTPException: Wenn Bericht nicht gefunden wird
    """
    report = session.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Bericht nicht gefunden")
    
    session.delete(report)
    session.commit()
    return {"message": "Bericht erfolgreich gelöscht"}

@router.post("/{report_id}/upload_image")
def upload_image(
    report_id: int, 
    file: UploadFile = File(...), 
    session: Session = Depends(get_session)
):
    """
    Bild zu einem Bericht hochladen.
    
    Args:
        report_id: Bericht-ID
        file: Hochgeladene Bilddatei
        session: Datenbank-Session
        
    Returns:
        dict: Upload-Informationen
        
    Raises:
        HTTPException: Wenn Bericht nicht gefunden wird oder Datei ungültig ist
    """
    # Prüfen ob der Bericht existiert
    report = session.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Bericht nicht gefunden")
    
    # Dateityp prüfen
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Nur Bilddateien sind erlaubt")
    
    # Eindeutigen Dateinamen generieren
    file_extension = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    try:
        # Datei speichern
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)
        
        return {
            "message": "Bild erfolgreich hochgeladen",
            "filename": unique_filename,
            "original_filename": file.filename,
            "file_path": file_path,
            "file_size": len(content)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Speichern der Datei: {str(e)}")

@router.get("/project/{project_id}", response_model=List[ReportSchema])
def get_reports_by_project(project_id: int, session: Session = Depends(get_session)):
    """
    Alle Berichte eines Projekts abrufen.
    
    Args:
        project_id: Projekt-ID
        session: Datenbank-Session
        
    Returns:
        List[ReportSchema]: Liste der Berichte des Projekts
        
    Raises:
        HTTPException: Wenn Projekt nicht gefunden wird
    """
    # Prüfen ob das Projekt existiert
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
    
    statement = select(Report).where(Report.project_id == project_id)
    reports = session.exec(statement).all()
    return reports

# Foto-Upload Endpunkte
@router.post("/{report_id}/upload")
async def upload_report_file(
    report_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """
    Foto für einen Bericht hochladen.
    """
    try:
        # Prüfe ob Bericht existiert
        report = session.get(Report, report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Bericht nicht gefunden")
        
        # Prüfe Dateityp (nur Bilder)
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Nur Bilddateien sind erlaubt")
        
        # Verwende den Originalnamen, aber stelle sicher, dass er eindeutig ist
        original_filename = file.filename
        # Entferne ungültige Zeichen aus dem Dateinamen
        import re
        safe_filename = re.sub(r'[^\w\.-]', '_', original_filename)
        
        # Füge Zeitstempel hinzu, um Eindeutigkeit zu gewährleisten
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_parts = os.path.splitext(safe_filename)
        unique_filename = f"{filename_parts[0]}_{timestamp}{filename_parts[1]}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Speichere Datei
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Speichere Bild-Informationen in der Datenbank
        from app.models import ReportImage
        print(f"DEBUG: Erstelle ReportImage für Bericht {report_id}")
        print(f"DEBUG: filename={unique_filename}, original={file.filename}, size={len(content)}")
        
        # Erstelle das ReportImage-Objekt
        report_image = ReportImage(
            report_id=report_id,
            filename=unique_filename,
            original_filename=file.filename,
            file_path=file_path,
            file_size=len(content)
        )
        
        # Speichere in der Datenbank
        try:
            print(f"DEBUG: Füge ReportImage zur Session hinzu...")
            session.add(report_image)
            print(f"DEBUG: Committe Session...")
            session.commit()
            print(f"DEBUG: ReportImage erfolgreich gespeichert")
            
            # Verifiziere, dass es wirklich gespeichert wurde
            from sqlmodel import select
            statement = select(ReportImage).where(ReportImage.filename == unique_filename)
            saved_image = session.exec(statement).first()
            if saved_image:
                print(f"DEBUG: Verifizierung erfolgreich - ReportImage ID {saved_image.id} für Bericht {saved_image.report_id} gespeichert")
            else:
                print(f"WARNUNG: ReportImage konnte nicht verifiziert werden!")
            # Zähle alle ReportImage-Einträge in der DB
            all_images = session.exec(select(ReportImage)).all()
            print(f"DEBUG: ReportImage-Einträge in DB nach Speichern: {len(all_images)}")
            
        except Exception as e:
            print(f"FEHLER beim Speichern der ReportImage: {e}")
            import traceback
            traceback.print_exc()
            session.rollback()
        
        return {
            "message": "Foto erfolgreich hochgeladen",
            "filename": unique_filename,
            "original_name": file.filename,
            "size": len(content)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Hochladen: {str(e)}")

@router.get("/{report_id}/files")
async def get_report_files(
    report_id: int,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """
    Alle Fotos eines Berichts abrufen.
    """
    try:
        # Prüfe ob Bericht existiert
        report = session.get(Report, report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Bericht nicht gefunden")
        
        # Lade die Bilder aus der Datenbank für diesen spezifischen Bericht
        files = []
        try:
            from app.models import ReportImage
            # Suche alle ReportImage-Einträge für diesen Bericht
            statement = select(ReportImage).where(ReportImage.report_id == report_id)
            report_images = session.exec(statement).all()
            
            # Konvertiere zu Datei-Informationen
            for image in report_images:
                if os.path.exists(image.file_path):
                    stat = os.stat(image.file_path)
                    files.append({
                        "filename": image.filename,
                        "size": image.file_size or stat.st_size,
                        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "original_filename": image.original_filename
                    })
            
            print(f"DEBUG: Bericht {report_id} - {len(files)} Bilder aus Datenbank geladen")
            
            # Wenn keine Bilder in der Datenbank gefunden wurden, versuche es mit Dateisystem-Fallback
            if len(files) == 0:
                print(f"DEBUG: Keine Bilder in Datenbank für Bericht {report_id}, versuche Dateisystem-Fallback")
                if os.path.exists(UPLOAD_DIR):
                    for filename in os.listdir(UPLOAD_DIR):
                        file_path = os.path.join(UPLOAD_DIR, filename)
                        if os.path.isfile(file_path):
                            stat = os.stat(file_path)
                            files.append({
                                "filename": filename,
                                "size": stat.st_size,
                                "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
                            })
                
                print(f"DEBUG: Bericht {report_id} - {len(files)} Dateien im Fallback gefunden")
        except Exception as e:
            print(f"FEHLER beim Laden der Bilder aus der Datenbank: {e}")
            import traceback
            traceback.print_exc()
        
        # Sortiere nach Erstellungsdatum (neueste zuerst)
        files.sort(key=lambda x: x['created'], reverse=True)
        
        return files
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Laden der Dateien: {str(e)}")

@router.get("/{report_id}/files/{filename}")
async def get_report_file(
    report_id: int,
    filename: str,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """
    Einzelnes Foto eines Berichts abrufen.
    """
    try:
        # Prüfe ob Bericht existiert
        report = session.get(Report, report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Bericht nicht gefunden")
        
        file_path = os.path.join(UPLOAD_DIR, filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Datei nicht gefunden")
        
        from fastapi.responses import FileResponse
        return FileResponse(file_path)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Laden der Datei: {str(e)}")

@router.delete("/{report_id}/files/{filename}")
async def delete_report_file(
    report_id: int,
    filename: str,
    session: Session = Depends(get_session),
    current_user = Depends(require_buchhalter_or_admin)
):
    """
    Foto eines Berichts löschen.
    """
    try:
        # Prüfe ob Bericht existiert
        report = session.get(Report, report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Bericht nicht gefunden")
        
        # Lösche Datei aus der Datenbank
        try:
            from app.models import ReportImage
            attachment_statement = select(ReportImage).where(
                ReportImage.report_id == report_id,
                ReportImage.filename == filename
            )
            attachment = session.exec(attachment_statement).first()
            
            if attachment:
                session.delete(attachment)
                session.commit()
                print(f"DEBUG: ReportImage {attachment.id} aus Datenbank gelöscht")
            else:
                print(f"WARNUNG: ReportImage für {filename} nicht in Datenbank gefunden")
        except Exception as e:
            print(f"Fehler beim Löschen aus der Datenbank: {e}")
        
        # Lösche Datei vom Dateisystem
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            return {"message": "Datei erfolgreich gelöscht"}
        else:
            raise HTTPException(status_code=404, detail="Datei nicht gefunden")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Löschen der Datei: {str(e)}")

@router.post("/{report_id}/upload_image", response_model=ReportImageSchema)
def upload_image(
    report_id: int,
    file: UploadFile = File(...),
    description: str = None,
    image_type: str = "progress",
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """
    Lädt ein Bild für einen Bericht hoch.
    """
    # Bericht existiert prüfen
    report = session.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Bericht nicht gefunden")
    
    # Dateityp prüfen
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Nur Bilddateien sind erlaubt")
    
    # Dateigröße prüfen (5MB Limit)
    content = file.file.read()
    if len(content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Dateigröße darf 5MB nicht überschreiten")
    
    # Eindeutigen Dateinamen generieren
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Verzeichnis erstellen falls nicht vorhanden
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    try:
        # Datei speichern
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        # Datenbank-Eintrag erstellen
        report_image = ReportImage(
            report_id=report_id,
            filename=unique_filename,
            original_filename=file.filename or "unknown",
            file_path=file_path,
            file_size=len(content),
            description=description,
            image_type=image_type
        )
        session.add(report_image)
        session.commit()
        session.refresh(report_image)
        return report_image
        
    except Exception as e:
        # Datei löschen falls Datenbank-Fehler
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Fehler beim Speichern: {str(e)}")

@router.get("/{report_id}/images", response_model=List[ReportImageSchema])
def get_report_images(
    report_id: int,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """
    Ruft alle Bilder für einen Bericht ab.
    """
    report = session.get(Report, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Bericht nicht gefunden")
    
    images = session.exec(
        select(ReportImage).where(ReportImage.report_id == report_id)
    ).all()
    return images

@router.delete("/images/{image_id}")
def delete_image(
    image_id: int,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """
    Löscht ein Berichtsbild.
    """
    image = session.get(ReportImage, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Bild nicht gefunden")
    
    # Datei vom Dateisystem löschen
    if os.path.exists(image.file_path):
        os.remove(image.file_path)
    
    # Datenbank-Eintrag löschen
    session.delete(image)
    session.commit()
    return {"message": "Bild erfolgreich gelöscht"}

@router.get("/images/{image_id}/download")
def download_image(
    image_id: int,
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """
    Lädt ein Berichtsbild herunter.
    """
    from fastapi.responses import FileResponse
    
    image = session.get(ReportImage, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Bild nicht gefunden")
    
    if not os.path.exists(image.file_path):
        raise HTTPException(status_code=404, detail="Bilddatei nicht gefunden")
    
    return FileResponse(
        path=image.file_path,
        filename=image.original_filename,
        media_type="application/octet-stream"
    )

@router.get("/images/{image_id}/view")
def view_report_image(
    image_id: int,
    session: Session = Depends(get_session)
):
    """
    Berichtsbild anzeigen (öffentlicher Endpoint für <img> tags).
    """
    from fastapi.responses import FileResponse
    
    image = session.get(ReportImage, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Bild nicht gefunden")
    
    if not os.path.exists(image.file_path):
        raise HTTPException(status_code=404, detail="Bilddatei nicht gefunden")
    
    # Bestimme den korrekten MIME-Type basierend auf der Dateiendung
    file_extension = os.path.splitext(image.file_path)[1].lower()
    media_type_map = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp'
    }
    media_type = media_type_map.get(file_extension, 'image/jpeg')
    
    return FileResponse(
        path=image.file_path,
        media_type=media_type
    )

