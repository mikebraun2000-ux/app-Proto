"""Mandantenfähiger Router für Stundenerfassungen."""

from __future__ import annotations

from datetime import date, datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..auth import get_current_user, require_employee_or_admin
from ..database import get_session
from ..models import Employee, Project, TimeEntry, User, UserRole
from ..schemas import TimeEntry as TimeEntrySchema
from ..schemas import TimeEntryCreate, TimeEntryUpdate

router = APIRouter(
    prefix="/time-entries",
    tags=["time-entries"],
    dependencies=[Depends(get_current_user)],
)


def _resolve_employee_id(session: Session, tenant_id: int, user_id: int) -> int:
    statement = select(Employee).where(Employee.user_id == user_id, Employee.tenant_id == tenant_id)
    employee = session.exec(statement).first()
    if employee is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Kein Mitarbeiterprofil gefunden")
    return employee.id


def _ensure_project_access(session: Session, tenant_id: int, project_id: int) -> Project:
    statement = select(Project).where(Project.id == project_id, Project.tenant_id == tenant_id)
    project = session.exec(statement).first()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Projekt nicht gefunden")
    return project


def _get_time_entry(session: Session, tenant_id: int, entry_id: int) -> TimeEntry:
    statement = select(TimeEntry).where(TimeEntry.id == entry_id, TimeEntry.tenant_id == tenant_id)
    entry = session.exec(statement).first()
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stundeneintrag nicht gefunden")
    return entry


def _serialize_entry(entry: TimeEntry) -> TimeEntrySchema:
    return TimeEntrySchema(
        id=entry.id,
        project_id=entry.project_id,
        employee_id=entry.employee_id,
        work_date=entry.work_date,
        clock_in=entry.clock_in,
        clock_out=entry.clock_out,
        break_start=entry.break_start,
        break_end=entry.break_end,
        total_break_minutes=entry.total_break_minutes,
        hours_worked=entry.hours_worked,
        description=entry.description,
        hourly_rate=entry.hourly_rate,
        total_cost=entry.total_cost,
        is_edited=entry.is_edited,
        edit_reason=entry.edit_reason,
        edited_by=entry.edited_by,
    )


@router.get("/", response_model=List[TimeEntrySchema])
def list_time_entries(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> List[TimeEntrySchema]:
    """Listet Stundeneinträge rollen- und mandantenabhängig."""
    statement = select(TimeEntry).where(TimeEntry.tenant_id == current_user.tenant_id)
    if current_user.role == UserRole.MITARBEITER:
        employee_id = _resolve_employee_id(session, current_user.tenant_id, current_user.id)
        statement = statement.where(TimeEntry.employee_id == employee_id)
    entries = session.exec(statement.order_by(TimeEntry.work_date.desc(), TimeEntry.id.desc())).all()
    return [_serialize_entry(entry) for entry in entries]


@router.post("/", response_model=TimeEntrySchema, status_code=status.HTTP_201_CREATED)
def create_time_entry(
    time_entry: TimeEntryCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_employee_or_admin),
) -> TimeEntrySchema:
    """Erstellt einen neuen Stundeneintrag innerhalb des aktuellen Tenants."""
    _ensure_project_access(session, current_user.tenant_id, time_entry.project_id)
    employee = session.exec(
        select(Employee).where(Employee.id == time_entry.employee_id, Employee.tenant_id == current_user.tenant_id)
    ).first()
    if employee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mitarbeiter nicht gefunden")

    if current_user.role == UserRole.MITARBEITER:
        own_employee_id = _resolve_employee_id(session, current_user.tenant_id, current_user.id)
        if own_employee_id != time_entry.employee_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Keine Berechtigung für diesen Mitarbeiter")

    work_date = datetime.fromisoformat(time_entry.work_date).date() if time_entry.work_date else date.today()
    hourly_rate = time_entry.hourly_rate or employee.hourly_rate or 0.0
    total_cost = round(time_entry.hours_worked * hourly_rate, 2)

    db_entry = TimeEntry(
        tenant_id=current_user.tenant_id,
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
        hourly_rate=hourly_rate,
        total_cost=total_cost,
        is_edited=False,
    )

    session.add(db_entry)
    session.commit()
    session.refresh(db_entry)
    return _serialize_entry(db_entry)


@router.get("/{time_entry_id}", response_model=TimeEntrySchema)
def get_time_entry(
    time_entry_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> TimeEntrySchema:
    """Gibt einen einzelnen Stundeneintrag zurück."""
    entry = _get_time_entry(session, current_user.tenant_id, time_entry_id)
    if current_user.role == UserRole.MITARBEITER:
        employee_id = _resolve_employee_id(session, current_user.tenant_id, current_user.id)
        if entry.employee_id != employee_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Keine Berechtigung")
    return _serialize_entry(entry)


@router.put("/{time_entry_id}", response_model=TimeEntrySchema)
def update_time_entry(
    time_entry_id: int,
    time_entry_update: TimeEntryUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> TimeEntrySchema:
    """Aktualisiert einen Stundeneintrag."""
    entry = _get_time_entry(session, current_user.tenant_id, time_entry_id)

    if current_user.role == UserRole.MITARBEITER:
        employee_id = _resolve_employee_id(session, current_user.tenant_id, current_user.id)
        if entry.employee_id != employee_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Keine Berechtigung")

    update_data = time_entry_update.model_dump(exclude_unset=True)
    if current_user.role == UserRole.MITARBEITER:
        update_data.pop("employee_id", None)
        update_data.pop("hourly_rate", None)

    if "project_id" in update_data:
        _ensure_project_access(session, current_user.tenant_id, update_data["project_id"])
    if "employee_id" in update_data:
        employee = session.exec(
            select(Employee).where(
                Employee.id == update_data["employee_id"],
                Employee.tenant_id == current_user.tenant_id,
            )
        ).first()
        if employee is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mitarbeiter nicht gefunden")

    if "work_date" in update_data and update_data["work_date"]:
        update_data["work_date"] = datetime.fromisoformat(update_data["work_date"]).date()

    for field_name, value in update_data.items():
        setattr(entry, field_name, value)

    entry.is_edited = True
    entry.edit_reason = time_entry_update.edit_reason or f"Bearbeitet von {current_user.username}"
    entry.edited_by = current_user.username
    entry.total_cost = round(entry.hours_worked * (entry.hourly_rate or 0), 2)

    session.add(entry)
    session.commit()
    session.refresh(entry)
    return _serialize_entry(entry)


@router.delete("/{time_entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_time_entry(
    time_entry_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_employee_or_admin),
) -> None:
    """Löscht einen Stundeneintrag."""
    entry = _get_time_entry(session, current_user.tenant_id, time_entry_id)
    if current_user.role == UserRole.MITARBEITER:
        employee_id = _resolve_employee_id(session, current_user.tenant_id, current_user.id)
        if entry.employee_id != employee_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Keine Berechtigung")
    session.delete(entry)
    session.commit()


@router.get("/project/{project_id}", response_model=List[TimeEntrySchema])
def list_time_entries_by_project(
    project_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_employee_or_admin),
) -> List[TimeEntrySchema]:
    """Listet alle Stundeneinträge eines Projekts im aktuellen Tenant."""
    _ensure_project_access(session, current_user.tenant_id, project_id)
    statement = select(TimeEntry).where(
        TimeEntry.project_id == project_id,
        TimeEntry.tenant_id == current_user.tenant_id,
    )
    if current_user.role == UserRole.MITARBEITER:
        employee_id = _resolve_employee_id(session, current_user.tenant_id, current_user.id)
        statement = statement.where(TimeEntry.employee_id == employee_id)
    entries = session.exec(statement.order_by(TimeEntry.work_date.desc(), TimeEntry.id.desc())).all()
    return [_serialize_entry(entry) for entry in entries]


@router.get("/employee/{employee_id}", response_model=List[TimeEntrySchema])
def list_time_entries_by_employee(
    employee_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_employee_or_admin),
) -> List[TimeEntrySchema]:
    """Listet alle Stundeneinträge eines Mitarbeiters."""
    employee = session.exec(
        select(Employee).where(Employee.id == employee_id, Employee.tenant_id == current_user.tenant_id)
    ).first()
    if employee is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mitarbeiter nicht gefunden")

    if current_user.role == UserRole.MITARBEITER:
        own_employee_id = _resolve_employee_id(session, current_user.tenant_id, current_user.id)
        if own_employee_id != employee_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Keine Berechtigung")

    statement = select(TimeEntry).where(
        TimeEntry.employee_id == employee_id,
        TimeEntry.tenant_id == current_user.tenant_id,
    )
    entries = session.exec(statement.order_by(TimeEntry.work_date.desc(), TimeEntry.id.desc())).all()
    return [_serialize_entry(entry) for entry in entries]
