# 🛡️ Haftung, Datenschutz & Dienstleister-Integration

**Erstellt am:** 3. Oktober 2025  
**Für:** Bau-Dokumentations-App (SaaS)  
**Status:** Handlungsempfehlungen

---

## 📋 Executive Summary

**Deine Hauptfragen:**
1. ✅ Macht Auslagerung an Hetzner Sinn? → **JA, aber mit klaren Verträgen**
2. ✅ Haftung? → **Erheblich, aber versicherbar**
3. ✅ Was auslagern? → **Hosting, Payment, Backups - aber NICHT ohne AVV**

**Kritisch:** Als SaaS-Anbieter für Baufirmen verarbeitest du:
- Personenbezogene Daten (Mitarbeiter, Kunden)
- Geschäftsdaten (Angebote, Rechnungen, Stundenzettel)
- Möglicherweise KRITIS-relevante Daten (je nach Kunden)

---

# TEIL 1: RECHTLICHE GRUNDLAGEN

## 1.1 Deine rechtliche Stellung

### Du bist VERANTWORTLICHER nach DSGVO Art. 4 Nr. 7

**Was das bedeutet:**
- Du entscheidest über Zweck und Mittel der Datenverarbeitung
- Du haftest für ALLE Verstöße (auch von Dienstleistern!)
- Du brauchst AVVs (Auftragsverarbeitungsverträge) mit JEDEM Dienstleister
- Bußgelder bis 20 Mio. € oder 4% des Jahresumsatzes (weltweit!)

### Pflichten als Verantwortlicher

#### 1. Rechenschaftspflicht (Art. 5 Abs. 2 DSGVO)
```
✅ Musst nachweisen können:
   - Welche Daten du verarbeitest
   - Warum du sie verarbeitest
   - Wo sie liegen
   - Wer Zugriff hat
   - Wie lange du sie speicherst
```

#### 2. Verzeichnis von Verarbeitungstätigkeiten (Art. 30 DSGVO)
```
Pflicht ab:
- 250+ Mitarbeiter ODER
- Regelmäßige Verarbeitung personenbezogener Daten

→ Betrifft dich ab dem ersten Kunden!
```

#### 3. Datenschutz-Folgenabschätzung (Art. 35 DSGVO)
```
Notwendig bei:
- Systematischer Überwachung
- Verarbeitung besonderer Kategorien
- Profiling mit rechtlicher Wirkung

→ Für deine App wahrscheinlich NICHT nötig
   (aber sicherheitshalber prüfen lassen!)
```

#### 4. Meldepflichten (Art. 33-34 DSGVO)
```
Bei Datenpanne:
- Binnen 72h an Aufsichtsbehörde melden
- Betroffene direkt informieren (wenn hohes Risiko)
- Dokumentation führen

Strafe bei Nichtmeldung: Bis zu 10 Mio. € oder 2% Jahresumsatz!
```

---

## 1.2 Haftungsrisiken

### Zivilrechtliche Haftung

#### Schadensersatz (Art. 82 DSGVO)
```
Betroffene können klagen wegen:
- Materiellem Schaden (z.B. Identitätsdiebstahl)
- Immateriellem Schaden (z.B. Ärger, Zeitaufwand)

Beispiel-Urteile:
- 5.000 € für Datenpanne (LG München)
- 15.000 € für systematische Verstöße (LG Berlin)
- 100.000+ € bei schwerem Verstoß
```

#### Vertragliche Haftung
```
Gegenüber Kunden:
- SLA-Verletzung (Service Level Agreement)
- Datenverlust
- Ausfall der Anwendung

Beispiel:
Kunde kann keine Rechnungen schreiben → Umsatzausfall → Schadensersatz!
```

#### Geschäftliche Risiken
```
Reputationsschaden:
- Negative Presse
- Kundenabwanderung
- Vertrauensverlust

Realität:
80% der KMU überleben eine schwere Datenpanne nicht!
```

### Strafrechtliche Haftung

#### Straftatbestände (StGB)
```
§ 202a StGB - Ausspähen von Daten: Bis 3 Jahre Haft
§ 303a StGB - Datenveränderung: Bis 2 Jahre
§ 303b StGB - Computersabotage: Bis 5 Jahre

→ Betrifft dich, wenn du fahrlässig handelst!
```

### Ordnungswidrigkeiten (DSGVO)

#### Bußgeldkatalog
```
BIS ZU 10 MIO. € / 2% JAHRESUMSATZ:
- Fehlende/fehlerhafte AVV
- Keine TOMs (Technisch-Organisatorische Maßnahmen)
- Fehlende Dokumentation

BIS ZU 20 MIO. € / 4% JAHRESUMSATZ:
- Verarbeitung ohne Rechtsgrundlage
- Verstoß gegen Betroffenenrechte
- Übermittlung in Drittland ohne Garantien
```

---

# TEIL 2: DIENSTLEISTER-AUSWAHL

## 2.1 Hosting: Hetzner vs. Alternativen

### ✅ EMPFEHLUNG: Hetzner Online GmbH

#### Vorteile
```
✅ Deutsches Unternehmen (Gunzenhausen, Bayern)
✅ Rechenzentren in Deutschland & Finnland (EU)
✅ DSGVO-konform, zertifiziert nach ISO 27001
✅ Günstig: Cloud-Server ab 4,15 €/Monat
✅ Guter Support (auch auf Deutsch)
✅ Standardisierte AVV verfügbar
✅ Backup-Service inklusive
✅ Keine US-Mutterfirma (kein Cloud Act!)
```

#### Nachteile
```
❌ Kein Managed Service (du musst selbst konfigurieren)
❌ Keine automatischen Security-Updates
❌ DDoS-Schutz nur gegen Aufpreis
```

#### Konkrete Empfehlung
```
Produkt: Hetzner Cloud
Server: CPX21 (3 vCPU, 4 GB RAM, 80 GB SSD)
Preis: ~8 €/Monat
Standort: Falkenstein (Deutschland) oder Helsinki (Finnland)

+ Backup-Space: 10 GB (gratis)
+ Volumes für Datenbank: 50 GB (~6 €/Monat)

Gesamtkosten: ~15 €/Monat für 100-500 Nutzer
```

### Alternative: Contabo

#### Vorteile
```
✅ Noch günstiger als Hetzner (ab 4,99 €/Monat)
✅ Deutsche Firma (München)
✅ EU-Rechenzentren
✅ AVV verfügbar
```

#### Nachteile
```
❌ Schlechterer Support
❌ Shared-CPU (Performance-Probleme möglich)
❌ Weniger moderne API
```

### Alternative: netcup

#### Vorteile
```
✅ Deutscher Hoster (Nürnberg)
✅ Günstig
✅ Guter Support
✅ Ökostrom
```

#### Nachteile
```
❌ Kleinerer Anbieter (Risiko?)
❌ Weniger skalierbar
```

### ❌ NICHT EMPFOHLEN: US-Cloud-Anbieter

```
AWS, Google Cloud, Microsoft Azure:

❌ US-amerikanische Firmen → Cloud Act
❌ Schrems-II-Urteil: Unsichere Drittlandübermittlung
❌ Zusätzliche Schutzmaßnahmen nötig (teuer, kompliziert)
❌ Teure Standardvertragsklauseln-Prüfung
❌ Compliance-Risiko für deine Kunden

AUSNAHME:
- AWS/Azure EU-Rechenzentren MIT zusätzlichen Garantien
- Nur, wenn Budget für Rechtsberatung vorhanden
```

---

## 2.2 Payment: Stripe vs. Alternativen

### ✅ EMPFEHLUNG: Stripe

#### Warum Stripe?
```
✅ Integrierst du bereits
✅ PCI-DSS Level 1 zertifiziert
✅ Kreditkartendaten bleiben bei Stripe (du bist raus aus der Haftung!)
✅ SCA-compliant (Strong Customer Authentication)
✅ Webhooks für Automation
✅ Gute Dokumentation
✅ Dispute-Management inklusive
```

#### Rechtliche Sicherheit
```
✅ Stripe ist AUFTRAGSVERARBEITER
✅ Daten werden in EU verarbeitet (Stripe Payments Europe)
✅ AVV ist in AGB integriert
✅ DSGVO-konform (mit kleinen Einschränkungen)

⚠️ ABER: Stripe Inc. ist US-Firma
→ Zusätzliche Garantien nötig (Standard Contractual Clauses)
→ Stripe bietet diese automatisch an
```

#### Kosten
```
1,4% + 0,25 € pro EU-Transaktion
2,9% + 0,25 € für UK/USA

Beispiel:
49 € Abo → 0,94 € Gebühren (1,9%)

Bei 100 Kunden: ~94 €/Monat Gebühren
```

#### Was du TUN musst
```
1. Stripe-AVV akzeptieren (im Dashboard)
2. In Datenschutzerklärung erwähnen:
   "Zahlungen werden über Stripe verarbeitet.
    Stripe speichert Kreditkartendaten nach PCI-DSS."
3. Kunden darüber informieren (Checkbox bei Registrierung)
```

### Alternative: Mollie

#### Vorteile
```
✅ Niederländisches Unternehmen (EU!)
✅ Günstiger als Stripe (1,0% + 0,25 €)
✅ SEPA-Lastschrift einfacher
✅ Sofortüberweisung, Klarna, PayPal integriert
✅ Guter Support auf Deutsch
```

#### Nachteile
```
❌ Weniger API-Features
❌ Stripe hat bessere Webhooks
❌ Kleinerer Anbieter (weniger stabil?)
```

### Alternative: PayPal

#### Vorteile
```
✅ Bekannt, vertrauenswürdig
✅ Viele Nutzer haben Account
✅ Käuferschutz
```

#### Nachteile
```
❌ US-Firma (Schrems-II-Problem)
❌ Hohe Gebühren (2,49% + 0,35 €)
❌ Willkürliche Kontosperrungen
❌ Schlechter B2B-Support
❌ Keine echten Subscriptions (nur Recurring)
```

### ⚠️ RECHTLICHER HINWEIS: PCI-DSS

```
NIEMALS selbst Kreditkartendaten speichern!

Wenn du Kreditkartendaten speicherst:
→ PCI-DSS Zertifizierung nötig (10.000-50.000 €/Jahr)
→ Jährliche Audits
→ Haftung bei Datenleck

Lösung: Stripe/Mollie übernehmen das für dich!
```

---

## 2.3 E-Mail-Versand

### ✅ EMPFEHLUNG: Postmark

#### Vorteile
```
✅ Fokus auf transaktionale E-Mails (Einladungen, Benachrichtigungen)
✅ 99,99% Zustellrate
✅ DSGVO-konform, EU-Server
✅ Einfache API
✅ Günstiger als SendGrid/Mailgun
```

#### Kosten
```
1,25 € pro 1.000 E-Mails
→ Bei 100 Kunden × 10 E-Mails/Monat = ~1,25 €/Monat
```

#### Rechtliches
```
✅ Postmark ist Auftragsverarbeiter
✅ AVV verfügbar
✅ Server in EU wählbar
```

### Alternative: AWS SES (EU Region)

#### Vorteile
```
✅ Sehr günstig (0,10 € / 1.000 E-Mails)
✅ EU-Region wählbar (Frankfurt)
```

#### Nachteile
```
❌ AWS = US-Firma (Schrems-II)
❌ Komplexe Konfiguration
❌ Schlechtere Zustellrate als Postmark
```

---

## 2.4 Backup & Disaster Recovery

### ⚠️ KRITISCH: Backups sind PFLICHT!

#### Rechtliche Anforderung
```
DSGVO Art. 32 (1) b:
"Fähigkeit, Vertraulichkeit, Integrität, Verfügbarkeit und
 Belastbarkeit der Systeme SICHERZUSTELLEN"

→ Ohne Backup = Verstoß gegen DSGVO!
```

### ✅ EMPFEHLUNG: 3-2-1-Backup-Strategie

```
3 Kopien der Daten
2 verschiedene Medien/Standorte
1 Kopie offline/extern

Konkret:
1. Produktiv-Datenbank (Hetzner Cloud)
2. Tägliches Backup (Hetzner Backup-Space) → automatisch
3. Wöchentliches Backup (externes Ziel: Borgbase oder Backblaze B2)
```

#### Umsetzung

**Backup 1: Hetzner Snapshots (automatisch)**
```bash
# In Hetzner Cloud aktivieren:
- Snapshot-Interval: täglich
- Retention: 7 Tage
- Kosten: Inklusive

→ Schützt vor: Fehler in App, versehentliches Löschen
→ Schützt NICHT vor: Hetzner-Ausfall, Ransomware mit Root-Zugriff
```

**Backup 2: Borgbase (verschlüsselt, extern)**
```bash
# Borg Backup nach Borgbase
→ Verschlüsselt, dedupliziert
→ EU-Rechenzentren (Dublin)
→ Kosten: 2 €/Monat für 100 GB

Vorteile:
✅ Schutz vor Ransomware (Borg = append-only)
✅ Anderer Anbieter (falls Hetzner ausfällt)
✅ Point-in-Time-Recovery
```

**Backup 3: Backblaze B2 (Cloud-Storage)**
```bash
# Für langfristige Archivierung
→ 0,005 €/GB/Monat
→ 100 GB = 0,50 €/Monat

Vorteile:
✅ Sehr günstig
✅ Unveränderliche Backups (Versioning)
✅ US-Firma, aber EU-Rechenzentren verfügbar
```

#### Backup-Plan Zusammenfassung

| Backup | Ziel | Häufigkeit | Retention | Kosten/Monat |
|--------|------|------------|-----------|--------------|
| Snapshot | Hetzner | Täglich | 7 Tage | Inkl. |
| Borg | Borgbase | Täglich | 30 Tage | 2 € |
| Archive | Backblaze B2 | Wöchentlich | 1 Jahr | 0,50 € |
| **GESAMT** | | | | **2,50 €** |

---

## 2.5 Monitoring & Logging

### ✅ EMPFEHLUNG: Sentry (Fehler-Tracking)

#### Vorteile
```
✅ Open Source (selbst hosten möglich!)
✅ EU-Cloud verfügbar
✅ DSGVO-konform
✅ Automatisches Error-Reporting
```

#### Kosten
```
Gratis-Tier: 5.000 Events/Monat
Team-Tier: 26 €/Monat (50.000 Events)

→ Für deinen Use-Case: Gratis ausreichend
```

#### Rechtliches
```
⚠️ ACHTUNG: Sentry sieht Stack-Traces!
→ Keine personenbezogenen Daten in Logs!
→ IP-Adressen maskieren
→ AVV mit Sentry abschließen
```

### Alternative: Self-Hosted (Empfohlen!)

```
Option 1: Sentry Self-Hosted (Docker)
→ Auf eigenem Hetzner-Server
→ Keine Daten an Dritte
→ Volle Kontrolle

Option 2: Grafana + Prometheus (Open Source)
→ Metrics & Logs auf eigenem Server
→ Kostenlos, DSGVO-konform

EMPFEHLUNG:
Für Produktivstart: Sentry EU-Cloud mit AVV
Später: Umzug auf Self-Hosted (ab 500+ Nutzer)
```

---

# TEIL 3: VERTRÄGE & DOKUMENTATION

## 3.1 Auftragsverarbeitungsvertrag (AVV)

### Was ist ein AVV?

```
Vertrag zwischen:
- DIR (Verantwortlicher)
- DIENSTLEISTER (Auftragsverarbeiter)

Regelt:
- Was der Dienstleister darf
- Wie er Daten schützen muss
- Wer haftet bei Verstößen

PFLICHT nach Art. 28 DSGVO!
Strafe bei fehlendem AVV: Bis zu 10 Mio. € Bußgeld
```

### Welche Dienstleister brauchen AVV?

```
✅ JA (AVV PFLICHT):
- Hetzner (Hosting)
- Stripe (Payment)
- Postmark (E-Mail)
- Sentry (Monitoring)
- Borgbase (Backup)

❌ NEIN (kein AVV):
- Domainregistrar (DENIC, Namecheap)
- SSL-Zertifikat (Let's Encrypt)
- GitHub (nur Code, keine Produktivdaten)
```

### Checkliste: Guter AVV muss enthalten

```
✅ Gegenstand und Dauer der Verarbeitung
✅ Art und Zweck der Verarbeitung
✅ Kategorien betroffener Personen
✅ Kategorien personenbezogener Daten
✅ Pflichten und Rechte des Verantwortlichen
✅ Technisch-organisatorische Maßnahmen (TOMs)
✅ Unterauftragsverarbeiter (wenn vorhanden)
✅ Unterstützung bei Betroffenenanfragen
✅ Löschung/Rückgabe nach Vertragsende
✅ Audit-Rechte
✅ Haftung und Schadensersatz
```

### Wo bekommst du AVVs?

#### Hetzner
```
Online verfügbar:
https://www.hetzner.com/rechtliches/avv

→ Formular ausfüllen, unterschreiben, per Post/E-Mail senden
→ Dauer: ~1 Woche
→ Kosten: Kostenlos
```

#### Stripe
```
Automatisch akzeptiert:
https://stripe.com/de/privacy/dpa

→ Im Stripe-Dashboard unter "Settings → Data Processing Agreement"
→ Click "Accept"
→ Fertig!
```

#### Postmark
```
Online verfügbar:
https://postmarkapp.com/terms/dpa

→ E-Mail an support@postmarkapp.com mit:
   "We need a signed DPA for GDPR compliance"
→ Dauer: ~2-3 Tage
```

---

## 3.2 Technisch-Organisatorische Maßnahmen (TOMs)

### Was sind TOMs?

```
Dokumentation deiner Sicherheitsmaßnahmen nach Art. 32 DSGVO

Kategorien:
1. Zutrittskontrolle (physisch)
2. Zugangskontrolle (System-Ebene)
3. Zugriffskontrolle (Daten-Ebene)
4. Weitergabekontrolle
5. Eingabekontrolle
6. Auftragskontrolle
7. Verfügbarkeitskontrolle
8. Trennungskontrolle (Mandantentrennung)
```

### Beispiel-TOMs für deine App

#### 1. Zutrittskontrolle
```
PHYSISCHER ZUGANG ZU SERVERN:

Rechenzentrum Hetzner:
✅ Gesicherte Rechenzentren (ISO 27001)
✅ Videoüberwachung
✅ Zutrittskontrolle mit Badges
✅ 24/7-Sicherheitspersonal

→ Dokumentiere: "Server gehostet bei Hetzner Online GmbH,
   Rechenzentrum Falkenstein, gesichert nach ISO 27001"
```

#### 2. Zugangskontrolle
```
WER KANN SICH EINLOGGEN?

✅ Passwort-Hashing mit Argon2 (ab Phase 1.1!)
✅ Mindestlänge 8 Zeichen
✅ JWT-Tokens mit 30min Ablaufzeit
✅ 2FA für Admins (TODO: implementieren)
✅ SSH nur mit Key, kein Root-Login

→ Dokumentiere alle Maßnahmen!
```

#### 3. Zugriffskontrolle
```
WER DARF WAS SEHEN?

✅ Rollenbasierte Zugriffskontrolle (RBAC)
   - Admin: alles
   - Buchhalter: Finanzen
   - Mitarbeiter: nur eigene Daten

✅ Tenant-Isolation (ab Phase 1.2!)
   - Kunde A sieht nur seine Daten
   - Kunde B sieht nur seine Daten

✅ SQL Injection Prevention (Whitelist-Validierung)

→ Dokumentiere: "Tenant-Isolation auf Datenbankebene,
   geprüft durch Unit-Tests"
```

#### 4. Weitergabekontrolle
```
WIE WERDEN DATEN ÜBERTRAGEN?

✅ HTTPS/TLS 1.3 für alle Verbindungen
✅ HSTS-Header (HTTP Strict Transport Security)
✅ CSP-Header (Content Security Policy)
✅ Sichere Cookies (Secure, HttpOnly, SameSite)

✅ Backups verschlüsselt (Borg mit GPG-Key)
✅ Datenbank-Backups verschlüsselt

→ Dokumentiere: "Alle Übertragungen verschlüsselt mit TLS 1.3,
   Zertifikat von Let's Encrypt"
```

#### 5. Eingabekontrolle
```
WER HAT DATEN GEÄNDERT?

✅ Audit-Logs für kritische Aktionen
   - Login-Versuche
   - Passwort-Änderungen
   - Daten-Löschungen

✅ Timestamps (created_at, updated_at) in allen Tabellen
✅ edited_by-Felder bei TimeEntries

TODO (ab Phase 1.3):
   ✅ Strukturiertes Logging mit User-ID
   ✅ Log-Rotation (10 Tage Aufbewahrung)
```

#### 6. Auftragskontrolle
```
WIE KONTROLLIERST DU DIENSTLEISTER?

✅ AVVs mit allen Dienstleistern
✅ Liste aller Unterauftragsverarbeiter
✅ Jährliche Überprüfung der Zertifikate
✅ Vertragsstrafen bei Verstößen

→ Dokumentiere: "Alle Dienstleister vertraglich gebunden,
   AVVs liegen vor, Liste siehe Anlage A"
```

#### 7. Verfügbarkeitskontrolle
```
WIE VERHINDERST DU AUSFÄLLE?

✅ 3-2-1-Backup-Strategie (siehe oben)
✅ Automatische Backups (täglich)
✅ Disaster-Recovery-Plan
✅ RTO (Recovery Time Objective): 4 Stunden
✅ RPO (Recovery Point Objective): 24 Stunden

✅ Monitoring (Sentry, Uptime-Checks)
✅ Alarmierung bei Ausfall (E-Mail, SMS)

→ Dokumentiere: "Wiederherstellung binnen 4h garantiert,
   Datenverlust max. 24h"
```

#### 8. Trennungskontrolle (Mandantentrennung)
```
WIE TRENNST DU KUNDENDATEN?

✅ Tenant-Isolation auf Datenbankebene
✅ tenant_id in allen Tabellen
✅ Queries immer gefiltert (tenant_scope.py ab Phase 1.2)
✅ Unit-Tests für Cross-Tenant-Zugriff

✅ Logische Trennung (keine physische DB pro Kunde)
   → Akzeptabel für <1.000 Kunden
   → Ab 1.000 Kunden: DB-Sharding erwägen

→ Dokumentiere: "Mandantentrennung durch tenant_id,
   validiert durch automatisierte Tests"
```

---

## 3.3 Datenschutzerklärung

### Pflicht-Inhalte nach Art. 13 DSGVO

```
1. Name und Kontaktdaten des Verantwortlichen
2. Kontaktdaten des Datenschutzbeauftragten (falls vorhanden)
3. Zwecke der Verarbeitung
4. Rechtsgrundlage (z.B. Art. 6 Abs. 1 lit. b - Vertrag)
5. Empfänger der Daten (Dienstleister!)
6. Übermittlung in Drittland (falls zutreffend)
7. Speicherdauer
8. Betroffenenrechte (Auskunft, Löschung, etc.)
9. Beschwerderecht bei Aufsichtsbehörde
10. Quelle der Daten (falls nicht vom Betroffenen)
```

### Konkret für deine App

```markdown
# Datenschutzerklärung

## 1. Verantwortlicher
[Dein Name/Firma]
[Adresse]
E-Mail: datenschutz@deine-app.de

## 2. Welche Daten verarbeiten wir?

### Beim Anlegen eines Accounts (Rechtsgrundlage: Art. 6 Abs. 1 lit. b DSGVO - Vertrag)
- E-Mail-Adresse
- Name
- Passwort (verschlüsselt mit Argon2)
- Firmenname
- Rechnungsadresse (optional)

### Bei Nutzung der App (Rechtsgrundlage: Art. 6 Abs. 1 lit. b DSGVO - Vertrag)
- Projekt-Daten (Kundennamen, Adressen, Angebote, Rechnungen)
- Mitarbeiter-Daten (Namen, Stundensätze, Arbeitszeiten)
- Fotos von Baustellen (optional)

### Server-Logs (Rechtsgrundlage: Art. 6 Abs. 1 lit. f DSGVO - berechtigtes Interesse)
- IP-Adresse (anonymisiert nach 7 Tagen)
- Browser-Typ
- Zugriffszeitpunkt
- Fehlermeldungen

## 3. An wen geben wir Daten weiter?

### Hosting
**Hetzner Online GmbH**
Industriestr. 25, 91710 Gunzenhausen
Zweck: Server-Betrieb
AVV: vorhanden
Standort: Deutschland (EU)

### Zahlungsabwicklung
**Stripe Payments Europe Ltd.**
1 Grand Canal Street Lower, Dublin 2, Irland
Zweck: Kreditkarten-Zahlungen
AVV: vorhanden (in Stripe-AGB integriert)
Standort: Irland (EU)
Hinweis: Kreditkartendaten werden ausschließlich bei Stripe gespeichert,
wir haben keinen Zugriff darauf.

### E-Mail-Versand
**Postmark (Wildbit LLC)**
225 Chestnut St, Philadelphia, PA 19106, USA
Zweck: Versand von Einladungen, Benachrichtigungen
AVV: vorhanden
Standort: EU-Server (Dublin)
Garantien: Standard Contractual Clauses (SCC)

### Backup
**BorgBase (Unaffiliated Ltd.)**
16 Great Chapel Street, London W1F 8FL, UK
Zweck: Verschlüsselte Backups
AVV: vorhanden
Standort: Irland (EU)

## 4. Wie lange speichern wir Daten?

| Datenart | Speicherdauer |
|----------|---------------|
| Account-Daten | Bis zur Löschung des Accounts |
| Projekt-Daten | Bis zur Löschung durch Nutzer |
| Server-Logs | 7 Tage (dann anonymisiert) |
| Backups | 30 Tage (rollierend) |
| Rechnungsdaten | 10 Jahre (gesetzl. Aufbewahrungspflicht) |

## 5. Deine Rechte

- **Auskunft** (Art. 15 DSGVO): Du kannst jederzeit Auskunft über deine Daten verlangen
- **Berichtigung** (Art. 16): Du kannst falsche Daten korrigieren lassen
- **Löschung** (Art. 17): Du kannst deine Daten löschen lassen
- **Einschränkung** (Art. 18): Du kannst die Verarbeitung einschränken
- **Datenportabilität** (Art. 20): Du kannst deine Daten exportieren
- **Widerspruch** (Art. 21): Du kannst der Verarbeitung widersprechen

Kontakt: datenschutz@deine-app.de

## 6. Beschwerderecht

Du hast das Recht, dich bei einer Datenschutz-Aufsichtsbehörde zu beschweren:

**Bayerisches Landesamt für Datenschutzaufsicht** (BayLDA)
Promenade 18, 91522 Ansbach
Telefon: 0981 180093-0
E-Mail: poststelle@lda.bayern.de

## 7. Änderungen dieser Datenschutzerklärung

Stand: [Datum]
Wir behalten uns vor, diese Datenschutzerklärung anzupassen.
Aktuelle Version: https://deine-app.de/datenschutz
```

---

## 3.4 AGB (Allgemeine Geschäftsbedingungen)

### Pflicht-Inhalte

```
1. Vertragspartner (du!)
2. Leistungsbeschreibung
3. Preise und Zahlungsbedingungen
4. Laufzeit und Kündigung
5. Haftung
6. Gewährleistung
7. Verfügbarkeit (SLA)
8. Datenschutz-Verweis
9. Gerichtsstand
10. Salvatorische Klausel
```

### Kritische Punkte

#### Haftungsbeschränkung
```
Du kannst Haftung NUR beschränken bei:
- Leichter Fahrlässigkeit
- Nicht-wesentlichen Vertragspflichten

Du kannst Haftung NICHT beschränken bei:
- Vorsatz
- Grober Fahrlässigkeit
- Körperschaden
- Garantiepflichten
- Produkthaftung

Beispiel-Formulierung:
"Bei leichter Fahrlässigkeit haften wir nur für die Verletzung
 wesentlicher Vertragspflichten (Kardinalspflichten). Die Haftung
 ist auf den vertragstypischen, vorhersehbaren Schaden begrenzt."
```

#### Service Level Agreement (SLA)
```
REALISTISCH für deine App:

Verfügbarkeit: 99,0% (~ 7 Stunden Ausfall/Monat)
Support-Reaktion: 24 Stunden (werktags)
Bug-Fixes: 7 Tage (kritische Bugs: 48h)

NICHT versprechen:
❌ 99,99% (nur mit 24/7-Team möglich)
❌ Echtzeit-Support (unbezahlbar)
❌ Garantierte Datenrettung (nur Best-Effort)
```

---

# TEIL 4: VERSICHERUNGEN

## 4.1 Cyber-Versicherung

### ✅ DRINGEND EMPFOHLEN!

#### Was deckt eine Cyber-Versicherung?

```
✅ Eigenschäden:
- Kosten für Datenwiederherstellung
- Betriebsunterbrechung
- Forensik & Incident Response
- Rechtsberatung
- Krisenmanagement

✅ Fremdschäden:
- Schadensersatz an Kunden
- Rechtsverteidigung
- Vertragsstrafen
- DSGVO-Bußgelder (teilweise!)

❌ NICHT gedeckt:
- Vorsätzliche Verstöße
- Bekannte Sicherheitslücken
- Erpressungszahlungen (meist optional)
```

#### Anbieter & Kosten

```
ANBIETER (Deutschland):
- Hiscox
- Allianz
- AXA
- ERGO
- CyberDirekt (Makler)

KOSTEN:
Deckungssumme 100.000 €: ~500-800 €/Jahr
Deckungssumme 500.000 €: ~1.500-2.500 €/Jahr
Deckungssumme 1 Mio. €: ~3.000-5.000 €/Jahr

EMPFEHLUNG für Start:
→ 250.000 € Deckung
→ ~1.000 €/Jahr
→ Inkl. Rechtsschutz & Betriebsunterbrechung
```

#### Was prüfen Versicherer?

```
Vor Vertragsabschluss:
✅ Haben Sie Firewalls?
✅ Backup-Strategie?
✅ Verschlüsselung?
✅ Mitarbeiter-Schulungen?
✅ Incident-Response-Plan?
✅ AVVs mit Dienstleistern?

→ Bereite Dokumentation vor!
→ Je besser deine Sicherheit, desto günstiger der Tarif
```

---

## 4.2 Betriebs-Haftpflicht

### ✅ PFLICHT!

#### Was deckt sie?

```
✅ Sach- und Personenschäden durch dein Unternehmen
✅ Vermögensschäden (wichtig für Software!)
✅ Rechtsschutz bei ungerechtfertigten Ansprüchen

Beispiel:
- Kunde verliert Daten durch Bug → Umsatzausfall → Haftpflicht zahlt
```

#### Kosten

```
Deckungssumme 3 Mio. €: ~300-500 €/Jahr (Basis)
Deckungssumme 5 Mio. €: ~600-1.000 €/Jahr

WICHTIG: "Vermögensschäden" explizit einschließen!
(Sonst nur Sach-/Personenschäden versichert)
```

---

## 4.3 Rechtsschutzversicherung

### Optional, aber sinnvoll

```
Gewerbliche Rechtsschutzversicherung: ~800-1.200 €/Jahr

Deckt:
✅ Anwaltskosten bei Rechtsstreitigkeiten
✅ Gerichtskosten
✅ Gutachterkosten

Beispiel:
- Kunde klagt wegen Datenpanne
- Rechtsschutz übernimmt Anwaltskosten (sonst 10.000+ €)
```

---

# TEIL 5: IMPLEMENTIERUNGS-PLAN

## 5.1 Prioritäten

### SOFORT (Woche 1-2)

```
1. ✅ Hetzner-Server bestellen
   → Kosten: 15 €/Monat
   → Standort: Falkenstein (DE)

2. ✅ Hetzner-AVV abschließen
   → Online-Formular: https://www.hetzner.com/rechtliches/avv
   → Dauer: ~1 Woche

3. ✅ Stripe-AVV akzeptieren
   → Im Dashboard: Settings → Data Processing Agreement
   → Sofort verfügbar

4. ✅ Backup einrichten (Hetzner Snapshots)
   → Im Dashboard aktivieren
   → Kostenlos

5. ✅ SSL/TLS konfigurieren (Let's Encrypt)
   → Automatisch via Certbot
   → Kostenlos
```

### PHASE 1 (Woche 3-4)

```
6. ✅ Postmark registrieren & AVV
   → E-Mail an support@postmarkapp.com
   → Dauer: 2-3 Tage

7. ✅ Borgbase Backup einrichten
   → Account erstellen
   → Borg-Backup konfigurieren
   → Kosten: 2 €/Monat

8. ✅ Datenschutzerklärung schreiben
   → Vorlage anpassen (siehe oben)
   → Rechtsanwalt prüfen lassen (optional, aber empfohlen)
   → Kosten: 200-500 € (einmalig)

9. ✅ AGB schreiben
   → Vorlage anpassen
   → Rechtsanwalt prüfen lassen (PFLICHT!)
   → Kosten: 500-1.000 € (einmalig)
```

### PHASE 2 (Woche 5-6)

```
10. ✅ TOMs dokumentieren
    → Vorlage ausfüllen (siehe oben)
    → In Cloud ablegen (z.B. Notion, Confluence)

11. ✅ Verzeichnis von Verarbeitungstätigkeiten erstellen
    → Vorlage: https://www.lda.bayern.de/media/muster_vvt.pdf
    → Ausfüllen & aktuell halten

12. ✅ Cyber-Versicherung abschließen
    → Angebot einholen (z.B. CyberDirekt)
    → Kosten: ~1.000 €/Jahr
```

### PHASE 3 (Woche 7-8)

```
13. ✅ Incident-Response-Plan erstellen
    → Was tun bei Datenpanne?
    → Verantwortliche benennen
    → Meldekette definieren

14. ✅ Disaster-Recovery testen
    → Backup wiederherstellen (Testlauf!)
    → RTO/RPO validieren
    → Dokumentation aktualisieren

15. ✅ Mitarbeiter schulen (falls vorhanden)
    → DSGVO-Basics
    → Umgang mit Kundendaten
    → Phishing-Awareness
```

---

## 5.2 Technische Umsetzung

### Hetzner-Server Setup

```bash
# 1. Server bestellen
# Produkt: CPX21 (4 GB RAM, 80 GB SSD)
# Standort: Falkenstein (DE)

# 2. SSH-Key hinterlegen (KEIN Passwort-Login!)
ssh-keygen -t ed25519 -C "admin@deine-app.de"
# Public Key in Hetzner-Dashboard einfügen

# 3. Server erstellen & verbinden
ssh root@<server-ip>

# 4. Firewall konfigurieren
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw enable

# 5. Automatische Updates aktivieren
apt install unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades

# 6. Fail2Ban installieren (Schutz vor Brute-Force)
apt install fail2ban
systemctl enable fail2ban
systemctl start fail2ban

# 7. Docker installieren (für deine App)
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 8. PostgreSQL (Managed Service oder Docker)
# EMPFEHLUNG: Hetzner Managed PostgreSQL (ab 15 €/Monat)
# → Automatische Backups, Updates, Monitoring

# 9. SSL/TLS mit Let's Encrypt
apt install certbot python3-certbot-nginx
certbot --nginx -d deine-app.de -d www.deine-app.de

# 10. Nginx konfigurieren
# → Reverse Proxy zu deiner FastAPI-App
# → Security-Headers (HSTS, CSP, etc.)
```

### Backup-Automation

```bash
# Borg Backup einrichten

# 1. Borg installieren
apt install borgbackup

# 2. Borgbase-Account erstellen
# https://www.borgbase.com
# → Neues Repo anlegen: "bauapp-backup"
# → SSH-Key hinterlegen

# 3. Borg initialisieren
export BORG_REPO='ssh://xxx@xxx.repo.borgbase.com/./repo'
export BORG_PASSPHRASE='<starkes-passwort>'
borg init --encryption=repokey

# 4. Backup-Skript erstellen
cat > /usr/local/bin/backup.sh << 'EOF'
#!/bin/bash
export BORG_REPO='ssh://xxx@xxx.repo.borgbase.com/./repo'
export BORG_PASSPHRASE='<starkes-passwort>'

# Datenbank dumpen
pg_dump bauapp > /tmp/backup.sql

# Borg Backup
borg create \
  --stats --progress \
  ::'{hostname}-{now}' \
  /var/lib/docker/volumes \
  /tmp/backup.sql

# Alte Backups löschen (>30 Tage)
borg prune \
  --keep-daily=30 \
  --keep-weekly=4 \
  --keep-monthly=6

# Aufräumen
rm /tmp/backup.sql
EOF

chmod +x /usr/local/bin/backup.sh

# 5. Cronjob einrichten (täglich 3 Uhr)
crontab -e
# Einfügen:
0 3 * * * /usr/local/bin/backup.sh >> /var/log/backup.log 2>&1
```

---

## 5.3 Checkliste vor Produktivstart

```
RECHTLICH:
☐ Impressum vorhanden (§5 TMG)
☐ Datenschutzerklärung vorhanden (Art. 13 DSGVO)
☐ AGB vorhanden & rechtssicher
☐ AVVs mit allen Dienstleistern abgeschlossen
☐ TOMs dokumentiert
☐ Verzeichnis von Verarbeitungstätigkeiten erstellt

TECHNISCH:
☐ HTTPS/TLS aktiviert (A+ Rating bei SSL Labs)
☐ Security-Headers gesetzt (CSP, HSTS, X-Frame-Options)
☐ Passwort-Hashing mit Argon2 (ab Phase 1.1)
☐ Tenant-Isolation implementiert (ab Phase 1.2)
☐ SQL-Injection-Schutz (Whitelist-Validierung)
☐ Backups automatisiert & getestet (RTO/RPO validiert)
☐ Monitoring aktiv (Uptime-Checks, Error-Tracking)
☐ Firewall konfiguriert
☐ Fail2Ban aktiv
☐ Automatische Updates aktiviert

VERSICHERUNGEN:
☐ Cyber-Versicherung abgeschlossen (mind. 250k € Deckung)
☐ Betriebs-Haftpflicht abgeschlossen (mind. 3 Mio. € Deckung)
☐ Optional: Rechtsschutzversicherung

PROZESSE:
☐ Incident-Response-Plan erstellt
☐ Disaster-Recovery getestet
☐ Verantwortlichkeiten definiert (wer ist bei Panne zuständig?)
☐ Notfallkontakte hinterlegt (24/7 erreichbar?)
```

---

# TEIL 6: KOSTEN-ÜBERSICHT

## Monatliche Kosten (Produktivbetrieb)

| Position | Anbieter | Kosten/Monat | Notizen |
|----------|----------|--------------|---------|
| **Hosting** | Hetzner Cloud (CPX21) | 8 € | 4 GB RAM, 80 GB SSD |
| **Storage** | Hetzner Volume (50 GB) | 6 € | Für Datenbank |
| **Backup** | Hetzner Snapshots | Inkl. | Täglich, 7 Tage |
| **Backup** | Borgbase (100 GB) | 2 € | Verschlüsselt, extern |
| **Backup** | Backblaze B2 (100 GB) | 0,50 € | Langzeitarchiv |
| **Payment** | Stripe | ~94 € | Bei 100 Kunden × 49 € |
| **E-Mail** | Postmark | 1,25 € | 1.000 E-Mails/Monat |
| **Monitoring** | Sentry (Gratis) | 0 € | Bis 5.000 Events |
| **Domain** | Namecheap | 1 € | .de-Domain |
| **SSL** | Let's Encrypt | 0 € | Kostenlos |
| | | | |
| **SUMME (Infrastruktur)** | | **~113 €** | **+ Stripe-Gebühren** |

## Jährliche Kosten

| Position | Kosten/Jahr | Notizen |
|----------|-------------|---------|
| **Cyber-Versicherung** | 1.000 € | 250k € Deckung |
| **Haftpflicht** | 500 € | 3 Mio. € Deckung |
| **Rechtsschutz** | 0 € | Optional: +1.000 € |
| **Rechtsberatung** | 1.000 € | AGB/Datenschutz prüfen |
| | | |
| **SUMME (Compliance)** | **2.500 €** | **Einmalig höher (Jahr 1)** |

## Einmalige Kosten (Start)

| Position | Kosten | Notizen |
|----------|--------|---------|
| AGB erstellen lassen | 500-1.000 € | Anwalt |
| Datenschutzerklärung | 200-500 € | Anwalt (optional) |
| TOMs-Dokumentation | 0 € | Selbst erstellen |
| Versicherungs-Setup | 0 € | Makler kostenfrei |
| Server-Setup | 0 € | Selbst konfigurieren |
| | | |
| **SUMME (Setup)** | **~1.500 €** | **Einmalig** |

## Hochrechnung: Break-Even

```
Fixkosten/Monat: ~113 € (Infrastruktur)
Fixkosten/Jahr: 2.500 € (Versicherungen, Rechtsberatung)

Gesamtkosten Jahr 1: ~4.900 €

Bei 49 €/Kunde/Monat:
→ 100 Kunden: 4.900 € Umsatz/Monat = 58.800 €/Jahr
→ Abzgl. Stripe (94 € × 12 = 1.128 €): 57.672 €/Jahr
→ Abzgl. Fixkosten (4.900 €): 52.772 €/Jahr GEWINN

Break-Even: ~10 Kunden (Monat 1)
Ab 25 Kunden: Vollzeit davon leben (2.500 €/Monat Gehalt)
Ab 100 Kunden: Profitable SaaS (50k+ € Gewinn/Jahr)
```

---

# TEIL 7: EMPFEHLUNGEN & ZUSAMMENFASSUNG

## ✅ Was du SOFORT tun solltest

1. **Hetzner-Server bestellen** (15 €/Monat)
   → Standort Deutschland
   → AVV abschließen

2. **Stripe-Setup abschließen**
   → AVV akzeptieren (im Dashboard)
   → Test-Transaktionen durchführen

3. **Backups einrichten**
   → Hetzner Snapshots (gratis)
   → Borgbase (2 €/Monat)

4. **Rechtsdokumente vorbereiten**
   → Datenschutzerklärung (Vorlage nutzen)
   → AGB (Anwalt beauftragen!)

5. **Cyber-Versicherung abschließen**
   → 250k € Deckung
   → ~1.000 €/Jahr

## ⚠️ Was du VERMEIDEN solltest

1. **❌ US-Cloud ohne Schrems-II-Garantien**
   → AWS/GCP/Azure nur mit EU-Rechenzentren + SCC

2. **❌ Selbst Kreditkartendaten speichern**
   → IMMER Stripe/Mollie nutzen!
   → Sonst PCI-DSS-Zertifizierung (50k+ €)

3. **❌ Keine AVVs abschließen**
   → Bußgeld bis 10 Mio. €!
   → Mit JEDEM Dienstleister AVV!

4. **❌ Keine Backups**
   → DSGVO-Verstoß (Art. 32)
   → Kundenverlust bei Datenpanne

5. **❌ Keine Versicherung**
   → Existenzbedrohend bei Datenpanne
   → Cyber-Versicherung ist Pflicht!

## 🎯 Finale Architektur-Übersicht

```
┌─────────────────────────────────────────────────────┐
│                   DEINE KUNDEN                       │
│            (Baufirmen mit Mitarbeitern)              │
└─────────────────┬───────────────────────────────────┘
                  │ HTTPS/TLS 1.3
                  ↓
┌─────────────────────────────────────────────────────┐
│              HETZNER CLOUD (DE)                      │
│  ┌──────────────────────────────────────────────┐   │
│  │  Nginx (Reverse Proxy + SSL)                 │   │
│  │  ┌────────────────────────────────────────┐  │   │
│  │  │ Docker: FastAPI App                     │  │   │
│  │  │ - Tenant-Isolation ✅                   │  │   │
│  │  │ - Argon2 Hashing ✅                     │  │   │
│  │  │ - Logging ✅                            │  │   │
│  │  └────────────────────────────────────────┘  │   │
│  │  ┌────────────────────────────────────────┐  │   │
│  │  │ PostgreSQL                              │  │   │
│  │  │ - Verschlüsselt                         │  │   │
│  │  │ - Backups (täglich)                     │  │   │
│  │  └────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────┬───────────────────────────────────┘
                  │
      ┌───────────┼───────────┐
      │           │           │
      ↓           ↓           ↓
┌─────────┐ ┌─────────┐ ┌─────────┐
│ STRIPE  │ │POSTMARK │ │BORGBASE │
│ (Payment)│ │ (E-Mail)│ │ (Backup)│
│  AVV ✅ │ │  AVV ✅ │ │  AVV ✅ │
└─────────┘ └─────────┘ └─────────┘
  EU-Daten    EU-Server   EU-Server
```

## 📞 Nächste Schritte

1. **Woche 1-2:** Hetzner + Stripe + Backups
2. **Woche 3-4:** Rechtsdokumente + TOMs
3. **Woche 5-6:** Versicherungen + Tests
4. **Woche 7-8:** Produktivstart

**Danach:** Weiter mit Phase 1.2 (Tenant-Isolation) aus dem Implementierungsplan!

---

## 📚 Weiterführende Ressourcen

### Behörden
- **BayLDA:** https://www.lda.bayern.de (Datenschutz-Aufsicht Bayern)
- **BSI:** https://www.bsi.bund.de (IT-Sicherheit)
- **DSGVO-Volltext:** https://dsgvo-gesetz.de

### Tools
- **DSGVO-Checkliste:** https://datenschutz-generator.de
- **AVV-Generator:** https://www.datenschutz-generator.de/avv-generator/
- **SSL-Test:** https://www.ssllabs.com/ssltest/

### Communities
- **DSGVO-Forum:** https://www.datenschutz-forum.eu
- **r/datenschutz** (Reddit)
- **OWASP:** https://owasp.org (Security Best Practices)

---

**Ende des Dokuments**

Bei Fragen: Stelle sie jetzt! 🚀

