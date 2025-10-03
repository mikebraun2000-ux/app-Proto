"""
Repariert die Benutzer-Passwort-Hashes in der Datenbank.
"""

import sqlite3
import hashlib
import os

def fix_user_passwords():
    """Repariert alle Benutzer-Passwörter mit einfachen SHA256-Hashes."""
    print("Repariere Benutzer-Passwörter...")
    
    # Datenbankverbindung
    db_path = "database.db"
    if not os.path.exists(db_path):
        print(f"Datenbank {db_path} nicht gefunden!")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Benutzer und ihre Passwörter
        users = [
            ("admin", "admin123"),
            ("buchhalter", "buchhalter123"),
            ("mitarbeiter1", "mitarbeiter123")
        ]
        
        for username, password in users:
            # SHA256-Hash mit "sha256:" Präfix (wie im Auth-System erwartet)
            password_hash = "sha256:" + hashlib.sha256(password.encode()).hexdigest()
            
            # Hash in der Datenbank aktualisieren
            cursor.execute(
                "UPDATE user SET hashed_password = ? WHERE username = ?",
                (password_hash, username)
            )
            
            print(f"Passwort für {username} repariert")
        
        conn.commit()
        print("Alle Passwörter erfolgreich repariert!")
        return True
        
    except Exception as e:
        print(f"Fehler beim Reparieren der Passwörter: {e}")
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    fix_user_passwords()