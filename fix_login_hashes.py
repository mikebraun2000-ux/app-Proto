#!/usr/bin/env python3
"""
Korrigiert die Passwort-Hashes in der Datenbank mit korrekten bcrypt-Hashes.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import create_engine, Session, text
from passlib.context import CryptContext

# Passwort-Hashing konfigurieren
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def fix_login_hashes():
    """Korrigiert die Passwort-Hashes in der Datenbank."""
    print("Korrigiere Login-Hashes...")
    
    engine = create_engine("sqlite:///database.db")
    
    with Session(engine) as session:
        # Hole alle Benutzer
        users = session.exec(text("SELECT id, username FROM user")).all()
        
        for user_id, username in users:
            # Erstelle korrekten bcrypt-Hash für "admin123"
            correct_hash = pwd_context.hash("admin123")
            
            # Aktualisiere den Hash
            session.exec(text("UPDATE user SET hashed_password = :hash WHERE id = :user_id"), 
                       {"hash": correct_hash, "user_id": user_id})
            
            print(f"Passwort für {username} korrigiert")
        
        session.commit()
        print("Alle Login-Hashes korrigiert!")
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
    fix_login_hashes()

