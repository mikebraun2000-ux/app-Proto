"""
SQLModel-Datenmodelle für die Bau-Dokumentations-App.
Definiert die Datenbankstruktur für Projekte, Berichte und Angebote.
"""

from sqlmodel import SQLModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum

class UserRole(str, Enum):
    """Benutzerrollen."""
    MITARBEITER = "mitarbeiter"
    BUCHHALTER = "buchhalter" 
    ADMIN = "admin"

class TenantStatus(str, Enum):
    ACTIVE = "active"
    TRIALING = "trialing"
    PAST_DUE = "past_due"
    SUSPENDED = "suspended"
    CANCELED = "canceled"


class Tenant(SQLModel, table=True):
    """
    Mandanten-Stammdaten.
    """
    __tablename__ = "tenant"
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=150, description="Mandantenname")
    status: TenantStatus = Field(default=TenantStatus.ACTIVE, description="Interner Mandantenstatus")
    subscription_status: str = Field(default="inactive", max_length=50, description="Stripe-Abo-Status")
    stripe_customer_id: Optional[str] = Field(default=None, max_length=120, description="Stripe Customer ID")
    stripe_subscription_id: Optional[str] = Field(default=None, max_length=120, description="Stripe Subscription ID")
    current_period_end: Optional[datetime] = Field(default=None, description="Ende der aktuellen Periode")
    trial_end: Optional[datetime] = Field(default=None, description="Ende der Testphase")
    last_payment_status: Optional[str] = Field(default=None, max_length=50, description="Letztes Zahlungsereignis")
    plan_price_id: Optional[str] = Field(default=None, max_length=120, description="Stripe Price ID")
    seats_limit: Optional[int] = Field(default=None, description="Limit für aktive Benutzer")
    projects_limit: Optional[int] = Field(default=None, description="Limit für Projekte")
    suspended_at: Optional[datetime] = Field(default=None, description="Zeitpunkt der Sperrung")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Erstellungszeitpunkt")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Letzte Aktualisierung")


class TenantSettings(SQLModel, table=True):
    """
    Konfiguration pro Mandant (Branding, Rechnungen, Compliance).
    """
    __tablename__ = "tenant_settings"
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True, unique=True, description="Zugehöriger Mandant")
    company_name: Optional[str] = Field(default="Trockenbau Stuttgart GmbH", max_length=150, description="Firmenname")
    company_address: Optional[str] = Field(default="Musterstraße 123, 70173 Stuttgart", max_length=400, description="Firmenadresse")
    company_phone: Optional[str] = Field(default="0711-123456", max_length=30, description="Telefonnummer")
    company_fax: Optional[str] = Field(default="0711-123457", max_length=30, description="Faxnummer")
    company_email: Optional[str] = Field(default="info@trockenbau-stuttgart.de", max_length=120, description="E-Mail-Adresse")
    company_website: Optional[str] = Field(default="https://www.trockenbau-stuttgart.de", max_length=200, description="Website")
    bank_name: Optional[str] = Field(default="Musterbank Stuttgart", max_length=120, description="Bankname")
    bank_iban: Optional[str] = Field(default="DE12 3456 7890 1234 5678 90", max_length=40, description="IBAN")
    bank_bic: Optional[str] = Field(default="GENODEF1S02", max_length=20, description="BIC")
    tax_number: Optional[str] = Field(default="12/345/67890", max_length=50, description="Steuernummer")
    vat_id: Optional[str] = Field(default="DE123456789", max_length=50, description="USt-IdNr.")
    invoice_prefix: Optional[str] = Field(default="INV", max_length=20, description="Standard-Rechnungspräfix")
    invoice_next_number: int = Field(default=1, description="Nächste Rechnungsnummer")
    payment_terms_days: int = Field(default=14, description="Zahlungsziel in Tagen")
    default_currency: str = Field(default="EUR", max_length=3, description="Standardwährung")
    tax_rate_default: Optional[float] = Field(default=None, description="Standard-Steuersatz")
    branding_primary_color: Optional[str] = Field(default=None, max_length=20, description="Primärfarbe")
    branding_secondary_color: Optional[str] = Field(default=None, max_length=20, description="Sekundärfarbe")
    footer_text: Optional[str] = Field(default=None, max_length=500, description="Footer-Text für PDFs")
    retention_days_time_entries: Optional[int] = Field(default=None, description="Aufbewahrungstage Zeitdaten")
    retention_days_logs: Optional[int] = Field(default=None, description="Aufbewahrungstage Logs")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Erstellungszeitpunkt")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Letzte Aktualisierung")


class ReportStatus(str, Enum):
    """Berichtsstatus-Kategorien."""
    BERICHT = "BERICHT"
    MELDUNG = "MELDUNG"
    SCHADEN = "SCHADEN"
    VERZOEGERUNG = "VERZOEGERUNG"
    QUALITAET = "QUALITAET"
    SICHERHEIT = "SICHERHEIT"
    MATERIAL = "MATERIAL"
    SONSTIGES = "SONSTIGES"

class User(SQLModel, table=True):
    """
    Datenmodell für Benutzer mit Authentifizierung.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=50, unique=True, description="Benutzername")
    email: str = Field(max_length=100, unique=True, description="E-Mail-Adresse")
    hashed_password: str = Field(max_length=255, description="Gehashtes Passwort")
    full_name: str = Field(max_length=100, description="Vollständiger Name")
    tenant_id: int = Field(default=1, foreign_key="tenant.id", index=True, description="Mandant")
    role: UserRole = Field(default=UserRole.MITARBEITER, description="Benutzerrolle")
    is_active: bool = Field(default=True, description="Aktiv")
    last_login: Optional[datetime] = Field(default=None, description="Letzte Anmeldung")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Erstellungsdatum")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Letzte Aktualisierung")

class Project(SQLModel, table=True):
    """
    Datenmodell für Bauprojekte (speziell für Trockenbau).
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(default=1, foreign_key="tenant.id", index=True, description="Mandant")
    name: str = Field(max_length=100, description="Projektname")
    description: Optional[str] = Field(default=None, max_length=500, description="Projektbeschreibung")
    address: Optional[str] = Field(default=None, max_length=200, description="Projektadresse")
    client_name: Optional[str] = Field(default=None, max_length=100, description="Kundenname")
    client_phone: Optional[str] = Field(default=None, max_length=20, description="Kundentelefon")
    client_email: Optional[str] = Field(default=None, max_length=100, description="Kunden-E-Mail")
    project_type: str = Field(default="trockenbau", max_length=50, description="Projekttyp")
    total_area: Optional[float] = Field(default=None, description="Gesamtfläche in m²")
    estimated_hours: Optional[float] = Field(default=None, description="Geschätzte Arbeitsstunden")
    hourly_rate: Optional[float] = Field(default=None, description="Stundensatz")
    start_date: Optional[datetime] = Field(default=None, description="Projektstart")
    end_date: Optional[datetime] = Field(default=None, description="Projektende")
    status: str = Field(default="aktiv", max_length=20, description="Projektstatus")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Erstellungsdatum")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Letzte Aktualisierung")

class Report(SQLModel, table=True):
    """
    Datenmodell für Trockenbau-Berichte.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(default=1, foreign_key="tenant.id", index=True, description="Mandant")
    project_id: int = Field(foreign_key="project.id", description="Zugehöriges Projekt")
    title: str = Field(max_length=100, description="Berichtstitel")
    content: Optional[str] = Field(default=None, description="Berichtsinhalt")
    report_date: datetime = Field(default_factory=datetime.utcnow, description="Berichtsdatum")
    work_type: Optional[str] = Field(default=None, max_length=100, description="Arbeitsart (z.B. Gipskarton, Dämmung)")
    status: str = Field(default="In Bearbeitung", description="Berichtsstatus")
    area_completed: Optional[float] = Field(default=None, description="Bearbeitete Fläche in m²")
    materials_used: Optional[str] = Field(default=None, description="Verwendete Materialien")
    quality_check: Optional[str] = Field(default=None, max_length=20, description="Qualitätskontrolle")
    issues_encountered: Optional[str] = Field(default=None, description="Aufgetretene Probleme")
    next_steps: Optional[str] = Field(default=None, description="Nächste Schritte")
    progress_percentage: Optional[float] = Field(default=None, description="Fortschritt in Prozent")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Erstellungsdatum")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Letzte Aktualisierung")

class Employee(SQLModel, table=True):
    """
    Datenmodell für Mitarbeiter.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(default=1, foreign_key="tenant.id", index=True, description="Mandant")
    user_id: int = Field(default=0, foreign_key="user.id", index=True, description="Verknüpfter Benutzer")
    full_name: str = Field(max_length=100, description="Mitarbeitername")
    position: Optional[str] = Field(default=None, max_length=50, description="Position")
    hourly_rate: Optional[float] = Field(default=None, description="Stundensatz")
    phone: Optional[str] = Field(default=None, max_length=20, description="Telefonnummer")
    email: Optional[str] = Field(default=None, max_length=100, description="E-Mail")
    is_active: bool = Field(default=True, description="Aktiv")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Erstellungsdatum")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Letzte Aktualisierung")

class TimeEntry(SQLModel, table=True):
    """
    Datenmodell für Stundenerfassung mit Ein-/Austempelsystem.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(default=1, foreign_key="tenant.id", index=True, description="Mandant")
    project_id: int = Field(foreign_key="project.id", description="Zugehöriges Projekt")
    employee_id: int = Field(foreign_key="employee.id", description="Mitarbeiter")
    work_date: date = Field(description="Arbeitstag")
    clock_in: Optional[str] = Field(default=None, description="Einstempelzeit (HH:MM)")
    clock_out: Optional[str] = Field(default=None, description="Austempelzeit (HH:MM)")
    break_start: Optional[str] = Field(default=None, description="Pausenbeginn (HH:MM)")
    break_end: Optional[str] = Field(default=None, description="Pausenende (HH:MM)")
    total_break_minutes: int = Field(default=0, description="Gesamte Pausenzeit in Minuten")
    hours_worked: float = Field(description="Gearbeitete Stunden")
    description: Optional[str] = Field(default=None, description="Arbeitsbeschreibung")
    hourly_rate: Optional[float] = Field(default=None, description="Stundensatz")
    total_cost: Optional[float] = Field(default=None, description="Gesamtkosten")
    is_edited: bool = Field(default=False, description="Wurde bearbeitet")
    edit_reason: Optional[str] = Field(default=None, description="Grund für Bearbeitung")
    edited_by: Optional[str] = Field(default=None, description="Wer hat bearbeitet")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Erstellungsdatum")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Letzte Aktualisierung")

class ProjectImage(SQLModel, table=True):
    """
    Datenmodell für Projektbilder.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(default=1, foreign_key="tenant.id", index=True, description="Mandant")
    project_id: int = Field(foreign_key="project.id", description="Zugehöriges Projekt")
    filename: str = Field(max_length=255, description="Dateiname")
    original_filename: str = Field(max_length=255, description="Originaler Dateiname")
    file_path: str = Field(max_length=500, description="Dateipfad")
    file_size: Optional[int] = Field(default=None, description="Dateigröße in Bytes")
    description: Optional[str] = Field(default=None, description="Bildbeschreibung")
    image_type: str = Field(default="progress", max_length=20, description="Bildtyp (progress, before, after, issue)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Erstellungsdatum")

class MaterialUsage(SQLModel, table=True):
    """
    Datenmodell für Materialverbrauch.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(default=1, foreign_key="tenant.id", index=True, description="Mandant")
    project_id: int = Field(foreign_key="project.id", description="Zugehöriges Projekt")
    material_name: str = Field(max_length=100, description="Materialname")
    quantity: float = Field(description="Menge")
    unit: str = Field(max_length=20, description="Einheit")
    unit_price: Optional[float] = Field(default=None, description="Einzelpreis")
    total_cost: Optional[float] = Field(default=None, description="Gesamtkosten")
    usage_date: datetime = Field(default_factory=datetime.utcnow, description="Verbrauchsdatum")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Erstellungsdatum")

class Invoice(SQLModel, table=True):
    """
    Datenmodell für Rechnungen.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(default=1, foreign_key="tenant.id", index=True, description="Mandant")
    project_id: int = Field(foreign_key="project.id", description="Zugehöriges Projekt")
    offer_id: Optional[int] = Field(default=None, foreign_key="offer.id", description="Zugehöriges Angebot")
    invoice_number: str = Field(max_length=50, description="Rechnungsnummer")
    title: str = Field(max_length=100, description="Rechnungstitel")
    description: Optional[str] = Field(default=None, description="Rechnungsbeschreibung")
    client_name: str = Field(max_length=100, description="Kundenname")
    client_address: Optional[str] = Field(default=None, max_length=200, description="Kundenadresse")
    total_amount: float = Field(description="Gesamtbetrag")
    currency: str = Field(default="EUR", max_length=3, description="Währung")
    invoice_date: datetime = Field(default_factory=datetime.utcnow, description="Rechnungsdatum")
    due_date: Optional[datetime] = Field(default=None, description="Fälligkeitsdatum")
    items: str = Field(description="Rechnungspositionen als JSON-String")
    status: str = Field(default="entwurf", max_length=20, description="Rechnungsstatus")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Erstellungsdatum")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Letzte Aktualisierung")

class Offer(SQLModel, table=True):
    """
    Datenmodell für Angebote.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(default=1, foreign_key="tenant.id", index=True, description="Mandant")
    project_id: int = Field(foreign_key="project.id", description="Zugehöriges Projekt")
    title: str = Field(max_length=100, description="Angebotstitel")
    description: Optional[str] = Field(default=None, description="Angebotsbeschreibung")
    client_name: str = Field(max_length=100, description="Kundenname")
    client_address: Optional[str] = Field(default=None, max_length=200, description="Kundenadresse")
    total_amount: float = Field(description="Gesamtbetrag")
    currency: str = Field(default="EUR", max_length=3, description="Währung")
    valid_until: Optional[datetime] = Field(default=None, description="Gültigkeitsdatum")
    items: str = Field(description="Angebotspositionen als JSON-String")
    status: str = Field(default="entwurf", max_length=20, description="Angebotsstatus")
    auto_generated: bool = Field(default=False, description="Wurde das Angebot automatisch generiert?")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Erstellungsdatum")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Letzte Aktualisierung")

class ReportImage(SQLModel, table=True):
    """
    Datenmodell für Berichtsbilder.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(default=1, foreign_key="tenant.id", index=True, description="Mandant")
    report_id: int = Field(foreign_key="report.id", description="Zugehöriger Bericht")
    filename: str = Field(max_length=255, description="Dateiname")
    original_filename: str = Field(max_length=255, description="Originaler Dateiname")
    file_path: str = Field(max_length=500, description="Dateipfad")
    file_size: Optional[int] = Field(default=None, description="Dateigröße in Bytes")
    description: Optional[str] = Field(default=None, description="Bildbeschreibung")
    image_type: str = Field(default="progress", max_length=20, description="Bildtyp (progress, before, after, issue)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Erstellungsdatum")

class CompanyLogo(SQLModel, table=True):
    """
    Datenmodell für Firmenlogos.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(default=1, foreign_key="tenant.id", index=True, description="Mandant")
    user_id: int = Field(foreign_key="user.id", description="Zugehöriger Admin-Benutzer")
    filename: str = Field(max_length=255, description="Dateiname")
    original_filename: str = Field(max_length=255, description="Originaler Dateiname")
    file_path: str = Field(max_length=500, description="Dateipfad")
    file_size: Optional[int] = Field(default=None, description="Dateigröße in Bytes")
    is_active: bool = Field(default=True, description="Aktives Logo")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Erstellungsdatum")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Letzte Aktualisierung")


class TenantInvitation(SQLModel, table=True):
    """
    Einladungen für neue Benutzer zu einem Mandanten.
    """
    __tablename__ = "tenant_invitation"
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", index=True, description="Zugehöriger Mandant")
    email: str = Field(max_length=255, index=True, description="E-Mail-Adresse des Eingeladenen")
    token_hash: str = Field(max_length=64, description="Gehashtes Einladungstoken")
    role: UserRole = Field(default=UserRole.MITARBEITER, description="Rolle des Eingeladenen")
    invited_by: Optional[int] = Field(default=None, foreign_key="user.id", description="Einladender Benutzer")
    accepted_at: Optional[datetime] = Field(default=None, description="Zeitpunkt der Annahme")
    expires_at: datetime = Field(description="Ablaufzeitpunkt der Einladung")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Erstellungsdatum")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Letzte Aktualisierung")


