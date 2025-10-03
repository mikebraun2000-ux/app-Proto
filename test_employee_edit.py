#!/usr/bin/env python3
"""
Script zum Testen der Mitarbeiter-Bearbeiten-Funktion.
"""

import requests
import json

def test_employee_edit():
    """Testet die Mitarbeiter-Bearbeiten-Funktion."""
    print("Teste Mitarbeiter-Bearbeiten-Funktion...")
    
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
        
        # 2. Mitarbeiter abrufen
        print("2. Mitarbeiter abrufen...")
        employees_response = requests.get('http://localhost:8000/employees/', headers=headers)
        
        if employees_response.status_code != 200:
            print(f"Mitarbeiter abrufen fehlgeschlagen: {employees_response.status_code}")
            return False
            
        employees = employees_response.json()
        print(f"{len(employees)} Mitarbeiter gefunden")
        
        if not employees:
            print("Keine Mitarbeiter zum Testen verfügbar")
            return False
            
        # 3. Ersten Mitarbeiter bearbeiten
        first_employee = employees[0]
        print(f"3. Teste Bearbeitung von Mitarbeiter {first_employee['id']}...")
        
        # Mitarbeiter-Daten für Update
        update_data = {
            'full_name': f"{first_employee.get('full_name', 'Test Mitarbeiter')} (Bearbeitet)",
            'email': first_employee.get('email', 'test@example.com'),
            'phone': first_employee.get('phone', '123456789'),
            'position': first_employee.get('position', 'Mitarbeiter'),
            'hourly_rate': first_employee.get('hourly_rate', 25.0),
            'is_active': True
        }
        
        # PUT-Request zum Bearbeiten
        update_response = requests.put(f'http://localhost:8000/employees/{first_employee["id"]}', 
                                     headers=headers, 
                                     json=update_data)
        
        if update_response.status_code == 200:
            print("Mitarbeiter erfolgreich bearbeitet")
            
            # 4. Überprüfen ob Änderung gespeichert wurde
            updated_employees = requests.get('http://localhost:8000/employees/', headers=headers).json()
            updated_employee = next((e for e in updated_employees if e['id'] == first_employee['id']), None)
            
            if updated_employee and "(Bearbeitet)" in updated_employee.get('full_name', ''):
                print("Änderung wurde korrekt gespeichert")
                return True
            else:
                print("Änderung wurde nicht gespeichert")
                print(f"Original: {first_employee.get('full_name', 'N/A')}")
                print(f"Updated: {updated_employee.get('full_name', 'N/A') if updated_employee else 'N/A'}")
                return False
        else:
            print(f"Mitarbeiter-Bearbeitung fehlgeschlagen: {update_response.status_code}")
            print(f"Response: {update_response.text}")
            return False
            
    except Exception as e:
        print(f"Fehler beim Testen: {e}")
        return False

if __name__ == "__main__":
    success = test_employee_edit()
    print(f"\n{'TEST ERFOLGREICH' if success else 'TEST FEHLGESCHLAGEN'}")
