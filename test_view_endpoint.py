#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

def test_view_endpoint():
    print("=== Test: /view Endpoint ===")
    base_url = "http://localhost:8000"
    image_id_to_test = 1 # Annahme: Bild mit ID 1 existiert

    view_url = f"{base_url}/reports/images/{image_id_to_test}/view"
    print(f"\nTeste Bild ID {image_id_to_test}: {view_url}")

    try:
        response = requests.get(view_url)
        print(f"  Status: {response.status_code}")
        print(f"  Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"  Content-Length: {len(response.content)}")

        if response.status_code == 200 and response.headers.get('Content-Type', '').startswith('image/'):
            print(f"  + Bild {image_id_to_test} erfolgreich geladen!")
        else:
            print(f"  - Bild {image_id_to_test} konnte nicht geladen werden oder ist kein Bild.")
            print(f"  Response-Text (erste 200 Zeichen): {response.text[:200]}")

    except requests.exceptions.ConnectionError:
        print("  - Fehler: Verbindung zum Server konnte nicht hergestellt werden. Ist der Server gestartet?")
    except Exception as e:
        print(f"  - Ein unerwarteter Fehler ist aufgetreten: {e}")

if __name__ == "__main__":
    test_view_endpoint()


