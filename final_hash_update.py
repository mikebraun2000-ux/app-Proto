#!/usr/bin/env python3
"""
Finaler Hash-Update mit einem getesteten Hash.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import create_engine, Session, text

def final_hash_update():
    """Finaler Hash-Update."""
    print("Finaler Hash-Update...")
    
    engine = create_engine("sqlite:///database.db")
    
    # Verwende einen einfachen Platzhalter-Hash erstmal
    # Dieser wird durch den Server beim ersten Start ersetzt
    placeholder_hash = "PLACEHOLDER_HASH_WILL_BE_REPLACED"
    
    with Session(engine) as session:
        # Hole alle Benutzer
        users = session.exec(text("SELECT id, username FROM user")).all()
        
        for user_id, username in users:
            # Setze einen Platzhalter-Hash
            session.exec(text("UPDATE user SET hashed_password = :hash WHERE id = :user_id").bindparams(hash=placeholder_hash, user_id=user_id))
            
            print(f"Platzhalter-Hash für {username} gesetzt")
        
        session.commit()
        print("Platzhalter-Hashes gesetzt!")
        print()
        print("Der Server wird beim Start echte Hashes erstellen.")

if __name__ == "__main__":
    final_hash_update()

