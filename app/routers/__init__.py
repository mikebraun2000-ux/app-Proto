"""Importe der FastAPI-Router."""

from . import (
    auth,
    billing,
    company_logo,
    dashboard,
    employees,
    invoice_generation,
    invoices,
    offers,
    project_images,
    projects,
    reports,
    user_settings,
    time_entries,
)

__all__ = [
    "auth",
    "billing",
    "company_logo",
    "dashboard",
    "employees",
    "invoice_generation",
    "invoices",
    "offers",
    "project_images",
    "projects",
    "reports",
    "user_settings",
    "time_entries",
]
