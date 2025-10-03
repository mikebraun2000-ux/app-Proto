#!/usr/bin/env python3
"""
Erstellt frische Testdaten für die Bau-Dokumentations-App.
Löscht alle bestehenden Daten und erstellt neue, realistische Testdaten.
"""

import os
import sys
from datetime import datetime, timedelta
import random

# Füge den App-Pfad hinzu
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_session
from app.models import SQLModel
from sqlmodel import create_engine
from app.models import User, Project, Employee, Report, Offer, TimeEntry, Invoice
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import text

def clear_database():
    """Löscht alle Daten aus der Datenbank."""
    print("Lösche alle bestehenden Daten...")
    
    # Erstelle neue Engine
    engine = create_engine("sqlite:///database.db")
    
    # Lösche alle Tabellen
    with Session(engine) as session:
        # Lösche alle Daten in der richtigen Reihenfolge (wegen Foreign Keys)
        try:
            session.exec(text("DELETE FROM time_entries"))
        except:
            pass
        try:
            session.exec(text("DELETE FROM invoices"))
        except:
            pass
        try:
            session.exec(text("DELETE FROM offers"))
        except:
            pass
        try:
            session.exec(text("DELETE FROM reports"))
        except:
            pass
        try:
            session.exec(text("DELETE FROM project_images"))
        except:
            pass
        try:
            session.exec(text("DELETE FROM material_usage"))
        except:
            pass
        try:
            session.exec(text("DELETE FROM projects"))
        except:
            pass
        try:
            session.exec(text("DELETE FROM employees"))
        except:
            pass
        try:
            session.exec(text("DELETE FROM users"))
        except:
            pass
        session.commit()
    
    print("Datenbank geleert")

def create_users():
    """Erstellt Benutzer."""
    print("Erstelle Benutzer...")
    
    users_data = [
        {
            "username": "admin",
            "email": "admin@bau-doku.de",
            "full_name": "Max Mustermann",
            "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/4.8.8.8",  # admin123
            "role": "admin",
            "is_active": True
        },
        {
            "username": "buchhalter",
            "email": "buchhaltung@bau-doku.de", 
            "full_name": "Anna Schmidt",
            "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/4.8.8.8",  # admin123
            "role": "buchhalter",
            "is_active": True
        },
        {
            "username": "mitarbeiter1",
            "email": "hans.mueller@bau-doku.de",
            "full_name": "Hans Müller",
            "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/4.8.8.8",  # admin123
            "role": "mitarbeiter",
            "is_active": True
        },
        {
            "username": "mitarbeiter2",
            "email": "petra.weber@bau-doku.de",
            "full_name": "Petra Weber",
            "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/4.8.8.8",  # admin123
            "role": "mitarbeiter",
            "is_active": True
        }
    ]
    
    session = next(get_session())
    try:
        for user_data in users_data:
            user = User(**user_data)
            session.add(user)
        session.commit()
        print("Benutzer erstellt")
    finally:
        session.close()

def create_employees():
    """Erstellt Mitarbeiter."""
    print("Erstelle Mitarbeiter...")
    
    employees_data = [
        {
            "name": "Hans Müller",
            "position": "Bauleiter",
            "email": "hans.mueller@bau-doku.de",
            "phone": "+49 123 456789",
            "hourly_rate": 45.0,
            "hire_date": datetime(2023, 1, 15).date(),
            "is_active": True
        },
        {
            "name": "Petra Weber", 
            "position": "Architektin",
            "email": "petra.weber@bau-doku.de",
            "phone": "+49 123 456790",
            "hourly_rate": 55.0,
            "hire_date": datetime(2022, 6, 1).date(),
            "is_active": True
        },
        {
            "name": "Klaus Schmidt",
            "position": "Maurer",
            "email": "klaus.schmidt@bau-doku.de", 
            "phone": "+49 123 456791",
            "hourly_rate": 35.0,
            "hire_date": datetime(2023, 3, 10).date(),
            "is_active": True
        },
        {
            "name": "Maria Fischer",
            "position": "Elektrikerin",
            "email": "maria.fischer@bau-doku.de",
            "phone": "+49 123 456792", 
            "hourly_rate": 42.0,
            "hire_date": datetime(2022, 9, 15).date(),
            "is_active": True
        },
        {
            "name": "Thomas Wagner",
            "position": "Zimmermann",
            "email": "thomas.wagner@bau-doku.de",
            "phone": "+49 123 456793",
            "hourly_rate": 38.0,
            "hire_date": datetime(2023, 2, 20).date(),
            "is_active": True
        }
    ]
    
    session = next(get_session())
    try:
        for emp_data in employees_data:
            employee = Employee(**emp_data)
            session.add(employee)
        session.commit()
        print("Mitarbeiter erstellt")
    finally:
        session.close()

def create_projects():
    """Erstellt Projekte."""
    print("Erstelle Projekte...")
    
    projects_data = [
        {
            "name": "Einfamilienhaus Musterstraße",
            "description": "Neubau eines modernen Einfamilienhauses mit 120qm Wohnfläche",
            "client_name": "Familie Mustermann",
            "client_address": "Musterstraße 1, 12345 Musterstadt",
            "start_date": datetime(2024, 1, 15).date(),
            "end_date": datetime(2024, 8, 30).date(),
            "budget": 350000.0,
            "status": "in_progress"
        },
        {
            "name": "Bürogebäude Zentrum",
            "description": "Sanierung und Umbau eines historischen Bürogebäudes",
            "client_name": "Immobilien AG",
            "client_address": "Hauptstraße 15, 12345 Musterstadt",
            "start_date": datetime(2024, 2, 1).date(),
            "end_date": datetime(2024, 12, 31).date(),
            "budget": 850000.0,
            "status": "in_progress"
        },
        {
            "name": "Wohnanlage Gartenviertel",
            "description": "Bau von 8 Reihenhäusern mit Garten",
            "client_name": "Bauverein Gartenviertel",
            "client_address": "Gartenstraße 1-8, 12345 Musterstadt",
            "start_date": datetime(2023, 9, 1).date(),
            "end_date": datetime(2024, 6, 30).date(),
            "budget": 1200000.0,
            "status": "completed"
        },
        {
            "name": "Kita Neubau",
            "description": "Neubau einer Kindertagesstätte für 60 Kinder",
            "client_name": "Stadt Musterstadt",
            "client_address": "Schulstraße 5, 12345 Musterstadt",
            "start_date": datetime(2024, 3, 1).date(),
            "end_date": datetime(2024, 10, 31).date(),
            "budget": 450000.0,
            "status": "in_progress"
        },
        {
            "name": "Villa am See",
            "description": "Luxusvilla mit Seeblick und Pool",
            "client_name": "Dr. Schmidt",
            "client_address": "Seestraße 42, 12345 Musterstadt",
            "start_date": datetime(2024, 4, 1).date(),
            "end_date": datetime(2025, 2, 28).date(),
            "budget": 1800000.0,
            "status": "in_progress"
        }
    ]
    
    session = next(get_session())
    try:
        for proj_data in projects_data:
            project = Project(**proj_data)
            session.add(project)
        session.commit()
        print("Projekte erstellt")
    finally:
        session.close()

def create_reports():
    """Erstellt Berichte."""
    print("Erstelle Berichte...")
    
    session = next(get_session())
    try:
        # Hole alle Projekte
        projects = session.exec(text("SELECT id FROM projects")).all()
        
        if not projects:
            print("Keine Projekte gefunden!")
            return
        
        for i in range(15):  # 15 Berichte
            project_id = random.choice(projects)[0]
            report_date = datetime.now() - timedelta(days=random.randint(1, 90))
            
            report = Report(
                project_id=project_id,
                title=f"Fortschrittsbericht {i+1}",
                content=f"Dies ist der Fortschrittsbericht Nr. {i+1}. Alle Arbeiten verlaufen planmaessig.",
                report_date=report_date.date(),
                weather="Sonnig",
                temperature=random.randint(5, 25),
                created_at=report_date,
                updated_at=report_date
            )
            session.add(report)
        
        session.commit()
        print("Berichte erstellt")
    finally:
        session.close()

def create_offers():
    """Erstellt Angebote."""
    print("Erstelle Angebote...")
    
    session = next(get_session())
    try:
        # Hole alle Projekte
        projects = session.exec(text("SELECT id FROM projects")).all()
        
        if not projects:
            print("Keine Projekte gefunden!")
            return
        
        for i in range(8):  # 8 Angebote
            project_id = random.choice(projects)[0]
            offer_date = datetime.now() - timedelta(days=random.randint(1, 60))
            valid_until = offer_date + timedelta(days=30)
            
            offer = Offer(
                project_id=project_id,
                title=f"Angebot {i+1}",
                client_name=f"Kunde {i+1}",
                client_address=f"Musterstrasse {i+1}, 12345 Musterstadt",
                total_amount=random.randint(50000, 500000),
                currency="EUR",
                offer_date=offer_date,
                valid_until=valid_until,
                items='[{"description": "Maurerarbeiten", "quantity": 100, "unit_price": 45.0}, {"description": "Elektroarbeiten", "quantity": 50, "unit_price": 65.0}]',
                status=random.choice(["entwurf", "versendet", "angenommen"]),
                created_at=offer_date,
                updated_at=offer_date
            )
            session.add(offer)
        
        session.commit()
        print("Angebote erstellt")
    finally:
        session.close()

def create_time_entries():
    """Erstellt Stundeneinträge."""
    print("Erstelle Stundeneintraege...")
    
    with get_session() as session:
        # Hole alle Projekte und Mitarbeiter
        projects = session.exec(text("SELECT id FROM projects")).all()
        employees = session.exec(text("SELECT id FROM employees")).all()
        
        if not projects or not employees:
            print("❌ Keine Projekte oder Mitarbeiter gefunden!")
            return
        
        for i in range(50):  # 50 Stundeneinträge
            project_id = random.choice(projects)[0]
            employee_id = random.choice(employees)[0]
            work_date = datetime.now() - timedelta(days=random.randint(1, 60))
            
            # Zufällige Arbeitszeiten
            clock_in_hour = random.randint(7, 9)
            clock_in_minute = random.randint(0, 59)
            clock_out_hour = clock_in_hour + random.randint(6, 10)
            clock_out_minute = random.randint(0, 59)
            
            clock_in = f"{clock_in_hour:02d}:{clock_in_minute:02d}"
            clock_out = f"{clock_out_hour:02d}:{clock_out_minute:02d}"
            hours_worked = clock_out_hour - clock_in_hour + (clock_out_minute - clock_in_minute) / 60.0
            
            time_entry = TimeEntry(
                project_id=project_id,
                employee_id=employee_id,
                work_date=work_date.date(),
                clock_in=clock_in,
                clock_out=clock_out,
                hours_worked=round(hours_worked, 2),
                description=f"Arbeitstag {i+1} - {random.choice(['Maurerarbeiten', 'Elektroarbeiten', 'Zimmerarbeiten', 'Sanitärarbeiten'])}",
                hourly_rate=random.randint(30, 60),
                total_cost=round(hours_worked * random.randint(30, 60), 2),
                created_at=work_date,
                updated_at=work_date
            )
            session.add(time_entry)
        
        session.commit()
    
    print("Stundeneintraege erstellt")

def create_invoices():
    """Erstellt Rechnungen."""
    print("Erstelle Rechnungen...")
    
    with get_session() as session:
        # Hole alle Projekte
        projects = session.exec(text("SELECT id FROM projects")).all()
        
        if not projects:
            print("❌ Keine Projekte gefunden!")
            return
        
        for i in range(12):  # 12 Rechnungen
            project_id = random.choice(projects)[0]
            invoice_date = datetime.now() - timedelta(days=random.randint(1, 30))
            due_date = invoice_date + timedelta(days=14)
            
            invoice = Invoice(
                project_id=project_id,
                invoice_number=f"R-2024-{i+1:03d}",
                title=f"Rechnung {i+1}",
                description=f"Rechnung für erbrachte Leistungen",
                client_name=f"Kunde {i+1}",
                client_address=f"Musterstraße {i+1}, 12345 Musterstadt",
                total_amount=random.randint(10000, 100000),
                currency="EUR",
                invoice_date=invoice_date,
                due_date=due_date,
                items='[{"description": "Maurerarbeiten", "quantity": 50, "unit_price": 45.0}, {"description": "Material", "quantity": 1, "unit_price": 5000.0}]',
                status=random.choice(["entwurf", "versendet", "bezahlt"]),
                created_at=invoice_date,
                updated_at=invoice_date
            )
            session.add(invoice)
        
        session.commit()
    
    print("Rechnungen erstellt")

def main():
    """Hauptfunktion - erstellt alle Testdaten."""
    print("Erstelle frische Testdaten fuer die Bau-Dokumentations-App...")
    print("=" * 60)
    
    try:
        # Erstelle neue Datenbank mit neuem Namen
        db_name = "database_fresh.db"
        if os.path.exists(db_name):
            os.remove(db_name)
            print("Alte frische Datenbank geloescht")
        
        # Erstelle neue Tabellen
        engine = create_engine(f"sqlite:///{db_name}")
        SQLModel.metadata.create_all(engine)
        print("Neue Datenbank erstellt")
        
        # Erstelle neue Daten
        create_users()
        create_employees()
        create_projects()
        create_reports()
        create_offers()
        create_time_entries()
        create_invoices()
        
        print("=" * 60)
        print("Alle Testdaten erfolgreich erstellt!")
        print()
        print("ZUSAMMENFASSUNG:")
        print("   4 Benutzer (admin, buchhalter, 2 mitarbeiter)")
        print("   5 Mitarbeiter")
        print("   5 Projekte")
        print("   15 Berichte")
        print("   8 Angebote")
        print("   50 Stundeneintraege")
        print("   12 Rechnungen")
        print()
        print("LOGIN-DATEN:")
        print("   Benutzername: admin")
        print("   Passwort: admin123")
        print()
        print("Die App ist bereit fuer Tests!")
        
    except Exception as e:
        print(f"Fehler beim Erstellen der Testdaten: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
