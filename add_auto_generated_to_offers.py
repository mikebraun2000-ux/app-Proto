"""
Migrations-Skript: Fügt das auto_generated-Feld zur Offer-Tabelle hinzu.
Führe dieses Skript einmalig aus, um die Datenbank zu aktualisieren.
"""

import sqlite3
from pathlib import Path

def migrate_database():
    """Fügt auto_generated-Spalte zur offer-Tabelle hinzu."""
    db_path = Path("database.db")
    
    if not db_path.exists():
        print(f"[ERROR] Datenbank nicht gefunden: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Prüfe ob Spalte bereits existiert
        cursor.execute("PRAGMA table_info(offer)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'auto_generated' in columns:
            print("[OK] Spalte 'auto_generated' existiert bereits")
            conn.close()
            return True
        
        # Füge Spalte hinzu
        print("[INFO] Fuege Spalte 'auto_generated' zur Tabelle 'offer' hinzu...")
        cursor.execute("""
            ALTER TABLE offer 
            ADD COLUMN auto_generated BOOLEAN DEFAULT 0 NOT NULL
        """)
        
        conn.commit()
        print("[OK] Migration erfolgreich!")
        
        # Verifiziere
        cursor.execute("PRAGMA table_info(offer)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'auto_generated' in columns:
            print("[OK] Spalte 'auto_generated' erfolgreich hinzugefuegt")
            
            # Zeige Anzahl der Angebote
            cursor.execute("SELECT COUNT(*) FROM offer")
            count = cursor.fetchone()[0]
            print(f"[INFO] Anzahl Angebote in Datenbank: {count}")
            
            return True
        else:
            print("[ERROR] Fehler: Spalte konnte nicht hinzugefuegt werden")
            return False
            
    except sqlite3.Error as e:
        print(f"[ERROR] Datenbankfehler: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Datenbank-Migration: auto_generated-Feld für Angebote")
    print("=" * 60)
    
    success = migrate_database()
    
    if success:
        print("\n[OK] Migration abgeschlossen!")
        print("[INFO] Der Server kann jetzt neu gestartet werden.")
    else:
        print("\n[ERROR] Migration fehlgeschlagen!")
        print("[INFO] Bitte pruefe die Fehlermeldungen oben.")

