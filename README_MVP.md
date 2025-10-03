# 🏗️ Bau-Dokumentations-App MVP

Eine moderne, benutzerfreundliche Anwendung speziell für kleinere Bauunternehmer wie Trockenbau. Verwaltung von Projekten, Mitarbeitern, Stundenerfassung, Berichten und Angeboten.

## ✨ Features

### 📊 Dashboard
- Übersicht über alle Projekte, Berichte und Angebote
- Statistiken und Kennzahlen
- Letzte Aktivitäten

### 🏗️ Projekt-Management
- Erstellen, bearbeiten und löschen von Projekten
- Projektstatus verwalten (Aktiv, Pausiert, Abgeschlossen)
- Kunden- und Adressinformationen
- Projekttyp-Spezialisierung (Trockenbau, Renovierung, etc.)
- Flächen- und Stundenschätzung
- Stundensatz-Verwaltung

### 👥 Mitarbeiter-Management
- Mitarbeiterstammdaten verwalten
- Positionen und Stundensätze definieren
- Kontaktdaten und Status verwalten

### ⏰ Stundenerfassung
- Tägliche Arbeitszeiten erfassen
- Projekt- und Mitarbeiterzuordnung
- Automatische Kostenberechnung
- Arbeitsbeschreibungen dokumentieren

### 📝 Trockenbau-Berichte
- Spezialisierte Berichte für Trockenbau
- Arbeitsart-Tracking (Gipskarton, Dämmung, etc.)
- Materialverbrauch dokumentieren
- Qualitätskontrolle und Problemverfolgung
- Fortschrittsverfolgung in m²
- Nächste Schritte planen

### 💰 Angebots-Management
- Professionelle Angebote erstellen
- Mehrere Angebotspositionen
- PDF-Export für Kunden
- Status-Tracking (Entwurf, Versendet, Angenommen, Abgelehnt)

### 🧾 Rechnungs-Management
- Automatische Rechnungen aus Stunden und Materialien
- Angebot-zu-Rechnung Konvertierung
- Professionelle PDF-Rechnungen mit MwSt.
- Rechnungsstatus verwalten
- Fälligkeitsdaten und Zahlungsverfolgung

## 🚀 Installation & Start

### Voraussetzungen
- Python 3.11 oder höher
- pip (Python Package Manager)

### 1. Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```

### 2. Anwendung starten
```bash
python start.py
```

### 3. Anwendung öffnen
- **Frontend**: http://localhost:8000/app
- **API Dokumentation**: http://localhost:8000/docs
- **API Root**: http://localhost:8000/

## 🎯 MVP-Features

### ✅ Implementiert
- [x] Moderne, responsive Benutzeroberfläche
- [x] Projekt-Management (CRUD) - speziell für Trockenbau
- [x] Mitarbeiter-Management (CRUD)
- [x] Stundenerfassung mit automatischer Kostenberechnung
- [x] Trockenbau-spezialisierte Berichte
- [x] Angebots-Management (CRUD)
- [x] PDF-Generierung für Angebote
- [x] Dashboard mit Statistiken
- [x] SQLite-Datenbank
- [x] RESTful API
- [x] Fehlerbehandlung
- [x] Responsive Design
- [x] Bild-Upload für Projekte
- [x] Materialverbrauch-Tracking

### 🔄 Geplant für nächste Version
- [ ] Benutzer-Authentifizierung
- [ ] Bild-Upload für Berichte
- [ ] E-Mail-Versand von Angeboten
- [ ] Backup-Funktionen
- [ ] Erweiterte Suchfunktionen
- [ ] Mobile App

## 🛠️ Technologie-Stack

### Backend
- **FastAPI** - Moderne Python Web-Framework
- **SQLModel** - Type-safe ORM
- **SQLite** - Leichte Datenbank
- **fpdf2** - PDF-Generierung

### Frontend
- **HTML5** - Struktur
- **Bootstrap 5** - CSS-Framework
- **JavaScript (ES6+)** - Interaktivität
- **Font Awesome** - Icons

## 📁 Projektstruktur

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI-Anwendung
│   ├── database.py          # Datenbankverbindung
│   ├── models.py            # Datenmodelle
│   ├── schemas.py           # API-Schemas
│   ├── routers/             # API-Router
│   │   ├── projects.py      # Projekt-Endpunkte
│   │   ├── reports.py       # Bericht-Endpunkte
│   │   └── offers.py        # Angebot-Endpunkte
│   └── utils/
│       └── pdf_utils.py     # PDF-Generierung
├── static/
│   ├── index.html           # Frontend-Interface
│   └── app.js               # Frontend-Logik
├── uploads/
│   └── images/              # Hochgeladene Bilder
├── requirements.txt         # Python-Abhängigkeiten
├── start.py                 # Startup-Script
└── README_MVP.md           # Diese Datei
```

## 🔧 API-Endpunkte

### Projekte
- `GET /projects/` - Alle Projekte abrufen
- `POST /projects/` - Neues Projekt erstellen
- `GET /projects/{id}` - Einzelnes Projekt abrufen
- `PUT /projects/{id}` - Projekt aktualisieren
- `DELETE /projects/{id}` - Projekt löschen

### Mitarbeiter
- `GET /employees/` - Alle Mitarbeiter abrufen
- `POST /employees/` - Neuen Mitarbeiter erstellen
- `GET /employees/{id}` - Einzelnen Mitarbeiter abrufen
- `PUT /employees/{id}` - Mitarbeiter aktualisieren
- `DELETE /employees/{id}` - Mitarbeiter deaktivieren

### Stundenerfassung
- `GET /time-entries/` - Alle Stundeneinträge abrufen
- `POST /time-entries/` - Neuen Stundeneintrag erstellen
- `GET /time-entries/{id}` - Einzelnen Stundeneintrag abrufen
- `PUT /time-entries/{id}` - Stundeneintrag aktualisieren
- `DELETE /time-entries/{id}` - Stundeneintrag löschen
- `GET /time-entries/project/{id}` - Stundeneinträge eines Projekts
- `GET /time-entries/employee/{id}` - Stundeneinträge eines Mitarbeiters

### Projektbilder
- `GET /project-images/` - Alle Projektbilder abrufen
- `POST /project-images/` - Neues Projektbild hochladen
- `GET /project-images/{id}` - Einzelnes Projektbild abrufen
- `DELETE /project-images/{id}` - Projektbild löschen
- `GET /project-images/project/{id}` - Bilder eines Projekts

### Rechnungen
- `GET /invoices/` - Alle Rechnungen abrufen
- `POST /invoices/` - Neue Rechnung erstellen
- `GET /invoices/{invoice_id}` - Einzelne Rechnung abrufen
- `PUT /invoices/{invoice_id}` - Rechnung aktualisieren
- `DELETE /invoices/{invoice_id}` - Rechnung löschen
- `POST /invoices/{invoice_id}/pdf` - PDF-Rechnung generieren
- `GET /invoices/project/{project_id}` - Rechnungen eines Projekts
- `POST /invoices/from-offer/{offer_id}` - Rechnung aus Angebot erstellen
- `POST /invoices/auto-generate/{project_id}` - Automatische Rechnung generieren

### Trockenbau-Berichte
- `GET /reports/` - Alle Berichte abrufen
- `POST /reports/` - Neuen Bericht erstellen
- `GET /reports/{id}` - Einzelnen Bericht abrufen
- `PUT /reports/{id}` - Bericht aktualisieren
- `DELETE /reports/{id}` - Bericht löschen
- `GET /reports/project/{id}` - Berichte eines Projekts

### Angebote
- `GET /offers/` - Alle Angebote abrufen
- `POST /offers/` - Neues Angebot erstellen
- `GET /offers/{id}` - Einzelnes Angebot abrufen
- `PUT /offers/{id}` - Angebot aktualisieren
- `DELETE /offers/{id}` - Angebot löschen
- `POST /offers/{id}/pdf` - PDF generieren

## 🎨 Benutzeroberfläche

Die Anwendung bietet eine moderne, intuitive Benutzeroberfläche mit:

- **Dashboard**: Übersicht über alle wichtigen Kennzahlen
- **Sidebar-Navigation**: Einfache Navigation zwischen den Bereichen
- **Responsive Design**: Funktioniert auf Desktop, Tablet und Mobile
- **Moderne UI-Komponenten**: Bootstrap 5 mit Custom-Styling
- **Interaktive Formulare**: Benutzerfreundliche Eingabefelder
- **Echtzeit-Updates**: Sofortige Aktualisierung der Daten

## 🔒 Sicherheit

- CORS-Konfiguration für Frontend-Kommunikation
- Input-Validierung auf API-Ebene
- Strukturierte Fehlerbehandlung
- SQL-Injection-Schutz durch SQLModel

## 📈 Performance

- Asynchrone API-Endpunkte
- Effiziente Datenbankabfragen
- Client-seitiges Caching
- Optimierte Frontend-Ladung

## 🐛 Fehlerbehandlung

- Globale Exception Handler
- Benutzerfreundliche Fehlermeldungen
- Strukturiertes Logging
- Graceful Error Recovery

## 📝 Lizenz

Dieses Projekt ist für den privaten und kommerziellen Gebrauch bestimmt.

## 🤝 Support

Bei Fragen oder Problemen:
1. Überprüfen Sie die API-Dokumentation unter `/docs`
2. Schauen Sie in die Logs für detaillierte Fehlermeldungen
3. Stellen Sie sicher, dass alle Abhängigkeiten installiert sind

---

**Viel Erfolg mit Ihrer Bau-Dokumentations-App! 🏗️✨**
