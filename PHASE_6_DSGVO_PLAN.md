# Phase 6: DSGVO-Retention Implementation Plan

## Ziel
Automatische Löschung personenbezogener Daten nach Ablauf der Aufbewahrungsfrist gemäß DSGVO.

## Anforderungen

### DSGVO-relevante Fristen
- **Geschäftliche Dokumente**: 10 Jahre (§147 AO, §257 HGB)
- **Personalakten**: 3 Jahre nach Ausscheiden (§195 BGB)
- **Zeiterfassungsdaten**: 2 Jahre (Nachweispflicht)
- **Einladungs-Token**: 7 Tage (kurze Gültigkeit)
- **Gelöschte Benutzer**: 30 Tage "Soft Delete" (Wiederherstellung)

## Phase 6.1: Retention-Policy Konfiguration

### 1. Neue Tabelle: `tenant_retention_policies`

```python
class TenantRetentionPolicy(SQLModel, table=True):
    __tablename__ = "tenant_retention_policies"
    
    id: int = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenants.id")
    
    # Policy-Typ
    policy_type: str = Field(...)  # "invoices", "time_entries", "users", "invitations"
    
    # Aufbewahrungsfrist in Tagen
    retention_days: int = Field(default=3650)  # 10 Jahre Standard
    
    # Aktivierung
    enabled: bool = Field(default=True)
    
    # Zusätzliche Einstellungen
    delete_method: str = Field(default="soft")  # "soft" oder "hard"
    notify_before_days: int = Field(default=30)  # Benachrichtigung vor Löschung
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### 2. Soft Delete Mechanismus

Alle relevanten Tabellen bekommen:
```python
deleted_at: Optional[datetime] = Field(default=None)
deleted_by: Optional[int] = Field(default=None, foreign_key="users.id")
```

### 3. Standard Retention-Policies

```python
DEFAULT_POLICIES = {
    "invoices": {
        "retention_days": 3650,  # 10 Jahre
        "delete_method": "soft",
        "notify_before_days": 90
    },
    "time_entries": {
        "retention_days": 730,  # 2 Jahre
        "delete_method": "soft",
        "notify_before_days": 30
    },
    "users": {
        "retention_days": 1095,  # 3 Jahre nach letzter Aktivität
        "delete_method": "soft",
        "notify_before_days": 60
    },
    "invitations": {
        "retention_days": 7,  # 7 Tage
        "delete_method": "hard",  # Sofort löschen
        "notify_before_days": 0
    }
}
```

## Phase 6.2: Retention Service implementieren

### 1. Service-Klasse: `RetentionService`

```python
class RetentionService:
    def __init__(self, session: Session):
        self.session = session
    
    async def scan_for_expired_data(self, tenant_id: int) -> Dict[str, int]:
        """Scannt alle Daten eines Tenants auf Ablauf."""
        
    async def soft_delete_expired(self, tenant_id: int, policy_type: str) -> int:
        """Markiert abgelaufene Daten als gelöscht."""
        
    async def hard_delete_soft_deleted(self, tenant_id: int, grace_period_days: int = 30) -> int:
        """Löscht soft-deleted Daten nach Grace Period."""
        
    async def restore_soft_deleted(self, tenant_id: int, entity_type: str, entity_id: int) -> bool:
        """Stellt soft-deleted Daten wieder her."""
        
    async def notify_upcoming_deletions(self, tenant_id: int) -> List[Dict]:
        """Benachrichtigt über bevorstehende Löschungen."""
```

### 2. Scheduled Background Task

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('cron', hour=3, minute=0)  # Täglich um 3 Uhr
async def retention_cleanup_job():
    """Führt Retention-Cleanup für alle Tenants durch."""
    with Session(engine) as session:
        tenants = session.exec(select(Tenant).where(Tenant.status == TenantStatus.ACTIVE)).all()
        
        for tenant in tenants:
            retention_service = RetentionService(session)
            await retention_service.scan_for_expired_data(tenant.id)
```

## Phase 6.3: Admin-UI für Retention-Management

### 1. Frontend-Sektion: "Datenschutz & Retention"

In der Verwaltung einen neuen Bereich:
- **Retention-Policies anzeigen**: Übersicht aller Policies
- **Policy bearbeiten**: Aufbewahrungsfristen anpassen
- **Soft-Deleted Daten**: Liste zum Wiederherstellen
- **Lösch-Historie**: Audit-Log für Löschungen

### 2. API-Endpoints

```python
@router.get("/admin/retention/policies")
async def get_retention_policies()

@router.put("/admin/retention/policies/{policy_type}")
async def update_retention_policy()

@router.get("/admin/retention/soft-deleted")
async def list_soft_deleted_items()

@router.post("/admin/retention/restore/{entity_type}/{entity_id}")
async def restore_deleted_item()

@router.get("/admin/retention/audit-log")
async def get_deletion_audit_log()
```

## Phase 6.4: Audit-Logging

### 1. Neue Tabelle: `retention_audit_log`

```python
class RetentionAuditLog(SQLModel, table=True):
    __tablename__ = "retention_audit_log"
    
    id: int = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenants.id")
    
    action: str  # "soft_delete", "hard_delete", "restore"
    entity_type: str  # "invoice", "user", etc.
    entity_id: int
    
    reason: str  # "retention_policy_expired", "manual_admin_deletion"
    performed_by: Optional[int] = Field(default=None, foreign_key="users.id")
    
    deleted_data_summary: Optional[str]  # JSON mit wichtigen Infos
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

## Phase 6.5: Testing & Validierung

### 1. Unit Tests
- Test: Soft Delete nach Ablauf
- Test: Hard Delete nach Grace Period
- Test: Restore funktioniert
- Test: Audit Log wird geschrieben

### 2. Integration Tests
- Test: Scheduled Job läuft korrekt
- Test: Benachrichtigungen werden versendet
- Test: Admin kann Policies ändern

### 3. Manual Tests
- Test: UI zeigt korrekte Daten
- Test: Wiederherstellung funktioniert
- Test: Löschung ist DSGVO-konform

## Risiken & Mitigation

### Risiko 1: Versehentliche Datenlöschung
- **Mitigation**: Soft Delete + 30 Tage Grace Period
- **Mitigation**: Benachrichtigung 30 Tage vorher
- **Mitigation**: Admin-Restore-Funktion

### Risiko 2: Performance bei großen Datenmengen
- **Mitigation**: Batch-Processing (1000 Datensätze pro Durchlauf)
- **Mitigation**: Scheduled Job läuft nachts
- **Mitigation**: Index auf `deleted_at` Spalte

### Risiko 3: Gesetzliche Anforderungen ändern sich
- **Mitigation**: Konfigurierbare Policies pro Tenant
- **Mitigation**: Dokumentation der gesetzlichen Grundlagen
- **Mitigation**: Admin kann Fristen anpassen

## Zeitplan

- **6.1 Datenmodell**: 2 Stunden
- **6.2 Retention Service**: 3 Stunden
- **6.3 Admin-UI**: 2 Stunden
- **6.4 Audit-Logging**: 1 Stunde
- **6.5 Testing**: 2 Stunden

**Gesamt**: ~10 Stunden

## Offene Fragen

1. Sollen Backups auch automatisch gelöscht werden?
2. Wie sollen Benachrichtigungen versendet werden (Email, In-App)?
3. Sollen Benutzer selbst Daten löschen können?
4. Export vor Löschung anbieten (DSGVO Auskunftsrecht)?

