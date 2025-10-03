"""
Systematische Analyse der Bau-Dokumentations-App.
Identifiziert alle Probleme und erstellt einen Reparaturplan.
"""

import sqlite3
import requests
import json
from datetime import datetime

def analyze_database():
    """Analysiert die Datenbankstruktur und -inhalte."""
    print("=== DATENBANK-ANALYSE ===")
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    try:
        # Tabellen auflisten
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tabellen: {tables}")
        
        # User-Tabelle analysieren
        if 'user' in tables:
            cursor.execute("SELECT COUNT(*) FROM user")
            user_count = cursor.fetchone()[0]
            print(f"Benutzer: {user_count}")
            
            cursor.execute("SELECT username, role, is_active FROM user")
            users = cursor.fetchall()
            print("Benutzer-Details:")
            for user in users:
                print(f"  - {user[0]} ({user[1]}) - Aktiv: {user[2]}")
        
        # Projekte analysieren
        if 'project' in tables:
            cursor.execute("SELECT COUNT(*) FROM project")
            project_count = cursor.fetchone()[0]
            print(f"Projekte: {project_count}")
        
        # Rechnungen analysieren
        if 'invoice' in tables:
            cursor.execute("SELECT COUNT(*) FROM invoice")
            invoice_count = cursor.fetchone()[0]
            print(f"Rechnungen: {invoice_count}")
            
    except Exception as e:
        print(f"Datenbank-Fehler: {e}")
    finally:
        conn.close()

def test_api_endpoints():
    """Testet alle wichtigen API-Endpoints."""
    print("\n=== API-ENDPOINT-TESTS ===")
    
    base_url = "http://localhost:8000"
    
    # 1. Health Check
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"Health Check: {response.status_code}")
    except Exception as e:
        print(f"Health Check FEHLER: {e}")
        return False
    
    # 2. Login testen
    try:
        login_data = {"username": "admin", "password": "admin123"}
        response = requests.post(f"{base_url}/auth/login", json=login_data, timeout=5)
        print(f"Login: {response.status_code}")
        
        if response.status_code == 200:
            token = response.json().get("access_token")
            print(f"Token erhalten: {token[:20]}...")
            return token
        else:
            print(f"Login-Fehler: {response.text}")
            return None
    except Exception as e:
        print(f"Login FEHLER: {e}")
        return None

def test_authenticated_endpoints(token):
    """Testet authentifizierte Endpoints."""
    print("\n=== AUTHENTIFIZIERTE ENDPOINT-TESTS ===")
    
    base_url = "http://localhost:8000"
    headers = {"Authorization": f"Bearer {token}"}
    
    endpoints = [
        "/projects/",
        "/employees/", 
        "/reports/",
        "/offers/",
        "/time-entries/",
        "/invoices/",
        "/invoice-generation/methods"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", headers=headers, timeout=5)
            print(f"{endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"  -> {len(data)} Einträge")
                elif isinstance(data, dict):
                    print(f"  -> {list(data.keys())}")
        except Exception as e:
            print(f"{endpoint} FEHLER: {e}")

def analyze_frontend():
    """Analysiert das Frontend."""
    print("\n=== FRONTEND-ANALYSE ===")
    
    base_url = "http://localhost:8000"
    
    # HTML-Seite testen
    try:
        response = requests.get(f"{base_url}/app", timeout=5)
        print(f"Frontend HTML: {response.status_code}")
        
        if response.status_code == 200:
            html_content = response.text
            if 'invoiceProjectSelect' in html_content:
                print("  -> invoiceProjectSelect gefunden")
            if 'autoInvoiceModal' in html_content:
                print("  -> autoInvoiceModal gefunden")
    except Exception as e:
        print(f"Frontend HTML FEHLER: {e}")
    
    # JavaScript testen
    try:
        response = requests.get(f"{base_url}/static/app_simple.js", timeout=5)
        print(f"JavaScript: {response.status_code}")
        
        if response.status_code == 200:
            js_content = response.text
            if 'showAutoInvoiceModal' in js_content:
                print("  -> showAutoInvoiceModal gefunden")
            if 'loadProjectsForInvoiceGeneration' in js_content:
                print("  -> loadProjectsForInvoiceGeneration gefunden")
    except Exception as e:
        print(f"JavaScript FEHLER: {e}")

def main():
    """Hauptfunktion für systematische Analyse."""
    print("SYSTEMATISCHE ANALYSE DER BAU-DOKUMENTATIONS-APP")
    print("=" * 50)
    
    # 1. Datenbank analysieren
    analyze_database()
    
    # 2. API testen
    token = test_api_endpoints()
    
    # 3. Authentifizierte Endpoints testen
    if token:
        test_authenticated_endpoints(token)
    
    # 4. Frontend analysieren
    analyze_frontend()
    
    print("\n=== ZUSAMMENFASSUNG ===")
    print("Analyse abgeschlossen. Prüfen Sie die Ergebnisse oben.")

if __name__ == "__main__":
    main()

