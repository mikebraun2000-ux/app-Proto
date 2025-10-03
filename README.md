# Bau-Dokumentations-App Backend

Ein FastAPI-Backend für eine lokale Bau-Dokumentations-Anwendung mit SQLite-Datenbank.

## Features

- **Projekt-Management**: CRUD-Operationen für Bauprojekte
- **Bericht-System**: Erstellung und Verwaltung von Bauberichten mit Bild-Upload
- **Angebot-Generator**: Erstellung von Angeboten mit PDF-Export
- **SQLite-Datenbank**: Lokale Datenbank mit SQLModel
- **REST-API**: Vollständige REST-API mit FastAPI

## Installation und Start

### 1. Virtuelle Umgebung erstellen

```bash
# Im backend-Verzeichnis
python -m venv venv

# Virtuelle Umgebung aktivieren (Windows)
venv\Scripts\activate

# Virtuelle Umgebung aktivieren (Linux/Mac)
source venv/bin/activate
```

### 2. Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

### 3. Server starten

```bash
uvicorn app.main:app --reload
```

Die API ist dann unter `http://localhost:8000` erreichbar.

### 4. API-Dokumentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API-Endpunkte

### Projekte
- `GET /projects` - Alle Projekte abrufen
- `POST /projects` - Neues Projekt erstellen
- `GET /projects/{id}` - Projekt abrufen
- `PUT /projects/{id}` - Projekt aktualisieren
- `DELETE /projects/{id}` - Projekt löschen

### Berichte
- `GET /reports` - Alle Berichte abrufen
- `POST /reports` - Neuen Bericht erstellen
- `GET /reports/{id}` - Bericht abrufen
- `PUT /reports/{id}` - Bericht aktualisieren
- `DELETE /reports/{id}` - Bericht löschen
- `POST /reports/{id}/upload_image` - Bild hochladen
- `GET /reports/project/{project_id}` - Berichte eines Projekts

### Angebote
- `GET /offers` - Alle Angebote abrufen
- `POST /offers` - Neues Angebot erstellen
- `GET /offers/{id}` - Angebot abrufen
- `PUT /offers/{id}` - Angebot aktualisieren
- `DELETE /offers/{id}` - Angebot löschen
- `POST /offers/{id}/pdf` - PDF-Angebot generieren
- `GET /offers/project/{project_id}` - Angebote eines Projekts

## Datenbank

Die SQLite-Datenbank wird automatisch als `database.db` im Backend-Verzeichnis erstellt. Die Tabellen werden beim ersten Start der Anwendung automatisch angelegt.

## Sicherheits- und Mandantenkonzept

- **Mandantenfähigkeit**: Jeder Mandant erhält einen eindeutig identifizierbaren `tenant_id`-Kontext, der in allen Datenbanktabellen als Pflichtfeld hinterlegt wird. API-Requests tragen den Tenant-Kontext als JWT-Claim, wodurch ausschließlich mandantenbezogene Datensätze geladen werden.
- **Mandantentrennung**: Auf Datenbankebene werden `ROW LEVEL SECURITY`-Policies vorbereitet (für SQLite über Query-Filter, bei einem späteren Wechsel zu PostgreSQL über native RLS). Zusätzlich werden sensible Assets (Dateiuploads, Reports) in tenant-spezifischen Verzeichnissen abgelegt.
- **Authentifizierung & Autorisierung**: Der Login erfolgt über OAuth2 Password Flow mit JWT-Tokens. Rollen (`admin`, `project_manager`, `employee`, `accounting`) steuern die Berechtigungen innerhalb eines Mandanten. Sicherheitskritische Aktionen (z. B. Export, Löschung) erfordern „step-up“-Authentifizierung über Einmalpasswörter.
- **Sicherheitsmaßnahmen**: Passwörter werden mit `bcrypt` gehasht, alle externen Verbindungen laufen über HTTPS, Rate-Limits schützen Login-Endpoints, und Audit-Logs erfassen sicherheitsrelevante Ereignisse pro Mandant.

## Release- und Betriebsanforderungen

- **Konfigurationsverwaltung**: Sensible Einstellungen (z. B. Secrets, SMTP-Zugangsdaten) werden ausschließlich über Environment-Variablen oder ein Secrets-Management-System gepflegt.
- **Logging & Monitoring**: Zentrales strukturiertes Logging (JSON) mit Rotation sowie Mandantenkennzeichnung. Basis-Metriken (Latenz, Fehlerraten) werden in Prometheus/Grafana überwacht.
- **Backup-Strategie**: Tägliche Datenbank-Backups inkl. Datei-Uploads, verschlüsselt gespeichert und automatisiert auf Wiederherstellbarkeit getestet.
- **Deployment-Pipeline**: CI/CD-Pipeline (z. B. GitHub Actions) führt automatisierte Tests, statische Analysen und Sicherheits-Scans aus, bevor ein Deployment in die Staging- bzw. Produktionsumgebung erfolgt.

## Projektstruktur

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI-Anwendung
│   ├── database.py          # Datenbankverbindung
│   ├── models.py            # SQLModel-Datenmodelle
│   ├── schemas.py           # Pydantic-Schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── projects.py      # Projekt-Router
│   │   ├── reports.py       # Bericht-Router
│   │   └── offers.py        # Angebot-Router
│   └── utils/
│       ├── __init__.py
│       └── pdf_utils.py     # PDF-Generierung
├── requirements.txt
└── README.md
```

