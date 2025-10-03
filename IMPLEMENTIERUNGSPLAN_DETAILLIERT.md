# 🚀 Detaillierter Implementierungsplan - Bau-Dokumentations-App

**Erstellt am:** 3. Oktober 2025  
**Version:** 1.0  
**Status:** Bereit zur Umsetzung

---

## 📋 Übersicht

Dieser Plan beschreibt **exakt**, wie die kritischen Verbesserungen umgesetzt werden.
Jeder Schritt enthält:
- ✅ Konkrete Code-Beispiele
- ✅ Befehle zum Kopieren
- ✅ Erwartete Ergebnisse
- ✅ Test-Anweisungen
- ✅ Zeitaufwand-Schätzung

---

# PHASE 1: SECURITY-FIXES (Woche 1)

**Zeitaufwand:** 40 Stunden (1 Woche Vollzeit)  
**Priorität:** ⚠️ KRITISCH  
**Ziel:** System produktionssicher machen

---

## 1.1 Passwort-Hashing auf Argon2 umstellen (4h)

### Schritt 1: Dependencies installieren (5min)

```bash
cd C:\Users\Michael\Tommy\backend

# Aktiviere venv
.\venv\Scripts\activate

# Installiere Passwort-Hashing-Bibliotheken
pip install passlib[argon2]==1.7.4
pip install argon2-cffi==23.1.0

# Requirements aktualisieren
pip freeze | Select-String -Pattern "passlib|argon2" >> requirements_new.txt
```

**Erwartetes Ergebnis:**
```
Successfully installed passlib-1.7.4 argon2-cffi-23.1.0
```

### Schritt 2: Auth-Modul aktualisieren (30min)

**Datei:** `app/auth.py`

```python
"""
Authentifizierung und Autorisierung für die Bau-Dokumentations-App.
Implementiert JWT-basierte Authentifizierung mit rollenbasierten Berechtigungen.
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext  # ✅ NEU!
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from app.database import get_session
from app.models import User, UserRole
from app.schemas import TokenData
import os  # ✅ NEU!

# Konfiguration
SECRET_KEY = os.getenv("SECRET_KEY")  # ✅ NEU: Aus ENV!
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY muss in .env gesetzt sein!")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ✅ NEU: Modernes Passwort-Hashing
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],  # Argon2 primär, bcrypt als Fallback
    deprecated="auto",  # Alte Hashes automatisch als deprecated markieren
    argon2__memory_cost=65536,  # 64 MB RAM
    argon2__time_cost=3,  # 3 Iterationen
    argon2__parallelism=4  # 4 Threads
)

# HTTP Bearer Token
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Überprüft ein Passwort gegen den Hash.
    
    Unterstützt:
    - Argon2 (neu, sicher)
    - Bcrypt (Fallback)
    - SHA256 (DEPRECATED, nur für Migration)
    """
    # Versuche moderne Hashes (Argon2/Bcrypt)
    try:
        if pwd_context.verify(plain_password, hashed_password):
            return True
    except Exception:
        pass
    
    # ⚠️ DEPRECATED: SHA256-Fallback (nur für Migration!)
    if hashed_password.startswith("sha256:"):
        import hashlib
        expected_hash = "sha256:" + hashlib.sha256(plain_password.encode()).hexdigest()
        if expected_hash == hashed_password:
            # TODO: Hash im Hintergrund auf Argon2 aktualisieren
            return True
    
    # Letzter Fallback: Klartext (sollte nie vorkommen!)
    if plain_password == "admin123" and hashed_password == plain_password:
        return True
    
    return False

def get_password_hash(password: str) -> str:
    """
    Erstellt einen sicheren Hash für ein Passwort.
    Verwendet Argon2 (memory-hard, GPU-resistent).
    """
    return pwd_context.hash(password)

def needs_rehash(hashed_password: str) -> bool:
    """
    Prüft, ob ein Hash aktualisiert werden sollte.
    """
    return pwd_context.needs_update(hashed_password)

# Rest des Codes bleibt gleich...
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Erstellt einen JWT-Token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[TokenData]:
    """Überprüft einen JWT-Token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return TokenData(username=username)
    except JWTError:
        return None

def get_user_by_username(session: Session, username: str) -> Optional[User]:
    """Holt einen Benutzer anhand des Benutzernamens."""
    statement = select(User).where(User.username == username)
    return session.exec(statement).first()

def authenticate_user(session: Session, username: str, password: str) -> Optional[User]:
    """
    Authentifiziert einen Benutzer.
    Aktualisiert automatisch alte Hashes auf Argon2.
    """
    user = get_user_by_username(session, username)
    if not user:
        return None
    
    if not verify_password(password, user.hashed_password):
        return None
    
    # ✅ NEU: Automatisches Rehashing alter Passwörter
    if needs_rehash(user.hashed_password):
        user.hashed_password = get_password_hash(password)
        session.add(user)
        session.commit()
        print(f"Password hash updated for user: {username}")  # Wird später durch Logging ersetzt
    
    return user

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    """Holt den aktuellen Benutzer aus dem Token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = verify_token(credentials.credentials)
    if token_data is None:
        raise credentials_exception
    
    user = get_user_by_username(session, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def require_role(required_role: UserRole):
    """Dependency für rollenbasierte Berechtigungen."""
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker

def require_admin(current_user: User = Depends(get_current_user)):
    """Dependency für Admin-Berechtigung."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def require_employee_or_admin(current_user: User = Depends(get_current_user)):
    """Dependency für Mitarbeiter oder Admin."""
    if current_user.role not in [UserRole.MITARBEITER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employee or admin access required"
        )
    return current_user

def require_buchhalter_or_admin(current_user: User = Depends(get_current_user)):
    """Dependency für Buchhalter oder Admin."""
    if current_user.role not in [UserRole.BUCHHALTER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Buchhalter or admin access required"
        )
    return current_user
```

### Schritt 3: .env-Datei erstellen (5min)

**Datei:** `.env` (erstellen im Projekt-Root)

```bash
# Generiere einen sicheren SECRET_KEY
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"

# Kopiere die Ausgabe in .env:
```

**Datei:** `.env`
```env
# Security
SECRET_KEY=<hier den generierten Key einfügen>

# Database
DATABASE_URL=sqlite:///./database.db

# Stripe (Test)
STRIPE_TEST_PUBLISHABLE_KEY=pk_test_51SDaKGQpDeiCy5Mxk5mxhyy7ZmmfbmoyOsJvPDjIByawgMUU5Hy6ALpOjCzmRXcyY8Xs0C68qnR5V796iOp02rjV00xqAqExEi
STRIPE_TEST_SECRET_KEY=<hier dein rotierter Test-Secret-Key>
STRIPE_ACTIVE_PRICE_ID=price_1SDaPGQpDeiCy5Mxx8VOvW4t

# Feature Flags
FEATURE_MULTI_TENANT=true
```

### Schritt 4: .gitignore aktualisieren (2min)

**Datei:** `.gitignore` (ergänzen)

```gitignore
# Secrets
.env
.env.local
.env.*.local

# Database
*.db
!database_backup*.db  # Backups dürfen committet werden (nur für Dev!)

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
venv311/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
.cursor/

# Logs
*.log
backend_server.log
backend_server.err

# OS
.DS_Store
Thumbs.db
```

### Schritt 5: Passwort-Migrations-Skript (1h)

**Datei:** `migrate_passwords_to_argon2.py` (neu erstellen)

```python
"""
Migriert alle Benutzer-Passwörter von SHA256 auf Argon2.

Achtung: Nur SHA256-Hashes können migriert werden.
Benutzer mit unbekannten Hashes müssen manuell zurückgesetzt werden.
"""

from sqlmodel import create_engine, Session, select
from app.models import User
from app.auth import get_password_hash, needs_rehash
import sys

DATABASE_URL = "sqlite:///./database.db"

def migrate_passwords():
    """Migriert alle Passwörter auf Argon2."""
    engine = create_engine(DATABASE_URL)
    
    print("🔐 Starte Passwort-Migration...")
    print("=" * 60)
    
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        
        print(f"📊 Gefunden: {len(users)} Benutzer")
        print()
        
        migrated = 0
        already_secure = 0
        manual_reset_needed = []
        
        for user in users:
            print(f"👤 Benutzer: {user.username} (ID: {user.id})")
            
            # Prüfe, ob Hash bereits modern ist
            if user.hashed_password.startswith("$argon2") or user.hashed_password.startswith("$2b$"):
                print("   ✅ Bereits Argon2/Bcrypt")
                already_secure += 1
                continue
            
            # SHA256-Hash erkannt
            if user.hashed_password.startswith("sha256:"):
                # Benutzer muss sich einmalig mit altem Passwort anmelden
                # Dann wird automatisch auf Argon2 aktualisiert (siehe authenticate_user)
                print("   ⚠️  SHA256 erkannt - wird bei nächstem Login aktualisiert")
                migrated += 1
                continue
            
            # Unbekanntes Format
            print("   ❌ Unbekanntes Hash-Format - MANUELLER RESET NÖTIG!")
            manual_reset_needed.append(user.username)
        
        print()
        print("=" * 60)
        print(f"✅ Bereits sicher: {already_secure}")
        print(f"⚠️  Automatisch bei Login: {migrated}")
        print(f"❌ Manueller Reset nötig: {len(manual_reset_needed)}")
        
        if manual_reset_needed:
            print()
            print("⚠️  Folgende Benutzer benötigen Passwort-Reset:")
            for username in manual_reset_needed:
                print(f"   - {username}")
            print()
            print("Führe aus:")
            print(f"  python reset_password.py <username> <neues_passwort>")
        
        print()
        print("💡 Hinweis:")
        print("   Benutzer mit SHA256-Hashes werden automatisch beim")
        print("   nächsten Login auf Argon2 aktualisiert.")
        print()
        print("✅ Migration abgeschlossen!")

if __name__ == "__main__":
    try:
        migrate_passwords()
    except Exception as e:
        print(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
```

### Schritt 6: Passwort-Reset-Skript (30min)

**Datei:** `reset_password.py` (neu erstellen)

```python
"""
Setzt das Passwort eines Benutzers zurück.

Verwendung:
    python reset_password.py <username> <neues_passwort>
"""

from sqlmodel import create_engine, Session, select
from app.models import User
from app.auth import get_password_hash
import sys

DATABASE_URL = "sqlite:///./database.db"

def reset_password(username: str, new_password: str):
    """Setzt Passwort eines Benutzers zurück."""
    engine = create_engine(DATABASE_URL)
    
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == username)).first()
        
        if not user:
            print(f"❌ Benutzer '{username}' nicht gefunden!")
            return False
        
        # Passwort-Validierung
        if len(new_password) < 8:
            print("❌ Passwort muss mindestens 8 Zeichen lang sein!")
            return False
        
        # Neuen Hash erstellen
        user.hashed_password = get_password_hash(new_password)
        session.add(user)
        session.commit()
        
        print(f"✅ Passwort für '{username}' erfolgreich zurückgesetzt!")
        print(f"   Neuer Hash: {user.hashed_password[:50]}...")
        return True

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Verwendung: python reset_password.py <username> <passwort>")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    if reset_password(username, password):
        sys.exit(0)
    else:
        sys.exit(1)
```

### Schritt 7: Migration durchführen (30min)

```bash
# 1. Backup erstellen
python -c "import shutil; from datetime import datetime; shutil.copy('database.db', f'database_backup_{datetime.now().strftime(\"%Y%m%d_%H%M%S\")}.db')"

# 2. Migration ausführen
python migrate_passwords_to_argon2.py

# 3. Admin-Passwort neu setzen (mit sicherem Passwort!)
python reset_password.py admin "NeuesSicheresPasswort123!"

# 4. Test-Login
python -c "
from app.auth import authenticate_user
from app.database import get_session
from sqlmodel import Session

with next(get_session()) as session:
    user = authenticate_user(session, 'admin', 'NeuesSicheresPasswort123!')
    if user:
        print('✅ Login erfolgreich!')
        print(f'Hash-Typ: {user.hashed_password[:10]}...')
    else:
        print('❌ Login fehlgeschlagen!')
"
```

### Schritt 8: Tests schreiben (1h)

**Datei:** `tests/unit/test_auth_security.py` (neu erstellen)

```python
"""
Unit-Tests für Authentifizierungs-Sicherheit.
"""

import pytest
from app.auth import get_password_hash, verify_password, needs_rehash

def test_password_hashing_is_secure():
    """Passwort-Hashing verwendet Argon2 (erkennbar am $argon2-Präfix)."""
    password = "test_password_123"
    hashed = get_password_hash(password)
    
    assert hashed.startswith("$argon2"), "Hash sollte Argon2 verwenden"
    assert password not in hashed, "Klartext-Passwort darf nicht im Hash sein"

def test_password_verification_works():
    """Passwort-Verifizierung funktioniert korrekt."""
    password = "correct_password"
    hashed = get_password_hash(password)
    
    assert verify_password(password, hashed), "Korrektes Passwort sollte verifiziert werden"
    assert not verify_password("wrong_password", hashed), "Falsches Passwort sollte abgelehnt werden"

def test_same_password_produces_different_hashes():
    """Gleiche Passwörter erzeugen unterschiedliche Hashes (Salt)."""
    password = "same_password"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)
    
    assert hash1 != hash2, "Hashes sollten unterschiedlich sein (Salt!)"
    assert verify_password(password, hash1), "Beide Hashes sollten verifizierbar sein"
    assert verify_password(password, hash2)

def test_legacy_sha256_hash_still_works():
    """Legacy SHA256-Hashes werden noch akzeptiert (Migration)."""
    import hashlib
    password = "admin123"
    legacy_hash = "sha256:" + hashlib.sha256(password.encode()).hexdigest()
    
    assert verify_password(password, legacy_hash), "Legacy-Hash sollte noch funktionieren"

def test_legacy_hash_needs_rehash():
    """Legacy-Hashes werden als 'needs rehash' erkannt."""
    import hashlib
    password = "admin123"
    legacy_hash = "sha256:" + hashlib.sha256(password.encode()).hexdigest()
    
    assert needs_rehash(legacy_hash), "Legacy-Hash sollte Rehash benötigen"

def test_modern_hash_does_not_need_rehash():
    """Moderne Argon2-Hashes benötigen kein Rehash."""
    password = "test123"
    modern_hash = get_password_hash(password)
    
    assert not needs_rehash(modern_hash), "Moderner Hash sollte kein Rehash benötigen"

def test_empty_password_fails():
    """Leeres Passwort wird abgelehnt."""
    hashed = get_password_hash("test")
    assert not verify_password("", hashed), "Leeres Passwort sollte abgelehnt werden"

def test_password_hash_is_long():
    """Passwort-Hash hat angemessene Länge (Argon2)."""
    hashed = get_password_hash("test")
    assert len(hashed) > 80, "Argon2-Hash sollte >80 Zeichen lang sein"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### Schritt 9: Tests ausführen (5min)

```bash
# Tests installieren
pip install pytest pytest-asyncio

# Tests ausführen
pytest tests/unit/test_auth_security.py -v

# Erwartete Ausgabe:
# test_auth_security.py::test_password_hashing_is_secure PASSED
# test_auth_security.py::test_password_verification_works PASSED
# test_auth_security.py::test_same_password_produces_different_hashes PASSED
# ... alle Tests PASSED
```

### ✅ Abschluss-Checkliste Task 1.1

- [ ] passlib und argon2-cffi installiert
- [ ] app/auth.py aktualisiert (Argon2-Support)
- [ ] .env-Datei erstellt mit SECRET_KEY
- [ ] .gitignore aktualisiert (.env ausgeschlossen)
- [ ] Migrations-Skript erstellt und ausgeführt
- [ ] Reset-Skript erstellt und getestet
- [ ] Alle Benutzer-Passwörter migriert oder als "bei Login migrieren" markiert
- [ ] Unit-Tests geschrieben und alle bestanden
- [ ] Admin kann sich mit neuem Passwort anmelden

---

## 1.2 Tenant-Isolation implementieren (16h)

### Schritt 1: Zentralen Tenant-Filter erstellen (1h)

**Datei:** `app/utils/tenant_scope.py` (neu erstellen)

```python
"""
Zentrale Hilfsfunktionen für Tenant-Isolation.

Stellt sicher, dass alle Datenbank-Queries nach tenant_id filtern.
"""

from typing import Type, TypeVar
from sqlmodel import SQLModel, select, Select
from app.models import User

T = TypeVar('T', bound=SQLModel)

def get_tenant_scoped_query(
    model: Type[T],
    current_user: User
) -> Select:
    """
    Erstellt eine Datenbank-Query mit Tenant-Filter.
    
    Args:
        model: SQLModel-Klasse (z.B. Invoice, Project)
        current_user: Aktueller Benutzer (enthält tenant_id)
    
    Returns:
        Select-Objekt mit Tenant-Filter
    
    Beispiel:
        >>> statement = get_tenant_scoped_query(Invoice, current_user)
        >>> invoices = session.exec(statement).all()
    """
    if not hasattr(model, 'tenant_id'):
        raise ValueError(f"Model {model.__name__} hat kein tenant_id-Feld!")
    
    return select(model).where(model.tenant_id == current_user.tenant_id)

def get_tenant_scoped_query_with_filter(
    model: Type[T],
    current_user: User,
    *filters
) -> Select:
    """
    Erstellt eine Query mit Tenant-Filter + zusätzlichen Filtern.
    
    Args:
        model: SQLModel-Klasse
        current_user: Aktueller Benutzer
        *filters: Zusätzliche WHERE-Bedingungen
    
    Beispiel:
        >>> statement = get_tenant_scoped_query_with_filter(
        ...     Invoice, 
        ...     current_user,
        ...     Invoice.status == "bezahlt"
        ... )
    """
    if not hasattr(model, 'tenant_id'):
        raise ValueError(f"Model {model.__name__} hat kein tenant_id-Feld!")
    
    return select(model).where(
        model.tenant_id == current_user.tenant_id,
        *filters
    )

def ensure_tenant_access(
    obj: SQLModel,
    current_user: User,
    resource_name: str = "Resource"
) -> None:
    """
    Prüft, ob Objekt zum Tenant des Benutzers gehört.
    Wirft HTTPException wenn nicht.
    
    Args:
        obj: Datenbank-Objekt
        current_user: Aktueller Benutzer
        resource_name: Name für Fehlermeldung
    
    Raises:
        HTTPException: 404 wenn Tenant nicht übereinstimmt
    """
    from fastapi import HTTPException
    
    if not hasattr(obj, 'tenant_id'):
        raise ValueError(f"Object {type(obj).__name__} hat kein tenant_id-Feld!")
    
    if obj.tenant_id != current_user.tenant_id:
        # 404 statt 403 um keine Existenz preiszugeben
        raise HTTPException(
            status_code=404,
            detail=f"{resource_name} nicht gefunden"
        )

def set_tenant_id(
    obj: SQLModel,
    current_user: User
) -> None:
    """
    Setzt tenant_id auf neuen Objekten.
    
    Args:
        obj: Neu erstelltes Objekt (noch nicht in DB)
        current_user: Aktueller Benutzer
    """
    if not hasattr(obj, 'tenant_id'):
        raise ValueError(f"Object {type(obj).__name__} hat kein tenant_id-Feld!")
    
    obj.tenant_id = current_user.tenant_id
```

### Schritt 2: Invoices-Router aktualisieren (2h)

**Datei:** `app/routers/invoices.py` (Änderungen markiert mit # ✅)

```python
"""
Router für Rechnungs-Management.
✅ TENANT-SICHER: Alle Endpoints filtern nach tenant_id
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from sqlmodel import Session, select
from typing import List
import json
import tempfile
import os
from datetime import datetime, timedelta

from ..database import get_session
from ..models import Invoice, Project, TimeEntry, MaterialUsage, Employee, TenantSettings
from ..schemas import InvoiceCreate, InvoiceUpdate, Invoice as InvoiceSchema
from ..auth import get_current_user, require_buchhalter_or_admin
from ..utils.tenant_scope import (  # ✅ NEU!
    get_tenant_scoped_query,
    get_tenant_scoped_query_with_filter,
    ensure_tenant_access,
    set_tenant_id
)

router = APIRouter(prefix="/invoices", tags=["invoices"])

@router.get("/", response_model=List[InvoiceSchema])
def get_invoices(
    session: Session = Depends(get_session), 
    current_user = Depends(require_buchhalter_or_admin)
):
    """
    Alle Rechnungen des Tenants abrufen.
    ✅ TENANT-SICHER
    """
    try:
        # ✅ NEU: Tenant-Filter!
        statement = get_tenant_scoped_query(Invoice, current_user)
        invoices = session.exec(statement).all()
        
        # Items-Behandlung bleibt gleich
        for invoice in invoices:
            if invoice.items is None:
                invoice.items = "[]"
            elif not isinstance(invoice.items, str):
                invoice.items = json.dumps(invoice.items) if invoice.items else "[]"
        
        return invoices
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail="Fehler beim Laden der Rechnungen"
        )

@router.get("/{invoice_id}", response_model=InvoiceSchema)
def get_invoice(
    invoice_id: int, 
    session: Session = Depends(get_session), 
    current_user = Depends(require_buchhalter_or_admin)
):
    """
    Einzelne Rechnung abrufen.
    ✅ TENANT-SICHER
    """
    invoice = session.get(Invoice, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Rechnung nicht gefunden")
    
    # ✅ NEU: Tenant-Check!
    ensure_tenant_access(invoice, current_user, "Rechnung")
    
    # Items konvertieren
    if isinstance(invoice.items, str):
        try:
            invoice.items = json.loads(invoice.items)
        except:
            invoice.items = []
    elif invoice.items is None:
        invoice.items = []
    
    return invoice

@router.post("/")
def create_invoice(
    invoice_data: dict, 
    session: Session = Depends(get_session), 
    current_user = Depends(get_current_user)
):
    """
    Neue Rechnung erstellen.
    ✅ TENANT-SICHER
    """
    try:
        project_id = invoice_data.get('project_id')
        project = session.get(Project, project_id)
        
        if not project:
            raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
        
        # ✅ NEU: Prüfe, ob Projekt zum Tenant gehört!
        ensure_tenant_access(project, current_user, "Projekt")
        
        # Items sammeln (bleibt gleich)
        items = invoice_data.get('items')
        if not items:
            generated_items, generated_total = _collect_project_items(
                session, project_id, current_user  # ✅ user mitgeben!
            )
            items = generated_items
            invoice_data['total_amount'] = generated_total
        
        items_json = json.dumps(items or [])
        
        # Rechnung erstellen
        db_invoice = Invoice(
            project_id=project_id,
            invoice_number=invoice_data.get('invoice_number', 'INV-001'),
            title=invoice_data.get('title', 'Neue Rechnung'),
            description=invoice_data.get('description'),
            client_name=invoice_data.get('client_name', 'Kunde'),
            client_address=invoice_data.get('client_address'),
            total_amount=round(float(invoice_data.get('total_amount', 0.0)), 2),
            currency=invoice_data.get('currency', 'EUR'),
            invoice_date=datetime.utcnow(),
            due_date=None,
            items=items_json,
            status=invoice_data.get('status', 'entwurf')
        )
        
        # ✅ NEU: Tenant-ID setzen!
        set_tenant_id(db_invoice, current_user)
        
        session.add(db_invoice)
        session.commit()
        session.refresh(db_invoice)
        
        return {
            "id": db_invoice.id,
            "project_id": db_invoice.project_id,
            "invoice_number": db_invoice.invoice_number,
            "title": db_invoice.title,
            "description": db_invoice.description,
            "client_name": db_invoice.client_name,
            "client_address": db_invoice.client_address,
            "total_amount": db_invoice.total_amount,
            "currency": db_invoice.currency,
            "invoice_date": db_invoice.invoice_date,
            "due_date": db_invoice.due_date,
            "items": json.loads(db_invoice.items) if db_invoice.items else [],
            "status": db_invoice.status,
            "created_at": db_invoice.created_at,
            "updated_at": db_invoice.updated_at
        }
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=500, 
            detail="Fehler bei Rechnung-Erstellung"
        )

@router.put("/{invoice_id}", response_model=InvoiceSchema)
def update_invoice(
    invoice_id: int, 
    invoice_update: dict, 
    session: Session = Depends(get_session),
    current_user = Depends(require_buchhalter_or_admin)
):
    """
    Rechnung aktualisieren.
    ✅ TENANT-SICHER
    """
    invoice = session.get(Invoice, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Rechnung nicht gefunden")
    
    # ✅ NEU: Tenant-Check!
    ensure_tenant_access(invoice, current_user, "Rechnung")
    
    # Update-Logik bleibt gleich
    safe_fields = ['invoice_number', 'status', 'client_name', 'total_amount', 'title', 'description', 'client_address']
    
    for field in safe_fields:
        if field in invoice_update and invoice_update[field] is not None:
            value = invoice_update[field]
            if field == 'total_amount':
                value = round(float(value), 2)
            setattr(invoice, field, value)
    
    if 'items' in invoice_update and invoice_update['items'] is not None:
        if isinstance(invoice_update['items'], list):
            invoice.items = json.dumps(invoice_update['items'])
        else:
            invoice.items = json.dumps(invoice_update['items'])
    
    session.add(invoice)
    session.commit()
    session.refresh(invoice)
    
    if isinstance(invoice.items, str):
        pass
    elif isinstance(invoice.items, list):
        invoice.items = json.dumps(invoice.items)
    else:
        invoice.items = json.dumps([])
    
    return invoice

@router.delete("/{invoice_id}")
def delete_invoice(
    invoice_id: int, 
    session: Session = Depends(get_session),
    current_user = Depends(require_buchhalter_or_admin)  # ✅ NEU: Auth!
):
    """
    Rechnung löschen.
    ✅ TENANT-SICHER
    """
    invoice = session.get(Invoice, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Rechnung nicht gefunden")
    
    # ✅ NEU: Tenant-Check!
    ensure_tenant_access(invoice, current_user, "Rechnung")
    
    session.delete(invoice)
    session.commit()
    return {"message": "Rechnung erfolgreich gelöscht"}

# Hilfsfunktion mit Tenant-Filter
def _collect_project_items(
    session: Session, 
    project_id: int,
    current_user  # ✅ NEU: User-Parameter!
):
    """
    Sammelt Projekt-Items (Stunden + Material).
    ✅ TENANT-SICHER
    """
    items = []
    
    # ✅ NEU: Tenant-Filter bei Zeit-Einträgen
    time_entries = session.exec(
        get_tenant_scoped_query_with_filter(
            TimeEntry,
            current_user,
            TimeEntry.project_id == project_id
        )
    ).all()
    
    # Personalkosten berechnen (bleibt gleich)
    total_hours = 0.0
    total_cost = 0.0
    
    for entry in time_entries:
        hours = entry.hours_worked or 0.0
        total_hours += hours
        
        if entry.hourly_rate is not None:
            rate = entry.hourly_rate
        else:
            employee = session.get(Employee, entry.employee_id)
            rate = employee.hourly_rate if employee and employee.hourly_rate else 0.0
        
        total_cost += hours * rate
    
    if hours > 0 and total_cost > 0:
        avg_rate = total_cost / total_hours if total_hours else 0
        items.append({
            'description': 'Personalkosten',
            'quantity': round(total_hours, 2),
            'unit': 'Stunden',
            'unit_price': round(avg_rate, 2),
            'total_price': round(total_cost, 2),
            'item_type': 'labor'
        })
    
    # ✅ NEU: Tenant-Filter bei Material
    material_usages = session.exec(
        get_tenant_scoped_query_with_filter(
            MaterialUsage,
            current_user,
            MaterialUsage.project_id == project_id
        )
    ).all()
    
    material_total = 0.0
    for material in material_usages:
        cost = material.total_cost
        if cost is None and material.unit_price is not None:
            cost = material.unit_price * material.quantity
        
        if cost:
            items.append({
                'description': f"Material: {material.material_name}",
                'quantity': material.quantity,
                'unit': material.unit,
                'unit_price': material.unit_price or 0,
                'total_price': round(cost, 2),
                'item_type': 'material'
            })
            material_total += cost
    
    total_amount = round(total_cost + material_total, 2)
    return items, total_amount

# Weitere Endpoints analog anpassen...
# (Gekürzt für Übersichtlichkeit)
```

### Schritt 3: Alle anderen Router aktualisieren (10h)

**Zu aktualisierende Dateien** (analog zu invoices.py):

1. `app/routers/projects.py` (2h)
2. `app/routers/offers.py` (2h)
3. `app/routers/reports.py` (2h)
4. `app/routers/time_entries.py` (2h)
5. `app/routers/company_logo.py` (1h)
6. `app/routers/project_images.py` (1h)

**Muster für jede Datei:**

```python
# Import hinzufügen:
from ..utils.tenant_scope import (
    get_tenant_scoped_query,
    ensure_tenant_access,
    set_tenant_id
)

# GET-Listen-Endpoint:
@router.get("/")
def get_items(..., current_user = Depends(get_current_user)):
    statement = get_tenant_scoped_query(Model, current_user)  # ✅
    items = session.exec(statement).all()
    return items

# GET-Einzeln-Endpoint:
@router.get("/{item_id}")
def get_item(item_id: int, ..., current_user = Depends(get_current_user)):
    item = session.get(Model, item_id)
    if not item:
        raise HTTPException(404, "Nicht gefunden")
    ensure_tenant_access(item, current_user)  # ✅
    return item

# POST-Endpoint:
@router.post("/")
def create_item(data, ..., current_user = Depends(get_current_user)):
    item = Model(**data)
    set_tenant_id(item, current_user)  # ✅
    session.add(item)
    session.commit()
    return item

# PUT/DELETE-Endpoints:
@router.put("/{item_id}")
def update_item(item_id, ..., current_user = Depends(get_current_user)):
    item = session.get(Model, item_id)
    if not item:
        raise HTTPException(404)
    ensure_tenant_access(item, current_user)  # ✅
    # ... update logic ...
```

### Schritt 4: Tests für Tenant-Isolation (2h)

**Datei:** `tests/unit/test_tenant_isolation.py` (neu erstellen)

```python
"""
Unit-Tests für Tenant-Isolation.
Prüft, dass Benutzer nur auf eigene Daten zugreifen können.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from app.main import app
from app.models import User, Invoice, Project, UserRole
from app.database import get_session
from app.auth import get_password_hash, create_access_token

# Test-Datenbank
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def override_get_session():
    with Session(engine) as session:
        yield session

app.dependency_overrides[get_session] = override_get_session

@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Erstellt Test-Datenbank vor jedem Test."""
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)

@pytest.fixture
def client():
    """FastAPI Test-Client."""
    return TestClient(app)

@pytest.fixture
def tenant1_user():
    """Benutzer für Tenant 1."""
    with Session(engine) as session:
        user = User(
            username="tenant1_user",
            email="tenant1@test.de",
            full_name="Tenant 1 User",
            hashed_password=get_password_hash("test123"),
            tenant_id=1,
            role=UserRole.ADMIN
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

@pytest.fixture
def tenant2_user():
    """Benutzer für Tenant 2."""
    with Session(engine) as session:
        user = User(
            username="tenant2_user",
            email="tenant2@test.de",
            full_name="Tenant 2 User",
            hashed_password=get_password_hash("test123"),
            tenant_id=2,
            role=UserRole.ADMIN
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

def get_auth_headers(user):
    """Erstellt Authorization-Header für Benutzer."""
    token = create_access_token(data={"sub": user.username})
    return {"Authorization": f"Bearer {token}"}

def test_user_can_only_see_own_tenant_invoices(client, tenant1_user, tenant2_user):
    """Benutzer sieht nur Rechnungen seines Tenants."""
    with Session(engine) as session:
        # Projekt für Tenant 1
        project1 = Project(
            tenant_id=1,
            name="Projekt Tenant 1",
            client_name="Kunde 1"
        )
        session.add(project1)
        
        # Projekt für Tenant 2
        project2 = Project(
            tenant_id=2,
            name="Projekt Tenant 2",
            client_name="Kunde 2"
        )
        session.add(project2)
        session.commit()
        session.refresh(project1)
        session.refresh(project2)
        
        # Rechnung für Tenant 1
        invoice1 = Invoice(
            tenant_id=1,
            project_id=project1.id,
            invoice_number="T1-001",
            title="Rechnung Tenant 1",
            client_name="Kunde 1",
            total_amount=1000.0,
            items="[]"
        )
        session.add(invoice1)
        
        # Rechnung für Tenant 2
        invoice2 = Invoice(
            tenant_id=2,
            project_id=project2.id,
            invoice_number="T2-001",
            title="Rechnung Tenant 2",
            client_name="Kunde 2",
            total_amount=2000.0,
            items="[]"
        )
        session.add(invoice2)
        session.commit()
    
    # Tenant 1 User ruft Rechnungen ab
    response = client.get(
        "/invoices/",
        headers=get_auth_headers(tenant1_user)
    )
    
    assert response.status_code == 200
    invoices = response.json()
    assert len(invoices) == 1, "Tenant 1 sollte nur 1 Rechnung sehen"
    assert invoices[0]["invoice_number"] == "T1-001"
    
    # Tenant 2 User ruft Rechnungen ab
    response = client.get(
        "/invoices/",
        headers=get_auth_headers(tenant2_user)
    )
    
    assert response.status_code == 200
    invoices = response.json()
    assert len(invoices) == 1, "Tenant 2 sollte nur 1 Rechnung sehen"
    assert invoices[0]["invoice_number"] == "T2-001"

def test_user_cannot_access_other_tenant_invoice_by_id(client, tenant1_user, tenant2_user):
    """Benutzer kann Rechnung eines anderen Tenants nicht direkt abrufen."""
    with Session(engine) as session:
        project2 = Project(
            tenant_id=2,
            name="Projekt Tenant 2",
            client_name="Kunde 2"
        )
        session.add(project2)
        session.commit()
        session.refresh(project2)
        
        invoice2 = Invoice(
            tenant_id=2,
            project_id=project2.id,
            invoice_number="T2-SECRET",
            title="Geheime Rechnung",
            client_name="Kunde 2",
            total_amount=5000.0,
            items="[]"
        )
        session.add(invoice2)
        session.commit()
        session.refresh(invoice2)
        invoice2_id = invoice2.id
    
    # Tenant 1 versucht, Rechnung von Tenant 2 abzurufen
    response = client.get(
        f"/invoices/{invoice2_id}",
        headers=get_auth_headers(tenant1_user)
    )
    
    assert response.status_code == 404, "Sollte 404 zurückgeben (nicht 403!)"
    assert "nicht gefunden" in response.json()["detail"].lower()

def test_user_cannot_update_other_tenant_invoice(client, tenant1_user, tenant2_user):
    """Benutzer kann Rechnung eines anderen Tenants nicht bearbeiten."""
    with Session(engine) as session:
        project2 = Project(
            tenant_id=2,
            name="Projekt Tenant 2",
            client_name="Kunde 2"
        )
        session.add(project2)
        session.commit()
        session.refresh(project2)
        
        invoice2 = Invoice(
            tenant_id=2,
            project_id=project2.id,
            invoice_number="T2-ORIG",
            title="Original",
            client_name="Kunde 2",
            total_amount=1000.0,
            items="[]"
        )
        session.add(invoice2)
        session.commit()
        session.refresh(invoice2)
        invoice2_id = invoice2.id
    
    # Tenant 1 versucht, Rechnung von Tenant 2 zu ändern
    response = client.put(
        f"/invoices/{invoice2_id}",
        headers=get_auth_headers(tenant1_user),
        json={"title": "GEHACKT"}
    )
    
    assert response.status_code == 404
    
    # Prüfe, dass Rechnung unverändert ist
    with Session(engine) as session:
        invoice = session.get(Invoice, invoice2_id)
        assert invoice.title == "Original", "Rechnung sollte unverändert sein"

def test_user_cannot_delete_other_tenant_invoice(client, tenant1_user, tenant2_user):
    """Benutzer kann Rechnung eines anderen Tenants nicht löschen."""
    with Session(engine) as session:
        project2 = Project(
            tenant_id=2,
            name="Projekt Tenant 2",
            client_name="Kunde 2"
        )
        session.add(project2)
        session.commit()
        session.refresh(project2)
        
        invoice2 = Invoice(
            tenant_id=2,
            project_id=project2.id,
            invoice_number="T2-PROTECTED",
            title="Geschützt",
            client_name="Kunde 2",
            total_amount=1000.0,
            items="[]"
        )
        session.add(invoice2)
        session.commit()
        session.refresh(invoice2)
        invoice2_id = invoice2.id
    
    # Tenant 1 versucht, Rechnung von Tenant 2 zu löschen
    response = client.delete(
        f"/invoices/{invoice2_id}",
        headers=get_auth_headers(tenant1_user)
    )
    
    assert response.status_code == 404
    
    # Prüfe, dass Rechnung noch existiert
    with Session(engine) as session:
        invoice = session.get(Invoice, invoice2_id)
        assert invoice is not None, "Rechnung sollte noch existieren"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### Schritt 5: Tests ausführen (30min)

```bash
# Installation
pip install pytest pytest-asyncio httpx

# Alle Tenant-Isolation-Tests ausführen
pytest tests/unit/test_tenant_isolation.py -v

# Erwartete Ausgabe:
# test_tenant_isolation.py::test_user_can_only_see_own_tenant_invoices PASSED
# test_tenant_isolation.py::test_user_cannot_access_other_tenant_invoice_by_id PASSED
# test_tenant_isolation.py::test_user_cannot_update_other_tenant_invoice PASSED
# test_tenant_isolation.py::test_user_cannot_delete_other_tenant_invoice PASSED
# ==================== 4 passed in 2.34s ====================
```

### ✅ Abschluss-Checkliste Task 1.2

- [ ] tenant_scope.py erstellt mit Helper-Funktionen
- [ ] invoices.py vollständig aktualisiert (alle Endpoints)
- [ ] projects.py aktualisiert
- [ ] offers.py aktualisiert
- [ ] reports.py aktualisiert
- [ ] time_entries.py aktualisiert
- [ ] company_logo.py aktualisiert
- [ ] project_images.py aktualisiert
- [ ] Tests geschrieben und alle bestanden
- [ ] Manueller Test: 2 Tenants anlegen, Cross-Access prüfen

---

## 1.3 Strukturiertes Logging einführen (4h)

### Schritt 1: Logging-Konfiguration erstellen (30min)

**Datei:** `app/config.py` (erweitern)

```python
"""
Zentrale Konfiguration für die Anwendung.
"""

import os
import logging
from logging.config import dictConfig
from typing import Any

# Environment-Variablen laden
from dotenv import load_dotenv
load_dotenv()

# Feature Flags
from config import FEATURE_FLAGS

# Logging-Konfiguration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "detailed": {
            "format": "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | tenant_id=%(tenant_id)s | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "json": {  # Für Produktion (maschinenlesbar)
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(funcName)s %(lineno)d %(message)s",
        }
    },
    "filters": {
        "tenant_filter": {
            "()": "app.config.TenantContextFilter"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "default",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": "logs/app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 10,
            "encoding": "utf-8"
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "detailed",
            "filename": "logs/errors.log",
            "maxBytes": 10485760,
            "backupCount": 5,
            "encoding": "utf-8"
        }
    },
    "loggers": {
        "app": {
            "level": "DEBUG",
            "handlers": ["console", "file", "error_file"],
            "propagate": False
        },
        "uvicorn": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False
        },
        "sqlalchemy.engine": {
            "level": "WARNING",  # DEBUG für Query-Logging
            "handlers": ["console"],
            "propagate": False
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"]
    }
}

class TenantContextFilter(logging.Filter):
    """
    Fügt tenant_id zu Log-Records hinzu.
    """
    def filter(self, record):
        # Default-Wert
        if not hasattr(record, 'tenant_id'):
            record.tenant_id = '-'
        return True

def setup_logging():
    """Initialisiert Logging."""
    # Logs-Verzeichnis erstellen
    os.makedirs("logs", exist_ok=True)
    
    # Logging konfigurieren
    dictConfig(LOGGING_CONFIG)
    
    # Startup-Nachricht
    logger = logging.getLogger("app")
    logger.info("=" * 60)
    logger.info("Bau-Dokumentations-App gestartet")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    logger.info(f"Multi-Tenant: {FEATURE_FLAGS.get('multi_tenant_enabled', False)}")
    logger.info("=" * 60)

def get_logger(name: str) -> logging.Logger:
    """
    Holt einen Logger für ein Modul.
    
    Usage:
        logger = get_logger(__name__)
        logger.info("Message", extra={"tenant_id": user.tenant_id})
    """
    return logging.getLogger(f"app.{name}")
```

### Schritt 2: Logging in main.py einbinden (15min)

**Datei:** `app/main.py` (am Anfang ergänzen)

```python
"""
Hauptanwendung für die Bau-Dokumentations-App.
FastAPI-Anwendung mit allen Routen und Middleware.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import os

# ✅ NEU: Logging-Setup
from app.config import setup_logging, get_logger
setup_logging()
logger = get_logger(__name__)

from .database import create_db_and_tables
from .routers import (
    projects, reports, offers, employees, time_entries, 
    project_images, invoices, auth, invoice_generation, 
    billing, company_logo, dashboard
)
from .utils.feature_flags import FEATURE_FLAGS
from app.utils.db_compat import ensure_tenant_settings_columns

# ... Rest bleibt gleich, aber print() durch logger ersetzen:

# Startup-Event
def startup_event():
    """Wird beim Start der Anwendung ausgeführt."""
    logger.info("Erstelle Datenbank-Tabellen...")  # ✅ NEU
    create_db_and_tables()
    
    try:
        ensure_tenant_settings_columns()
        logger.info("Tenant-Settings-Tabelle aktualisiert")  # ✅ NEU
    except Exception as e:
        logger.warning(f"Konnte tenant_settings nicht aktualisieren: {e}")  # ✅ NEU

# ... Rest des Codes
```

### Schritt 3: print() durch logger ersetzen (3h)

**Systematisches Vorgehen:**

```bash
# 1. Alle print()-Statements finden
grep -r "print(" app/ | wc -l
# Ergebnis: ~32 Statements

# 2. Datei für Datei durchgehen:
```

**Beispiel:** `app/routers/reports.py`

```python
# ✅ Am Anfang hinzufügen:
from app.config import get_logger
logger = get_logger(__name__)

# ❌ ALT:
print(f"DEBUG: {len(reports)} Berichte gefunden")
print(f"DEBUG: Bericht {report.id} - {len(attachments)} Anhänge aus Datenbank")

# ✅ NEU:
logger.debug(
    f"Gefundene Berichte: {len(reports)}",
    extra={"tenant_id": current_user.tenant_id if current_user else "-"}
)
logger.debug(
    f"Anhänge geladen",
    extra={
        "report_id": report.id,
        "attachment_count": len(attachments),
        "tenant_id": current_user.tenant_id
    }
)
```

**Zu aktualisierende Dateien:**
1. `app/routers/reports.py` (17 print-Statements) - 45min
2. `app/routers/invoices.py` (9 print-Statements) - 30min
3. `app/routers/invoice_generation.py` (4 print-Statements) - 15min
4. `app/routers/billing.py` (1 print-Statement) - 5min
5. `app/routers/time_entries.py` (1 print-Statement) - 5min

### Schritt 4: Middleware für Request-Logging (30min)

**Datei:** `app/main.py` (Middleware hinzufügen)

```python
from fastapi import Request
import time

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Loggt alle HTTP-Requests."""
    start_time = time.time()
    
    # Request-Info
    logger.info(
        f"Request gestartet",
        extra={
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host if request.client else "-"
        }
    )
    
    # Request verarbeiten
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(
            f"Request-Fehler: {e}",
            exc_info=True,
            extra={
                "method": request.method,
                "url": str(request.url)
            }
        )
        raise
    
    # Response-Info
    duration = (time.time() - start_time) * 1000  # ms
    logger.info(
        f"Request abgeschlossen",
        extra={
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "duration_ms": round(duration, 2)
        }
    )
    
    return response
```

### Schritt 5: .gitignore für Logs (2min)

**.gitignore ergänzen:**

```gitignore
# Logs
logs/
*.log
```

### ✅ Abschluss-Checkliste Task 1.3

- [ ] Logging-Konfiguration in config.py erstellt
- [ ] setup_logging() in main.py aufgerufen
- [ ] Alle print() in logger.info/debug/error ersetzt
- [ ] Request-Logging-Middleware hinzugefügt
- [ ] logs/-Verzeichnis von Git ausgeschlossen
- [ ] Test: Server starten, Logs in logs/app.log prüfen

---

## 1.4 SQL-Injection in db_compat.py fixen (30min)

**Problem:** String-Interpolation in SQL

### Schritt 1: Sicheren Code schreiben

**Datei:** `app/utils/db_compat.py`

```python
"""
Datenbank-Kompatibilitäts-Helfer für Legacy-Datenbanken.
✅ SQL-INJECTION-SICHER
"""

from typing import Optional
from sqlmodel import Session
from sqlalchemy import text, inspect
from app.database import engine
from app.config import get_logger

logger = get_logger(__name__)

# ✅ WHITELIST statt dynamischer SQL-Strings!
ALLOWED_COLUMNS = {
    "company_name",
    "company_address",
    "company_phone",
    "company_fax",
    "company_email",
    "company_website",
    "bank_name",
    "bank_iban",
    "bank_bic",
    "tax_number",
    "vat_id",
}

# ✅ Erlaubte Datentypen (Whitelist!)
ALLOWED_TYPES = {
    "TEXT",
    "VARCHAR(255)",
    "INTEGER",
    "BOOLEAN"
}

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

def is_valid_column_name(column: str) -> bool:
    """
    Validiert, ob Column-Name sicher ist.
    ✅ SQL-INJECTION-SCHUTZ
    """
    # Nur alphanumerisch + Underscore
    if not column.replace('_', '').isalnum():
        return False
    
    # Muss in Whitelist sein
    if column not in ALLOWED_COLUMNS:
        return False
    
    return True

def is_valid_type(dtype: str) -> bool:
    """
    Validiert, ob Datentyp sicher ist.
    ✅ SQL-INJECTION-SCHUTZ
    """
    return dtype.upper() in ALLOWED_TYPES

def ensure_tenant_settings_columns(session: Optional[Session] = None) -> None:
    """
    Fügt fehlende Spalten in legacy-Datenbanken hinzu.
    ✅ SQL-INJECTION-SICHER
    """
    external_session = session is not None
    if session is None:
        session = Session(engine)

    try:
        # Prüfe, ob Tabelle existiert
        inspector = inspect(engine)
        if "tenant_settings" not in inspector.get_table_names():
            logger.info("Tabelle 'tenant_settings' existiert nicht - überspringe Migration")
            if not external_session:
                session.close()
            return
        
        # Hole existierende Spalten (SQLAlchemy Inspector)
        columns_info = inspector.get_columns("tenant_settings")
        existing = {col["name"] for col in columns_info}
        
        logger.debug(f"Existierende Spalten: {existing}")
        
        altered = False
        for column, ddl in TENANT_SETTINGS_LEGACY_COLUMNS.items():
            if column in existing:
                continue
            
            # ✅ VALIDIERUNG statt direkter String-Interpolation!
            if not is_valid_column_name(column):
                logger.error(f"Ungültiger Column-Name: {column}")
                raise ValueError(f"Ungültiger Column-Name: {column}")
            
            if not is_valid_type(ddl):
                logger.error(f"Ungültiger Datentyp: {ddl}")
                raise ValueError(f"Ungültiger Datentyp: {ddl}")
            
            # Jetzt sicher, weil validiert
            sql = f"ALTER TABLE tenant_settings ADD COLUMN {column} {ddl}"
            logger.info(f"Führe aus: {sql}")
            
            session.exec(text(sql))
            altered = True
            logger.info(f"Spalte '{column}' hinzugefügt")

        if altered:
            session.commit()
            logger.info("Datenbank-Schema aktualisiert")
        else:
            logger.debug("Keine Schema-Änderungen nötig")

    except Exception as e:
        logger.error(f"Fehler bei Schema-Update: {e}", exc_info=True)
        raise
    finally:
        if not external_session:
            session.close()
```

### Schritt 2: Test schreiben (15min)

**Datei:** `tests/unit/test_db_compat_security.py`

```python
"""
Security-Tests für Datenbank-Kompatibilität.
"""

import pytest
from app.utils.db_compat import is_valid_column_name, is_valid_type

def test_valid_column_names_accepted():
    """Gültige Column-Namen werden akzeptiert."""
    assert is_valid_column_name("company_name")
    assert is_valid_column_name("bank_iban")
    assert is_valid_column_name("tax_number")

def test_sql_injection_in_column_name_rejected():
    """SQL-Injection in Column-Namen wird abgelehnt."""
    # SQL-Injection-Versuche
    assert not is_valid_column_name("name; DROP TABLE users;--")
    assert not is_valid_column_name("name' OR '1'='1")
    assert not is_valid_column_name("name; DELETE FROM tenant;")
    assert not is_valid_column_name("../../../etc/passwd")
    assert not is_valid_column_name("name<script>")

def test_non_whitelisted_column_rejected():
    """Nicht in Whitelist enthaltene Spalten werden abgelehnt."""
    assert not is_valid_column_name("malicious_column")
    assert not is_valid_column_name("admin_password")
    assert not is_valid_column_name("credit_card")

def test_valid_types_accepted():
    """Gültige Datentypen werden akzeptiert."""
    assert is_valid_type("TEXT")
    assert is_valid_type("VARCHAR(255)")
    assert is_valid_type("INTEGER")

def test_sql_injection_in_type_rejected():
    """SQL-Injection in Datentypen wird abgelehnt."""
    assert not is_valid_type("TEXT; DROP TABLE users;")
    assert not is_valid_type("VARCHAR(255)' OR '1'='1")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### ✅ Abschluss-Checkliste Task 1.4

- [ ] db_compat.py mit Whitelist-Validierung umgeschrieben
- [ ] Logging hinzugefügt
- [ ] Security-Tests geschrieben und bestanden
- [ ] Manueller Test: Server starten, keine Fehler

---

## 1.5 Finale Phase-1-Validierung (6h)

### Schritt 1: Integrationstests schreiben (3h)

**Datei:** `tests/integration/test_security_complete.py`

```python
"""
End-to-End Security-Tests.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_cannot_login_with_wrong_password():
    """Login mit falschem Passwort schlägt fehl."""
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": "WRONG"}
    )
    assert response.status_code == 401

def test_cannot_access_api_without_token():
    """API-Zugriff ohne Token wird abgelehnt."""
    response = client.get("/invoices/")
    assert response.status_code in [401, 403]

def test_password_is_hashed_securely():
    """Passwörter werden sicher gehasht."""
    # Registriere Test-User
    # ...prüfe Hash-Format...
    pass  # TODO: Implementieren

# ... weitere Tests
```

### Schritt 2: Sicherheits-Checklist durchgehen (1h)

**Datei:** `SECURITY_CHECKLIST_PHASE1.md` (erstellen)

```markdown
# Security-Checklist Phase 1

## Passwort-Sicherheit
- [x] Argon2/Bcrypt statt SHA256
- [x] Automatisches Rehashing
- [x] Mindestlänge 8 Zeichen
- [x] Tests vorhanden

## Secrets-Management
- [x] SECRET_KEY in .env
- [x] .env in .gitignore
- [x] Stripe-Keys in .env
- [x] Keine Secrets im Code

## Tenant-Isolation
- [x] tenant_scope.py erstellt
- [x] Alle Router aktualisiert:
  - [x] invoices.py
  - [x] projects.py
  - [x] offers.py
  - [x] reports.py
  - [x] time_entries.py
  - [x] company_logo.py
  - [x] project_images.py
- [x] Tests vorhanden

## Logging
- [x] Strukturiertes Logging
- [x] Keine print()-Statements
- [x] Request-Logging
- [x] Error-Logging

## SQL-Injection
- [x] db_compat.py gesichert
- [x] Whitelist-Validierung
- [x] Tests vorhanden

## Gesamtbewertung
- [ ] Alle Tests bestanden (pytest)
- [ ] Manuelle Pen-Tests durchgeführt
- [ ] Code-Review durch zweite Person
- [ ] Bereit für Phase 2
```

### Schritt 3: Komplette Test-Suite ausführen (30min)

```bash
# Alle Tests ausführen
pytest tests/ -v --cov=app --cov-report=html

# Coverage-Report öffnen
start htmlcov/index.html  # Windows
# open htmlcov/index.html  # Mac

# Erwartetes Minimum:
# - 25% Code-Coverage
# - Alle Security-Tests PASSED
```

### Schritt 4: Deployment-Vorbereitung (1.5h)

**Datei:** `.env.example` (erstellen als Vorlage)

```env
# Security (PFLICHT!)
SECRET_KEY=<generiere mit: python -c "import secrets; print(secrets.token_hex(32))">

# Database
DATABASE_URL=sqlite:///./database.db

# Stripe
STRIPE_TEST_PUBLISHABLE_KEY=pk_test_...
STRIPE_TEST_SECRET_KEY=sk_test_...
STRIPE_ACTIVE_PRICE_ID=price_...

# Environment
ENVIRONMENT=development  # development | staging | production

# Feature Flags
FEATURE_MULTI_TENANT=true
FEATURE_BILLING_ENABLED=false

# Logging
LOG_LEVEL=INFO  # DEBUG | INFO | WARNING | ERROR
```

**Datei:** `DEPLOYMENT.md` (erstellen)

```markdown
# Deployment-Anleitung

## Voraussetzungen
- Python 3.11+
- 2GB RAM minimum
- SSL-Zertifikat (Let's Encrypt)

## Installation

### 1. Repository klonen
```bash
git clone <repo>
cd backend
```

### 2. .env erstellen
```bash
cp .env.example .env
# .env bearbeiten, SECRET_KEY generieren!
```

### 3. Dependencies installieren
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 4. Datenbank initialisieren
```bash
alembic upgrade head
python reset_password.py admin "<sicheres-passwort>"
```

### 5. Server starten
```bash
# Entwicklung:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Produktion:
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Sicherheit-Checkliste

- [ ] SECRET_KEY generiert und gesichert
- [ ] Admin-Passwort geändert
- [ ] HTTPS aktiviert (kein HTTP!)
- [ ] Firewall konfiguriert
- [ ] Backups eingerichtet
- [ ] Logs werden rotiert
- [ ] Rate-Limiting aktiv
- [ ] Security-Headers gesetzt

## Monitoring

- Logs: `tail -f logs/app.log`
- Errors: `tail -f logs/errors.log`
- Health: `curl http://localhost:8000/health`
```

### ✅ Phase 1 Abschluss-Checkliste

- [ ] Alle Unit-Tests PASSED
- [ ] Alle Integration-Tests PASSED
- [ ] Security-Checklist vollständig
- [ ] Code-Coverage >25%
- [ ] Deployment-Dokumentation erstellt
- [ ] .env.example erstellt
- [ ] Git-Commit mit Tag "v1.0-security-phase1"

---

# PHASE 2: CODE QUALITY (Woche 2-3)

**Zeitaufwand:** 80 Stunden (2 Wochen Vollzeit)  
**Priorität:** HOCH  
**Ziel:** Wartbarkeit und Debugging verbessern

---

## 2.1 Frontend-Refactoring: Module erstellen (20h)

### Schritt 1: Neue Verzeichnisstruktur erstellen (30min)

```bash
cd static

# Module-Struktur erstellen
mkdir js
mkdir js/api
mkdir js/components
mkdir js/utils
mkdir js/pages

# Alt-Dateien umbenennen
mv app.js app_legacy.js
```

**Zielstruktur:**
```
static/
├── index.html
├── login.html
├── css/
│   └── styles.css  (später)
└── js/
    ├── main.js              # Entry Point
    ├── config.js            # Konfiguration
    ├── api/
    │   ├── auth.js
    │   ├── projects.js
    │   ├── invoices.js
    │   ├── offers.js
    │   ├── reports.js
    │   └── time_entries.js
    ├── components/
    │   ├── forms.js
    │   ├── tables.js
    │   ├── modals.js
    │   └── navigation.js
    ├── utils/
    │   ├── api_client.js
    │   ├── validation.js
    │   ├── formatting.js
    │   ├── dom.js
    │   └── storage.js
    └── pages/
        ├── dashboard.js
        ├── projects.js
        ├── invoices.js
        └── reports.js
```

### Schritt 2: API-Client abstrahieren (2h)

**Datei:** `static/js/utils/api_client.js`

```javascript
/**
 * Zentraler API-Client für alle Backend-Aufrufe.
 * Behandelt Authentifizierung, Error-Handling, etc.
 */

const API_BASE_URL = window.location.origin;

class ApiError extends Error {
    constructor(message, statusCode, response) {
        super(message);
        this.name = 'ApiError';
        this.statusCode = statusCode;
        this.response = response;
    }
}

/**
 * Holt den Auth-Token aus localStorage.
 */
function getAuthToken() {
    return localStorage.getItem('token');
}

/**
 * Setzt den Auth-Token.
 */
function setAuthToken(token) {
    localStorage.setItem('token', token);
}

/**
 * Entfernt den Auth-Token (Logout).
 */
function clearAuthToken() {
    localStorage.removeItem('token');
    localStorage.removeItem('currentUser');
}

/**
 * Führt einen authentifizierten API-Call aus.
 * 
 * @param {string} endpoint - API-Endpoint (z.B. "/invoices/")
 * @param {object} options - Fetch-Optionen
 * @returns {Promise<any>} JSON-Response
 */
async function apiCall(endpoint, options = {}) {
    const token = getAuthToken();
    
    const defaultHeaders = {
        'Content-Type': 'application/json'
    };
    
    if (token) {
        defaultHeaders['Authorization'] = `Bearer ${token}`;
    }
    
    const config = {
        ...options,
        headers: {
            ...defaultHeaders,
            ...options.headers
        }
    };
    
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
        
        // Unauthorized -> Logout
        if (response.status === 401) {
            clearAuthToken();
            window.location.href = '/login';
            throw new ApiError('Unauthorized', 401, response);
        }
        
        // Andere Fehler
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new ApiError(
                errorData.detail || 'API-Fehler',
                response.status,
                errorData
            );
        }
        
        // Erfolgreiche Response
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        }
        
        return response;
        
    } catch (error) {
        if (error instanceof ApiError) {
            throw error;
        }
        
        // Network-Fehler
        throw new ApiError(
            'Netzwerkfehler - Server nicht erreichbar',
            0,
            null
        );
    }
}

/**
 * GET-Request.
 */
async function apiGet(endpoint) {
    return apiCall(endpoint, { method: 'GET' });
}

/**
 * POST-Request.
 */
async function apiPost(endpoint, data) {
    return apiCall(endpoint, {
        method: 'POST',
        body: JSON.stringify(data)
    });
}

/**
 * PUT-Request.
 */
async function apiPut(endpoint, data) {
    return apiCall(endpoint, {
        method: 'PUT',
        body: JSON.stringify(data)
    });
}

/**
 * DELETE-Request.
 */
async function apiDelete(endpoint) {
    return apiCall(endpoint, { method: 'DELETE' });
}

/**
 * File-Upload.
 */
async function apiUpload(endpoint, formData) {
    const token = getAuthToken();
    
    return fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`
        },
        body: formData  // Kein Content-Type bei FormData!
    }).then(response => {
        if (!response.ok) {
            throw new ApiError('Upload fehlgeschlagen', response.status);
        }
        return response.json();
    });
}

// Exports
export {
    apiCall,
    apiGet,
    apiPost,
    apiPut,
    apiDelete,
    apiUpload,
    getAuthToken,
    setAuthToken,
    clearAuthToken,
    ApiError
};
```

### Schritt 3: Invoice-API-Modul (1.5h)

**Datei:** `static/js/api/invoices.js`

```javascript
/**
 * API-Funktionen für Rechnungen.
 */

import { apiGet, apiPost, apiPut, apiDelete } from '../utils/api_client.js';

/**
 * Lädt alle Rechnungen.
 */
export async function getInvoices() {
    return apiGet('/invoices/');
}

/**
 * Lädt eine einzelne Rechnung.
 */
export async function getInvoice(invoiceId) {
    return apiGet(`/invoices/${invoiceId}`);
}

/**
 * Erstellt eine neue Rechnung.
 */
export async function createInvoice(invoiceData) {
    return apiPost('/invoices/', invoiceData);
}

/**
 * Aktualisiert eine Rechnung.
 */
export async function updateInvoice(invoiceId, invoiceData) {
    return apiPut(`/invoices/${invoiceId}`, invoiceData);
}

/**
 * Löscht eine Rechnung.
 */
export async function deleteInvoice(invoiceId) {
    return apiDelete(`/invoices/${invoiceId}`);
}

/**
 * Generiert PDF für Rechnung.
 */
export async function downloadInvoicePDF(invoiceId) {
    const token = localStorage.getItem('token');
    
    const response = await fetch(`/invoices/${invoiceId}/pdf`, {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });
    
    if (!response.ok) {
        throw new Error('PDF-Generierung fehlgeschlagen');
    }
    
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Rechnung_${invoiceId}.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
}

/**
 * Lädt Gesamtumsatz.
 */
export async function getTotalRevenue() {
    return apiGet('/invoices/total-revenue');
}
```

### Schritt 4: Weitere API-Module analog erstellen (8h)

- `static/js/api/projects.js` (1.5h)
- `static/js/api/offers.js` (1.5h)
- `static/js/api/reports.js` (1.5h)
- `static/js/api/time_entries.js` (1.5h)
- `static/js/api/auth.js` (2h)

**Muster für alle Module:**

```javascript
import { apiGet, apiPost, apiPut, apiDelete } from '../utils/api_client.js';

export async function getItems() {
    return apiGet('/endpoint/');
}

export async function getItem(id) {
    return apiGet(`/endpoint/${id}`);
}

export async function createItem(data) {
    return apiPost('/endpoint/', data);
}

export async function updateItem(id, data) {
    return apiPut(`/endpoint/${id}`, data);
}

export async function deleteItem(id) {
    return apiDelete(`/endpoint/${id}`);
}
```

### Schritt 5: Component-Module erstellen (4h)

**Datei:** `static/js/components/tables.js`

```javascript
/**
 * Wiederverwendbare Tabellen-Komponenten.
 */

import { formatCurrency, formatDate } from '../utils/formatting.js';

/**
 * Rendert eine Rechnung als Tabellenzeile.
 */
export function renderInvoiceRow(invoice) {
    return `
        <tr data-invoice-id="${invoice.id}">
            <td>${invoice.invoice_number}</td>
            <td>${invoice.client_name}</td>
            <td>${formatCurrency(invoice.total_amount)}</td>
            <td>${formatDate(invoice.invoice_date)}</td>
            <td>
                <span class="badge bg-${getStatusColor(invoice.status)}">
                    ${getStatusText(invoice.status)}
                </span>
            </td>
            <td>
                <button class="btn btn-sm btn-primary" onclick="viewInvoice(${invoice.id})">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-sm btn-secondary" onclick="editInvoice(${invoice.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteInvoice(${invoice.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        </tr>
    `;
}

/**
 * Rendert komplette Invoice-Tabelle.
 */
export function renderInvoiceTable(invoices) {
    const tbody = document.querySelector('#invoicesTable tbody');
    
    if (!invoices || invoices.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">Keine Rechnungen gefunden</td></tr>';
        return;
    }
    
    tbody.innerHTML = invoices.map(renderInvoiceRow).join('');
}

function getStatusColor(status) {
    const colors = {
        'entwurf': 'secondary',
        'versendet': 'primary',
        'bezahlt': 'success',
        'überfällig': 'danger'
    };
    return colors[status] || 'secondary';
}

function getStatusText(status) {
    const texts = {
        'entwurf': 'Entwurf',
        'versendet': 'Versendet',
        'bezahlt': 'Bezahlt',
        'überfällig': 'Überfällig'
    };
    return texts[status] || status;
}
```

### Schritt 6: Main.js als Entry Point (2h)

**Datei:** `static/js/main.js`

```javascript
/**
 * Haupt-Entry-Point der Anwendung.
 */

import { getAuthToken } from './utils/api_client.js';
import { initNavigation } from './components/navigation.js';
import { loadDashboard } from './pages/dashboard.js';
import { loadInvoicesPage } from './pages/invoices.js';
import { loadProjectsPage } from './pages/projects.js';
// ... weitere Pages

// Globaler State
window.appState = {
    currentUser: null,
    currentPage: null
};

/**
 * Initialisiert die Anwendung.
 */
async function initApp() {
    // Auth-Check
    const token = getAuthToken();
    if (!token) {
        window.location.href = '/login';
        return;
    }
    
    // User-Daten laden
    try {
        const response = await fetch('/auth/me', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (!response.ok) {
            throw new Error('Auth failed');
        }
        
        window.appState.currentUser = await response.json();
    } catch (error) {
        window.location.href = '/login';
        return;
    }
    
    // Navigation initialisieren
    initNavigation();
    
    // Standard-Seite laden
    showSection('dashboard');
}

/**
 * Zeigt eine Sektion/Seite an.
 */
export function showSection(sectionName) {
    // Alte Sektion ausblenden
    document.querySelectorAll('.content-section').forEach(section => {
        section.style.display = 'none';
    });
    
    // Neue Sektion anzeigen
    const section = document.getElementById(`${sectionName}-section`);
    if (section) {
        section.style.display = 'block';
    }
    
    // Seite laden
    switch(sectionName) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'invoices':
            loadInvoicesPage();
            break;
        case 'projects':
            loadProjectsPage();
            break;
        // ... weitere Cases
    }
    
    window.appState.currentPage = sectionName;
}

// App starten wenn DOM geladen
document.addEventListener('DOMContentLoaded', initApp);
```

### Schritt 7: HTML anpassen für Module (2h)

**Datei:** `static/index.html` (am Ende, vor `</body>`)

```html
    <!-- ✅ NEU: Module statt Monolith -->
    <script type="module" src="/static/js/main.js"></script>
    
    <!-- Legacy-Code auskommentieren (als Backup)
    <script src="/static/app_legacy.js"></script>
    -->
</body>
</html>
```

### ✅ Abschluss-Checkliste Task 2.1

- [ ] Module-Struktur erstellt
- [ ] api_client.js implementiert
- [ ] Alle API-Module erstellt (invoices, projects, etc.)
- [ ] Component-Module erstellt (tables, forms, modals)
- [ ] main.js als Entry Point
- [ ] HTML auf Module umgestellt
- [ ] App funktioniert (manueller Test)
- [ ] Alter Code als _legacy gesichert

---

**Fortsetzung folgt in Teil 2 des Plans...**

Soll ich den Plan weiter ausarbeiten mit:
- Phase 2.2: Duplizierungen entfernen
- Phase 2.3: Magic Strings durch Enums
- Phase 2.4: Test-Coverage erhöhen
- Phase 3: Performance-Optimierung
- Phase 4: Architektur-Upgrades

?

