#!/usr/bin/env python3
"""
Aktualisiert die Datenbank mit dem korrekten Hash.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import create_engine, Session, text

def update_with_correct_hash():
    """Aktualisiert die Datenbank mit dem korrekten Hash."""
    print("Aktualisiere Datenbank mit korrektem Hash...")
    
    engine = create_engine("sqlite:///database.db")
    
    # Der korrekte Hash für "admin123"
    correct_hash = "$pbkdf2-sha256$29000$jrHWGoOwFoJQKsUYw5izVg$hsWxpeozE5TcSenXq9ycBmyWbTDKAZlgoe.hKeuave4"
    
    with Session(engine) as session:
        # Hole alle Benutzer
        users = session.exec(text("SELECT id, username FROM user")).all()
        
        for user_id, username in users:
            # Aktualisiere den Hash
            session.exec(text("UPDATE user SET hashed_password = :hash WHERE id = :user_id").bindparams(hash=correct_hash, user_id=user_id))
            
            print(f"Hash für {username} aktualisiert")
        
        session.commit()
        print()
        print("🎉 ALLE PASSWORT-HASHES ERFOLGREICH AKTUALISIERT!")
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
    update_with_correct_hash()

