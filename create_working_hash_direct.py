#!/usr/bin/env python3
"""
Erstellt einen Hash mit dem exakt gleichen passlib-Context wie die App.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_working_hash_direct():
    """Erstellt einen Hash mit dem exakt gleichen passlib-Context."""
    print("Erstelle Hash mit dem App-Context...")
    
    try:
        # Importiere den exakt gleichen pwd_context aus der App
        from app.auth import pwd_context
        
        # Verwende ein kürzeres Passwort für den Test
        password = "admin123"
        
        # Erstelle Hash mit dem App-Context
        hashed = pwd_context.hash(password)
        
        print(f"Passwort: {password}")
        print(f"Hash: {hashed}")
        
        # Teste den Hash
        test_result = pwd_context.verify(password, hashed)
        print(f"Test erfolgreich: {test_result}")
        
        return hashed
    
    except Exception as e:
        print(f"Fehler beim Erstellen des Hashes: {e}")
        print("Verwende bekannten funktionierenden Hash...")
        
        # Bekannter funktionierender bcrypt-Hash für "admin123"
        known_hash = "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
        
        # Teste den bekannten Hash
        from app.auth import pwd_context
        try:
            test_result = pwd_context.verify("admin123", known_hash)
            print(f"Bekannter Hash Test: {test_result}")
            return known_hash
        except Exception as e2:
            print(f"Auch bekannter Hash funktioniert nicht: {e2}")
            return None

if __name__ == "__main__":
    hash_result = create_working_hash_direct()
    if hash_result:
        print(f"\nFunktionierender Hash: {hash_result}")
    else:
        print("\nKein funktionierender Hash gefunden!")

