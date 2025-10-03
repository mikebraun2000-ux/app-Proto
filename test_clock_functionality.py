#!/usr/bin/env python3
"""
Test der Clock-Funktionalität
"""
import requests
import json
from datetime import datetime, timedelta

def test_clock_functionality():
    print("=== CLOCK-FUNKTIONALITÄT TEST ===")
    
    # Login
    login = requests.post('http://localhost:8000/auth/login', 
                         json={'username': 'admin', 'password': 'admin123'})
    
    if login.status_code != 200:
        print("FEHLER Login fehlgeschlagen:", login.status_code)
        return False
    
    token = login.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    print("OK Login erfolgreich")
    
    # Teste Time-Entries API
    print("\n--- Time-Entries API Test ---")
    
    # Aktuelle Stundeneinträge abrufen
    response = requests.get('http://localhost:8000/time-entries/', headers=headers)
    if response.status_code == 200:
        current_entries = response.json()
        print(f"OK Aktuelle Stundeneinträge: {len(current_entries)}")
    else:
        print(f"FEHLER Time-Entries GET: {response.status_code}")
        return False
    
    # Teste Stundeneintrag-Erstellung
    print("\n--- Stundeneintrag-Erstellung Test ---")
    
    # Testdaten für Stundeneintrag
    now = datetime.now()
    start_time = now - timedelta(hours=1)  # 1 Stunde vorher
    
    time_entry_data = {
        "project_id": 1,  # Erstes Projekt
        "employee_id": 1,  # Erster Mitarbeiter
        "work_date": now.strftime('%Y-%m-%d'),
        "clock_in": start_time.strftime('%H:%M'),
        "clock_out": now.strftime('%H:%M'),
        "total_break_minutes": 0,
        "hours_worked": 1.0,
        "description": "Test Stundeneintrag - Clock-Funktionalität"
    }
    
    print(f"Erstelle Test-Stundeneintrag: {time_entry_data['description']}")
    
    # Stundeneintrag erstellen
    create_response = requests.post('http://localhost:8000/time-entries/', 
                                   headers=headers, 
                                   json=time_entry_data)
    
    if create_response.status_code == 200:
        new_entry = create_response.json()
        print(f"OK Stundeneintrag erstellt: ID {new_entry.get('id', 'unbekannt')}")
        
        # Prüfe ob Eintrag in der Liste erscheint
        response_after = requests.get('http://localhost:8000/time-entries/', headers=headers)
        if response_after.status_code == 200:
            entries_after = response_after.json()
            print(f"OK Stundeneinträge nach Erstellung: {len(entries_after)}")
            
            if len(entries_after) > len(current_entries):
                print("OK Stundeneintrag erfolgreich hinzugefügt!")
                return True
            else:
                print("WARNUNG: Stundeneintrag wurde nicht in der Liste gefunden")
                return False
        else:
            print(f"FEHLER Time-Entries GET nach Erstellung: {response_after.status_code}")
            return False
    else:
        print(f"FEHLER Stundeneintrag-Erstellung: {create_response.status_code}")
        print(f"Response: {create_response.text}")
        return False

if __name__ == "__main__":
    test_clock_functionality()

