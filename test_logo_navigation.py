#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_logo_navigation():
    """Teste die Logo-Navigation für Admins."""
    
    base_url = "http://localhost:8000"
    
    print("=== Test: Logo-Navigation für Admins ===")
    
    # 1. Login als Admin
    print("\n1. Login als Admin...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{base_url}/auth/login", json=login_data)
    if response.status_code == 200:
        token_data = response.json()
        token = token_data["access_token"]
        print("+ Login erfolgreich")
        print(f"  Rolle: {token_data.get('role', 'N/A')}")
    else:
        print(f"- Login fehlgeschlagen: {response.status_code}")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Teste Logo-Management-Endpoints
    print("\n2. Teste Logo-Management-Endpoints...")
    
    # Teste Logo-Historie (sollte funktionieren)
    response = requests.get(f"{base_url}/company-logo/history", headers=headers)
    if response.status_code == 200:
        print("+ Logo-Historie-Endpoint funktioniert")
    else:
        print(f"- Logo-Historie-Endpoint fehlgeschlagen: {response.status_code}")
    
    # Teste aktuelles Logo (sollte 404 sein, da kein Logo hochgeladen)
    response = requests.get(f"{base_url}/company-logo/current", headers=headers)
    if response.status_code == 404:
        print("+ Aktuelles Logo-Endpoint funktioniert (kein Logo vorhanden)")
    elif response.status_code == 200:
        print("+ Aktuelles Logo-Endpoint funktioniert (Logo vorhanden)")
    else:
        print(f"- Aktuelles Logo-Endpoint fehlgeschlagen: {response.status_code}")
    
    # 3. Teste als Nicht-Admin (Mitarbeiter)
    print("\n3. Teste als Mitarbeiter...")
    login_data_mitarbeiter = {
        "username": "meister",
        "password": "admin123"
    }
    
    response = requests.post(f"{base_url}/auth/login", json=login_data_mitarbeiter)
    if response.status_code == 200:
        token_data = response.json()
        token_mitarbeiter = token_data["access_token"]
        print("+ Mitarbeiter-Login erfolgreich")
        print(f"  Rolle: {token_data.get('role', 'N/A')}")
        
        headers_mitarbeiter = {"Authorization": f"Bearer {token_mitarbeiter}"}
        
        # Teste Logo-Upload als Mitarbeiter (sollte 403 sein)
        test_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\nIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xdd\x8d\xb4\x1c\x00\x00\x00\x00IEND\xaeB`\x82'
        files = {'file': ('test_logo.png', test_image_data, 'image/png')}
        
        response = requests.post(f"{base_url}/company-logo/upload", files=files, headers=headers_mitarbeiter)
        if response.status_code == 403:
            print("+ Logo-Upload korrekt für Mitarbeiter blockiert (403)")
        else:
            print(f"- Logo-Upload sollte für Mitarbeiter blockiert sein: {response.status_code}")
    else:
        print(f"- Mitarbeiter-Login fehlgeschlagen: {response.status_code}")
    
    print("\n4. Frontend-Test:")
    print("   - Öffne http://localhost:8000/app")
    print("   - Logge dich als Admin ein")
    print("   - Prüfe, ob 'Firmenlogo' in der Navigation sichtbar ist")
    print("   - Klicke auf 'Firmenlogo' und teste die Funktionalität")

if __name__ == "__main__":
    test_logo_navigation()


