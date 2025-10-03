#!/usr/bin/env python3
"""
Testet den kompletten Login-Flow.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import Session
from app.database import get_session
from app.auth import authenticate_user

def test_login_flow():
    """Testet den kompletten Login-Flow."""
    print("Teste kompletten Login-Flow...")
    
    try:
        session = next(get_session())
        
        # Teste Authentifizierung
        user = authenticate_user(session, "admin", "admin123")
        
        if user:
            print(f"✅ Login erfolgreich: {user.username} ({user.role})")
        else:
            print("❌ Login fehlgeschlagen")
        
        session.close()
        
    except Exception as e:
        print(f"❌ Fehler beim Login-Test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_login_flow()

