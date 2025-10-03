# Vorgeschlagene Aufgaben

## Tippfehler korrigieren
- **Datei:** `start.py`
- **Problem:** In der Warnmeldung wird "Passworter" statt "Passwörter" ausgegeben.
- **Auswirkung:** Wirkt unprofessionell und kann in deutschsprachiger UI zu Irritation führen.
- **Vorschlag:** Schreibweise in "Passwörter" anpassen.

## Programmierfehler beheben
- **Datei:** `app/routers/invoices.py`
- **Problem:** Der Endpoint `create_invoice_from_calculation` deklariert seine Parameter als Funktionsargumente, wodurch FastAPI sie als Query-Parameter erwartet. Das Frontend sendet jedoch einen JSON-Body und erhält dadurch einen 422-Fehler.
- **Auswirkung:** Automatisch generierte Rechnungen können nicht gespeichert werden.
- **Vorschlag:** Einen Pydantic-Body (z. B. `InvoiceCreateFromCalculation`) einführen oder `Body(...)` verwenden, damit FastAPI die Felder aus dem Request-Body liest.

## Dokumentations-/Kommentar-Korrektur
- **Datei:** `README.md`
- **Problem:** Die Projektstruktur listet einen Ordner `backend/`, obwohl das Repository auf der obersten Ebene `app/` verwendet.
- **Auswirkung:** Verwirrt neue Entwickler beim Einstieg und bei der Navigation im Repo.
- **Vorschlag:** Strukturdiagramm und Text an die tatsächliche Ordnerstruktur anpassen.

## Test verbessern
- **Datei:** `tests/unit/test_auth_security.py`
- **Problem:** Es fehlt ein Test für den ultimativen Fallback in `verify_password`, der alte Klartext-Passwörter (`"admin123"`) akzeptiert.
- **Auswirkung:** Die kritische Notfalllogik ist ungetestet; eine unbeabsichtigte Änderung bliebe unbemerkt.
- **Vorschlag:** Einen Test ergänzen, der `verify_password("admin123", "admin123")` abdeckt und sicherstellt, dass gleichzeitig Rehashing ausgelöst wird.
