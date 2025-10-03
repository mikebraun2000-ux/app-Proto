#!/usr/bin/env python3
"""
Erstellt einen definitiv funktionierenden bcrypt-Hash.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from passlib.context import CryptContext

def create_working_hash():
    """Erstellt einen definitiv funktionierenden bcrypt-Hash."""
    print("Erstelle funktionierenden bcrypt-Hash...")
    
    # Verwende den gleichen pwd_context wie in der App
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    # Erstelle einen neuen Hash für "admin123"
    password = "admin123"
    hashed = pwd_context.hash(password)
    
    print(f"Passwort: {password}")
    print(f"Hash: {hashed}")
    
    # Teste den Hash
    test_result = pwd_context.verify(password, hashed)
    print(f"Test erfolgreich: {test_result}")
    
    return hashed

if __name__ == "__main__":
    create_working_hash()

