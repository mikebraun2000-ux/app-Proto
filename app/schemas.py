"""
Pydantic-Schemas für API-Requests und -Responses.
Definiert die Datenstrukturen für die Kommunikation mit dem Frontend.
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from datetime import date
from app.models import UserRole

# User Schemas
class UserBase(BaseModel):
    """Basis-Schema für Benutzer."""
    username: str
    email: str
    full_name: str
    tenant_id: Optional[int] = None
    role: UserRole = UserRole.MITARBEITER

class UserCreate(UserBase):
    """Schema für die Erstellung neuer Benutzer."""
    password: str

class UserLogin(BaseModel):
    """Schema für Benutzeranmeldung."""
    username: str
    password: str

class UserUpdate(BaseModel):
    """Schema für die Aktualisierung von Benutzern."""
    email: Optional[str] = None
    full_name: Optional[str] = None
    tenant_id: Optional[int] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class User(UserBase):
    """Schema für Benutzer-Responses."""
    id: int
    name: Optional[str] = None
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    """Schema für JWT-Token."""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schema für Token-Daten."""
    username: Optional[str] = None

# Project Schemas
class ProjectBase(BaseModel):
    """Basis-Schema für Projekte."""
    name: str
    description: Optional[str] = None
    address: Optional[str] = None
    client_name: Optional[str] = None
    client_phone: Optional[str] = None
    client_email: Optional[str] = None
    project_type: str = "trockenbau"
    total_area: Optional[float] = None
    estimated_hours: Optional[float] = None
    hourly_rate: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: str = "aktiv"

class ProjectCreate(ProjectBase):
    """Schema für die Erstellung neuer Projekte."""
    pass

class ProjectUpdate(BaseModel):
    """Schema für die Aktualisierung von Projekten."""
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    client_name: Optional[str] = None
    client_phone: Optional[str] = None
    client_email: Optional[str] = None
    project_type: Optional[str] = None
    total_area: Optional[float] = None
    estimated_hours: Optional[float] = None
    hourly_rate: Optional[float] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = None

class Project(ProjectBase):
    """Schema für Projekt-Responses."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Report Schemas
class ReportBase(BaseModel):
    """Basis-Schema für Trockenbau-Berichte."""
    project_id: int
    title: str
    content: Optional[str] = None
    work_type: Optional[str] = None
    status: str = "In Bearbeitung"
    area_completed: Optional[float] = None
    materials_used: Optional[str] = None
    quality_check: Optional[str] = None
    issues_encountered: Optional[str] = None
    next_steps: Optional[str] = None
    progress_percentage: Optional[float] = None

class ReportCreate(BaseModel):
    """Schema für die Erstellung neuer Berichte."""
    project_id: int
    title: str
    content: Optional[str] = None
    report_date: Optional[str] = None  # ISO-Date-String vom Frontend
    work_type: Optional[str] = None
    area_completed: Optional[float] = None
    materials_used: Optional[str] = None
    quality_check: Optional[str] = None
    issues_encountered: Optional[str] = None
    next_steps: Optional[str] = None
    progress_percentage: Optional[float] = None

class ReportUpdate(BaseModel):
    """Schema für die Aktualisierung von Berichten."""
    project_id: Optional[int] = None
    title: Optional[str] = None
    content: Optional[str] = None
    report_date: Optional[str] = None  # ISO-Date-String
    work_type: Optional[str] = None
    status: Optional[str] = None
    area_completed: Optional[float] = None
    materials_used: Optional[str] = None
    quality_check: Optional[str] = None
    issues_encountered: Optional[str] = None
    next_steps: Optional[str] = None
    progress_percentage: Optional[float] = None

class Report(BaseModel):
    """Schema für Bericht-Responses."""
    id: int
    project_id: int
    title: str
    content: Optional[str] = None
    report_date: Optional[datetime] = None  # DateTime-Objekt für Response
    work_type: Optional[str] = None
    status: Optional[str] = None
    area_completed: Optional[float] = None
    materials_used: Optional[str] = None
    quality_check: Optional[str] = None
    issues_encountered: Optional[str] = None
    next_steps: Optional[str] = None
    progress_percentage: Optional[float] = None
    attachments: Optional[List[Dict[str, Any]]] = None  # Anhänge für Bilder
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Tenant Settings Schemas
class TenantSettingsBase(BaseModel):
    company_name: Optional[str] = None
    company_address: Optional[str] = None
    company_phone: Optional[str] = None
    company_fax: Optional[str] = None
    company_email: Optional[str] = None
    company_website: Optional[str] = None
    bank_name: Optional[str] = None
    bank_iban: Optional[str] = None
    bank_bic: Optional[str] = None
    tax_number: Optional[str] = None
    vat_id: Optional[str] = None
    invoice_prefix: Optional[str] = None
    payment_terms_days: Optional[int] = None
    default_currency: Optional[str] = None
    tax_rate_default: Optional[float] = None
    branding_primary_color: Optional[str] = None
    branding_secondary_color: Optional[str] = None
    footer_text: Optional[str] = None


class TenantSettingsUpdate(TenantSettingsBase):
    pass


class TenantSettingsResponse(TenantSettingsBase):
    id: int
    tenant_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserSettingsBase(BaseModel):
    """Gemeinsame Felder für Benutzer-Einstellungen."""

    theme_preference: Optional[str] = None


class UserSettingsUpdate(UserSettingsBase):
    """Schema für Aktualisierung der Benutzer-Einstellungen."""

    pass


class UserSettingsResponse(UserSettingsBase):
    """Antwort-Schema für Benutzer-Einstellungen."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Offer Schemas
class OfferItem(BaseModel):
    """Schema für Angebotspositionen."""
    position: Optional[int] = None
    description: str
    quantity: float
    unit: str = "Stück"
    unit_price: float
    total_price: float

class OfferBase(BaseModel):
    """Basis-Schema für Angebote."""
    project_id: int
    title: str
    description: Optional[str] = None
    client_name: str
    client_address: Optional[str] = None
    total_amount: float
    currency: str = "EUR"
    valid_until: Optional[str] = None  # ISO-Date-String
    items: List[dict]  # Einfache Dictionary-Liste
    status: str = "entwurf"
    auto_generated: bool = False

class OfferCreate(OfferBase):
    """Schema für die Erstellung neuer Angebote."""
    pass

class OfferUpdate(BaseModel):
    """Schema für die Aktualisierung von Angeboten."""
    title: Optional[str] = None
    description: Optional[str] = None
    client_name: Optional[str] = None
    client_address: Optional[str] = None
    total_amount: Optional[float] = None
    currency: Optional[str] = None
    valid_until: Optional[str] = None  # ISO-Date-String
    items: Optional[List[dict]] = None  # Einfache Dictionary-Liste
    status: Optional[str] = None
    auto_generated: Optional[bool] = None

class Offer(BaseModel):
    """Schema für Angebot-Responses."""
    id: int
    project_id: int
    title: str
    description: Optional[str] = None
    client_name: str
    client_address: Optional[str] = None
    total_amount: float
    currency: str = "EUR"
    valid_until: Optional[datetime] = None  # DateTime-Objekt für Response
    items: str  # JSON-String wie in der Datenbank
    status: str = "entwurf"
    auto_generated: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OfferGenerationRequest(BaseModel):
    """Schema für automatische Angebotserstellung."""
    project_id: int
    client_name: Optional[str] = None
    client_address: Optional[str] = None
    currency: str = "EUR"
    items: Optional[List[OfferItem]] = None  # Falls vorgegeben, sonst werden Default-Items generiert

# Employee Schemas
class EmployeeBase(BaseModel):
    """Basis-Schema für Mitarbeiter."""
    user_id: Optional[int] = None
    full_name: str
    position: Optional[str] = None
    hourly_rate: Optional[float] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: bool = True

class EmployeeCreate(EmployeeBase):
    """Schema für die Erstellung neuer Mitarbeiter."""
    pass

class EmployeeUpdate(BaseModel):
    """Schema für die Aktualisierung von Mitarbeitern."""
    full_name: Optional[str] = None
    position: Optional[str] = None
    hourly_rate: Optional[float] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None

class Employee(EmployeeBase):
    """Schema für Mitarbeiter-Responses."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Time Entry Schemas
class TimeEntryCreate(BaseModel):
    """Schema für die Erstellung neuer Stundeneinträge."""
    project_id: int
    employee_id: int
    work_date: str  # ISO-Date-String
    clock_in: Optional[str] = None  # Time-String (HH:MM)
    clock_out: Optional[str] = None  # Time-String (HH:MM)
    break_start: Optional[str] = None  # Time-String (HH:MM)
    break_end: Optional[str] = None  # Time-String (HH:MM)
    total_break_minutes: int = 0
    hours_worked: float
    description: Optional[str] = None
    hourly_rate: Optional[float] = None
    
    class Config:
        json_encoders = {
            str: lambda v: v  # String bleibt String
        }

class TimeEntryUpdate(BaseModel):
    """Schema für die Aktualisierung von Stundeneinträgen."""
    work_date: Optional[str] = None
    clock_in: Optional[str] = None
    clock_out: Optional[str] = None
    project_id: Optional[int] = None
    employee_id: Optional[int] = None
    break_start: Optional[str] = None
    break_end: Optional[str] = None
    total_break_minutes: Optional[int] = None
    hours_worked: Optional[float] = None
    description: Optional[str] = None
    hourly_rate: Optional[float] = None
    edit_reason: Optional[str] = None

class TimeEntry(BaseModel):
    """Schema für Stundeneintrag-Responses."""
    id: int
    project_id: int
    employee_id: int
    work_date: date | str  # ISO-Date-String oder Datum für Response
    clock_in: Optional[str] = None  # Time-String für Response
    clock_out: Optional[str] = None  # Time-String für Response
    break_start: Optional[str] = None  # Time-String für Response
    break_end: Optional[str] = None  # Time-String für Response
    total_break_minutes: int = 0
    hours_worked: float
    description: Optional[str] = None
    hourly_rate: Optional[float] = None
    total_cost: Optional[float] = None
    is_edited: bool = False
    edit_reason: Optional[str] = None
    edited_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Project Image Schemas
class ProjectImageBase(BaseModel):
    """Basis-Schema für Projektbilder."""
    project_id: int
    description: Optional[str] = None
    image_type: str = "progress"

class ProjectImageCreate(ProjectImageBase):
    """Schema für die Erstellung neuer Projektbilder."""
    pass

class ProjectImage(ProjectImageBase):
    """Schema für Projektbild-Responses."""
    id: int
    filename: str
    original_filename: str
    file_path: str
    file_size: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Material Usage Schemas
class MaterialUsageBase(BaseModel):
    """Basis-Schema für Materialverbrauch."""
    project_id: int
    material_name: str
    quantity: float
    unit: str
    unit_price: Optional[float] = None
    usage_date: Optional[datetime] = None

class MaterialUsageCreate(MaterialUsageBase):
    """Schema für die Erstellung neuer Materialverbrauchseinträge."""
    pass

class MaterialUsageUpdate(BaseModel):
    """Schema für die Aktualisierung von Materialverbrauchseinträgen."""
    material_name: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    unit_price: Optional[float] = None
    usage_date: Optional[datetime] = None

class MaterialUsage(MaterialUsageBase):
    """Schema für Materialverbrauch-Responses."""
    id: int
    total_cost: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Invoice Schemas
class InvoiceItem(BaseModel):
    """Schema für Rechnungspositionen."""
    description: str
    quantity: float
    unit: Optional[str] = "Stk"
    unit_price: float
    total_price: Optional[float] = None
    item_type: str = "service"  # "service", "material", "labor"
    labor_cost: Optional[float] = None  # Lohnanteil für UStG §14
    material_cost: Optional[float] = None  # Materialkosten
    service_cost: Optional[float] = None  # Dienstleistungskosten

class InvoiceBase(BaseModel):
    """Basis-Schema für Rechnungen."""
    project_id: int
    offer_id: Optional[int] = None
    invoice_number: str
    title: str
    description: Optional[str] = None
    client_name: str
    client_address: Optional[str] = None
    total_amount: float
    currency: str = "EUR"
    invoice_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    items: List[InvoiceItem]
    status: str = "entwurf"

class InvoiceCreate(InvoiceBase):
    """Schema für die Erstellung neuer Rechnungen."""
    pass

class InvoiceUpdate(BaseModel):
    """Schema für die Aktualisierung von Rechnungen."""
    invoice_number: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    client_name: Optional[str] = None
    client_address: Optional[str] = None
    total_amount: Optional[float] = None
    currency: Optional[str] = None
    invoice_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    items: Optional[List[InvoiceItem]] = None
    status: Optional[str] = None

class Invoice(InvoiceBase):
    """Schema für Rechnung-Responses."""
    id: int
    created_at: datetime
    updated_at: datetime
    items: str  # JSON-String wie in der Datenbank

    class Config:
        from_attributes = True

# Automatische Rechnungsgenerierung Schemas
class InvoiceGenerationRequest(BaseModel):
    """Schema für Rechnungsgenerierungs-Anfrage."""
    project_id: int
    generation_method: str = "hybrid"  # "reports", "offers", "time_entries", "hybrid"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    include_materials: bool = True
    include_labor: bool = True
    tax_rate: float = 19.0  # USt-Satz
    labor_cost_percentage: float = 0.0  # Lohnanteil in Prozent

class InvoiceGenerationData(BaseModel):
    """Schema für Rechnungsgenerierungs-Daten."""
    project: Dict[str, Any]
    time_entries: List[Dict[str, Any]]
    reports: List[Dict[str, Any]]
    offers: List[Dict[str, Any]]
    materials: List[Dict[str, Any]]
    employees: List[Dict[str, Any]]

class InvoiceCalculationResult(BaseModel):
    """Schema für Rechnungsberechnungsergebnis."""
    total_labor_cost: float
    total_material_cost: float
    total_service_cost: float
    subtotal: float
    tax_amount: float
    total_amount: float
    labor_percentage: float
    items: List[InvoiceItem]

# Report Image Schemas
class ReportImageBase(BaseModel):
    """Basis-Schema für Berichtsbilder."""
    filename: str
    original_filename: str
    file_path: str
    file_size: Optional[int] = None
    description: Optional[str] = None
    image_type: str = "progress"

class ReportImageCreate(ReportImageBase):
    """Schema für die Erstellung neuer Berichtsbilder."""
    report_id: int

class ReportImage(ReportImageBase):
    """Schema für Berichtsbild-Responses."""
    id: int
    report_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Company Logo Schemas
class CompanyLogoBase(BaseModel):
    """Basis-Schema für Firmenlogos."""
    filename: str
    original_filename: str
    file_path: str
    file_size: Optional[int] = None
    is_active: bool = True

class CompanyLogoCreate(CompanyLogoBase):
    """Schema für die Erstellung neuer Firmenlogos."""
    pass

class CompanyLogo(CompanyLogoBase):
    """Schema für Firmenlogo-Responses."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Image Upload Schema
class ImageUpload(BaseModel):
    """Schema für Bild-Uploads."""
    filename: str
    content_type: str

