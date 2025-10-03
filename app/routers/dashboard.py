"""
Router für Dashboard-Daten.
Bietet aggregierte Statistiken und Übersichten.
"""

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func

from ..auth import get_current_user
from ..database import get_session
from ..models import Invoice, Offer, Project, Report, TimeEntry

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/")
async def get_dashboard_data(
    session: Session = Depends(get_session),
    current_user = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Dashboard-Statistiken abrufen.
    
    Returns:
        Dict mit verschiedenen Statistiken
    """
    try:
        tenant_id = current_user.tenant_id

        def scalar(query):
            value = session.exec(query).one()
            return value if value is not None else 0

        # Projekte
        total_projects = scalar(select(func.count()).select_from(Project).where(Project.tenant_id == tenant_id))
        active_projects = scalar(
            select(func.count()).select_from(Project).where(
                Project.tenant_id == tenant_id, Project.status == "aktiv"
            )
        )

        # Rechnungen
        total_invoices = scalar(select(func.count()).select_from(Invoice).where(Invoice.tenant_id == tenant_id))
        total_revenue = scalar(select(func.sum(Invoice.total_amount)).where(Invoice.tenant_id == tenant_id))

        # Offene Rechnungen (bezahlt == False)
        open_invoices = scalar(
            select(func.count()).select_from(Invoice).where(
                Invoice.tenant_id == tenant_id, Invoice.status != "bezahlt"
            )
        )

        # Angebote
        total_offers = scalar(select(func.count()).select_from(Offer).where(Offer.tenant_id == tenant_id))
        pending_offers = scalar(
            select(func.count()).select_from(Offer).where(
                Offer.tenant_id == tenant_id, Offer.status == "offen"
            )
        )

        # Berichte
        total_reports = scalar(select(func.count()).select_from(Report).where(Report.tenant_id == tenant_id))

        # Stundeneinträge
        total_hours = scalar(select(func.sum(TimeEntry.hours_worked)).where(TimeEntry.tenant_id == tenant_id))
        
        # Aktuelle Woche
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        hours_this_week = scalar(
            select(func.sum(TimeEntry.hours_worked)).where(
                TimeEntry.tenant_id == tenant_id,
                TimeEntry.work_date >= week_start.date(),
                TimeEntry.work_date <= week_end.date(),
            )
        )
        
        # Aktueller Monat
        month_start = today.replace(day=1)
        revenue_this_month = scalar(
            select(func.sum(Invoice.total_amount)).where(
                Invoice.tenant_id == tenant_id,
                Invoice.invoice_date >= month_start,
            )
        )
        
        return {
            "projects": {
                "total": total_projects,
                "active": active_projects
            },
            "invoices": {
                "total": total_invoices,
                "open": open_invoices,
                "total_revenue": float(total_revenue)
            },
            "offers": {
                "total": total_offers,
                "pending": pending_offers
            },
            "reports": {
                "total": total_reports
            },
            "time_tracking": {
                "total_hours": float(total_hours),
                "hours_this_week": float(hours_this_week)
            },
            "revenue": {
                "this_month": float(revenue_this_month),
                "total": float(total_revenue)
            }
        }
    
    except Exception as e:
        print(f"Fehler beim Laden der Dashboard-Daten: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Fehler beim Laden der Dashboard-Daten: {str(e)}"
        )

