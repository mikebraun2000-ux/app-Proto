#!/usr/bin/env python3
"""
Erstellt einen Hash mit der korrekten Konfiguration.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from passlib.context import CryptContext

def create_correct_hash():
    """Erstellt einen Hash mit der korrekten Konfiguration."""
    print("Erstelle Hash mit korrekter pbkdf2_sha256 Konfiguration...")
    
    # Verwende die exakt gleiche Konfiguration wie in der App
    pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
    
    password = "admin123"
    
    # Erstelle Hash mit der korrekten Konfiguration
    hashed = pwd_context.hash(password)
    
    print(f"Passwort: {password}")
    print(f"Hash: {hashed}")
    
    # Teste den Hash
    test_result = pwd_context.verify(password, hashed)
    print(f"Test erfolgreich: {test_result}")
    
    return hashed

if __name__ == "__main__":
    hash_result = create_correct_hash()
    if hash_result:
        print(f"\nKorrekter Hash: {hash_result}")

