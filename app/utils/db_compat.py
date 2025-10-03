from typing import Optional
from sqlmodel import Session
from sqlalchemy import text
from app.database import engine

TENANT_SETTINGS_LEGACY_COLUMNS = {
    "company_name": "TEXT",
    "company_address": "TEXT",
    "company_phone": "TEXT",
    "company_fax": "TEXT",
    "company_email": "TEXT",
    "company_website": "TEXT",
    "bank_name": "TEXT",
    "bank_iban": "TEXT",
    "bank_bic": "TEXT",
    "tax_number": "TEXT",
    "vat_id": "TEXT",
}


def ensure_tenant_settings_columns(session: Optional[Session] = None) -> None:
    """Fügt fehlende Spalten in legacy-Datenbanken hinzu."""
    external_session = session is not None
    if session is None:
        session = Session(engine)

    try:
        info_rows = session.exec(text("PRAGMA table_info(tenant_settings)")).all()
    except Exception:
        if not external_session:
            session.close()
        return

    existing = {row[1] for row in info_rows}
    altered = False

    for column, ddl in TENANT_SETTINGS_LEGACY_COLUMNS.items():
        if column not in existing:
            session.exec(text(f"ALTER TABLE tenant_settings ADD COLUMN {column} {ddl}"))
            altered = True

    if altered:
        session.commit()

    if not external_session:
        session.close()
