"""FastAPI-Router für das Mitarbeiter-Management.

Alle Endpunkte sind mandantenfähig implementiert und verlangen Administrationsrechte,
da nur Administratoren Mitarbeiterdatensätze verwalten dürfen.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..auth import get_current_user, require_admin
from ..database import get_session
from ..models import Employee, User
from ..schemas import Employee as EmployeeSchema
from ..schemas import EmployeeCreate, EmployeeUpdate

router = APIRouter(
    prefix="/employees",
    tags=["employees"],
    dependencies=[Depends(get_current_user)],
)


def _get_employee_for_tenant(
    session: Session, tenant_id: int, employee_id: int
) -> Employee:
    """Lädt einen Mitarbeiter und stellt sicher, dass er zum aktuellen Tenant gehört."""
    statement = select(Employee).where(
        Employee.id == employee_id, Employee.tenant_id == tenant_id
    )
    employee = session.exec(statement).first()
    if employee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mitarbeiter nicht gefunden",
        )
    return employee


@router.get("/", response_model=List[EmployeeSchema])
def list_employees(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
) -> List[Employee]:
    """Gibt alle Mitarbeiter des aktuellen Tenants zurück."""
    statement = select(Employee).where(Employee.tenant_id == current_user.tenant_id)
    return session.exec(statement).all()


@router.post("/", response_model=EmployeeSchema, status_code=status.HTTP_201_CREATED)
def create_employee(
    employee: EmployeeCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
) -> Employee:
    """Erstellt einen neuen Mitarbeiter innerhalb des aktuellen Tenants."""
    if employee.user_id is not None:
        linked_user = session.get(User, employee.user_id)
        if linked_user is None or linked_user.tenant_id != current_user.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Zugeordneter Benutzer gehört nicht zum aktuellen Mandanten",
            )

    db_employee = Employee.model_validate(employee, update={"tenant_id": current_user.tenant_id})
    session.add(db_employee)
    session.commit()
    session.refresh(db_employee)
    return db_employee


@router.get("/{employee_id}", response_model=EmployeeSchema)
def get_employee(
    employee_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
) -> Employee:
    """Liefert einen einzelnen Mitarbeiter des Tenants."""
    return _get_employee_for_tenant(session, current_user.tenant_id, employee_id)


@router.put("/{employee_id}", response_model=EmployeeSchema)
def update_employee(
    employee_id: int,
    employee_update: EmployeeUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
) -> Employee:
    """Aktualisiert einen bestehenden Mitarbeiter."""
    employee = _get_employee_for_tenant(session, current_user.tenant_id, employee_id)

    update_data = employee_update.model_dump(exclude_unset=True)
    for field_name, value in update_data.items():
        setattr(employee, field_name, value)

    session.add(employee)
    session.commit()
    session.refresh(employee)
    return employee


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_employee(
    employee_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
) -> None:
    """Deaktiviert einen Mitarbeiter anstatt ihn hart zu löschen."""
    employee = _get_employee_for_tenant(session, current_user.tenant_id, employee_id)
    employee.is_active = False
    session.add(employee)
    session.commit()
