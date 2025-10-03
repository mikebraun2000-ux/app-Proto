# Kompletter Test-Durchlauf - Bau-Dokumentations-App

**Datum**: 2025-10-02  
**Ziel**: Alle Funktionen testen und Probleme sammeln

---

## 🧪 Test-Kategorien

### 1. Login & Authentifizierung
- [ ] Login mit Admin-Account funktioniert
- [ ] Falsches Passwort wird abgelehnt
- [ ] Token-Refresh funktioniert
- [ ] Logout funktioniert
- [ ] Automatischer Login nach Reload

**Status**: ⏳ Noch nicht getestet  
**Probleme**: -

---

### 2. Dashboard
- [ ] Dashboard lädt korrekt
- [ ] Statistiken werden angezeigt
- [ ] Charts/Grafiken funktionieren
- [ ] Dark Mode funktioniert auf Dashboard

**Status**: ⏳ Noch nicht getestet  
**Probleme**: -

---

### 3. Projekte
- [ ] Projektliste lädt
- [ ] Neues Projekt erstellen funktioniert
- [ ] Projekt bearbeiten funktioniert
- [ ] Projekt löschen funktioniert
- [ ] Projekt-Details anzeigen
- [ ] Filter/Suche funktioniert
- [ ] Bilder hochladen funktioniert
- [ ] Bilder werden angezeigt

**Status**: ⏳ Noch nicht getestet  
**Probleme**: -

---

### 4. Berichte
- [ ] Berichtsliste lädt
- [ ] Neuen Bericht erstellen funktioniert
- [ ] Bericht bearbeiten funktioniert
- [ ] Bericht löschen funktioniert
- [ ] Bilder zu Bericht hochladen
- [ ] Bilder werden angezeigt
- [ ] Progress-Slider funktioniert
- [ ] Status-Änderung funktioniert

**Status**: ⏳ Noch nicht getestet  
**Probleme**: -

---

### 5. Angebote
- [ ] Angebotsliste lädt
- [ ] Neues Angebot erstellen funktioniert
- [ ] Angebot bearbeiten funktioniert
- [ ] Angebot löschen funktioniert
- [ ] Positionen hinzufügen funktioniert
- [ ] Preisberechnung funktioniert korrekt
- [ ] Angebot als PDF generieren
- [ ] PDF-Qualität ist gut
- [ ] "Automatisches Angebot erstellen" Button vorhanden?

**Status**: ⏳ Noch nicht getestet  
**Probleme**: -

---

### 6. Rechnungen
- [ ] Rechnungsliste lädt
- [ ] Neue Rechnung erstellen funktioniert
- [ ] Rechnung bearbeiten funktioniert
- [ ] Rechnung löschen funktioniert
- [ ] Rechnung generieren (aus Angebot) funktioniert
- [ ] Rechnungs-PDF generieren
- [ ] PDF-Layout entspricht Referenz (Rechnung_13-37.pdf)
- [ ] Logo wird im PDF angezeigt
- [ ] Firmen-Stammdaten werden verwendet
- [ ] Status-Änderung funktioniert
- [ ] Zahlungsstatus wird korrekt angezeigt

**Status**: ⏳ Noch nicht getestet  
**Probleme**: -

---

### 7. Zeiterfassung (Stundenerfassung)
- [ ] Zeiteinträge-Liste lädt
- [ ] Neuen Zeiteintrag erstellen funktioniert
- [ ] Zeiteintrag bearbeiten funktioniert
  - [ ] Projekte werden im Dropdown angezeigt
  - [ ] Daten werden korrekt geladen
- [ ] Zeiteintrag löschen funktioniert
  - [ ] Eintrag verschwindet sofort aus UI
- [ ] Stundenberechnung ist korrekt
- [ ] Filter nach Projekt funktioniert
- [ ] Filter nach Mitarbeiter funktioniert

**Status**: ⏳ Noch nicht getestet  
**Probleme**: -

---

### 8. Verwaltung (Settings)
- [ ] Verwaltungs-Sektion lädt

#### 8.1 Firmen-Stammdaten
- [ ] Formular wird angezeigt
- [ ] Alle Felder sind vorhanden (Adresse, Telefon, Fax, Email, Bank, Steuernummer, USt-ID)
- [ ] Daten können eingegeben werden
- [ ] Daten werden gespeichert
- [ ] Gespeicherte Daten werden in Rechnungen verwendet
- [ ] Preview/Vorschau funktioniert

#### 8.2 Logo-Verwaltung
- [ ] Logo hochladen funktioniert
- [ ] Logo-Preview wird angezeigt (nicht weiß)
- [ ] Logo wird in Rechnungen/Angeboten verwendet
- [ ] Aktuelles Logo wird angezeigt

#### 8.3 Mitarbeiter
- [ ] Mitarbeiterliste lädt
- [ ] Neuen Mitarbeiter erstellen funktioniert
- [ ] Mitarbeiter bearbeiten funktioniert
- [ ] Mitarbeiter löschen funktioniert
- [ ] Passwort-Reset für Mitarbeiter funktioniert
- [ ] Username wird als `name.vorname` generiert

#### 8.4 Einladungen
- [ ] Einladungsliste lädt
- [ ] Neue Einladung erstellen funktioniert
- [ ] Einladung per Link versenden
- [ ] Einladung erneut senden funktioniert
- [ ] Einladung zurückziehen funktioniert
- [ ] Einladungs-Link funktioniert (Registrierung)

**Status**: ⏳ Noch nicht getestet  
**Probleme**: -

---

### 9. Abonnement & Billing
- [ ] Abonnement-Status wird angezeigt
- [ ] Status ist korrekt ("Inaktiv", da Multi-Tenant ausgeschaltet)
- [ ] Plan-Informationen werden angezeigt
- [ ] Message wird angezeigt
- [ ] "Zur Kasse" Button ist vorhanden
- [ ] "Status aktualisieren" Button funktioniert
- [ ] Kontrast ist gut (Light & Dark Mode)

**Status**: ⏳ Noch nicht getestet  
**Probleme**: -

---

### 10. UI/UX Allgemein
- [ ] Navigation funktioniert überall
- [ ] Alle Links sind klickbar
- [ ] Alle Buttons sind klickbar
- [ ] Dark/Light Mode funktioniert überall
- [ ] Kontrast ist überall ausreichend
- [ ] Responsive Design funktioniert
- [ ] Keine JavaScript-Fehler in Console
- [ ] Keine Netzwerk-Fehler (außer erwartete 401)
- [ ] Ladezeiten sind akzeptabel
- [ ] Forms validieren korrekt
- [ ] Fehler werden sauber angezeigt

**Status**: ⏳ Noch nicht getestet  
**Probleme**: -

---

## 🐛 Gefundene Probleme

### Kritisch (Blocker)
*Keine gefunden*

### Hoch (Wichtig, aber nicht blockierend)
*Noch nicht getestet*

### Mittel (Sollte behoben werden)
*Noch nicht getestet*

### Niedrig (Nice to have)
*Noch nicht getestet*

---

## 📊 Test-Zusammenfassung

- **Gesamt**: 0/XX Tests abgeschlossen
- **Erfolgreich**: 0
- **Mit Problemen**: 0
- **Nicht funktionsfähig**: 0

---

## 🎯 Nächste Schritte nach Tests

1. Probleme priorisieren
2. Kritische Bugs sofort beheben
3. Wichtige Bugs als nächstes
4. Mittel/Niedrig je nach Zeit
5. Entscheidung: Phase 7 (RBAC) oder Produktionsreife

