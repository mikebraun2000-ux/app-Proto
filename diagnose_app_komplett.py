"""
Kompletter App-Diagnose-Test
Testet alle wichtigen Backend-Funktionen systematisch
"""

import requests
import json
import sys
from datetime import datetime

API_BASE = "http://localhost:8000"
TEST_USER = "admin"
TEST_PASSWORD = "admin123"

# Farben für Terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_section(title):
    print(f"\n{BLUE}{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}{RESET}\n")

def print_test(name, success, details=""):
    status = f"{GREEN}[OK]{RESET}" if success else f"{RED}[FEHLER]{RESET}"
    print(f"{status} {name}")
    if details and not success:
        print(f"   {YELLOW}-> {details}{RESET}")
    elif details and success:
        print(f"   -> {details}")

def test_login():
    print_section("1. Login & Authentifizierung")
    
    try:
        # Test 1: Erfolgreicher Login
        response = requests.post(f"{API_BASE}/auth/login", 
            json={"username": TEST_USER, "password": TEST_PASSWORD}
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print_test("Login erfolgreich", True, f"Token: {token[:20]}...")
            return token
        else:
            print_test("Login erfolgreich", False, f"Status {response.status_code}")
            return None
            
    except Exception as e:
        print_test("Login erfolgreich", False, str(e))
        return None

def test_auth_me(token):
    try:
        response = requests.get(f"{API_BASE}/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        
        if response.status_code == 200:
            user = response.json()
            print_test("Benutzer-Info abrufen", True, f"User: {user.get('username', 'Unknown')}")
            return user
        else:
            print_test("Benutzer-Info abrufen", False, f"Status {response.status_code}")
            return None
    except Exception as e:
        print_test("Benutzer-Info abrufen", False, str(e))
        return None

def test_projects(token):
    print_section("2. Projekte")
    
    try:
        # Liste abrufen
        response = requests.get(f"{API_BASE}/projects/", headers={
            "Authorization": f"Bearer {token}"
        })
        
        if response.status_code == 200:
            projects = response.json()
            print_test("Projektliste laden", True, f"{len(projects)} Projekte gefunden")
        else:
            print_test("Projektliste laden", False, f"Status {response.status_code}")
            
    except Exception as e:
        print_test("Projektliste laden", False, str(e))

def test_reports(token):
    print_section("3. Berichte")
    
    try:
        response = requests.get(f"{API_BASE}/reports/", headers={
            "Authorization": f"Bearer {token}"
        })
        
        if response.status_code == 200:
            reports = response.json()
            print_test("Berichtsliste laden", True, f"{len(reports)} Berichte gefunden")
        else:
            print_test("Berichtsliste laden", False, f"Status {response.status_code}")
            
    except Exception as e:
        print_test("Berichtsliste laden", False, str(e))

def test_offers(token):
    print_section("4. Angebote")
    
    try:
        response = requests.get(f"{API_BASE}/offers/", headers={
            "Authorization": f"Bearer {token}"
        })
        
        if response.status_code == 200:
            offers = response.json()
            print_test("Angebotsliste laden", True, f"{len(offers)} Angebote gefunden")
        else:
            print_test("Angebotsliste laden", False, f"Status {response.status_code}")
            
    except Exception as e:
        print_test("Angebotsliste laden", False, str(e))

def test_invoices(token):
    print_section("5. Rechnungen")
    
    try:
        response = requests.get(f"{API_BASE}/invoices/", headers={
            "Authorization": f"Bearer {token}"
        })
        
        if response.status_code == 200:
            invoices = response.json()
            print_test("Rechnungsliste laden", True, f"{len(invoices)} Rechnungen gefunden")
        else:
            print_test("Rechnungsliste laden", False, f"Status {response.status_code}")
            
    except Exception as e:
        print_test("Rechnungsliste laden", False, str(e))

def test_time_entries(token):
    print_section("6. Zeiterfassung")
    
    try:
        response = requests.get(f"{API_BASE}/time-entries/", headers={
            "Authorization": f"Bearer {token}"
        })
        
        if response.status_code == 200:
            entries = response.json()
            print_test("Zeiteinträge laden", True, f"{len(entries)} Einträge gefunden")
        else:
            print_test("Zeiteinträge laden", False, f"Status {response.status_code}")
            
    except Exception as e:
        print_test("Zeiteinträge laden", False, str(e))

def test_employees(token):
    print_section("7. Mitarbeiter")
    
    try:
        response = requests.get(f"{API_BASE}/employees/", headers={
            "Authorization": f"Bearer {token}"
        })
        
        if response.status_code == 200:
            employees = response.json()
            print_test("Mitarbeiterliste laden", True, f"{len(employees)} Mitarbeiter gefunden")
        else:
            print_test("Mitarbeiterliste laden", False, f"Status {response.status_code}")
            
    except Exception as e:
        print_test("Mitarbeiterliste laden", False, str(e))

def test_tenant_settings(token):
    print_section("8. Firmen-Stammdaten")
    
    try:
        response = requests.get(f"{API_BASE}/auth/tenant/settings", headers={
            "Authorization": f"Bearer {token}"
        })
        
        if response.status_code == 200:
            settings = response.json()
            print_test("Stammdaten laden", True, f"Company: {settings.get('company_name', 'N/A')}")
        else:
            print_test("Stammdaten laden", False, f"Status {response.status_code}")
            
    except Exception as e:
        print_test("Stammdaten laden", False, str(e))

def test_invitations(token):
    print_section("9. Einladungen")
    
    try:
        response = requests.get(f"{API_BASE}/auth/invitations", headers={
            "Authorization": f"Bearer {token}"
        })
        
        if response.status_code == 200:
            invitations = response.json()
            print_test("Einladungsliste laden", True, f"{len(invitations)} Einladungen gefunden")
        else:
            print_test("Einladungsliste laden", False, f"Status {response.status_code}")
            
    except Exception as e:
        print_test("Einladungsliste laden", False, str(e))

def test_billing(token):
    print_section("10. Abonnement & Billing")
    
    try:
        response = requests.get(f"{API_BASE}/billing/status", headers={
            "Authorization": f"Bearer {token}"
        })
        
        if response.status_code == 200:
            billing = response.json()
            status = billing.get('subscription_status', 'unknown')
            print_test("Billing-Status laden", True, f"Status: {status}")
        else:
            print_test("Billing-Status laden", False, f"Status {response.status_code}")
            
    except Exception as e:
        print_test("Billing-Status laden", False, str(e))

def main():
    print(f"\n{BLUE}{'='*60}")
    print("  KOMPLETTER APP-TEST")
    print(f"{'='*60}{RESET}")
    print(f"Server: {API_BASE}")
    print(f"User: {TEST_USER}")
    print(f"Start: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Login
    token = test_login()
    if not token:
        print(f"\n{RED}ABBRUCH: Login fehlgeschlagen{RESET}\n")
        sys.exit(1)
    
    # Benutzer-Info
    user = test_auth_me(token)
    
    # Alle anderen Tests
    test_projects(token)
    test_reports(token)
    test_offers(token)
    test_invoices(token)
    test_time_entries(token)
    test_employees(token)
    test_tenant_settings(token)
    test_invitations(token)
    test_billing(token)
    
    print(f"\n{BLUE}{'='*60}")
    print("  ALLE TESTS ABGESCHLOSSEN")
    print(f"{'='*60}{RESET}")
    print(f"Ende: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

if __name__ == "__main__":
    main()
