"""
Router für Dashboard-Daten.
Bietet aggregierte Statistiken und Übersichten.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from typing import Dict, Any
from datetime import datetime, timedelta
from ..database import get_session
from ..models import Project, Invoice, TimeEntry, Report, Offer
from ..auth import get_current_user

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
        # Projekte
        total_projects = session.exec(select(func.count(Project.id))).one()
        active_projects = session.exec(
            select(func.count(Project.id)).where(Project.status == "aktiv")
        ).one()
        
        # Rechnungen
        total_invoices = session.exec(select(func.count(Invoice.id))).one()
        total_revenue = session.exec(select(func.sum(Invoice.total_amount))).one() or 0
        
        # Offene Rechnungen (bezahlt == False)
        open_invoices = session.exec(
            select(func.count(Invoice.id)).where(Invoice.status != "bezahlt")
        ).one()
        
        # Angebote
        total_offers = session.exec(select(func.count(Offer.id))).one()
        pending_offers = session.exec(
            select(func.count(Offer.id)).where(Offer.status == "offen")
        ).one()
        
        # Berichte
        total_reports = session.exec(select(func.count(Report.id))).one()
        
        # Stundeneinträge
        total_hours = session.exec(select(func.sum(TimeEntry.hours_worked))).one() or 0
        
        # Aktuelle Woche
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        hours_this_week = session.exec(
            select(func.sum(TimeEntry.hours_worked)).where(
                TimeEntry.work_date >= week_start.date(),
                TimeEntry.work_date <= week_end.date()
            )
        ).one() or 0
        
        # Aktueller Monat
        month_start = today.replace(day=1)
        revenue_this_month = session.exec(
            select(func.sum(Invoice.total_amount)).where(
                Invoice.invoice_date >= month_start
            )
        ).one() or 0
        
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

