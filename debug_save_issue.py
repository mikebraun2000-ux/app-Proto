#!/usr/bin/env python3
"""
Debugging-Tool für Speicher-Probleme in der Bau-Dokumentations-App.
Simuliert Frontend-Aktionen und identifiziert das genaue Problem.
"""

import requests
import json
import time
from datetime import datetime

# API Base URL
API_BASE = "http://localhost:8000"

def log_section(title):
    """Formatierte Ausgabe für Sektionen."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def log_step(step, description):
    """Formatierte Ausgabe für Schritte."""
    print(f"\n[SCHRITT {step}] {description}")
    print("-" * 50)

def get_auth_token():
    """Holt einen gültigen Auth-Token."""
    try:
        response = requests.post(f"{API_BASE}/auth/login", json={
            "username": "admin",
            "password": "admin123"
        })
        if response.status_code == 200:
            token_data = response.json()
            print(f"OK Login erfolgreich")
            print(f"  Token-Typ: {token_data.get('token_type', 'N/A')}")
            return token_data.get("access_token")
        else:
            print(f"FEHLER Login fehlgeschlagen: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print(f"FEHLER Login-Exception: {e}")
        return None

def test_api_endpoints(token):
    """Testet alle relevanten API-Endpunkte."""
    log_step(1, "API-Endpunkte testen")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    endpoints = [
        ("GET", "/health", "Health Check"),
        ("GET", "/auth/me", "Benutzerdaten"),
        ("GET", "/projects", "Projekte abrufen"),
        ("GET", "/employees", "Mitarbeiter abrufen"),
        ("GET", "/reports", "Berichte abrufen"),
        ("GET", "/offers", "Angebote abrufen")
    ]
    
    all_ok = True
    for method, endpoint, description in endpoints:
        try:
            response = requests.request(method, f"{API_BASE}{endpoint}", headers=headers)
            if response.status_code == 200:
                print(f"OK {description}: OK")
            else:
                print(f"FEHLER {description}: FEHLER {response.status_code}")
                print(f"  Error: {response.text[:200]}...")
                all_ok = False
        except Exception as e:
            print(f"FEHLER {description}: EXCEPTION - {e}")
            all_ok = False
    
    return all_ok

def test_project_creation_detailed(token):
    """Detaillierter Test der Projekterstellung."""
    log_step(2, "Projekt-Erstellung detailliert testen")
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Test 1: Minimale Daten (nur Name)
    print("\nTest 1: Minimale Projekt-Daten")
    project_data = {"name": "Debug Test Minimal"}
    
    print(f"Sende Daten: {json.dumps(project_data, indent=2)}")
    
    try:
        response = requests.post(f"{API_BASE}/projects", json=project_data, headers=headers)
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"OK Projekt erstellt mit ID: {result.get('id')}")
            return result.get('id')
        else:
            print(f"FEHLER Projekt-Erstellung fehlgeschlagen")
            return None
    except Exception as e:
        print(f"FEHLER Exception bei Projekt-Erstellung: {e}")
        return None

def test_frontend_like_data(token):
    """Testet Daten wie sie das Frontend senden würde."""
    log_step(3, "Frontend-ähnliche Daten testen")
    
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    # Simuliere Frontend FormData
    frontend_data = {
        "name": "Frontend Debug Projekt",
        "description": "Ein Projekt aus dem Frontend Debug",
        "client_name": "Debug Kunde",
        "project_type": "trockenbau",
        "status": "aktiv"
    }
    
    print(f"Frontend-ähnliche Daten: {json.dumps(frontend_data, indent=2)}")
    
    try:
        response = requests.post(f"{API_BASE}/projects", json=frontend_data, headers=headers)
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("OK Frontend-ähnliche Daten erfolgreich")
            return True
        else:
            print("FEHLER Frontend-ähnliche Daten fehlgeschlagen")
            return False
    except Exception as e:
        print(f"FEHLER Exception: {e}")
        return False

def test_browser_simulation(token):
    """Simuliert exakt was ein Browser senden würde."""
    log_step(4, "Browser-Simulation")
    
    # Simuliere Browser-Headers
    browser_headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    browser_data = {
        "name": "Browser Test Projekt",
        "description": "Test aus Browser-Simulation",
        "client_name": "Browser Test Kunde",
        "project_type": "sanierung",
        "status": "pausiert"
    }
    
    print(f"Browser Headers: {json.dumps(browser_headers, indent=2)}")
    print(f"Browser Daten: {json.dumps(browser_data, indent=2)}")
    
    try:
        response = requests.post(f"{API_BASE}/projects", 
                               json=browser_data, 
                               headers=browser_headers)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("OK Browser-Simulation erfolgreich")
            return True
        else:
            print("FEHLER Browser-Simulation fehlgeschlagen")
            return False
    except Exception as e:
        print(f"FEHLER Exception: {e}")
        return False

def test_cors_and_options(token):
    """Testet CORS und OPTIONS-Requests."""
    log_step(5, "CORS und OPTIONS testen")
    
    # Test OPTIONS request
    try:
        response = requests.options(f"{API_BASE}/projects")
        print(f"OPTIONS Response Status: {response.status_code}")
        print(f"CORS Headers: {dict(response.headers)}")
        
        if response.status_code in [200, 204]:
            print("OK OPTIONS Request erfolgreich")
        else:
            print("FEHLER OPTIONS Request fehlgeschlagen")
            
    except Exception as e:
        print(f"FEHLER OPTIONS Exception: {e}")

def debug_server_logs():
    """Versucht Server-Logs zu analysieren."""
    log_step(6, "Server-Status prüfen")
    
    try:
        # Test ob Server überhaupt läuft
        response = requests.get(f"{API_BASE}/")
        print(f"Root Endpoint Status: {response.status_code}")
        
        if response.status_code == 200:
            print("OK Server läuft und antwortet")
        else:
            print("FEHLER Server-Problem")
            
    except Exception as e:
        print(f"FEHLER Server nicht erreichbar: {e}")

def check_database_state(token):
    """Prüft den Zustand der Datenbank."""
    log_step(7, "Datenbank-Zustand prüfen")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE}/projects", headers=headers)
        if response.status_code == 200:
            projects = response.json()
            print(f"OK Aktuelle Projekte in DB: {len(projects)}")
            
            if projects:
                print("Letztes Projekt:")
                last_project = projects[-1]
                print(f"  ID: {last_project.get('id')}")
                print(f"  Name: {last_project.get('name')}")
                print(f"  Erstellt: {last_project.get('created_at')}")
            
            return True
        else:
            print(f"FEHLER Fehler beim DB-Zugriff: {response.status_code}")
            return False
    except Exception as e:
        print(f"FEHLER DB-Exception: {e}")
        return False

def main():
    """Hauptfunktion für alle Debug-Tests."""
    log_section("SPEICHER-PROBLEM DEBUGGING")
    print("Identifiziert systematisch warum das Speichern nicht funktioniert...")
    
    # 1. Authentifizierung
    log_step(0, "Authentifizierung")
    token = get_auth_token()
    if not token:
        print("\n❌ STOP: Kein gültiges Token erhalten!")
        return
    
    # 2. API-Endpunkte testen
    endpoints_ok = test_api_endpoints(token)
    
    # 3. Datenbank-Zustand prüfen
    db_ok = check_database_state(token)
    
    # 4. CORS testen
    test_cors_and_options(token)
    
    # 5. Server-Status
    debug_server_logs()
    
    # 6. Projekt-Erstellung testen
    project_id = test_project_creation_detailed(token)
    
    # 7. Frontend-ähnliche Daten testen
    frontend_ok = test_frontend_like_data(token)
    
    # 8. Browser-Simulation
    browser_ok = test_browser_simulation(token)
    
    # Finale Diagnose
    log_section("DIAGNOSE ERGEBNIS")
    
    if endpoints_ok and db_ok and project_id and frontend_ok and browser_ok:
        print("OK ALLE BACKEND-TESTS ERFOLGREICH!")
        print("\nDas Problem liegt wahrscheinlich im FRONTEND:")
        print("  - JavaScript-Fehler in der Browser-Konsole?")
        print("  - Event-Listener nicht korrekt registriert?")
        print("  - FormData wird nicht korrekt gesendet?")
        print("  - Token wird nicht mitgesendet?")
        print("\nNÄCHSTE SCHRITTE:")
        print("  1. Öffnen Sie die Browser-Entwicklertools (F12)")
        print("  2. Gehen Sie zum 'Console' Tab")
        print("  3. Versuchen Sie ein Projekt zu speichern")
        print("  4. Schauen Sie nach JavaScript-Fehlern")
        print("  5. Prüfen Sie den 'Network' Tab für HTTP-Requests")
    else:
        print("❌ BACKEND-PROBLEME GEFUNDEN!")
        print(f"  - API-Endpunkte OK: {endpoints_ok}")
        print(f"  - Datenbank OK: {db_ok}")
        print(f"  - Projekt-Erstellung OK: {bool(project_id)}")
        print(f"  - Frontend-Daten OK: {frontend_ok}")
        print(f"  - Browser-Simulation OK: {browser_ok}")

if __name__ == "__main__":
    main()
