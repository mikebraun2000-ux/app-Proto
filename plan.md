# 🏗️ Bau-Dokumentations-App - Verbesserungsplan

## 📋 Aktueller System-Status

### ✅ **Was bereits implementiert ist:**

**Backend (FastAPI + SQLModel):**
- Vollständige CRUD-APIs für alle Kernobjekte
- SQLite-Datenbank mit strukturierten Modellen
- PDF-Generierung für Rechnungen
- Automatische Rechnungserstellung aus Stunden/Materialien
- Stundenerfassung mit Kostenberechnung
- Mitarbeiter-Management
- Projekt-Management

**Frontend:**
- Bootstrap 5 UI mit responsivem Design
- Dashboard mit Statistiken
- Vollständige CRUD-Interfaces für alle Module

### 🎯 **Kernfunktionen - Aktueller Stand:**

1. **⏰ Zeiterfassung**: ✅ Grundfunktionen vorhanden
2. **👥 Nutzerverwaltung**: ✅ Mitarbeiter-Management vorhanden  
3. **💰 Automatische Rechnungserstellung**: ✅ Basis-Implementierung vorhanden

---

## 🚀 **Verbesserungsplan für die Kernfunktionen**

## 1. **⏰ Zeiterfassung - Verbesserungsvorschläge**

### **Aktuelle Stärken:**
- Vollständige CRUD-API vorhanden
- Automatische Kostenberechnung
- Projekt- und Mitarbeiterzuordnung

### **Geplante Verbesserungen:**

#### **A) Benutzerfreundlichkeit:**
- **Schnell-Eingabe-Interface**: Ein-Klick-Zeiterfassung für häufige Tätigkeiten
- **Zeitstempel-Buttons**: "Jetzt starten/stoppen" Funktionalität
- **Vorlagen**: Häufige Arbeitsbeschreibungen als Dropdown
- **Mobile-optimierte Eingabe**: Touch-freundliche Zeitauswahl

#### **B) Validierung & Qualitätssicherung:**
- **Überstunden-Warnung**: Bei >8h/Tag automatische Benachrichtigung
- **Doppelte Einträge verhindern**: Prüfung auf überlappende Zeiten
- **Pflichtfelder**: Arbeitsbeschreibung als Pflichtfeld
- **Zeitbereich-Validierung**: Nur Arbeitszeiten 6:00-22:00 erlaubt

#### **C) Berichte & Auswertungen:**
- **Tägliche/Wöchentliche Übersicht**: Zeit pro Mitarbeiter/Projekt
- **Produktivitäts-Metriken**: Stunden pro m², Effizienz-Kennzahlen
- **Export-Funktionen**: Excel/CSV für Buchhaltung
- **Visuelle Charts**: Zeitverläufe, Projektfortschritt

---

## 2. **👥 Nutzerverwaltung - Verbesserungsvorschläge**

### **Aktuelle Stärken:**
- Mitarbeiter-CRUD vollständig implementiert
- Stundensätze pro Mitarbeiter
- Aktiv/Inaktiv Status

### **Geplante Verbesserungen:**

#### **A) Rollen & Berechtigungen:**
- **Benutzerrollen**: Admin, Projektleiter, Mitarbeiter, Buchhaltung
- **Berechtigungsmatrix**: Wer darf was sehen/bearbeiten
- **Projekt-Zugriff**: Mitarbeiter nur für zugewiesene Projekte
- **Rechnungs-Zugriff**: Nur Buchhaltung kann Rechnungen erstellen

#### **B) Benutzer-Authentifizierung:**
- **Login-System**: Passwort-basierte Anmeldung
- **Session-Management**: Automatische Abmeldung nach Inaktivität
- **Passwort-Richtlinien**: Mindestlänge, Komplexität
- **Profil-Management**: Eigene Daten bearbeiten

#### **C) Erweiterte Mitarbeiter-Features:**
- **Qualifikationen**: Zertifikate, Fähigkeiten, Spezialisierungen
- **Verfügbarkeit**: Urlaub, Krankheit, Arbeitszeiten
- **Projektzuweisungen**: Welcher Mitarbeiter arbeitet an welchem Projekt
- **Performance-Tracking**: Arbeitsqualität, Pünktlichkeit

---

## 3. **💰 Automatische Rechnungserstellung - Verbesserungsvorschläge**

### **Aktuelle Stärken:**
- Automatische Generierung aus Stunden + Materialien
- PDF-Export funktioniert
- Angebot-zu-Rechnung Konvertierung

### **Geplante Verbesserungen:**

#### **A) Rechnungs-Templates & Vorlagen:**
- **Firmen-Templates**: Logo, Adresse, Zahlungsbedingungen
- **Rechnungstypen**: Teilrechnung, Schlussrechnung, Abschlagsrechnung
- **Automatische Nummerierung**: Fortlaufende Rechnungsnummern
- **MwSt-Handling**: Automatische Berechnung, verschiedene Sätze

#### **B) Workflow-Automatisierung:**
- **Rechnungszyklen**: Monatliche/quartalsweise automatische Rechnungen
- **Erinnerungen**: Zahlungserinnerungen, Mahnungen
- **Status-Tracking**: Entwurf → Versendet → Bezahlt → Überfällig
- **Zahlungsverfolgung**: Eingangsbestätigungen, Teilzahlungen

#### **C) Erweiterte Rechnungsfeatures:**
- **Skonto-Handling**: Frühzahlungsrabatte
- **Zahlungsarten**: Überweisung, SEPA, PayPal
- **Mehrsprachigkeit**: Deutsch/Englisch Templates
- **E-Mail-Integration**: Automatischer Versand an Kunden
- **Buchhaltungs-Export**: DATEV, CSV für Steuerberater

---

## 🗺️ **Implementierungs-Roadmap**

### **Phase 1: Sofortige Verbesserungen (1-2 Wochen)**
**Priorität: HOCH** 🔴

1. **Zeiterfassung UI/UX:**
   - Schnell-Eingabe-Interface
   - Zeitstempel-Buttons (Start/Stop)
   - Mobile-Optimierung

2. **Validierung:**
   - Überstunden-Warnung
   - Doppelte Einträge verhindern
   - Pflichtfelder

3. **Basis-Berichte:**
   - Tägliche/Wöchentliche Übersicht
   - Excel-Export

### **Phase 2: Nutzerverwaltung (2-3 Wochen)**
**Priorität: HOCH** 🔴

1. **Login-System:**
   - Passwort-Authentifizierung
   - Session-Management
   - Basis-Berechtigungen

2. **Rollen-System:**
   - Admin, Projektleiter, Mitarbeiter
   - Projekt-Zugriffskontrolle

### **Phase 3: Rechnungs-Automatisierung (3-4 Wochen)**
**Priorität: MITTEL** 🟡

1. **Templates:**
   - Firmen-Logo/Adresse
   - Rechnungstypen
   - Automatische Nummerierung

2. **Workflow:**
   - Status-Tracking
   - Zahlungserinnerungen
   - E-Mail-Integration

### **Phase 4: Erweiterte Features (4+ Wochen)**
**Priorität: NIEDRIG** 🟢

1. **Performance-Tracking**
2. **Erweiterte Berichte**
3. **Mobile App**
4. **API-Integrationen**

---

## 📊 **Zusammenfassung & Empfehlungen**

### **🎯 Nächste Schritte:**

**Sofort starten mit:**
1. **Zeiterfassung UI verbessern** - Größter Nutzen für tägliche Arbeit
2. **Login-System implementieren** - Sicherheit und Benutzerfreundlichkeit
3. **Rechnungs-Templates** - Professionelleres Aussehen

### **💡 Technische Empfehlungen:**

#### **Backend-Erweiterungen:**
- JWT-Token für Authentifizierung
- Erweiterte Validierung in den APIs
- Caching für bessere Performance

#### **Frontend-Verbesserungen:**
- React/Vue.js für bessere Interaktivität (optional)
- Progressive Web App (PWA) für Mobile
- Offline-Funktionalität

#### **Datenbank:**
- Migration zu PostgreSQL für Produktion
- Backup-Strategien
- Datenbank-Indizes für Performance

### **🚀 Sofortige Quick-Wins:**

## 🔐 Sicherheits- und Mandantenkonzept

- **Mandantenkontext**: Jeder Request führt eine `tenant_id`, die beim Login im JWT hinterlegt und bei jeder Datenbankabfrage als Filter erzwungen wird. Alle Tabellen besitzen eine verpflichtende Tenant-Spalte.
- **Isolierte Speicherbereiche**: Datei-Uploads werden in nach Mandant getrennten Verzeichnissen mit Zugriffsbeschränkungen gespeichert. Für eine PostgreSQL-Migration werden pro Mandant Schema-Segregation und Row-Level-Security-Regeln vorbereitet.
- **Rollenmodell**: Innerhalb eines Mandanten steuern Rollen (Admin, Projektleitung, Buchhaltung, Mitarbeiter) die verfügbaren Endpunkte und Aktionen. Sensible Aktionen lösen zusätzliche Prüfungen (Audit-Log, Step-up-PIN) aus.
- **Sicherheitsmaßnahmen**: Durchgehende TLS-Verschlüsselung, harte Passwort-Policies, Rotation von Anwendungsschlüsseln sowie Sicherheits-Scans (Dependency-Checks, SAST) in der Pipeline.

## 🚀 Go-Live Fahrplan

1. **Stufe 0 – Vorbereitung (Woche 1)**
   - Abgleich der Anforderungen mit Stakeholdern, Definition von Tenants und Rollen.
   - Infrastruktur vorbereiten (Produktions- und Staging-Umgebungen, Secrets-Management).
   - Aufsetzen der CI/CD-Pipeline inkl. statischer Analysen, Tests und Security-Checks.
2. **Stufe 1 – Technische Stabilisierung (Woche 2)**
   - Automatisierte Testsuite (Unit, Integration, API-Contract) vervollständigen.
   - Datenbank-Migration mit Tenant-Spalte und Seed-Daten für Muster-Mandanten.
   - Einführung von strukturiertem Logging und Basis-Monitoring.
3. **Stufe 2 – Qualitätssicherung (Woche 3)**
   - End-to-End-Tests in Staging mit realistischen Mandanten-Szenarien.
   - Penetrationstest/Threat-Modeling mit Fokus auf Tenant-Isolation und Auth.
   - Abnahme durch Key-User, Schulungen für Admin- und Buchhaltungsrollen.
4. **Stufe 3 – Produktionsstart (Woche 4)**
   - Backup-Plan aktivieren: tägliche DB-Dumps, stündliche Log-Exports, Restore-Tests.
   - Datenmigration aus Alt-Systemen, Validierung durch Stichproben.
   - Finaler Go/No-Go-Workshop, Release-Freeze, Deployment in Produktion.
5. **Stufe 4 – Hypercare (Woche 5)**
   - Engmaschiges Monitoring, Incident-Playbook aktiv halten.
   - Geplante Patch-Fenster für Hotfixes, Abschlussbericht nach 2 Wochen.

### 🔬 Teststrategie

- **Automatisierte Tests**: Unit- und Integrationstests pro Module, End-to-End-Suites für kritische Mandanten-Flows, Security-Tests (JWT-Manipulation, Rechteeskalation).
- **Manuelle Tests**: Explorative Tests durch Fachanwender, Regressionstests vor Release, Checklisten für Mandantenwechsel.
- **Backup- und Restore-Tests**: Monatliche Restore-Übungen auf separatem System, Validierung der Datenkonsistenz und Zugriffstrennung.

## ⚠️ Offene Risiken

- **Datenbank-Migration**: Wechsel von SQLite zu PostgreSQL ist notwendig für echte Mandantenfähigkeit; Risiko durch Migrationskomplexität.
- **Rechteverwaltung**: Rollenkonzept muss sauber implementiert werden, sonst drohen Rechte-Eskalationen.
- **Performance**: Mandantenfilter können Abfragen verlangsamen; Indizes und Query-Optimierung sind einzuplanen.
- **Organisatorische Adoption**: Schulungsaufwand für Nutzer, besonders bei mehrstufiger Authentifizierung.

1. **Zeiterfassung-Validierung** (1 Tag)
2. **Bessere Fehlermeldungen** (1 Tag)  
3. **Export-Funktionen** (2 Tage)
4. **Mobile-Responsive Verbesserungen** (2 Tage)

---

## 📝 **Detaillierte Aufgabenliste**

### **Zeiterfassung Verbesserungen:**

#### **UI/UX Verbesserungen:**
- [ ] Schnell-Eingabe-Interface für häufige Tätigkeiten
- [ ] Start/Stop Timer-Buttons
- [ ] Dropdown für Arbeitsbeschreibungen
- [ ] Mobile-optimierte Zeitauswahl
- [ ] Touch-freundliche Bedienung

#### **Validierung:**
- [ ] Überstunden-Warnung (>8h/Tag)
- [ ] Überlappende Zeiten verhindern
- [ ] Arbeitsbeschreibung als Pflichtfeld
- [ ] Zeitbereich-Validierung (6:00-22:00)
- [ ] Doppelte Einträge prüfen

#### **Berichte:**
- [ ] Tägliche Übersicht pro Mitarbeiter
- [ ] Wöchentliche Projektübersicht
- [ ] Excel/CSV Export
- [ ] Produktivitäts-Charts
- [ ] Zeitverlauf-Diagramme

### **Nutzerverwaltung Verbesserungen:**

#### **Authentifizierung:**
- [ ] Login-System implementieren
- [ ] Passwort-Hashing (bcrypt)
- [ ] Session-Management
- [ ] Automatische Abmeldung
- [ ] Passwort-Richtlinien

#### **Rollen & Berechtigungen:**
- [ ] Benutzerrollen definieren
- [ ] Berechtigungsmatrix erstellen
- [ ] Projekt-Zugriffskontrolle
- [ ] Rechnungs-Berechtigungen
- [ ] Admin-Interface

#### **Erweiterte Features:**
- [ ] Mitarbeiter-Qualifikationen
- [ ] Verfügbarkeits-Kalender
- [ ] Projektzuweisungen
- [ ] Performance-Tracking
- [ ] Profil-Management

### **Rechnungs-Automatisierung:**

#### **Templates:**
- [ ] Firmen-Logo Integration
- [ ] Adress-Templates
- [ ] Rechnungstypen (Teil/Schluss/Abschlag)
- [ ] Automatische Nummerierung
- [ ] MwSt-Handling

#### **Workflow:**
- [ ] Status-Tracking System
- [ ] Zahlungserinnerungen
- [ ] Mahnungen
- [ ] Zahlungsverfolgung
- [ ] E-Mail-Integration

#### **Erweiterte Features:**
- [ ] Skonto-Handling
- [ ] Zahlungsarten
- [ ] Mehrsprachigkeit
- [ ] Buchhaltungs-Export
- [ ] Automatische Rechnungszyklen

---

## 🎯 **Erfolgsmetriken**

### **Zeiterfassung:**
- Reduzierung der Eingabezeit um 50%
- 90% weniger doppelte Einträge
- 100% Validierung der Arbeitszeiten

### **Nutzerverwaltung:**
- Sichere Anmeldung für alle Benutzer
- Rollenbasierte Zugriffskontrolle
- Zentrale Benutzerverwaltung

### **Rechnungs-Automatisierung:**
- 80% Reduzierung der manuellen Rechnungsarbeit
- Automatische Rechnungsgenerierung
- Professionelle PDF-Templates

---

**Erstellt am:** $(date)  
**Version:** 1.0  
**Status:** Planungsphase

---

# 🌐 SaaS-Mandantenfähigkeit & Benutzer=Mitglieder-Konzept (Detailplan)

## 0. Zielbild

- Ein Kunde erwirbt ein Abo → automatisierte Mandantenanlage mit erstem Admin-Zugang
- Jeder Mitarbeiter ist gleichzeitig ein Benutzerkonto (Single Source of Truth)
- Trennung aller Daten per `tenant_id`, DSGVO-konformes Lifecycle-Management
- Erweiterbar für dynamische Rollenmodelle, Branding, Steuer-Settings, Stripe-Billing
- UI konsolidiert: „Benutzer & Rollen“ ersetzt „Mitarbeiter“

## 1. Architektur-Überblick

### 1.1 Komponenten
- **FastAPI Backend** (weiterhin monolithisch, modulare Router)
- **SQLModel / SQLAlchemy** mit Mandanten-Attributen
- **PostgreSQL (Produktiv)**, SQLite nur lokal → Migration vorbereitet
- **Stripe Billing** (Checkout, Webhooks, Portal)
- **Mail-Dienst** (z. B. SendGrid) für Einladungen & Reminder
- **Frontends**: bestehendes HTML/JS (später ggf. auf SPA migrierbar)

### 1.2 Mandanten-Isolation
- Jeder User hat `tenant_id`
- Alle Geschäftsobjekte (Projekte, Angebote, Rechnungen, Zeiterfassungen, Dokumente, Logos) referenzieren `tenant_id`
- Queries erhalten zentrale Filter-Helfer (`TenantScopedQuery`)
- Background-Jobs (Reminder, Cleanup) laufen pro Tenant

### 1.3 Tenant Settings
- Tabelle `tenant_settings`
  - `tenant_id`
  - `branding` (JSON: Farben, Logo-IDs, PDF-Titel)
  - `invoice_config` (JSON: Steuer-IDs, Nummernkreis, IBAN, Textbausteine)
  - `compliance` (JSON: Aufbewahrungsfristen, Löschregeln)
  - `timestamps`
- Zugriff via Service-Layer + Cache (In-Memory oder Redis-ready)

## 2. Datenmodell & Migrationen

### 2.1 Tabellen-Erweiterungen
- `tenant` (neu): `id`, `name`, `status`, `subscription_status`, `stripe_customer_id`, `stripe_subscription_id`, `current_period_end`, `trial_end`, `created_at`, `updated_at`
- `tenant_user` (neu, optional als Join): `tenant_id`, `user_id`, `role_id`, `invited_by`
- Bestehende Tabellen (`project`, `invoice`, `offer`, `time_entry`, `company_logo`, …) erhalten `tenant_id`
- `users` (Bestand) → Spalten ergänzen: `tenant_id`, `position`, `hourly_rate`, `phone`, `address`, `invite_token`, `invite_expires_at`, `password_set_at`
- `roles`, `permissions`, `role_permissions`, `user_roles` (für zukünftiges dynamisches RBAC) – initial befüllt mit Standardrollen

### 2.2 Migrationstrategie
1. Alembic-Skripte erzeugen (obwohl SQLModel → direkter Einsatz von Alembic empfohlen)
2. Migration 001: Tabellen `tenant`, `tenant_settings`
3. Migration 002: `tenant_id` zu allen Kern-Tabellen hinzufügen (Default = 1 für Bestandsmandant)
4. Migration 003: `users`-Erweiterung (Mitarbeiter-Felder + Invite)
5. Migration 004: Optionale RBAC-Tabellen
6. Datenmigration: bestehende Employees → Users mappen
   - Für `employee.full_name`: Split in Vor-/Nachname, generiere E-Mail `vorname.nachname@test.local`
   - Stundensätze, Position, Kontaktdaten übertragen
   - Admin-Mapping: existierender Superuser bleibt Admin
   - Zeit- und Projekt-Referenzen anpassen (`employee_id` → `user_id`)

### 2.3 Datenbankkompatibilität
- Alembic Templates Postgres- und MySQL-kompatibel gestalten (z. B. `UUID` vs. `VARCHAR`)
- Nutzung von `naming_convention` für Constraints
- Indexe anlegen (`tenant_id`, `status`, `created_at`)

## 3. Geschäftslogik & APIs

### 3.1 Auth & Onboarding
- `POST /tenants/register` – nimmt Firmenname, Admin-Kontakt, Payment-Plan-ID entgegen
- Stripe Checkout Session → Redirect
- Webhook `checkout.session.completed` → erstellt Tenant + Admin-User, sendet Einladung
- Einladungslink (`/auth/accept-invite?token=...`) gültig 7 Tage, einmalig, TLS-geschützt
- `POST /auth/invite` – Admin lädt Mitarbeiter ein; optional Rolle, Position, Stundensatz
- `POST /auth/accept-invite` – setzt Passwort, bestätigt AGB/DSGVO
- `POST /auth/resend-invite`, `DELETE /auth/invite/{id}`
- Login `POST /auth/login` liefert JWT/Sets cookie; Claims: `sub`, `tenant_id`, `role`, `exp`

### 3.2 Benutzer-Management
- `GET /users` – tenant-spezifisch, filterbar nach Rolle/Status
- `POST /users` – legt Benutzer direkt an (optional sofort aktiv, sonst Einladung)
- `PUT /users/{id}` – Update (Name, Rolle, Stundensatz, Mobilnummer, …)
- `POST /users/{id}/reset-password` – Admin setzt Passwort neu
- `POST /users/{id}/deactivate` / `activate`
- Self-Service: `GET/PUT /users/me/profile` (+Telefon, Adresse, Bankdaten)

### 3.3 Rollen & Berechtigungen
- Kurzfristig: `UserRole` Enum weiterverwenden (admin/buchhalter/mitarbeiter)
- Langfristig: `roles`-Tabelle, UI zum Rollen-Config
- Permission-Matrix definieren:
  - `admin`: alle Ressourcen, Mandanten-Einstellungen, Billing, Einladung
  - `buchhalter`: Angebote, Rechnungen, Reports, aber kein User-Management
  - `mitarbeiter`: eigene Zeiterfassung, zugewiesene Projekte, Dokumente
  - Gatekeeper in Endpoints (`require_role` erweitert um Tenant)

### 3.4 Tenant Settings & Branding
- `GET/PUT /tenant/settings` – Admin pflegt Branding (Logo, Farben), Rechnungsnummernkreise, Steuer-ID, Zahlungsbedingungen, DSGVO-Optionen
- PDF-Generator `beautiful_pdf_generator` lädt Settings → generiert Layout dynamisch
- Invoice Preview (Frontend) zeigt Branding live an (Cache-Busting)

### 3.5 Billing & Subscription Lifecycle
- Stripe Einrichtung:
  1. Produkte & Preise (Monat/Jahr, evtl. Staffelpreise)
  2. Checkout Link (Client-Integration) oder Billing Portal (Plan-Wechsel, Zahlungsmethode)
  3. Webhooks: `customer.subscription.created/updated/deleted`, `invoice.payment_failed/succeeded`
- Backend Actions:
  - `subscription_status`: `active`, `trialing`, `past_due`, `canceled`, `suspended`
  - Grace Period (z. B. 7 Tage Past Due) → danach `suspended`
  - `POST /billing/reactivate` – generiert Portal Link
- Reminder Jobs (Celery/apscheduler): 7 Tage vor Ablauf, am Tag X, 3 Tage nach Ablauf

#### 3.5.1 Stripe-Sandbox & Testkunden Setup
1. **Haupt-Sandbox-Konto anlegen:**
   - Auf stripe.com registrieren, „Testmodus“ aktivieren
   - API-Keys (Publishable + Secret) notieren → `.env` Einträge `STRIPE_TEST_PUBLISHABLE_KEY`, `STRIPE_TEST_SECRET_KEY`
2. **Zusätzliche Sandbox-Accounts (A–C):**
   - Zwei weitere Testkonten über neue Stripe-Registrierungen anlegen
   - Nutzungsideen: A = Standardflow, B = Planwechsel/Preisanpassung, C = Fehlerfälle/Webhook-Retries
   - Keys entsprechend dokumentieren (`STRIPE_TEST_SECRET_KEY_B`, `STRIPE_TEST_SECRET_KEY_C` etc.)
3. **Testkunden D & E:**
   - In Sandbox A unter "Kunden" zwei Dummy-Kunden anlegen (z. B. `tenant-test-d`, `tenant-test-e`)
   - Für jeden Kunden ein Test-Abo mit dem 49 €-Monats-Preis erzeugen
   - Customer-IDs (`cus_…`) und Subscription-IDs (`sub_…`) notieren → spätere Stresstests/Sperrlogik
4. **Plan-/Preisverwaltung:**
   - Produkt "BauDocs Subscription" anlegen, Price-ID `price_49_monthly`
   - Für künftige Preisanpassungen zusätzliche Prices anlegen (z. B. `price_59_monthly`, `price_annual_499`)
   - Im Backend nur die aktive Price-ID aus `.env` ziehen (`STRIPE_ACTIVE_PRICE_ID`)
5. **Webhook-Testvorbereitung:**
   - Stripe CLI installieren (`stripe login`)
   - Forwarding-Command notieren (`stripe listen --forward-to localhost:8000/billing/webhooks`)
   - Testevents definieren (Success, Failure, Cancellation)
6. **Dokumentation & Secrets-Verwaltung:**
   - Tabelle in `plan.md` oder separater Notion/Confluence-Seite mit Account/Key-Zuordnung pflegen
   - Sicherstellen, dass Keys nur lokal/.env liegen; keine Commits in Git

#### 3.5.2 Aktuelle Stripe-Konfiguration (Stand 02.10.2025)
- `STRIPE_TEST_PUBLISHABLE_KEY`: `pk_test_51SDaKGQpDeiCy5Mxk5mxhyy7ZmmfbmoyOsJvPDjIByawgMUU5Hy6ALpOjCzmRXcyY8Xs0C68qnR5V796iOp02rjV00xqAqExEi`
- `STRIPE_TEST_SECRET_KEY`: (rotierter Test-Secret-Key, lokal in `.env`, nicht im Repo)
- Produkt: `prod_T9uDmiWk52j7F9` („Monatsabo 49 €“)
- Aktiver Preis (Monat, 49 €): `price_1SDaPGQpDeiCy5Mxx8VOvW4t`
- Default-Checkout-URLs (lokal):
  - Erfolg: `http://localhost:8000/app#billing-success`
  - Abbruch: `http://localhost:8000/app#billing-cancel`
- Webhook-Signing-Key: wird später ergänzt (`STRIPE_WEBHOOK_SECRET`), sobald Webhook/Stripe CLI angebunden ist

### 3.6 DSGVO & Retention
- `compliance.retention_days` pro Kategorie (Zeiteinträge, Dokumente, Logs)
- Cronjob löscht/anonymisiert Einträge > Frist, protokolliert in `audit_log`
- Option für Export/Account-Löschung auf Admin-Anfrage

## 4. Frontend-Umsetzung

### 4.1 Navigation & Layout
- Sidebar: „Dashboard“, „Projekte“, „Zeit“, „Angebote“, „Rechnungen“, „Berichte“, „Benutzer & Rollen“, „Verwaltung“, „Einstellungen“
- „Benutzer & Rollen“ mit Tabellen-Layout + Aktionen:
  - `name` (editierbar)
  - `username` (`nachname.vorname` – editierbar, unique)
  - `rolle` (Dropdown)
  - `position`, `stundensatz`, `telefon`, `status`
  - Buttons: Bearbeiten, Passwort zurücksetzen, Einladung erneut senden
- Einladungserstellung: Modal mit Feldern (Name, E-Mail, Rolle, Position, Stundensatz)
- Onboarding-Status (ausstehend vs. aktiv) visualisieren

### 4.2 Formular- & Datenfluss
- Client lädt `users` + `tenant_settings` beim Aufruf der Sektion
- POST-Requests für neue Benutzer, PUT für Updates
- Passwort-Reset: ruft `handleEmployeePasswordReset` (jetzt nur noch `resetUserPassword`), kein zusätzlicher Prompt
- Einladungsstatus/Token im Table Tag „Einladung läuft ab in X Tagen“

### 4.3 Mandantenkontext im Frontend
- Nach Login: `tenant_name` in Navbar/Sidebar
- Unter „Einstellungen“: Branding, Steuerdaten, Retention-Einstellungen
- Logoupload → `tenant_settings.branding.logo_id`

## 5. Sicherheit & Compliance

- JWT Refresh Tokens oder kurze Laufzeit + Silent Refresh
- CSRF-Schutz (für Cookie-basierten Ansatz)
- Rate Limiting für Login/Invite anlegbar (z. B. via `slowapi` oder reverse proxy)
- Audit-Trail (`audit_log` Tabelle) für Änderungen an Benutzern/Billing
- Logging mit Tenant-Tagging (JSON-Log, z. B. `tenant_id`, `user_id`, `action`)
- Zwei-Faktor-Authentisierung als Zukunftsausbau

## 6. Roadmap & Phasenplanung (Detail)

### Phase 0 – Grundlagen (1 Woche)
1. Alembic integrieren (falls noch nicht) & Basismigration vorbereiten
2. Tabellen `tenant`, `tenant_settings` anlegen
3. `tenant_id` in allen bestehenden Tabellen ergänzen, Backfill = 1
4. Services (z. B. `get_current_user`) um Tenant-Validierung erweitern

### Phase 1 – Benutzer=Mitarbeiter (2 Wochen)
1. Migration: `users` um Mitarbeiterfelder erweitern, `Employee`-Daten migrieren
2. Endpoints `employees` → `users` refactoren, alt: Deprecation + Weiterleitung
3. Frontend: Mitarbeiter-Sektion entfernen, neue Benutzerverwaltung integrieren
4. Passwort-Reset, Rollenumschaltung, Status-Anzeige direkt im UI
5. Tests: Unit (Mapping, Roles), Integration (UI Flow), Regression (Zeiterfassung)

### Phase 2 – Onboarding & Einladungen (2 Wochen)
1. Endpoints `POST /auth/invite`, `POST /auth/accept-invite`, Tokenhandling
2. E-Mail-Service anbinden (Template, TLS, Fallback Logging)
3. Frontend: Einladungsflow, Status-Anzeige, Resend/Sperren
4. Bestandsbenutzer: Admin kann Einladung erneut senden
5. Security: Tokens salted hashed speichern, TTL Check im Backend

### Phase 3 – Billing & Subscription (3 Wochen)
1. Stripe-Integration (API Keys, Secrets via ENV)
2. Checkout Flow + Webhook Endpoint + Tests mit Stripe CLI
3. Subscription Status ins Tenant-Modell übernehmen, Feature-Gates im Frontend
4. Reminder Jobs (apscheduler) + E-Mail Templates
5. UI: Billing-Seite (Status, Nächste Abbuchung, Portal-Link)

### Phase 4 – Settings & Branding (1.5 Wochen)
1. `tenant_settings` CRUD + Caching
2. Frontend-Formulare für Branding, Steuer, Compliance
3. PDF Generator + Preview um Settings erweitern
4. Tests für Layout & Fallbacks (kein Logo, Standardfarben)

### Phase 5 – DSGVO Automatisierung (1 Woche)
1. Retention-Konfiguration umsetzen
2. Cleanup-Jobs + Audit-Logs
3. Admin-Dashboard mit Lösch-/Export-Funktionen

### Phase 6 – RBAC (Optional, 2 Wochen)
1. Rollen-Tabellen finalisieren, UI für Rollen/Permissions
2. Mapping existierender Rollen auf RBAC-Struktur
3. Endpoint-Decorator umbauen (`@requires_permission`)

## 7. Risiken & Fallbacks
- **Migration**: Risiko inkonsistenter Daten → umfassende Backups + Dry-Run auf Kopie
- **Stripe**: Abhängigkeit von externem Service → Sandbox testen, Webhook-Signaturen validieren
- **Einladungen**: E-Mail Zustellung → Fallback (Token-URL im Admin UI anzeigen)
- **Mandantenfilter**: Gefahr unerwünschter Datenlecks → zentraler Query-Wrapper + Tests
- **Performance**: Tenant-Indexe auf allen Queries, Connection Pool prüfen

## 8. Monitoring & QA
- Unit-Tests für neue Services (Invite, Billing, Settings)
- Integrationstests (Registrierung → Invite → Login → Billing-Statuswechsel)
- End-to-End Smoke Tests (z. B. via Playwright) für kritische Flows
- Monitoring: Basic Health Endpoint (`/health/tenant`) + Prometheus/Logging-Vorbereitung

## 9. Dokumentation
- `README` aktualisieren (Setup mit Alembic, Stripe Webhooks, Mail)
- `plan.md` (dieses Dokument) regelmäßig fortschreiben
- Developer Guide: TenantID im Code, Testing-Strategie, Feature Flags
- Kundendoku: Onboarding, Benutzerverwaltung, Billing FAQ

---

✅ **Nächste konkrete Schritte (Kurzfassung)**
1. Alembic + Tenant-Basis-Migrationen implementieren
2. Employee → User Migration samt UI-Anpassungen
3. Einladungssystem & Passwortrücksetzung überarbeiten
4. Stripe-Integration vorbereiten (Sandbox Keys, Webhooks)
5. Tenant Settings APIs + Frontend entwerfen
6. DSGVO-Retention-Konzept verfeinern und automatisieren

Dieser Detailplan dient als Arbeitsgrundlage für die kommenden Iterationen und wird nach jeder Phase aktualisiert.

---

# 🔁 Überarbeitung des Plans – vertiefte Entscheidungen & Migrationsdetails

## A. Architektur‑Grundsatzentscheidungen (re‑evaluated)

- **Mandantenisolation (Start)**: Ein Datenbank‑Cluster, gemeinsame Schemata mit `tenant_id` auf allen Objekten; strikte Filterung in jedem Endpoint. Vorteil: geringe Komplexität, schnelle Umsetzung.  
  **Option (später)**: PostgreSQL Row Level Security (RLS) mit `SET app.tenant_id` je Session oder Schema‑pro‑Tenant für sehr große Kunden.  
  Entscheidung: Start mit `tenant_id` + konsistentem Filterlayer; RLS als möglicher Hardening‑Schritt in Phase 5+.

- **Users = Mitarbeiter**: `Employee` wird in `User` integriert (Profilfelder: `position`, `hourly_rate`, `phone`). Alle Referenzen (`employee_id`) werden auf `user_id` migriert. Eine schmale Compatibility‑Schicht übersetzt alte API‑Parameter, bis Frontend komplett umgestellt ist.

- **Benutzername‑Politik**: Standard `nachname.vorname` (ASCII, lowercased, Umlaute → ae/oe/ue/ss).  
  - Eindeutigkeit: per Tenant eindeutig; bei Kollision Suffix `-2`, `-3`, …  
  - Unabhängig von E-Mail; E-Mail kann leer sein (Testmigration), für Einladungen jedoch empfohlen/erforderlich.

- **Rollenmodell**: Kurzfristig fix (`admin`, `buchhalter`, `mitarbeiter`).  
  Vorbereitung RBAC: Tabellen `roles`, `permissions`, `role_permissions`, `user_roles` per Tenant; später aktivierbar, ohne Breaking Changes.

- **Tenant Settings**: Tabelle `tenant_settings` (typed + JSON‑Spalten) mit Validierung in Serviceschicht:  
  - Branding: Logo‑ID, Primärfarbe, Sekundärfarbe, PDF‑Titel, Fußzeile  
  - Rechnungen: Steuer‑ID/USt‑ID, IBAN/BIC, Zahlungsziel, Nummernkreis (Prefix, Start, Jahr‑Reset), Rundung  
  - Compliance: Aufbewahrungsfristen je Kategorie, Export/Anonymisierung  
  - Performance: leichte Caches, invalide bei Update, ETag für Frontend

- **Billing**: Stripe (Checkout + Billing Portal).  
  - Status: `trialing`, `active`, `past_due`, `canceled`, `suspended` (intern)  
  - Grace‑Period: z. B. 7 Tage nach `past_due`  
  - Feature‑Gates & Limits: Planabhängige Quoten (Benutzer, Projekte, Speicher)

- **Datenbank**: Entwicklung SQLite, Produktion PostgreSQL.  
  - Alembic‑Migrations strikt pflegen  
  - Indizes: `(tenant_id)`, `(tenant_id, status)`, `(tenant_id, created_at)`

- **Security**:  
  - JWT mit `tenant_id`, `role`, kurze Laufzeit + Refresh‑Mechanik  
  - Secrets über `.env`/Env‑Vars (nie im Code); CORS/TLS‑Härtung; Rate‑Limit auf Login/Invite  
  - Audit‑Logs für kritische Aktionen; E‑Mail‑Webhook‑Verifikation

## B. Migration „Employee → User“ (Detail)

1) Felder ergänzen: `user`: `tenant_id`, `position`, `hourly_rate`, `phone`, `address`, `invite_token`, `invite_expires_at`, `password_set_at`  
2) Mapping:
- Split `employee.full_name` in `vorname`, `nachname` (Fallback: Komplett in Nachname, Vorname = "user").
- Generiere `username = sanitize(nachname).".".sanitize(vorname)`; prüfe Kollision je Tenant → Suffix.
- Falls `employee.email` fehlt: setze Test‑E‑Mail `vorname.nachname+<id>@test.local` (nur Migration).
- Übertrage `hourly_rate`, `position`, `phone` in `user`.
- Markiere migrierte `employee` als „migrated“ (oder belasse Tabelle read‑only/hidden bis Cleanup).  
3) Referenzen: `time_entry.employee_id` → `user_id`, ebenso in Reports/Invoices/Offers falls vorhanden.  
4) Backfill‑Script mit Dry‑Run, Report (Kollisionen, fehlende Namen).  
5) Tests: 
- Unit: Username‑Generator, Sanitizer, Suffix‑Strategie  
- Integration: CRUD Zeitbuchung vor/nach Migration identisch  
- Regression: PDF‑Inhalte nutzen neuen Benutzerkontext

## C. Einladungen & Ablaufpolitik

- Invite‑Token (random, 32–64 Byte), Server‑seitig gehasht gespeichert, TTL default 7 Tage  
- Einmal nutzbar, danach invalid  
- Admin‑UI: Liste offener Einladungen, „erneut senden“, „löschen“, Restlaufzeit  
- Reminder E‑Mails: 3 Tage vor Ablauf, am letzten Tag  
- Nach Ablauf: erneuter Versand möglich (neues Token)  
- Optional: Einladung ohne E‑Mail via manuelle Übergabe eines sicheren Links (Admin sieht Token‑URL einmalig)

## D. DSGVO & Retention (konkret)

- Kategorien + Fristen pro Tenant:  
  - Zeiteinträge: z. B. 3 Jahre  
  - Rechnungsdokumente: 10 Jahre (gesetzlich), keine frühere Löschung  
  - Systemlogs: 30–90 Tage  
- Aktionen: Anonymisieren statt harter Löschung, wo fachlich möglich  
- Admin‑Exports (Maschinenlesbar, JSON/CSV/PDF), Right‑to‑be‑forgotten Workflows  
- Protokollierung jeder Lösch‑/Anonymisierungsaktion im `audit_log`

## E. Endpoint‑Umbau (Kurzüberblick)

- `GET /users` ersetzt `GET /employees` (Altroute: deprecated mit 302/410 und Hinweismeldung)  
- `POST /users` erlaubt: Namen, Rolle, Position, Stundensatz, optional E‑Mail → wahlweise direkte Anlage oder Invite  
- `POST /auth/invite`, `POST /auth/accept-invite`  
- `GET/PUT /tenant/settings`  
- `POST /billing/reactivate` liefert Stripe‑Portal  
- Alle `GET`/`POST`/`PUT`/`DELETE` Endpoints erhalten `tenant`‑Scoping im Service

## F. UI‑Konzept (präzisiert)

- Navigation: „Benutzer & Rollen“ bündelt bisherige Mitarbeiterfunktionen  
- Tabelle: `Name`, `Benutzername`, `Rolle`, `Position`, `Stundensatz`, `Status`, `Aktionen`  
- Aktionen: Bearbeiten (Modal), Passwort‑Reset (Admin), Einladung erneut senden (wenn ausstehend)  
- Filter: Rolle/Status  
- Einstellungen: Branding/Steuer/Compliance unter „Einstellungen“  
- Rechnungsvorschau liest Branding live; Cache‑Busting via Query‑Param (ts)

## G. Billing‑Flows (Stripe, konkret)

- Checkout: Preispläne (Monat/Jahr), optional Trial  
- Webhooks:  
  - `invoice.payment_succeeded` → `active`  
  - `invoice.payment_failed` → `past_due`  
  - `customer.subscription.deleted` → `canceled`  
  - App setzt `suspended` nach Grace‑Period  
- Reminder Mails: 7 Tage vorher, Tag X, +3 Tage danach  
- Reaktivierung: Portal‑Link im UI  
- Gating: Bei `suspended` nur Billing & Support sichtbar; Lesezugriff optional

## H. Qualität, Sicherheit, Betrieb

- Tests: 
  - Unit: Username‑Gen, Settings‑Validierung, Token‑TTL  
  - Integration: Invite‑Flow, Tenant‑Scoping, Billing‑Webhook  
  - E2E: Onboarding → Login → Useranlage → Rechnung mit Branding  
- Observability: strukturierte Logs (tenant_id, user_id, action), Basis‑Metriken  
- Backups: DB‑Dumps täglich, Verschlüsselung, Test‑Restore monatlich  
- Secrets: nur via env/KeyVault, strikte Trennung dev/stage/prod

## I. Roadmap (feiner)

1) Woche 1: Alembic, `tenant`, `tenant_settings`, Backfill `tenant_id`  
2) Woche 2–3: Migration Employee→User, Endpoints/Frontend refactor, Tests  
3) Woche 4–5: Invite‑Flow + E‑Mail, UI/Status/Reminder  
4) Woche 6–8: Stripe‑Integration komplett + Gates/Quoten  
5) Woche 9: Branding/Settings in PDF/Preview  
6) Woche 10: DSGVO‑Retention + Audit  
7) Optional 11–12: RBAC

## J. Risiken & Gegenmaßnahmen (Update)

- Datenlecks durch fehlenden Tenant‑Filter → zentraler Decorator + Tests  
- Username‑Kollisionen → Suffix‑Strategie + Validierung im Backend  
- Invite‑Zustellung scheitert → Admin‑Fallback: Token‑URL manuell kopieren  
- Billing‑Inkongruenzen → Webhook‑Signaturprüfung + idempotente Handler

---

Dieses Update schärft Entscheidungen (Isolationsmodell, Username‑Politik), macht Migration und Endpoints konkreter, stärkt Compliance/Billing und legt eine feinere Roadmap fest. Es bleibt erweiterbar für RBAC und RLS.

---

# 🧭 Schritt‑für‑Schritt‑Vorgehen mit Risiken, Prüfungen und Rollback‑Strategie

## Phase 0 – Vorbereitung & Sicherheitsnetz

1. Repro‑Sicherung
   - [ ] Vollständiges DB‑Backup (dev/test/prod getrennt)
   - [ ] Versionsstände taggen (`pre-tenant-migration`)
   - [ ] Feature‑Flag „multi_tenant_enabled=false“ einführen (ENV)
   - Akzeptanzkriterium: Restore‑Test erfolgreich (Stichprobe)
   - Risiko: Unvollständige Backups → Maßnahme: Test‑Restore vor Start

2. Alembic integrieren
   - [ ] Alembic scaffold, naming_convention setzen
   - [ ] CI‑Check: `alembic upgrade head` muss lokal/CI laufen
   - Risiko: Divergierende lokale DBs → Maßnahme: `alembic stamp head` vor Start

3. Testgrundlage
   - [ ] E2E‑Smoke Tests (Login, Projekte, Zeiten, Rechnung PDF)
   - [ ] Unit‑Tests Username‑Generator, Sanitizer, Suffix‑Kollision
   - [ ] Integration Tests für PDF/Branding Fallback

Rollback (Phase 0): Bei Problemen bleiben Flags aus; keine Schema‑Änderung produktiv.

## Phase 1 – Tenant‑Grundlagen

1. Migration 001: Tabellen `tenant`, `tenant_settings`
   - Spalten: siehe Plan oben
   - [ ] Indizes auf `tenant.id`, `tenant_settings.tenant_id`
   - Prüfung: Alembic upgrade/downgrade sauber

2. Migration 002: `tenant_id` in Kern‑Tabellen
   - [ ] Tabellen: `project`, `time_entry`, `offer`, `invoice`, `company_logo`, `report` …
   - [ ] Default‑Backfill auf `1` (Bestandsmandant)
   - Prüfung: SELECT‑Join‑Smoke Tests × 3 Tabellen
   - Risiko: Foreign Keys/Nulls → Maßnahme: NOT NULL erst nach Backfill

3. Service‑Layer Tenant‑Filter
   - [ ] Decorator/Helper `require_tenant_scope`
   - [ ] Alle Reads/Writes nur für `current_user.tenant_id`
   - Prüfung: Unit‑Test, dass Cross‑Tenant unzugänglich

Rollback (Phase 1): Alembic downgrade 002→001→base; Code‑Pfad via Feature‑Flag ausgeschaltet.

## Phase 2 – Mitarbeiter=Benutzer Migration

1. Migration 003: `users` erweitern
   - [ ] Felder: `tenant_id`, `position`, `hourly_rate`, `phone`, `address`, `invite_token`, `invite_expires_at`, `password_set_at`
   - Prüfung: Default‑Werte & Indizes

2. Datenmigration Employees → Users
   - [ ] Script: Name splitten, `username=nachname.vorname` (sanitize, unique per tenant)
   - [ ] E‑Mails generieren, wenn leer: `vorname.nachname+<id>@test.local`
   - [ ] Felder übertragen (`hourly_rate`, `position`, `phone`)
   - [ ] Mapping‑Tabelle `employee_id → user_id` protokollieren
   - Prüfungen: 
     - [ ] Anzahl Employees == Anzahl neu gemappter Users
     - [ ] Keine doppelten Usernames pro Tenant
   - Risiken: fehlende Namen → Maßnahme: Fallback `user<n>` + Reportliste

3. Referenzen umhängen
   - [ ] `time_entry.employee_id` → `user_id`
   - [ ] Weitere Tabellen prüfen (Reports/Offers/Invoices Autorfelder)
   - Prüfung: E2E Smoke (Zeiten laden/bearbeiten, Rechnung erzeugen)

4. API‑Kompatibilität
   - [ ] Alte `employees`‑Endpoints deprecaten (HTTP 410 mit Hinweis)
   - [ ] Frontend schrittweise auf `/users` umstellen
   - Risiko: gemischte Clients → Maßnahme: Übergangsweise 302‑Mapping auf `/users`

Rollback (Phase 2): Downgrade Migration, Restore Backups, alten Codepfad via Flag aktivieren.

## Phase 3 – Einladungen & Passwort‑Flows

1. Endpoints
   - [ ] `POST /auth/invite` (Admin): erstellt Nutzer (status „invited“), generiert Token (hash), TTL=7 Tage
   - [ ] `POST /auth/accept-invite`: setzt Passwort, aktiviert Account, setzt `password_set_at`
   - [ ] `POST /auth/resend-invite`, `DELETE /auth/invite/{id}`
   - [ ] `POST /users/{id}/reset-password` (Admin‑Reset ohne E‑Mail nötig)
   - Prüfungen: Token‑TTL, Einmalverwendung, 401/403‑Pfad

2. UI
   - [ ] Benutzer & Rollen: Einladungen erstellen, Status/Restlaufzeit anzeigen
   - [ ] Reset‑Button: nutzt feste User‑Zuordnung, kein Prompt notwendig

3. E‑Mail
   - [ ] Mail‑Provider anbinden; Templates mit Branding
   - Risiko: Zustellbarkeit → Maßnahme: Fallback Anzeige des Invite‑Links im Admin‑UI (einmalig)

Rollback (Phase 3): Einladungen deaktivieren, nur Direktanlage erlauben.

## Phase 4 – Billing & Sperrlogik

1. Stripe Integration
   - [ ] Produkte/Preise; Checkout Link
   - [ ] Webhooks: `payment_succeeded`, `payment_failed`, `subscription.updated`
   - [ ] `subscription_status` + `current_period_end` aktualisieren
   - Prüfung: Stripe CLI E2E

2. Gating & Reminder
   - [ ] Grace‑Period (7 Tage) → `suspended`
   - [ ] Reminder‑Jobs: 7 Tage vorher, Tag X, +3 Tage nachher
   - [ ] Reaktivierung via Portal‑Link
   - Risiken: Webhook‑Ausfälle → Maßnahme: Idempotente Handler + Retry

Rollback (Phase 4): Billing‑Schalter aus; „kostenloser Modus“ für Tests.

## Phase 5 – Tenant Settings & Branding

1. CRUD & Cache
   - [ ] `GET/PUT /tenant/settings` (auth: admin)
   - [ ] Validierung (IBAN/USt‑ID), Defaults
   - [ ] Cache mit ETag; Invalidierung bei Update

2. PDF/Preview
   - [ ] `beautiful_pdf_generator` liest Settings (Logo, Farben, Texte)
   - [ ] UI‑Preview mit Cache‑Busting (ts)
   - Prüfung: 3 Referenzlayouts, Fallback ohne Logo

Rollback (Phase 5): Fallback auf Standard‑Branding.

## Phase 6 – DSGVO Retention

1. Konfiguration
   - [ ] `tenant_settings.compliance.retention_days` je Kategorie
   - [ ] Anonymisierung/Löschung als Jobs (apscheduler)
   - [ ] Audit‑Logging aller Maßnahmen
   - Risiken: gesetzliche Aufbewahrung (Rechnungen) → niemals vorzeitig löschen

Rollback (Phase 6): Jobs deaktivieren; manuelle Prüfung.

## Phase 7 – RBAC (optional)

1. Tabellen & Services
   - [ ] `roles`, `permissions`, `role_permissions`, `user_roles` (per Tenant)
   - [ ] Decorator `@requires_permission` + Mapping der alten Rollen
   - Prüfung: E2E Rechte‑Matrix (Lesen/Schreiben/Verwalten)

Rollback (Phase 7): Fallback auf festes Rollenmodell.

---

## Cross‑Cutting Prüfungen & KPIs

- Smoke Tests nach jeder Phase (Login, Zeiten, Rechnung, Branding)
- Sicherheit: Linting, SAST (z. B. Bandit), Dependency Audit
- Performance: einfache Load‑Tests auf kritischen Endpoints
- Observability: strukturierte Logs mit `tenant_id`, Alerts bei 5xx‑Spikes

## Dokumentation & Kommunikation

- `README`/`plan.md` nach jeder Phase aktualisieren
- Migrations‑Guide (Hinweise zu Downtime/Flags)
- Admin‑Changelog im UI (was ändert sich?)

