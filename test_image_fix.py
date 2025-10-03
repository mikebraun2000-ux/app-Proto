#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import os

def test_image_fix():
    print("=== Test: Bild-Anzeige-Fix ===")

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
    
    # 2. Berichte abrufen
    print("\n2. Berichte abrufen...")
    response = requests.get(f"{base_url}/reports/", headers=headers)
    if response.status_code == 200:
        reports = response.json()
        print(f"+ {len(reports)} Berichte gefunden")
        
        # Ersten Bericht mit Bildern finden
        report_with_images = None
        for report in reports:
            images_response = requests.get(f"{base_url}/reports/{report['id']}/images", headers=headers)
            if images_response.status_code == 200:
                images = images_response.json()
                if len(images) > 0:
                    report_with_images = report
                    print(f"+ Bericht {report['id']} hat {len(images)} Bilder")
                    break
        
        if not report_with_images:
            print("- Kein Bericht mit Bildern gefunden")
            return
            
        # 3. Bilder des Berichts abrufen
        print(f"\n3. Bilder für Bericht {report_with_images['id']} abrufen...")
        response = requests.get(f"{base_url}/reports/{report_with_images['id']}/images", headers=headers)
        if response.status_code == 200:
            images = response.json()
            print(f"+ {len(images)} Bilder gefunden")
            
            # 4. Teste den neuen /view Endpoint
            print("\n4. Teste /view Endpoint...")
            for image in images:
                view_url = f"{base_url}/reports/images/{image['id']}/view"
                print(f"Teste: {view_url}")
                
                # Test ohne Authorization Header (wie im Browser)
                view_response = requests.get(view_url)
                if view_response.status_code == 200:
                    print(f"+ Bild {image['id']} über /view Endpoint erfolgreich geladen")
                    print(f"  Content-Type: {view_response.headers.get('content-type', 'N/A')}")
                    print(f"  Content-Length: {len(view_response.content)} bytes")
                else:
                    print(f"- Bild {image['id']} über /view Endpoint fehlgeschlagen: {view_response.status_code}")
                
                # Teste auch den /download Endpoint (sollte weiterhin funktionieren)
                download_url = f"{base_url}/reports/images/{image['id']}/download"
                download_response = requests.get(download_url, headers=headers)
                if download_response.status_code == 200:
                    print(f"+ Bild {image['id']} über /download Endpoint erfolgreich geladen")
                else:
                    print(f"- Bild {image['id']} über /download Endpoint fehlgeschlagen: {download_response.status_code}")
                
                break  # Nur das erste Bild testen
        else:
            print(f"- Bilder konnten nicht abgerufen werden: {response.status_code}")
    else:
        print(f"- Berichte konnten nicht abgerufen werden: {response.status_code}")

if __name__ == "__main__":
    test_image_fix()


