#!/usr/bin/env python3
"""
Script um die Datenbank-Hashes zu korrigieren.
"""

from sqlmodel import create_engine, Session, text

def fix_hashes():
    """Korrigiert die Benutzer-Hashes in der Datenbank."""
    print("Korrigiere Datenbank-Hashes...")
    
    try:
        engine = create_engine("sqlite:///database.db")
        
        with Session(engine) as session:
            # Aktualisiere alle Hashes zu "admin123"
            session.exec(text("UPDATE user SET hashed_password = 'admin123' WHERE hashed_password = 'SIMPLE_HASH_admin123'"))
            session.commit()
            
            # Überprüfe das Ergebnis
            users = session.exec(text("SELECT username, hashed_password FROM user")).all()
            for username, hashed_password in users:
                print(f"{username}: {hashed_password}")
            
            print("Hashes erfolgreich korrigiert!")
            
    except Exception as e:
        print(f"Fehler: {e}")

if __name__ == "__main__":
    fix_hashes()

