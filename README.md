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

