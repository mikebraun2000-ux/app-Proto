"""
Router für Stundenerfassung.
Bietet CRUD-Operationen für Arbeitszeiten.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from ..database import get_session
from ..models import TimeEntry, Employee, Project
from ..schemas import TimeEntryCreate, TimeEntryUpdate, TimeEntry as TimeEntrySchema
from ..auth import get_current_user, require_employee_or_admin

router = APIRouter(prefix="/time-entries", tags=["time-entries"])

@router.get("/", response_model=List[TimeEntrySchema])
def get_time_entries(session: Session = Depends(get_session), current_user = Depends(get_current_user)):
    """
    Stundeneinträge abrufen - rollenbasiert gefiltert.
    
    Returns:
        List[TimeEntrySchema]: Liste der Stundeneinträge (gefiltert nach Rolle)
    """
    try:
        # Rollenbasierte Filterung
        if current_user.role == "admin":
            # Admin sieht alle Einträge
            statement = select(TimeEntry)
        elif current_user.role == "buchhalter":
            # Buchhalter sieht alle Einträge
            statement = select(TimeEntry)
        else:
            # Mitarbeiter sieht nur eigene Einträge (über employee_id = 1 für jetzt)
            statement = select(TimeEntry).where(TimeEntry.employee_id == 1)
        
        time_entries = session.exec(statement).all()
        
        # Manuelle Serialisierung für problematische Felder
        result = []
        for entry in time_entries:
            entry_dict = {
                "id": entry.id,
                "project_id": entry.project_id,
                "employee_id": entry.employee_id,
                "work_date": entry.work_date.isoformat() if entry.work_date else None,
                "clock_in": entry.clock_in,
                "clock_out": entry.clock_out,
                "break_start": entry.break_start,
                "break_end": entry.break_end,
                "total_break_minutes": entry.total_break_minutes,
                "hours_worked": entry.hours_worked,
                "description": entry.description,
                "hourly_rate": entry.hourly_rate,
                "total_cost": entry.total_cost,
                "is_edited": entry.is_edited,
                "edit_reason": entry.edit_reason,
                "edited_by": entry.edited_by,
                "created_at": entry.created_at,
                "updated_at": entry.updated_at
            }
            result.append(entry_dict)
        
        return result
    except Exception as e:
        print(f"Error in get_time_entries: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Laden der Stundeneinträge: {str(e)}")

@router.post("/", response_model=TimeEntrySchema)
def create_time_entry(time_entry: TimeEntryCreate, session: Session = Depends(get_session), current_user = Depends(require_employee_or_admin)):
    """
    Neuen Stundeneintrag erstellen.
    
    Args:
        time_entry: Stundeneintrag-Daten
        session: Datenbank-Session
        
    Returns:
        TimeEntrySchema: Erstellter Stundeneintrag
        
    Raises:
        HTTPException: Wenn Projekt oder Mitarbeiter nicht gefunden wird
    """
    # Prüfen ob das Projekt existiert
    project = session.get(Project, time_entry.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
    
    # Prüfen ob der Mitarbeiter existiert
    employee = session.get(Employee, time_entry.employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Mitarbeiter nicht gefunden")
    
    # Stundensatz aus Mitarbeiterdaten übernehmen falls nicht angegeben
    if not time_entry.hourly_rate and employee.hourly_rate:
        time_entry.hourly_rate = employee.hourly_rate
    
    # Gesamtkosten berechnen
    total_cost = time_entry.hours_worked * (time_entry.hourly_rate or 0)
    
    # Stundeneintrag direkt erstellen
    from datetime import datetime, date
    
    # Datum konvertieren für Datenbank
    work_date = datetime.fromisoformat(time_entry.work_date).date() if time_entry.work_date else date.today()
    
    # Stundeneintrag erstellen
    db_time_entry = TimeEntry(
        project_id=time_entry.project_id,
        employee_id=time_entry.employee_id,
        work_date=work_date,
        clock_in=time_entry.clock_in,
        clock_out=time_entry.clock_out,
        break_start=time_entry.break_start,
        break_end=time_entry.break_end,
        total_break_minutes=time_entry.total_break_minutes or 0,
        hours_worked=time_entry.hours_worked,
        description=time_entry.description,
        hourly_rate=time_entry.hourly_rate,
        total_cost=total_cost
    )
    
    session.add(db_time_entry)
    session.commit()
    session.refresh(db_time_entry)
    
    # Response für Schema konvertieren
    return {
        "id": db_time_entry.id,
        "project_id": db_time_entry.project_id,
        "employee_id": db_time_entry.employee_id,
        "work_date": db_time_entry.work_date.isoformat() if db_time_entry.work_date else None,
        "clock_in": db_time_entry.clock_in,
        "clock_out": db_time_entry.clock_out,
        "break_start": db_time_entry.break_start,
        "break_end": db_time_entry.break_end,
        "total_break_minutes": db_time_entry.total_break_minutes,
        "hours_worked": db_time_entry.hours_worked,
        "description": db_time_entry.description,
        "hourly_rate": db_time_entry.hourly_rate,
        "total_cost": db_time_entry.total_cost,
        "is_edited": db_time_entry.is_edited,
        "edit_reason": db_time_entry.edit_reason,
        "created_at": db_time_entry.created_at,
        "updated_at": db_time_entry.updated_at
    }

@router.get("/{time_entry_id}", response_model=TimeEntrySchema)
def get_time_entry(time_entry_id: int, session: Session = Depends(get_session), current_user = Depends(get_current_user)):
    """
    Einzelnen Stundeneintrag anhand der ID abrufen.
    
    Args:
        time_entry_id: Stundeneintrag-ID
        session: Datenbank-Session
        
    Returns:
        TimeEntrySchema: Stundeneintrag-Daten
        
    Raises:
        HTTPException: Wenn Stundeneintrag nicht gefunden wird
    """
    time_entry = session.get(TimeEntry, time_entry_id)
    if not time_entry:
        raise HTTPException(status_code=404, detail="Stundeneintrag nicht gefunden")
    
    # Für Mitarbeiter: Stundensatz ausblenden
    if current_user.role == "mitarbeiter":
        time_entry.hourly_rate = 0.0
    
    # Manuelle Serialisierung, damit Pydantic keine Probleme mit Datums-/Zeitobjekten hat
    return {
        "id": time_entry.id,
        "project_id": time_entry.project_id,
        "employee_id": time_entry.employee_id,
        "work_date": time_entry.work_date.isoformat() if time_entry.work_date else None,
        "clock_in": time_entry.clock_in,
        "clock_out": time_entry.clock_out,
        "break_start": time_entry.break_start,
        "break_end": time_entry.break_end,
        "total_break_minutes": time_entry.total_break_minutes,
        "hours_worked": time_entry.hours_worked,
        "description": time_entry.description,
        "hourly_rate": time_entry.hourly_rate,
        "total_cost": time_entry.total_cost,
        "is_edited": time_entry.is_edited,
        "edit_reason": time_entry.edit_reason,
        "edited_by": time_entry.edited_by,
        "created_at": time_entry.created_at,
        "updated_at": time_entry.updated_at
    }

@router.put("/{time_entry_id}", response_model=TimeEntrySchema)
def update_time_entry(
    time_entry_id: int, 
    time_entry_update: TimeEntryUpdate, 
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
):
    """
    Stundeneintrag aktualisieren.
    
    Args:
        time_entry_id: Stundeneintrag-ID
        time_entry_update: Aktualisierte Stundeneintrag-Daten
        session: Datenbank-Session
        current_user: Aktueller Benutzer
        
    Returns:
        TimeEntrySchema: Aktualisierter Stundeneintrag
        
    Raises:
        HTTPException: Wenn Stundeneintrag nicht gefunden wird oder keine Berechtigung
    """
    time_entry = session.get(TimeEntry, time_entry_id)
    if not time_entry:
        raise HTTPException(status_code=404, detail="Stundeneintrag nicht gefunden")
    
    # Rollenbasierte Berechtigung prüfen
    if current_user.role == "mitarbeiter" and time_entry.employee_id != 1:
        raise HTTPException(status_code=403, detail="Keine Berechtigung, diesen Stundeneintrag zu bearbeiten")
    
    # Nur gesetzte Felder aktualisieren
    time_entry_data = time_entry_update.model_dump(exclude_unset=True)
    
    # Mitarbeiter können keinen Stundensatz ändern
    if current_user.role == "mitarbeiter" and 'hourly_rate' in time_entry_data:
        time_entry_data.pop('hourly_rate')
        print(f"Stundensatz-Änderung von Mitarbeiter {current_user.username} ignoriert")
    
    # Datum konvertieren falls vorhanden
    if 'work_date' in time_entry_data and time_entry_data['work_date']:
        from datetime import datetime
        time_entry_data['work_date'] = datetime.fromisoformat(time_entry_data['work_date']).date()
    
    # Felder aktualisieren
    for field, value in time_entry_data.items():
        setattr(time_entry, field, value)
    
    # Als bearbeitet markieren
    time_entry.is_edited = True
    time_entry.edit_reason = f"Bearbeitet von {current_user.username}"
    
    # Admin-Benachrichtigung für Mitarbeiter-Änderungen
    if current_user.role == "mitarbeiter":
        print(f"ADMIN-BENACHRICHTIGUNG: Mitarbeiter {current_user.username} hat Stundeneintrag {time_entry_id} bearbeitet")
        # TODO: Hier könnte eine echte Benachrichtigung implementiert werden
    
    # Gesamtkosten neu berechnen
    if 'hours_worked' in time_entry_data or 'hourly_rate' in time_entry_data:
        time_entry.total_cost = time_entry.hours_worked * (time_entry.hourly_rate or 0)
    
    session.add(time_entry)
    session.commit()
    session.refresh(time_entry)
    
    # Response für Schema konvertieren
    return {
        "id": time_entry.id,
        "project_id": time_entry.project_id,
        "employee_id": time_entry.employee_id,
        "work_date": time_entry.work_date.isoformat() if time_entry.work_date else None,
        "clock_in": time_entry.clock_in,
        "clock_out": time_entry.clock_out,
        "break_start": time_entry.break_start,
        "break_end": time_entry.break_end,
        "total_break_minutes": time_entry.total_break_minutes,
        "hours_worked": time_entry.hours_worked,
        "description": time_entry.description,
        "hourly_rate": time_entry.hourly_rate,
        "total_cost": time_entry.total_cost,
        "is_edited": time_entry.is_edited,
        "edit_reason": time_entry.edit_reason,
        "created_at": time_entry.created_at,
        "updated_at": time_entry.updated_at
    }

@router.delete("/{time_entry_id}")
def delete_time_entry(time_entry_id: int, session: Session = Depends(get_session)):
    """
    Stundeneintrag löschen.
    
    Args:
        time_entry_id: Stundeneintrag-ID
        session: Datenbank-Session
        
    Returns:
        dict: Erfolgsmeldung
        
    Raises:
        HTTPException: Wenn Stundeneintrag nicht gefunden wird
    """
    time_entry = session.get(TimeEntry, time_entry_id)
    if not time_entry:
        raise HTTPException(status_code=404, detail="Stundeneintrag nicht gefunden")
    
    session.delete(time_entry)
    session.commit()
    return {"message": "Stundeneintrag erfolgreich gelöscht"}

@router.get("/project/{project_id}", response_model=List[TimeEntrySchema])
def get_time_entries_by_project(project_id: int, session: Session = Depends(get_session)):
    """
    Alle Stundeneinträge eines Projekts abrufen.
    
    Args:
        project_id: Projekt-ID
        session: Datenbank-Session
        
    Returns:
        List[TimeEntrySchema]: Liste der Stundeneinträge des Projekts
        
    Raises:
        HTTPException: Wenn Projekt nicht gefunden wird
    """
    # Prüfen ob das Projekt existiert
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
    
    statement = select(TimeEntry).where(TimeEntry.project_id == project_id)
    time_entries = session.exec(statement).all()
    return time_entries

@router.get("/employee/{employee_id}", response_model=List[TimeEntrySchema])
def get_time_entries_by_employee(employee_id: int, session: Session = Depends(get_session)):
    """
    Alle Stundeneinträge eines Mitarbeiters abrufen.
    
    Args:
        employee_id: Mitarbeiter-ID
        session: Datenbank-Session
        
    Returns:
        List[TimeEntrySchema]: Liste der Stundeneinträge des Mitarbeiters
        
    Raises:
        HTTPException: Wenn Mitarbeiter nicht gefunden wird
    """
    # Prüfen ob der Mitarbeiter existiert
    employee = session.get(Employee, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Mitarbeiter nicht gefunden")
    
    statement = select(TimeEntry).where(TimeEntry.employee_id == employee_id)
    time_entries = session.exec(statement).all()
    return time_entries

