#!/usr/bin/env python3
"""
Teste Hash direkt mit der App-Konfiguration.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from passlib.context import CryptContext

def test_hash_direct():
    """Teste Hash direkt."""
    print("Teste Hash direkt...")
    
    # Verwende die exakt gleiche Konfiguration
    pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
    
    password = "admin123"
    
    # Erstelle neuen Hash
    new_hash = pwd_context.hash(password)
    print(f"Neuer Hash: {new_hash}")
    
    # Teste neuen Hash
    result = pwd_context.verify(password, new_hash)
    print(f"Neuer Hash Test: {result}")
    
    # Teste den alten Hash
    old_hash = "$pbkdf2-sha256$29000$jrHWGoOwFoJQKsUYw5izVg$hsWxpeozE5TcSenXq9ycBmyWbTDKAZlgoe.hKeuave4"
    try:
        result_old = pwd_context.verify(password, old_hash)
        print(f"Alter Hash Test: {result_old}")
    except Exception as e:
        print(f"Alter Hash Fehler: {e}")
    
    return new_hash

if __name__ == "__main__":
    test_hash_direct()

