#!/usr/bin/env python3
"""
Erstellt einen bcrypt-Hash.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from passlib.context import CryptContext

def create_bcrypt_hash():
    """Erstellt einen bcrypt-Hash."""
    print("Erstelle bcrypt-Hash...")
    
    # Verwende bcrypt wie in der App
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    password = "admin123"
    
    # Erstelle Hash
    hashed = pwd_context.hash(password)
    
    print(f"Passwort: {password}")
    print(f"Hash: {hashed}")
    
    # Teste den Hash
    test_result = pwd_context.verify(password, hashed)
    print(f"Test erfolgreich: {test_result}")
    
    return hashed

if __name__ == "__main__":
    hash_result = create_bcrypt_hash()
    if hash_result:
        print(f"\nBcrypt-Hash: {hash_result}")

