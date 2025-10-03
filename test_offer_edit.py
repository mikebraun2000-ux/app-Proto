#!/usr/bin/env python3
"""
Test-Script für die Angebote-Bearbeiten-Funktion.
"""

import requests
import json

def test_offer_edit():
    """Testet die Angebote-Bearbeiten-Funktion."""
    print("Teste Angebote-Bearbeiten-Funktion...")
    
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
        
        # 2. Angebote abrufen
        print("2. Angebote abrufen...")
        offers_response = requests.get('http://localhost:8000/offers/', headers=headers)
        
        if offers_response.status_code != 200:
            print(f"Angebote abrufen fehlgeschlagen: {offers_response.status_code}")
            return False
            
        offers = offers_response.json()
        print(f"{len(offers)} Angebote gefunden")
        
        if not offers:
            print("Keine Angebote zum Testen verfügbar")
            return False
            
        # 3. Erstes Angebot bearbeiten
        first_offer = offers[0]
        print(f"3. Teste Bearbeitung von Angebot {first_offer['id']}...")
        
        # Angebot-Daten für Update
        update_data = {
            'title': f"{first_offer['title']} (Bearbeitet)",
            'description': f"{first_offer.get('description', '')} - Aktualisiert",
            'client_name': first_offer.get('client_name', 'Test Kunde'),
            'total_amount': first_offer.get('total_amount', 1000.0)
        }
        
        # PUT-Request zum Bearbeiten
        update_response = requests.put(f'http://localhost:8000/offers/{first_offer["id"]}', 
                                     headers=headers, 
                                     json=update_data)
        
        if update_response.status_code == 200:
            print("Angebot erfolgreich bearbeitet")
            
            # 4. Überprüfen ob Änderung gespeichert wurde
            updated_offers = requests.get('http://localhost:8000/offers/', headers=headers).json()
            updated_offer = next((o for o in updated_offers if o['id'] == first_offer['id']), None)
            
            if updated_offer and "(Bearbeitet)" in updated_offer['title']:
                print("Änderung wurde korrekt gespeichert")
                return True
            else:
                print("Änderung wurde nicht gespeichert")
                return False
        else:
            print(f"Angebot-Bearbeitung fehlgeschlagen: {update_response.status_code}")
            print(f"Response: {update_response.text}")
            return False
            
    except Exception as e:
        print(f"Fehler beim Testen: {e}")
        return False

if __name__ == "__main__":
    success = test_offer_edit()
    print(f"\n{'TEST ERFOLGREICH' if success else 'TEST FEHLGESCHLAGEN'}")
