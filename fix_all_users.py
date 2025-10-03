"""
Repariert alle Benutzer-Passwörter.
"""

import sqlite3
import hashlib

def fix_all_user_passwords():
    """Repariert alle Benutzer-Passwörter."""
    print("Repariere alle Benutzer-Passwörter...")
    
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    try:
        # Hole alle Benutzer
        cursor.execute("SELECT id, username FROM user")
        users = cursor.fetchall()
        
        print(f"Gefundene Benutzer: {len(users)}")
        
        for user_id, username in users:
            # SHA256 Hash für "admin123"
            password = "admin123"
            sha256_hash = "sha256:" + hashlib.sha256(password.encode()).hexdigest()
            
            # Aktualisiere Passwort
            cursor.execute("UPDATE user SET hashed_password = ? WHERE id = ?", (sha256_hash, user_id))
            print(f"   {username}: Passwort repariert")
        
        conn.commit()
        print("Alle Passwörter erfolgreich repariert!")
        
    except Exception as e:
        print(f"Fehler: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_all_user_passwords()

