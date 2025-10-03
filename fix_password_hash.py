#!/usr/bin/env python3
"""
Korrigiert das Passwort-Hashing in der Datenbank.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import create_engine, Session, text
import hashlib

def fix_passwords():
    """Korrigiert die Passwort-Hashes in der Datenbank."""
    print("Korrigiere Passwort-Hashes...")
    
    engine = create_engine("sqlite:///database.db")
    
    with Session(engine) as session:
        # Hole alle Benutzer
        users = session.exec(text("SELECT id, username FROM user")).all()
        
        for user_id, username in users:
            # Erstelle einfachen Hash für "admin123"
            password = "admin123"
            correct_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # Aktualisiere den Hash
            session.exec(text("UPDATE user SET hashed_password = :hash WHERE id = :user_id"), 
                       {"hash": correct_hash, "user_id": user_id})
            
            print(f"Passwort für {username} korrigiert")
        
        session.commit()
        print("Alle Passwörter korrigiert!")

if __name__ == "__main__":
    fix_passwords()
