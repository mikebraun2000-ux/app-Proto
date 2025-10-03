#!/usr/bin/env python3
"""
Aktualisiert die Datenbank mit dem neuen funktionierenden Hash.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import create_engine, Session, text

def update_with_new_hash():
    """Aktualisiert die Datenbank mit dem neuen Hash."""
    print("Aktualisiere Datenbank mit neuem Hash...")
    
    engine = create_engine("sqlite:///database.db")
    
    # Der neue funktionerende Hash
    new_hash = "$pbkdf2-sha256$29000$IcSYU4qRcs659/7//38PYQ$EDTcy/wEMOLuLPaiGRrxSAjmgZDJWpDEmQPW0o1xe7o"
    
    with Session(engine) as session:
        # Hole alle Benutzer
        users = session.exec(text("SELECT id, username FROM user")).all()
        
        for user_id, username in users:
            # Aktualisiere den Hash
            session.exec(text("UPDATE user SET hashed_password = :hash WHERE id = :user_id").bindparams(hash=new_hash, user_id=user_id))
            
            print(f"Hash für {username} aktualisiert")
        
        session.commit()
        print("Alle Hashes erfolgreich aktualisiert!")

if __name__ == "__main__":
    update_with_new_hash()

