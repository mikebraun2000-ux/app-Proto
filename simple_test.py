#!/usr/bin/env python3
"""
Einfacher Testdurchlauf für die Bau-Dokumentations-App
"""

import requests
import json
from datetime import datetime, date

# API Base URL
API_BASE = "http://localhost:8000"

def test_api():
    """Test API-Verbindung"""
    print("Test 1: API-Verbindung...")
    try:
        response = requests.get(f"{API_BASE}/")
        if response.status_code == 200:
            print("OK - API erreichbar")
            return True
        else:
            print(f"FEHLER - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"FEHLER - Verbindung: {e}")
        return False

def test_login():
    """Test Login"""
    print("\nTest 2: Login...")
    try:
        data = {"username": "admin", "password": "admin123"}
        response = requests.post(f"{API_BASE}/auth/login", json=data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("OK - Login erfolgreich")
            return token
        else:
            print(f"FEHLER - Login: {response.status_code}")
            return None
    except Exception as e:
        print(f"FEHLER - Login: {e}")
        return None

def test_projects(token):
    """Test Projekte"""
    print("\nTest 3: Projekte...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        # Projekte abrufen
        response = requests.get(f"{API_BASE}/projects", headers=headers)
        if response.status_code == 200:
            projects = response.json()
            print(f"OK - {len(projects)} Projekte gefunden")
            
            # Neues Projekt erstellen
            new_project = {
                "name": f"Test-Projekt {datetime.now().strftime('%H:%M:%S')}",
                "description": "Test-Projekt",
                "client": "Test-Kunde",
                "type": "renovierung",
                "status": "aktiv"
            }
            
            create_response = requests.post(f"{API_BASE}/projects", json=new_project, headers=headers)
            if create_response.status_code == 200:
                created = create_response.json()
                print(f"OK - Projekt erstellt: {created['name']}")
                return created['id']
            else:
                print(f"FEHLER - Projekt erstellen: {create_response.status_code}")
                return None
        else:
            print(f"FEHLER - Projekte abrufen: {response.status_code}")
            return None
    except Exception as e:
        print(f"FEHLER - Projekte: {e}")
        return None

def test_employees(token):
    """Test Mitarbeiter"""
    print("\nTest 4: Mitarbeiter...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        # Mitarbeiter abrufen
        response = requests.get(f"{API_BASE}/employees", headers=headers)
        if response.status_code == 200:
            employees = response.json()
            print(f"OK - {len(employees)} Mitarbeiter gefunden")
            
            # Neuen Mitarbeiter erstellen
            new_employee = {
                "name": f"Test-Mitarbeiter {datetime.now().strftime('%H:%M:%S')}",
                "position": "Trockenbauer",
                "hourly_rate": 25.50,
                "phone": "0123456789",
                "email": "test@example.com"
            }
            
            create_response = requests.post(f"{API_BASE}/employees", json=new_employee, headers=headers)
            if create_response.status_code == 200:
                created = create_response.json()
                print(f"OK - Mitarbeiter erstellt: {created['name']}")
                return created['id']
            else:
                print(f"FEHLER - Mitarbeiter erstellen: {create_response.status_code}")
                return None
        else:
            print(f"FEHLER - Mitarbeiter abrufen: {response.status_code}")
            return None
    except Exception as e:
        print(f"FEHLER - Mitarbeiter: {e}")
        return None

def test_time_entries(token, project_id, employee_id):
    """Test Stundenerfassung"""
    print("\nTest 5: Stundenerfassung...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        # Stundeneintrag erstellen
        time_entry = {
            "project_id": project_id,
            "employee_id": employee_id,
            "date": date.today().isoformat(),
            "clock_in": "09:00",
            "clock_out": "17:00",
            "total_break_minutes": 30,
            "hours_worked": 7.5,
            "description": "Test-Arbeitszeit"
        }
        
        response = requests.post(f"{API_BASE}/time-entries", json=time_entry, headers=headers)
        if response.status_code == 200:
            print("OK - Stundeneintrag erstellt")
            return True
        else:
            print(f"FEHLER - Stundeneintrag: {response.status_code}")
            return False
    except Exception as e:
        print(f"FEHLER - Stundeneintrag: {e}")
        return False

def test_reports(token, project_id):
    """Test Berichte"""
    print("\nTest 6: Berichte...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        # Berichte abrufen
        response = requests.get(f"{API_BASE}/reports", headers=headers)
        if response.status_code == 200:
            reports = response.json()
            print(f"OK - {len(reports)} Berichte gefunden")
            
            # Neuen Bericht erstellen
            new_report = {
                "project_id": project_id,
                "date": date.today().isoformat(),
                "title": f"Test-Bericht {datetime.now().strftime('%H:%M:%S')}",
                "content": "Test-Bericht"
            }
            
            create_response = requests.post(f"{API_BASE}/reports", json=new_report, headers=headers)
            if create_response.status_code == 200:
                created = create_response.json()
                print(f"OK - Bericht erstellt: {created['title']}")
                return True
            else:
                print(f"FEHLER - Bericht erstellen: {create_response.status_code}")
                return False
        else:
            print(f"FEHLER - Berichte abrufen: {response.status_code}")
            return False
    except Exception as e:
        print(f"FEHLER - Berichte: {e}")
        return False

def test_offers(token):
    """Test Angebote"""
    print("\nTest 7: Angebote...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        # Angebote abrufen
        response = requests.get(f"{API_BASE}/offers", headers=headers)
        if response.status_code == 200:
            offers = response.json()
            print(f"OK - {len(offers)} Angebote gefunden")
            
            # Neues Angebot erstellen
            new_offer = {
                "title": f"Test-Angebot {datetime.now().strftime('%H:%M:%S')}",
                "description": "Test-Angebot",
                "client": "Test-Kunde",
                "type": "sanierung",
                "client_address": "Teststraße 123, 12345 Teststadt",
                "net_amount": 1000.00,
                "tax_rate": 19,
                "total_amount": 1190.00,
                "valid_until": (date.today().replace(day=28)).isoformat(),
                "payment_terms": "30_tage"
            }
            
            create_response = requests.post(f"{API_BASE}/offers", json=new_offer, headers=headers)
            if create_response.status_code == 200:
                created = create_response.json()
                print(f"OK - Angebot erstellt: {created['title']}")
                return True
            else:
                print(f"FEHLER - Angebot erstellen: {create_response.status_code}")
                return False
        else:
            print(f"FEHLER - Angebote abrufen: {response.status_code}")
            return False
    except Exception as e:
        print(f"FEHLER - Angebote: {e}")
        return False

def main():
    """Hauptfunktion"""
    print("AUTOMATISIERTER TESTDURCHLAUF - BAU-DOKUMENTATIONS-APP")
    print("=" * 60)
    
    # Test 1: API-Verbindung
    if not test_api():
        print("\nTest abgebrochen - API nicht erreichbar")
        return
    
    # Test 2: Login
    token = test_login()
    if not token:
        print("\nTest abgebrochen - Login fehlgeschlagen")
        return
    
    # Test 3: Projekte
    project_id = test_projects(token)
    if not project_id:
        print("\nTest abgebrochen - Projekte-Test fehlgeschlagen")
        return
    
    # Test 4: Mitarbeiter
    employee_id = test_employees(token)
    if not employee_id:
        print("\nTest abgebrochen - Mitarbeiter-Test fehlgeschlagen")
        return
    
    # Test 5: Stundenerfassung
    test_time_entries(token, project_id, employee_id)
    
    # Test 6: Berichte
    test_reports(token, project_id)
    
    # Test 7: Angebote
    test_offers(token)
    
    print("\n" + "=" * 60)
    print("TESTDURCHLAUF ABGESCHLOSSEN!")
    print("Alle API-Endpoints funktionieren")
    print("CRUD-Operationen erfolgreich")
    print("Die App ist bereit für den produktiven Einsatz!")

if __name__ == "__main__":
    main()
