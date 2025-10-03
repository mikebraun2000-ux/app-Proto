#!/usr/bin/env python3
"""
Start-Script für die Bau-Dokumentations-App.
Startet den FastAPI-Server mit allen notwendigen Einstellungen.
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Prüft die Python-Version."""
    if sys.version_info < (3, 8):
        print("❌ FEHLER: Python 3.8 oder höher erforderlich!")
        print(f"   Aktuelle Version: {sys.version}")
        return False
    return True

def check_dependencies():
    """Prüft ob alle erforderlichen Pakete installiert sind."""
    required_packages = ['uvicorn', 'fastapi', 'sqlmodel', 'sqlalchemy', 'pydantic']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"⚠️  Fehlende Pakete: {', '.join(missing_packages)}")
        print("   Installiere Abhängigkeiten...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            print("✅ Abhängigkeiten erfolgreich installiert!")
        except subprocess.CalledProcessError:
            print("❌ FEHLER: Konnte Abhängigkeiten nicht installieren!")
            return False
    
    return True

def start_server():
    """Startet den FastAPI-Server."""
    print("\n" + "="*50)
    print("   BAU-DOKUMENTATIONS-APP")
    print("="*50)
    print()
    print("Die App ist verfügbar unter:")
    print("   http://localhost:8000/app")
    print()
    print("Login-Daten:")
    print("   Benutzername: admin")
    print("   Passwort: admin123")
    print()
    print("Funktionen:")
    print("   Projekte verwalten")
    print("   Mitarbeiter verwalten")
    print("   Berichte erstellen")
    print("   Angebote erstellen")
    print("   Stundenerfassung")
    print()
    print("Zum Stoppen drücken Sie Ctrl+C")
    print("="*50)
    print()
    
    try:
        # Starte den Server
        subprocess.run([
            sys.executable, '-m', 'uvicorn', 
            'app.main:app', 
            '--reload', 
            '--host', '0.0.0.0', 
            '--port', '8000'
        ])
    except KeyboardInterrupt:
        print("\n\n✅ Server wurde erfolgreich beendet.")
    except Exception as e:
        print(f"\n❌ FEHLER beim Starten des Servers: {e}")
        return False
    
    return True

def fix_user_passwords():
    """Repariert die Benutzer-Passwörter beim Start."""
    print("Prüfe und repariere Benutzer-Passwörter...")
    
    try:
        # Füge den App-Pfad hinzu
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from sqlmodel import create_engine, Session, text
        
        engine = create_engine("sqlite:///database.db")
        
        # Verwende SHA256 Hash für "admin123"
        import hashlib
        password = "admin123"
        prepared_hash = "sha256:" + hashlib.sha256(password.encode()).hexdigest()
        
        with Session(engine) as session:
            # Hole alle Benutzer
            users = session.exec(text("SELECT id, username FROM user")).all()
            
            for user_id, username in users:
                # Aktualisiere den Hash für alle Benutzer
                session.exec(text("UPDATE user SET hashed_password = :hash WHERE id = :user_id").bindparams(hash=prepared_hash, user_id=user_id))
                print(f"   Passwort für {username} repariert")
            
            session.commit()
            print("Alle Benutzer-Passwörter repariert!")
            
    except Exception as e:
        print(f"Warnung: Konnte Passworter nicht reparieren: {e}")
        print("   Die App funktioniert möglicherweise trotzdem.")

def main():
    """Hauptfunktion."""
    print("Starte Bau-Dokumentations-App...")
    
    # 1. Python-Version prüfen
    if not check_python_version():
        input("Drücken Sie Enter zum Beenden...")
        return
    
    # 2. Abhängigkeiten prüfen
    if not check_dependencies():
        input("Drücken Sie Enter zum Beenden...")
        return
    
    # 3. Server starten
    start_server()

if __name__ == "__main__":
    main()