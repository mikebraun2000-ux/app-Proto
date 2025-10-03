#!/usr/bin/env python3
"""
Aktualisiert die Datenbank mit dem funktionierenden Hash.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import create_engine, Session, text

def update_database_with_working_hash():
    """Aktualisiert die Datenbank mit dem funktionierenden Hash."""
    print("Aktualisiere Datenbank mit funktionierendem Hash...")
    
    engine = create_engine("sqlite:///database.db")
    
    # Der funktionerende Hash für "admin123"
    working_hash = "$pbkdf2-sha256$29000$izHm/B.j1BrDGCMk5Ly39g$hLseZdplvK6l24B5.Hy6RcPaxwGR0/TNTEA6JOEEGsU"
    
    with Session(engine) as session:
        # Hole alle Benutzer
        users = session.exec(text("SELECT id, username FROM user")).all()
        
        for user_id, username in users:
            # Aktualisiere den Hash
            session.exec(text("UPDATE user SET hashed_password = :hash WHERE id = :user_id").bindparams(hash=working_hash, user_id=user_id))
            
            print(f"Hash für {username} aktualisiert")
        
        session.commit()
        print("Alle Passwort-Hashes erfolgreich aktualisiert!")
        print()
        print("LOGIN-DATEN:")
        print("   Benutzername: admin")
        print("   Passwort: admin123")
        print()
        print("   Benutzername: buchhalter")
        print("   Passwort: admin123")
        print()
        print("   Benutzername: mitarbeiter1")
        print("   Passwort: admin123")
        print()
        print("Der Server muss neu gestartet werden!")

if __name__ == "__main__":
    update_database_with_working_hash()

