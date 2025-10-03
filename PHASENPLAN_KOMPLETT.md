# 🗓️ Kompletter Phasenplan - Bau-Dokumentations-App

**Erstellt am:** 3. Oktober 2025  
**Version:** 2.0 - Mit Compliance-Integration  
**Gesamtdauer:** 8-12 Wochen (je nach Ressourcen)

---

## 📊 Übersicht der Phasen

```
PHASE 1-2: CORE ENTWICKLUNG (6-8 Wochen)
├── Security-Fixes
├── Code Quality
├── Performance
└── Architektur

PHASE 3: PRODUKT-FINALISIERUNG (1-2 Wochen)
├── UI/UX Polish
├── Feature-Komplettierung
└── Beta-Testing

PHASE 4: COMPLIANCE & GO-LIVE (1-2 Wochen)
├── Rechtliche Vorbereitung
├── Infrastruktur-Setup
├── Versicherungen
└── Produktivstart
```

---

# PHASE 1-2: CORE ENTWICKLUNG (Wochen 1-8)

## Fokus: App funktional & sicher machen

**Was wir JETZT umsetzen:**
- ✅ Passwort-Hashing (Argon2)
- ✅ Tenant-Isolation
- ✅ Logging-System
- ✅ SQL-Injection-Schutz
- ✅ Code-Qualität
- ✅ Performance-Optimierung

**Was wir NICHT jetzt machen:**
- ❌ Produktiv-Server aufsetzen (läuft auf localhost)
- ❌ AVVs abschließen (erst bei Go-Live)
- ❌ Versicherungen (erst bei Go-Live)
- ❌ Rechtsdokumente finalisieren (Entwürfe reichen)

### Entwicklungs-Umgebung

```
Development Setup:
- Local: localhost:8000
- Datenbank: SQLite (database.db)
- Secrets: Testdaten OK (noch nicht produktiv)
- Backups: Manuell (Git-Commits reichen)
- Monitoring: Console-Logs

→ Schnelle Entwicklung ohne Compliance-Overhead!
```

---

# PHASE 3: PRODUKT-FINALISIERUNG (Wochen 9-10)

## 3.1 Feature-Freeze & Polish (1 Woche)

### Aufgaben

```
✅ Alle geplanten Features implementiert
✅ UI/UX durchgetestet & poliert
✅ Alle kritischen Bugs gefixt
✅ Performance akzeptabel (< 1s Ladezeit)
✅ Mobile-Ansicht funktioniert
✅ PDF-Generierung perfekt
✅ Alle Formulare validiert
```

### Checkliste: Feature-Komplettierung

```
KERN-FEATURES:
☐ Projekt-Management (CRUD)
☐ Angebots-Erstellung (manuell + automatisch)
☐ Rechnungs-Generierung (inkl. PDF)
☐ Stundenerfassung (Clock-In/Out)
☐ Berichte mit Fotos
☐ Mitarbeiter-Verwaltung
☐ Firmenstammdaten
☐ Logo-Upload

ZUSATZ-FEATURES:
☐ Dashboard mit Statistiken
☐ Rechnungsvorschau
☐ PDF-Download
☐ Status-Tracking (Angebote, Rechnungen)
☐ Einladungs-System (Tenant-Onboarding)
☐ Stripe-Integration (Subscriptions)

SICHERHEIT:
☐ Login funktioniert
☐ Passwort-Reset
☐ Rollenbasierte Rechte (Admin, Buchhalter, Mitarbeiter)
☐ Tenant-Isolation (User A sieht nur seine Daten)
```

## 3.2 Beta-Testing (1 Woche)

### Aufgaben

```
1. ✅ 3-5 Test-Nutzer einladen (Freunde, Familie, Beta-Kunden)
2. ✅ Realistische Nutzung simulieren
3. ✅ Feedback sammeln (Google Forms / Notion)
4. ✅ Kritische Bugs priorisieren & fixen
5. ✅ Performance-Probleme identifizieren
```

### Beta-Test-Szenarien

```
Szenario 1: Neues Projekt anlegen
- Projekt erstellen
- Mitarbeiter zuordnen
- Stundenerfassung nutzen
- Bericht mit Fotos erstellen

Szenario 2: Angebot & Rechnung
- Angebot erstellen (manuell)
- PDF generieren & prüfen
- Angebot in Rechnung umwandeln
- Rechnung versenden

Szenario 3: Multi-User
- Admin lädt Mitarbeiter ein
- Mitarbeiter loggt sich ein
- Mitarbeiter erfasst Stunden
- Admin sieht Stunden (Buchhalter-Rolle)

Szenario 4: Tenant-Trennung
- 2 verschiedene Accounts anlegen
- Prüfen: User A sieht NICHT Daten von User B
- Cross-Tenant-Access testen (sollte fehlschlagen!)
```

### Beta-Feedback-Formular

```
Fragen:
1. Wie einfach war die Registrierung? (1-10)
2. Wie intuitiv ist die Navigation? (1-10)
3. Was hat dir gefehlt?
4. Was hat dich verwirrt?
5. Welches Feature findest du am wichtigsten?
6. Würdest du 49 €/Monat zahlen? (Ja/Nein/Kommentar)
7. Bugs gefunden? (Freitext)
```

---

# PHASE 4: COMPLIANCE & GO-LIVE (Wochen 11-12)

## 🎯 Ziel: App rechtskonform & versichert in Produktion bringen

**Jetzt wird ernst!** Ab hier brauchst du:
- Echte Infrastruktur (Hetzner)
- Rechtsdokumente (AGB, Datenschutz)
- Versicherungen (Cyber, Haftpflicht)
- AVVs mit Dienstleistern

---

## 4.1 Infrastruktur-Setup (Woche 11, Tag 1-3)

### Tag 1: Hetzner-Server (4h)

#### Schritt 1: Server bestellen (30min)

```
1. Gehe zu: https://www.hetzner.com/cloud
2. Registriere dich / Logge ein
3. Bestelle Server:
   - Produkt: CPX21 (3 vCPU, 4 GB RAM, 80 GB SSD)
   - Standort: Falkenstein (Deutschland)
   - Image: Ubuntu 24.04 LTS
   - Zusatz: Backups aktivieren (gratis)

Kosten: ~8,16 €/Monat

4. SSH-Key hinterlegen:
   - Generiere Key: ssh-keygen -t ed25519 -C "admin@deine-app.de"
   - Public Key in Hetzner-Dashboard einfügen
   - WICHTIG: Private Key sicher aufbewahren!

5. Server erstellen & IP notieren
```

#### Schritt 2: Server absichern (1h)

```bash
# SSH-Verbindung testen
ssh root@<server-ip>

# System updaten
apt update && apt upgrade -y

# Firewall konfigurieren
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw enable

# Fail2Ban installieren (Schutz vor Brute-Force)
apt install fail2ban -y
systemctl enable fail2ban
systemctl start fail2ban

# Automatische Updates
apt install unattended-upgrades -y
dpkg-reconfigure -plow unattended-upgrades

# Root-Login deaktivieren (später, nach Non-Root-User erstellt)
```

#### Schritt 3: Docker installieren (30min)

```bash
# Docker installieren
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Docker Compose installieren
apt install docker-compose-plugin -y

# Docker-Service starten
systemctl enable docker
systemctl start docker

# Test
docker run hello-world
```

#### Schritt 4: PostgreSQL (1h)

```bash
# Option A: Docker PostgreSQL (Einfach)
mkdir -p /opt/bauapp/postgres
cd /opt/bauapp

# docker-compose.yml erstellen
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  postgres:
    image: postgres:16-alpine
    restart: always
    environment:
      POSTGRES_DB: bauapp
      POSTGRES_USER: bauapp_user
      POSTGRES_PASSWORD: <STARKES-PASSWORT-HIER>
    volumes:
      - ./postgres:/var/lib/postgresql/data
    ports:
      - "127.0.0.1:5432:5432"
EOF

# Starten
docker-compose up -d

# Option B: Hetzner Managed PostgreSQL (Empfohlen für Produktion)
# → Im Hetzner-Dashboard bestellen (ab 15 €/Monat)
# → Automatische Backups, Updates, Monitoring inklusive
```

#### Schritt 5: App deployen (1h)

```bash
# App-Verzeichnis erstellen
mkdir -p /opt/bauapp/app
cd /opt/bauapp/app

# Git-Repo klonen (oder via FTP/SFTP hochladen)
git clone <dein-repo-url> .

# .env erstellen
cat > .env << 'EOF'
SECRET_KEY=<generiere mit: python -c "import secrets; print(secrets.token_hex(32))">
DATABASE_URL=postgresql://bauapp_user:<PASSWORT>@localhost:5432/bauapp
STRIPE_TEST_SECRET_KEY=<dein-stripe-key>
STRIPE_TEST_PUBLISHABLE_KEY=<dein-publishable-key>
STRIPE_ACTIVE_PRICE_ID=price_1SDaPGQpDeiCy5Mxx8VOvW4t
ENVIRONMENT=production
EOF

# Docker-Container für App
docker build -t bauapp:latest .

# Starten
docker run -d \
  --name bauapp \
  --restart always \
  -p 127.0.0.1:8000:8000 \
  --env-file .env \
  bauapp:latest
```

### Tag 2: SSL & Domain (2h)

#### Schritt 1: Domain einrichten (30min)

```
1. Domain kaufen (z.B. Namecheap, Hetzner, IONOS)
   → bauapp.de oder dein-name.de
   → Kosten: ~10-15 €/Jahr

2. DNS-Einträge setzen:
   A-Record: @ → <hetzner-server-ip>
   A-Record: www → <hetzner-server-ip>

3. Warten (5-60 Minuten Propagation)
```

#### Schritt 2: SSL-Zertifikat (1h)

```bash
# Nginx installieren
apt install nginx -y

# Certbot installieren
apt install certbot python3-certbot-nginx -y

# Nginx konfigurieren
cat > /etc/nginx/sites-available/bauapp << 'EOF'
server {
    listen 80;
    server_name deine-app.de www.deine-app.de;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# Aktivieren
ln -s /etc/nginx/sites-available/bauapp /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

# SSL-Zertifikat generieren
certbot --nginx -d deine-app.de -d www.deine-app.de

# Auto-Renewal testen
certbot renew --dry-run
```

### Tag 3: Backup & Monitoring (4h)

#### Schritt 1: Borg Backup (2h)

```bash
# Borg installieren
apt install borgbackup -y

# Borgbase-Account erstellen
# → https://www.borgbase.com
# → Neues Repo anlegen: "bauapp-backup"
# → SSH-Key hinterlegen

# Borg initialisieren
export BORG_REPO='ssh://xxx@xxx.repo.borgbase.com/./repo'
export BORG_PASSPHRASE='<SICHERES-PASSWORT>'
borg init --encryption=repokey

# Backup-Skript erstellen
cat > /usr/local/bin/backup.sh << 'EOF'
#!/bin/bash
export BORG_REPO='ssh://xxx@xxx.repo.borgbase.com/./repo'
export BORG_PASSPHRASE='<PASSWORT-HIER>'

# Datenbank dumpen
docker exec postgres pg_dump -U bauapp_user bauapp > /tmp/backup.sql

# Borg Backup
borg create \
  --stats --progress \
  ::'{hostname}-{now}' \
  /opt/bauapp \
  /tmp/backup.sql

# Alte Backups löschen
borg prune \
  --keep-daily=30 \
  --keep-weekly=4 \
  --keep-monthly=6

rm /tmp/backup.sql
EOF

chmod +x /usr/local/bin/backup.sh

# Cronjob (täglich 3 Uhr)
crontab -e
# Einfügen:
0 3 * * * /usr/local/bin/backup.sh >> /var/log/backup.log 2>&1

# Ersten Backup testen
/usr/local/bin/backup.sh
```

#### Schritt 2: Monitoring (2h)

```bash
# Uptime Monitoring: UptimeRobot (Gratis)
# → https://uptimerobot.com
# → Monitor anlegen: https://deine-app.de/health
# → E-Mail-Benachrichtigung bei Ausfall

# Sentry für Error-Tracking
# 1. Account erstellen: https://sentry.io
# 2. Neues Projekt: "bauapp"
# 3. DSN notieren
# 4. In .env ergänzen:
#    SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx

# Sentry in app/main.py integrieren:
import sentry_sdk
sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    environment=os.getenv("ENVIRONMENT"),
    traces_sample_rate=0.1,
)
```

---

## 4.2 Rechtliche Vorbereitung (Woche 11, Tag 4-5)

### Tag 4: AVVs abschließen (4h)

#### Schritt 1: Hetzner-AVV (1h)

```
1. Gehe zu: https://www.hetzner.com/rechtliches/avv
2. Formular ausfüllen:
   - Deine Firmendaten / Name
   - Adresse
   - Verarbeitungszweck: "SaaS-Hosting für Bau-Dokumentations-Software"
   - Datenkategorien: "Personenbezogene Daten von Endkunden"
3. Unterschreiben (digital oder Ausdruck)
4. Per E-Mail an: legal@hetzner.com
5. Warten auf Bestätigung (~3-7 Tage)

WICHTIG: App NICHT live schalten vor AVV-Bestätigung!
```

#### Schritt 2: Stripe-AVV (5min)

```
1. Login: https://dashboard.stripe.com
2. Settings → Data Processing Agreement
3. Klicke "Accept DPA"
4. Screenshot/PDF speichern (Nachweis)
5. ✅ Fertig!
```

#### Schritt 3: Postmark-AVV (30min)

```
1. E-Mail an: support@postmarkapp.com
2. Betreff: "Request for Data Processing Agreement (DPA)"
3. Text:
   "Hello,
   
   We are using Postmark for transactional emails in our SaaS application.
   For GDPR compliance, we need a signed Data Processing Agreement.
   
   Company: [Dein Name/Firma]
   Account: [Postmark-Account-ID]
   
   Please send us the DPA.
   
   Best regards,
   [Dein Name]"
   
4. Warten auf Antwort (2-3 Tage)
5. DPA unterschreiben & zurücksenden
```

#### Schritt 4: Borgbase-AVV (30min)

```
1. E-Mail an: support@borgbase.com
2. Betreff: "GDPR Data Processing Agreement"
3. Text ähnlich wie Postmark
4. DPA erhalten & unterschreiben
```

### Tag 5: Rechtsdokumente finalisieren (4h)

#### Schritt 1: Impressum (30min)

```
Pflichtangaben (§5 TMG):
- Name (oder Firmenname)
- Anschrift (KEINE Postfachadresse!)
- E-Mail
- Telefon (optional, aber empfohlen)
- Umsatzsteuer-ID (falls vorhanden)
- Handelsregister-Nummer (bei GmbH/UG)

Generator nutzen:
→ https://www.e-recht24.de/impressum-generator.html

In App einbinden:
→ static/index.html: Footer mit Link zu /impressum
→ Separate HTML-Seite oder Modal
```

#### Schritt 2: Datenschutzerklärung (2h)

```
Vorlage aus HAFTUNG_DATENSCHUTZ_DIENSTLEISTER_PLAN.md nutzen

Anpassen:
1. Deine Kontaktdaten einfügen
2. Dienstleister-Liste aktualisieren (Hetzner, Stripe, etc.)
3. AVV-Status bestätigen ("AVV vorhanden: Ja")
4. Cookie-Banner ergänzen (falls Cookies genutzt werden)

Optional: Anwalt prüfen lassen (200-500 €)
→ Empfohlen, aber nicht zwingend

In App einbinden:
→ Link im Footer: /datenschutz
→ Checkbox bei Registrierung: "Ich akzeptiere die Datenschutzerklärung"
```

#### Schritt 3: AGB (1,5h)

```
WICHTIG: AGB sollten von Anwalt geprüft werden!
Kosten: 500-1.000 € (einmalig)

Entwurf-Vorlage nutzen (aus Online-Generatoren):
→ https://www.it-recht-kanzlei.de
→ https://www.activemind.de/agb-generator/

Kritische Punkte:
1. Leistungsumfang (Was bietest du?)
2. Preise & Zahlungsbedingungen (49 €/Monat, monatlich kündbar)
3. Laufzeit & Kündigung (Monatlich, 1 Monat Kündigungsfrist)
4. Haftungsbeschränkung (Nur bei leichter Fahrlässigkeit)
5. Gewährleistung (Verfügbarkeit 99%, Support 24h Reaktionszeit)
6. Datenschutz-Verweis
7. Gerichtsstand (Dein Wohnort)

In App einbinden:
→ Link im Footer: /agb
→ Checkbox bei Registrierung: "Ich akzeptiere die AGB"
```

---

## 4.3 Versicherungen (Woche 12, Tag 1-2)

### Tag 1: Cyber-Versicherung (4h)

#### Schritt 1: Angebot einholen (2h)

```
Anbieter kontaktieren:
1. CyberDirekt (Makler): https://cyberdirekt.de
   → Online-Formular ausfüllen
   → 3-5 Angebote vergleichen

2. Hiscox: https://www.hiscox.de/cyber
   → Direkt-Angebot online

3. Allianz: https://www.allianz.de/cyber
   → Telefonisch: 0800 4 100 100

Angaben bereithalten:
- Branche: IT / SaaS
- Umsatz: [Prognose]
- Anzahl Kunden: [Prognose]
- Datenvolumen: [Schätzung]
- Sicherheitsmaßnahmen: Argon2, Tenant-Isolation, Backups, etc.
```

#### Schritt 2: Versicherung abschließen (2h)

```
Empfohlene Deckung:
- Deckungssumme: 250.000 € (Start) bis 500.000 € (ab 50+ Kunden)
- Eigenschäden: Ja (Datenwiederherstellung, Betriebsunterbrechung)
- Fremdschäden: Ja (Schadensersatz, Rechtsverteidigung)
- DSGVO-Bußgelder: Ja (soweit versicherbar)

Kosten: ~1.000-1.500 €/Jahr

Vertragsunterlagen:
→ Aufbewahren in Cloud (Notion, Google Drive)
→ Kontaktdaten 24/7-Hotline notieren (für Notfall!)
```

### Tag 2: Haftpflicht & Optional Rechtsschutz (2h)

#### Betriebs-Haftpflicht (1h)

```
Anbieter:
- Haftpflichtkasse Darmstadt
- Allianz
- ERGO

Deckungssumme: 3-5 Mio. €
WICHTIG: "Vermögensschäden" einschließen!

Kosten: ~300-600 €/Jahr

Abschluss: Online oder telefonisch
```

#### Rechtsschutz (optional, 1h)

```
Gewerbliche Rechtsschutzversicherung

Deckt:
- Vertragsrecht
- Arbeitsrecht (falls Mitarbeiter)
- Internetrecht (z.B. Abmahnungen)

Kosten: ~800-1.200 €/Jahr

OPTIONAL: Nur, wenn Budget vorhanden
→ Erst ab 50+ Kunden wirklich sinnvoll
```

---

## 4.4 Dokumentation & TOMs (Woche 12, Tag 3)

### Aufgaben (4h)

#### Schritt 1: TOMs dokumentieren (2h)

```
Vorlage aus HAFTUNG_DATENSCHUTZ_DIENSTLEISTER_PLAN.md nutzen

Ausfüllen:
1. Zutrittskontrolle: "Hetzner Rechenzentrum, ISO 27001"
2. Zugangskontrolle: "Argon2, JWT, 2FA (geplant)"
3. Zugriffskontrolle: "RBAC, Tenant-Isolation, Unit-Tests"
4. Weitergabekontrolle: "TLS 1.3, HTTPS, verschlüsselte Backups"
5. Eingabekontrolle: "Audit-Logs, created_at/updated_at"
6. Auftragskontrolle: "AVVs mit allen Dienstleistern"
7. Verfügbarkeitskontrolle: "3-2-1-Backup, RTO 4h, RPO 24h"
8. Trennungskontrolle: "tenant_id in allen Tabellen, Unit-Tests"

Speichern als: TOMs_Bauapp.pdf
```

#### Schritt 2: Verzeichnis von Verarbeitungstätigkeiten (1h)

```
Vorlage herunterladen:
→ https://www.lda.bayern.de/media/muster_vvt.pdf

Ausfüllen für jede Verarbeitung:
1. Benutzerverwaltung (Login, Registrierung)
2. Projekt-Daten (Angebote, Rechnungen)
3. Mitarbeiter-Daten (Stundenerfassung)
4. Fotos (Berichts-Uploads)
5. Zahlungsdaten (Stripe Subscriptions)

Speichern als: VVT_Bauapp.pdf
```

#### Schritt 3: Incident-Response-Plan (1h)

```
Was tun bei Datenpanne?

1. ERKENNUNG (automatisch via Monitoring)
   → Sentry-Alert: Error-Spike
   → Uptime-Alert: Server down
   → Manuell: Kunden-Meldung

2. BEWERTUNG (binnen 1h)
   → Wie viele Nutzer betroffen?
   → Welche Daten betroffen?
   → Risiko-Level: Niedrig / Mittel / Hoch

3. EINDÄMMUNG (binnen 4h)
   → Server isolieren (Firewall)
   → Passwörter zurücksetzen
   → Backup wiederherstellen

4. MELDUNG (binnen 72h!)
   → Bei Aufsichtsbehörde: https://www.lda.bayern.de
   → Bei Betroffenen (wenn hohes Risiko)

5. DOKUMENTATION
   → Vorfall in Logbuch eintragen
   → Post-Mortem erstellen
   → Maßnahmen ableiten

Verantwortliche:
- Incident Commander: [Dein Name]
- Technischer Lead: [Dein Name oder Entwickler]
- Kommunikation: [Dein Name]

Notfall-Kontakte:
- Cyber-Versicherung 24/7: [Hotline-Nummer]
- Anwalt (Datenschutz): [Telefon]
- Hetzner-Support: +49 9831 505-0
```

---

## 4.5 Go-Live Vorbereitung (Woche 12, Tag 4-5)

### Tag 4: Finale Tests (4h)

#### Checkliste: Pre-Launch

```
TECHNISCH:
☐ App läuft auf Produktiv-Server (ohne Fehler)
☐ HTTPS funktioniert (SSL Labs: A+ Rating)
☐ Backup läuft automatisch (geprüft: /var/log/backup.log)
☐ Monitoring aktiv (Sentry + UptimeRobot)
☐ Datenbank-Migration erfolgreich (SQLite → PostgreSQL)
☐ Stripe live-Modus aktiviert (echte Zahlungen)
☐ E-Mail-Versand funktioniert (Postmark)
☐ Performance OK (< 1s Ladezeit)

RECHTLICH:
☐ Impressum vorhanden & korrekt
☐ Datenschutzerklärung vorhanden
☐ AGB vorhanden & von Anwalt geprüft
☐ Cookie-Banner (falls Cookies)
☐ AVVs mit allen Dienstleistern abgeschlossen
☐ TOMs dokumentiert
☐ VVT erstellt
☐ Incident-Response-Plan vorhanden

VERSICHERUNGEN:
☐ Cyber-Versicherung aktiv
☐ Haftpflicht aktiv
☐ Versicherungs-Hotlines notiert

GESCHÄFTLICH:
☐ Pricing festgelegt (49 €/Monat)
☐ Stripe-Produkt & Preis erstellt
☐ Erste Test-Kunden eingeladen (3-5 Personen)
☐ Support-E-Mail eingerichtet (support@deine-app.de)
☐ FAQ erstellt (Notion, Intercom, oder HTML-Seite)
```

### Tag 5: Soft Launch (4h)

#### Schritt 1: Erste echte Kunden (2h)

```
1. Beta-Tester kontaktieren (aus Phase 3)
   → "Die App ist jetzt live!"
   → 50% Rabatt für erste 3 Monate (24,50 € statt 49 €)
   → Lifetime-Discount als Dankeschön (39 € statt 49 €)

2. Registrierung überwachen
   → Sentry: Errors?
   → Server-Load: OK?
   → Stripe: Zahlungen erfolgreich?

3. Onboarding-E-Mail senden
   → Willkommen!
   → Quick-Start-Guide
   → Support-Kontakt
```

#### Schritt 2: Marketing-Soft-Launch (2h)

```
Kanäle:
1. LinkedIn-Post (persönliches Profil)
   → "Ich habe eine SaaS für Baufirmen gelauncht! 🎉"
   → Screenshot der App
   → Link zur Landing-Page
   → #SaaS #Construction #Startups

2. Xing-Post (falls du dort aktiv bist)

3. Lokale Unternehmer-Gruppen (Facebook, WhatsApp)
   → "Kennt jemand Trockenbauer, die digitaler werden wollen?"

4. Bauunternehmer-Foren (z.B. bauexpertenforum.de)
   → Vorsichtig: Nicht zu werblich!
   → Hilfreiche Beiträge, dann Signatur mit Link

KEIN Public Launch (Product Hunt, Hacker News) - noch nicht!
→ Erst ab 20+ zahlenden Kunden
```

---

## 4.6 Post-Launch Monitoring (Woche 13+)

### Aufgaben (fortlaufend)

#### Täglich (15min)

```
☐ Sentry prüfen (neue Errors?)
☐ UptimeRobot prüfen (Ausfälle?)
☐ Stripe-Dashboard (neue Zahlungen? Fehlgeschlagene?)
☐ Support-E-Mails beantworten
```

#### Wöchentlich (1h)

```
☐ Backup testen (restore durchführen)
☐ Server-Ressourcen prüfen (CPU, RAM, Disk)
☐ Performance-Metriken (Ladezeiten)
☐ Kunden-Feedback sammeln & priorisieren
☐ Neue Features planen (User-Requests)
```

#### Monatlich (4h)

```
☐ Sicherheits-Updates installieren (Server, Dependencies)
☐ Compliance-Dokumente aktualisieren (falls nötig)
☐ Versicherungen prüfen (Deckung noch ausreichend?)
☐ AVVs verlängern (falls Ablauf)
☐ Finanz-Report (Umsatz, Kosten, Gewinn)
```

---

# ZUSAMMENFASSUNG: ZEITPLAN

## Übersicht

```
WOCHEN 1-8: ENTWICKLUNG
├── Phase 1: Security (Woche 1)
├── Phase 2: Code Quality (Wochen 2-3)
├── Zwischentest (Woche 4)
├── Phase 3: Performance (Woche 5)
├── Phase 4: Architektur (Wochen 6-7)
└── Integration & Tests (Woche 8)

WOCHEN 9-10: FINALISIERUNG
├── Feature-Freeze & Polish (Woche 9)
└── Beta-Testing (Woche 10)

WOCHEN 11-12: COMPLIANCE & GO-LIVE
├── Infrastruktur (Tag 1-3)
├── Rechtliches (Tag 4-5)
├── Versicherungen (Tag 6-7)
├── Dokumentation (Tag 8)
├── Finale Tests (Tag 9)
└── Soft Launch (Tag 10)

WOCHE 13+: BETRIEB
└── Monitoring & Optimierung
```

## Kosten-Übersicht

### Entwicklungsphase (Wochen 1-10)

```
Kosten: ~0 € (nur deine Zeit!)
- Entwicklung: localhost
- Datenbank: SQLite (gratis)
- Tests: lokal (gratis)
```

### Go-Live (Wochen 11-12)

```
Einmalige Kosten:
- Domain: 10-15 €
- AGB-Prüfung (Anwalt): 500-1.000 €
- Datenschutz-Prüfung (optional): 200-500 €
─────────────────────────────────────────
SUMME einmalig: ~1.500 €
```

### Laufende Kosten (ab Go-Live)

```
Monatlich:
- Hetzner Server: 8 €
- Hetzner Volume: 6 €
- Borgbase Backup: 2 €
- Postmark E-Mail: 1,25 €
- Domain: ~1 €
- Stripe-Gebühren: ~94 € (bei 100 Kunden)
─────────────────────────────────────────
SUMME monatlich: ~112 € + Stripe-Gebühren

Jährlich:
- Cyber-Versicherung: 1.000 €
- Haftpflicht: 500 €
─────────────────────────────────────────
SUMME jährlich: ~1.500 €

Gesamt Jahr 1: ~4.900 € (Infrastruktur + Versicherung + Einmalig)
```

### Break-Even

```
Bei 49 €/Kunde/Monat:

10 Kunden: 490 €/Monat → Break-Even Infrastruktur
25 Kunden: 1.225 €/Monat → Break-Even Gesamt
50 Kunden: 2.450 €/Monat → Vollzeit davon leben
100 Kunden: 4.900 €/Monat → 50k+ € Gewinn/Jahr 🎉
```

---

# NEXT STEPS

## Was du JETZT tun solltest:

1. ✅ **Weitermachen mit Phase 1.1** (Argon2-Hashing)
   - Ist bereits begonnen!
   - Tests laufen durch ✅
   - Migrations-Skripte noch erstellen

2. ✅ **Fokus auf Entwicklung** (Wochen 1-8)
   - Compliance kommt später
   - Schnell Features bauen
   - App nutzbar machen

3. ✅ **Compliance merken für später** (Wochen 11-12)
   - Haftungsplan liegt bereit
   - Wird umgesetzt vor Go-Live
   - Kein Stress jetzt!

## Nächster Schritt JETZT:

**Erstelle .env-Datei mit Test-SECRET_KEY:**

```bash
cd C:\Users\Michael\Tommy\backend

# .env erstellen
echo "SECRET_KEY=test-development-key-please-change-in-production" > .env
echo "DATABASE_URL=sqlite:///./database.db" >> .env
echo "ENVIRONMENT=development" >> .env
```

**Dann weiter mit Implementierung Phase 1.1:**
- Migrations-Skript für Passwörter
- Reset-Skript
- Weitere Tests

---

**Alles klar? Lass uns mit der Entwicklung weitermachen! 🚀**

