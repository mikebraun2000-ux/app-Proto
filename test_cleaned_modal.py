#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_cleaned_modal():
    print("=== Test: Bereinigtes Bericht-Modal ===")

    base_url = "http://localhost:8000"
    admin_credentials = {"username": "admin", "password": "admin123"}

    # 1. Login
    print("\n1. Login...")
    response = requests.post(f"{base_url}/auth/login", json=admin_credentials)
    if response.status_code == 200:
        token_data = response.json()
        token = token_data["access_token"]
        print("+ Login erfolgreich")
    else:
        print(f"- Login fehlgeschlagen: {response.status_code}")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Neuen Bericht ohne Arbeitsart erstellen
    print("\n2. Neuen Bericht ohne Arbeitsart erstellen...")
    new_report_data = {
        "project_id": 1,
        "title": "Test Bericht ohne Arbeitsart",
        "content": "Dieser Bericht sollte keine Arbeitsart haben.",
        "report_date": "2023-10-28",
        "status": "BERICHT" # Standardstatus
    }
    response = requests.post(f"{base_url}/reports/", headers=headers, json=new_report_data)
    if response.status_code == 200:
        report = response.json()
        print(f"+ Bericht erstellt mit ID: {report['id']}")
        print(f"  Titel: {report['title']}")
        print(f"  Status: {report['status']}")
        print(f"  Arbeitsart: {report.get('work_type')}") # Sollte None sein
        new_report_id = report['id']
    else:
        print(f"- Berichtserstellung fehlgeschlagen: {response.status_code} - {response.text}")
        return

    # 3. Bericht aktualisieren (ohne Arbeitsart)
    print("\n3. Bericht aktualisieren...")
    update_data = {
        "title": "Aktualisierter Test Bericht",
        "status": "QUALITAET"
    }
    response = requests.put(f"{base_url}/reports/{new_report_id}", headers=headers, json=update_data)
    if response.status_code == 200:
        updated_report = response.json()
        print(f"+ Bericht aktualisiert")
        print(f"  Neuer Titel: {updated_report['title']}")
        print(f"  Neuer Status: {updated_report['status']}")
    else:
        print(f"- Berichtsaktualisierung fehlgeschlagen: {response.status_code} - {response.text}")
        return

    # 4. Alle Berichte abrufen und prüfen
    print("\n4. Alle Berichte abrufen...")
    response = requests.get(f"{base_url}/reports/", headers=headers)
    if response.status_code == 200:
        reports = response.json()
        print(f"+ {len(reports)} Berichte gefunden")
        for r in reports:
            if r['id'] >= new_report_id - 2: # Nur die letzten Berichte anzeigen
                print(f"  Bericht {r['id']}: '{r['title']}' - Status: {r['status']}")
    else:
        print(f"- Berichte konnten nicht abgerufen werden: {response.status_code} - {response.text}")
        return

if __name__ == "__main__":
    test_cleaned_modal()


