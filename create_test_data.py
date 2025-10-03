#!/usr/bin/env python3
"""
Testdaten-Generator für die Bau-Dokumentations-App.
Erstellt realistische Testdaten für alle Module.
"""

from app.database import get_session
from app.models import User, Project, Employee, Report, Offer, TimeEntry
from app.auth import get_password_hash
from datetime import datetime, date, timedelta
import json
from sqlmodel import select

def create_test_data():
    """Erstellt umfassende Testdaten für die App."""
    session = next(get_session())
    
    print("Erstelle Testdaten...")
    
    # 1. Benutzer erstellen
    print("Erstelle Benutzer...")
    users_data = [
        {
            "username": "admin",
            "email": "admin@bau-dokumentation.de",
            "password": "admin123",
            "full_name": "Administrator",
            "role": "admin"
        },
        {
            "username": "buchhalter",
            "email": "buchhalter@bau-dokumentation.de", 
            "password": "buchhalter123",
            "full_name": "Maria Schmidt",
            "role": "buchhalter"
        },
        {
            "username": "mitarbeiter1",
            "email": "max.mustermann@bau-dokumentation.de",
            "password": "mitarbeiter123",
            "full_name": "Max Mustermann",
            "role": "mitarbeiter"
        },
        {
            "username": "mitarbeiter2",
            "email": "anna.mueller@bau-dokumentation.de",
            "password": "mitarbeiter123", 
            "full_name": "Anna Müller",
            "role": "mitarbeiter"
        }
    ]
    
    for user_data in users_data:
        try:
            # Prüfen ob Benutzer bereits existiert
            existing_user = session.exec(select(User).where(User.username == user_data["username"])).first()
            if existing_user:
                print(f"Benutzer {user_data['username']} existiert bereits")
                continue
                
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                full_name=user_data["full_name"],
                role=user_data["role"],
                is_active=True
            )
            session.add(user)
        except Exception as e:
            print(f"Fehler beim Erstellen von Benutzer {user_data['username']}: {e}")
    
    session.commit()
    print("Benutzer erstellt")
    
    # 2. Projekte erstellen
    print("Erstelle Projekte...")
    projects_data = [
        {
            "name": "Bürogebäude Renovierung",
            "description": "Komplette Renovierung eines 3-stöckigen Bürogebäudes",
            "client_name": "Musterfirma GmbH",
            "project_type": "renovierung",
            "status": "aktiv"
        },
        {
            "name": "Wohnhaus Neubau",
            "description": "Einfamilienhaus mit Keller und Dachgeschoss",
            "client_name": "Familie Schmidt",
            "project_type": "neubau", 
            "status": "aktiv"
        },
        {
            "name": "Kita Sanierung",
            "description": "Sanierung der Kindertagesstätte inkl. Brandschutz",
            "client_name": "Stadt Musterstadt",
            "project_type": "sanierung",
            "status": "in_progress"
        },
        {
            "name": "Restaurant Umbau",
            "description": "Umbau eines Restaurants mit neuer Küche",
            "client_name": "Restaurant Goldener Löwe",
            "project_type": "renovierung",
            "status": "planned"
        },
        {
            "name": "Wohnung Trockenbau",
            "description": "Trockenbauarbeiten in 4-Zimmer-Wohnung",
            "client_name": "Privatperson",
            "project_type": "trockenbau",
            "status": "aktiv"
        }
    ]
    
    projects = []
    for project_data in projects_data:
        project = Project(**project_data)
        session.add(project)
        projects.append(project)
    
    session.commit()
    print("Projekte erstellt")
    
    # 3. Mitarbeiter erstellen
    print("Erstelle Mitarbeiter...")
    employees_data = [
        {
            "full_name": "Max Mustermann",
            "position": "Trockenbauer",
            "hourly_rate": 25.50,
            "phone": "0123456789",
            "email": "max.mustermann@bau-dokumentation.de"
        },
        {
            "full_name": "Anna Müller", 
            "position": "Geselle",
            "hourly_rate": 22.00,
            "phone": "0987654321",
            "email": "anna.mueller@bau-dokumentation.de"
        },
        {
            "full_name": "Peter Schmidt",
            "position": "Meister",
            "hourly_rate": 30.00,
            "phone": "0555123456",
            "email": "peter.schmidt@bau-dokumentation.de"
        },
        {
            "full_name": "Lisa Weber",
            "position": "Auszubildende",
            "hourly_rate": 15.00,
            "phone": "0555987654",
            "email": "lisa.weber@bau-dokumentation.de"
        }
    ]
    
    employees = []
    for employee_data in employees_data:
        employee = Employee(**employee_data)
        session.add(employee)
        employees.append(employee)
    
    session.commit()
    print("Mitarbeiter erstellt")
    
    # 4. Berichte erstellen
    print("Erstelle Berichte...")
    reports_data = [
        {
            "project_id": projects[0].id,
            "title": "Wöchentlicher Fortschrittsbericht",
            "content": "Alle geplanten Arbeiten wurden termingerecht abgeschlossen. Keine Probleme aufgetreten.",
            "report_date": datetime.now() - timedelta(days=1)
        },
        {
            "project_id": projects[1].id,
            "title": "Fundamentarbeiten abgeschlossen",
            "content": "Das Fundament wurde erfolgreich gegossen. Qualitätskontrolle bestanden.",
            "report_date": datetime.now() - timedelta(days=3)
        },
        {
            "project_id": projects[2].id,
            "title": "Brandschutzmaßnahmen",
            "content": "Alle Brandschutzmaßnahmen wurden nach Vorschrift umgesetzt.",
            "report_date": datetime.now() - timedelta(days=5)
        },
        {
            "project_id": projects[0].id,
            "title": "Materiallieferung erhalten",
            "content": "Alle bestellten Materialien sind eingetroffen und wurden geprüft.",
            "report_date": datetime.now() - timedelta(days=7)
        }
    ]
    
    for report_data in reports_data:
        report = Report(**report_data)
        session.add(report)
    
    session.commit()
    print("Berichte erstellt")
    
    # 5. Angebote erstellen
    print("Erstelle Angebote...")
    offers_data = [
        {
            "project_id": projects[0].id,
            "title": "Renovierungsangebot Bürogebäude",
            "description": "Komplette Renovierung inkl. Trockenbau, Malerarbeiten und Elektrik",
            "client_name": "Musterfirma GmbH",
            "client_address": "Musterstraße 1, 12345 Musterstadt",
            "total_amount": 45000.00,
            "currency": "EUR",
            "valid_until": datetime.now() + timedelta(days=30),
            "items": json.dumps([
                {
                    "description": "Trockenbauarbeiten",
                    "quantity": 1,
                    "unit": "Auftrag",
                    "unit_price": 25000.00,
                    "total_price": 25000.00,
                    "tax_rate": 19
                },
                {
                    "description": "Malerarbeiten",
                    "quantity": 1,
                    "unit": "Auftrag", 
                    "unit_price": 15000.00,
                    "total_price": 15000.00,
                    "tax_rate": 19
                }
            ]),
            "status": "entwurf"
        },
        {
            "project_id": projects[1].id,
            "title": "Neubau Einfamilienhaus",
            "description": "Kompletter Neubau eines Einfamilienhauses",
            "client_name": "Familie Schmidt",
            "client_address": "Hauptstraße 15, 54321 Musterdorf",
            "total_amount": 180000.00,
            "currency": "EUR",
            "valid_until": datetime.now() + timedelta(days=45),
            "items": json.dumps([
                {
                    "description": "Rohbauarbeiten",
                    "quantity": 1,
                    "unit": "Auftrag",
                    "unit_price": 120000.00,
                    "total_price": 120000.00,
                    "tax_rate": 19
                },
                {
                    "description": "Innenausbau",
                    "quantity": 1,
                    "unit": "Auftrag",
                    "unit_price": 60000.00,
                    "total_price": 60000.00,
                    "tax_rate": 19
                }
            ]),
            "status": "versendet"
        }
    ]
    
    for offer_data in offers_data:
        offer = Offer(**offer_data)
        session.add(offer)
    
    session.commit()
    print("Angebote erstellt")
    
    # 6. Stundeneinträge erstellen
    print("Erstelle Stundeneinträge...")
    time_entries_data = [
        {
            "project_id": projects[0].id,
            "employee_id": employees[0].id,
                   "work_date": date.today() - timedelta(days=1),
            "clock_in": "08:00",
            "clock_out": "16:30",
            "total_break_minutes": 30,
            "hours_worked": 8.0,
            "description": "Trockenbauarbeiten im 2. Obergeschoss",
            "hourly_rate": employees[0].hourly_rate,
            "total_cost": 8.0 * employees[0].hourly_rate
        },
        {
            "project_id": projects[0].id,
            "employee_id": employees[1].id,
                   "work_date": date.today() - timedelta(days=1),
            "clock_in": "07:30",
            "clock_out": "15:30",
            "total_break_minutes": 30,
            "hours_worked": 7.5,
            "description": "Vorbereitungsarbeiten für Trockenbau",
            "hourly_rate": employees[1].hourly_rate,
            "total_cost": 7.5 * employees[1].hourly_rate
        },
        {
            "project_id": projects[1].id,
            "employee_id": employees[2].id,
                   "work_date": date.today() - timedelta(days=2),
            "clock_in": "08:00",
            "clock_out": "17:00",
            "total_break_minutes": 45,
            "hours_worked": 8.25,
            "description": "Fundamentarbeiten und Betonarbeiten",
            "hourly_rate": employees[2].hourly_rate,
            "total_cost": 8.25 * employees[2].hourly_rate
        },
        {
            "project_id": projects[2].id,
            "employee_id": employees[0].id,
                   "work_date": date.today() - timedelta(days=3),
            "clock_in": "09:00",
            "clock_out": "16:00",
            "total_break_minutes": 30,
            "hours_worked": 6.5,
            "description": "Brandschutzmaßnahmen in der Kita",
            "hourly_rate": employees[0].hourly_rate,
            "total_cost": 6.5 * employees[0].hourly_rate
        }
    ]
    
    for time_entry_data in time_entries_data:
        time_entry = TimeEntry(**time_entry_data)
        session.add(time_entry)
    
    session.commit()
    print("Stundeneinträge erstellt")
    
    print("\nTestdaten erfolgreich erstellt!")
    print(f"Statistiken:")
    print(f"   Benutzer: {len(users_data)}")
    print(f"   Projekte: {len(projects_data)}")
    print(f"   Mitarbeiter: {len(employees_data)}")
    print(f"   Berichte: {len(reports_data)}")
    print(f"   Angebote: {len(offers_data)}")
    print(f"   Stundeneinträge: {len(time_entries_data)}")
    print("\nDie App ist bereit für den produktiven Einsatz!")

if __name__ == "__main__":
    create_test_data()
