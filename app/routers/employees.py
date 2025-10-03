"""
Router für Mitarbeiter-Management.
Bietet CRUD-Operationen für Mitarbeiter.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from ..database import get_session
from ..models import Employee
from ..schemas import EmployeeCreate, EmployeeUpdate, Employee as EmployeeSchema
from ..auth import get_current_user, require_admin

router = APIRouter(
    prefix="/employees",
    tags=["employees"],
    dependencies=[Depends(get_current_user)],
)

@router.get("/", response_model=List[EmployeeSchema])
def get_employees(session: Session = Depends(get_session), current_user = Depends(require_admin)):
    """
    Alle Mitarbeiter des Tenants abrufen.
    """
    try:
        statement = select(Employee).where(Employee.tenant_id == current_user.tenant_id, Employee.is_active == True)
        employees = session.exec(statement).all()

        result = []
        for employee in employees:
            employee_dict = {
                "id": employee.id,
                "full_name": employee.full_name,
                "position": employee.position,
                "hourly_rate": employee.hourly_rate,
                "phone": employee.phone,
                "email": employee.email,
                "is_active": employee.is_active,
                "created_at": employee.created_at,
                "updated_at": employee.updated_at
            }
            result.append(employee_dict)

        return result
    except Exception as e:
        print(f"Error in get_employees: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Laden der Mitarbeiter: {str(e)}")

@router.post("/", response_model=EmployeeSchema)
def create_employee(
    employee: EmployeeCreate,
    session: Session = Depends(get_session),
    current_user = Depends(require_admin),
):
    """
    Neuen Mitarbeiter erstellen.
    
    Args:
        employee: Mitarbeiter-Daten
        session: Datenbank-Session
        
    Returns:
        EmployeeSchema: Erstellter Mitarbeiter
    """
    db_employee = Employee.model_validate(employee)
    session.add(db_employee)
    session.commit()
    session.refresh(db_employee)
    return db_employee

@router.get("/{employee_id}", response_model=EmployeeSchema)
def get_employee(
    employee_id: int,
    session: Session = Depends(get_session),
    current_user = Depends(require_admin),
):
    """
    Einzelnen Mitarbeiter anhand der ID abrufen.
    
    Args:
        employee_id: Mitarbeiter-ID
        session: Datenbank-Session
        
    Returns:
        EmployeeSchema: Mitarbeiter-Daten
        
    Raises:
        HTTPException: Wenn Mitarbeiter nicht gefunden wird
    """
    employee = session.get(Employee, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Mitarbeiter nicht gefunden")
    return employee

@router.put("/{employee_id}", response_model=EmployeeSchema)
def update_employee(
    employee_id: int,
    employee_update: EmployeeUpdate,
    session: Session = Depends(get_session),
    current_user = Depends(require_admin),
):
    """
    Mitarbeiter aktualisieren.
    
    Args:
        employee_id: Mitarbeiter-ID
        employee_update: Aktualisierte Mitarbeiter-Daten
        session: Datenbank-Session
        
    Returns:
        EmployeeSchema: Aktualisierter Mitarbeiter
        
    Raises:
        HTTPException: Wenn Mitarbeiter nicht gefunden wird
    """
    employee = session.get(Employee, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Mitarbeiter nicht gefunden")
    
    # Nur gesetzte Felder aktualisieren
    employee_data = employee_update.model_dump(exclude_unset=True)
    for field, value in employee_data.items():
        setattr(employee, field, value)
    
    session.add(employee)
    session.commit()
    session.refresh(employee)
    return employee

@router.delete("/{employee_id}")
def delete_employee(
    employee_id: int,
    session: Session = Depends(get_session),
    current_user = Depends(require_admin),
):
    """
    Mitarbeiter deaktivieren (soft delete).
    
    Args:
        employee_id: Mitarbeiter-ID
        session: Datenbank-Session
        
    Returns:
        dict: Erfolgsmeldung
        
    Raises:
        HTTPException: Wenn Mitarbeiter nicht gefunden wird
    """
    employee = session.get(Employee, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Mitarbeiter nicht gefunden")
    
    employee.is_active = False
    session.add(employee)
    session.commit()
    return {"message": "Mitarbeiter erfolgreich deaktiviert"}

