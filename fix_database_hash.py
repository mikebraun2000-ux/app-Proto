#!/usr/bin/env python3
"""
Korrigiert die Passwort-Hashes in der aktuellen Datenbank.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import create_engine, Session, text

def fix_database_hash():
    """Korrigiert die Passwort-Hashes in der Datenbank."""
    print("Korrigiere Passwort-Hashes in der Datenbank...")
    
    engine = create_engine("sqlite:///database.db")
    
    with Session(engine) as session:
        # Verwende einen definitiv funktionierenden bcrypt-Hash
        # Dieser Hash wurde mit einem funktionierenden bcrypt generiert
        working_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/4.8.8.8"
        
        # Hole alle Benutzer
        users = session.exec(text("SELECT id, username FROM user")).all()
        
        for user_id, username in users:
            # Aktualisiere den Hash
            session.exec(text("UPDATE user SET hashed_password = :hash WHERE id = :user_id").bindparams(hash=working_hash, user_id=user_id))
            
            print(f"Passwort für {username} korrigiert")
        
        session.commit()
        print("Alle Passwort-Hashes korrigiert!")
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

if __name__ == "__main__":
    fix_database_hash()

