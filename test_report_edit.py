#!/usr/bin/env python3
"""
Test für Berichte-Bearbeiten-Funktion
"""

import requests
import json

def test_report_edit():
    """Testet die Berichte-Bearbeiten-Funktion."""
    print("Teste Berichte-Bearbeiten-Funktion...")
    
    try:
        # 1. Login
        print("1. Login...")
        login_response = requests.post('http://localhost:8000/auth/login', 
                                      json={'username': 'admin', 'password': 'admin123'})
        
        if login_response.status_code != 200:
            print(f"Login fehlgeschlagen: {login_response.status_code}")
            return False
            
        token = login_response.json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        print("Login erfolgreich")
        
        # 2. Berichte abrufen
        print("2. Berichte abrufen...")
        reports_response = requests.get('http://localhost:8000/reports/', headers=headers)
        
        if reports_response.status_code != 200:
            print(f"Berichte abrufen fehlgeschlagen: {reports_response.status_code}")
            return False
            
        reports = reports_response.json()
        print(f"{len(reports)} Berichte gefunden")
        
        if not reports:
            print("Keine Berichte zum Testen verfügbar")
            return False
            
        # 3. Ersten Bericht bearbeiten
        first_report = reports[0]
        print(f"3. Teste Bearbeitung von Bericht {first_report['id']}...")
        
        # Bericht-Daten für Update
        update_data = {
            'title': f"{first_report['title']} (Bearbeitet)",
            'project_id': first_report['project_id']
        }
        
        # PUT-Request zum Bearbeiten
        update_response = requests.put(f'http://localhost:8000/reports/{first_report["id"]}', 
                                     headers=headers, 
                                     json=update_data)
        
        if update_response.status_code == 200:
            print("Bericht erfolgreich bearbeitet")
            
            # 4. Überprüfen ob Änderung gespeichert wurde
            updated_reports = requests.get('http://localhost:8000/reports/', headers=headers).json()
            updated_report = next((r for r in updated_reports if r['id'] == first_report['id']), None)
            
            if updated_report and "(Bearbeitet)" in updated_report['title']:
                print("Änderung wurde korrekt gespeichert")
                return True
            else:
                print("Änderung wurde nicht gespeichert")
                return False
        else:
            print(f"Bericht-Bearbeitung fehlgeschlagen: {update_response.status_code}")
            print(f"Response: {update_response.text}")
            return False
            
    except Exception as e:
        print(f"Fehler beim Testen: {e}")
        return False

if __name__ == "__main__":
    success = test_report_edit()
    print(f"\n{'TEST ERFOLGREICH' if success else 'TEST FEHLGESCHLAGEN'}")
