#!/usr/bin/env python3
"""
Einfaches Script zum Erstellen frischer Testdaten.
"""

import os
import sys
from datetime import datetime, timedelta
import random

# Füge den App-Pfad hinzu
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import create_engine, Session, text
from app.models import SQLModel, User, Project, Employee, Report, Offer, TimeEntry, Invoice

def create_fresh_database():
    """Erstellt eine neue Datenbank mit frischen Testdaten."""
    print("Erstelle frische Testdaten...")
    
    # Lösche alte Datenbank
    db_name = "database_fresh.db"
    if os.path.exists(db_name):
        os.remove(db_name)
        print("Alte Datenbank geloescht")
    
    # Erstelle neue Engine
    engine = create_engine(f"sqlite:///{db_name}")
    SQLModel.metadata.create_all(engine)
    print("Neue Datenbank erstellt")
    
    with Session(engine) as session:
        # Erstelle Benutzer
        print("Erstelle Benutzer...")
        users = [
            User(
                username="admin",
                email="admin@bau-doku.de",
                full_name="Max Mustermann",
                hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/4.8.8.8",
                role="admin",
                is_active=True
            ),
            User(
                username="buchhalter",
                email="buchhaltung@bau-doku.de",
                full_name="Anna Schmidt",
                hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/4.8.8.8",
                role="buchhalter",
                is_active=True
            ),
            User(
                username="mitarbeiter1",
                email="hans.mueller@bau-doku.de",
                full_name="Hans Müller",
                hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/4.8.8.8",
                role="mitarbeiter",
                is_active=True
            )
        ]
        
        for user in users:
            session.add(user)
        session.commit()
        print("Benutzer erstellt")
        
        # Erstelle Mitarbeiter
        print("Erstelle Mitarbeiter...")
        employees = [
            Employee(
                full_name="Hans Müller",
                position="Bauleiter",
                email="hans.mueller@bau-doku.de",
                phone="+49 123 456789",
                hourly_rate=45.0,
                hire_date=datetime(2023, 1, 15).date(),
                is_active=True
            ),
            Employee(
                full_name="Petra Weber",
                position="Architektin",
                email="petra.weber@bau-doku.de",
                phone="+49 123 456790",
                hourly_rate=55.0,
                hire_date=datetime(2022, 6, 1).date(),
                is_active=True
            ),
            Employee(
                full_name="Klaus Schmidt",
                position="Maurer",
                email="klaus.schmidt@bau-doku.de",
                phone="+49 123 456791",
                hourly_rate=35.0,
                hire_date=datetime(2023, 3, 10).date(),
                is_active=True
            )
        ]
        
        for emp in employees:
            session.add(emp)
        session.commit()
        print("Mitarbeiter erstellt")
        
        # Erstelle Projekte
        print("Erstelle Projekte...")
        projects = [
            Project(
                name="Einfamilienhaus Musterstraße",
                description="Neubau eines modernen Einfamilienhauses mit 120qm Wohnfläche",
                client_name="Familie Mustermann",
                client_address="Musterstraße 1, 12345 Musterstadt",
                start_date=datetime(2024, 1, 15).date(),
                end_date=datetime(2024, 8, 30).date(),
                budget=350000.0,
                status="in_progress"
            ),
            Project(
                name="Bürogebäude Zentrum",
                description="Sanierung und Umbau eines historischen Bürogebäudes",
                client_name="Immobilien AG",
                client_address="Hauptstraße 15, 12345 Musterstadt",
                start_date=datetime(2024, 2, 1).date(),
                end_date=datetime(2024, 12, 31).date(),
                budget=850000.0,
                status="in_progress"
            ),
            Project(
                name="Wohnanlage Gartenviertel",
                description="Bau von 8 Reihenhäusern mit Garten",
                client_name="Bauverein Gartenviertel",
                client_address="Gartenstraße 1-8, 12345 Musterstadt",
                start_date=datetime(2023, 9, 1).date(),
                end_date=datetime(2024, 6, 30).date(),
                budget=1200000.0,
                status="completed"
            )
        ]
        
        for proj in projects:
            session.add(proj)
        session.commit()
        print("Projekte erstellt")
        
        # Erstelle Berichte
        print("Erstelle Berichte...")
        for i in range(10):
            project_id = random.randint(1, 3)
            report_date = datetime.now() - timedelta(days=random.randint(1, 30))
            
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
        
        # Erstelle Angebote
        print("Erstelle Angebote...")
        for i in range(5):
            project_id = random.randint(1, 3)
            offer_date = datetime.now() - timedelta(days=random.randint(1, 20))
            valid_until = offer_date + timedelta(days=30)
            
            offer = Offer(
                project_id=project_id,
                title=f"Angebot {i+1}",
                client_name=f"Kunde {i+1}",
                client_address=f"Musterstrasse {i+1}, 12345 Musterstadt",
                total_amount=random.randint(50000, 300000),
                currency="EUR",
                offer_date=offer_date,
                valid_until=valid_until,
                items='[{"description": "Maurerarbeiten", "quantity": 100, "unit_price": 45.0}]',
                status=random.choice(["entwurf", "versendet", "angenommen"]),
                created_at=offer_date,
                updated_at=offer_date
            )
            session.add(offer)
        
        session.commit()
        print("Angebote erstellt")
        
        # Erstelle Stundeneintraege
        print("Erstelle Stundeneintraege...")
        for i in range(20):
            project_id = random.randint(1, 3)
            employee_id = random.randint(1, 3)
            work_date = datetime.now() - timedelta(days=random.randint(1, 30))
            
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
                description=f"Arbeitstag {i+1} - {random.choice(['Maurerarbeiten', 'Elektroarbeiten', 'Zimmerarbeiten'])}",
                hourly_rate=random.randint(30, 60),
                total_cost=round(hours_worked * random.randint(30, 60), 2),
                created_at=work_date,
                updated_at=work_date
            )
            session.add(time_entry)
        
        session.commit()
        print("Stundeneintraege erstellt")
        
        # Erstelle Rechnungen
        print("Erstelle Rechnungen...")
        for i in range(8):
            project_id = random.randint(1, 3)
            invoice_date = datetime.now() - timedelta(days=random.randint(1, 15))
            due_date = invoice_date + timedelta(days=14)
            
            invoice = Invoice(
                project_id=project_id,
                invoice_number=f"R-2024-{i+1:03d}",
                title=f"Rechnung {i+1}",
                description=f"Rechnung für erbrachte Leistungen",
                client_name=f"Kunde {i+1}",
                client_address=f"Musterstrasse {i+1}, 12345 Musterstadt",
                total_amount=random.randint(10000, 100000),
                currency="EUR",
                invoice_date=invoice_date,
                due_date=due_date,
                items='[{"description": "Maurerarbeiten", "quantity": 50, "unit_price": 45.0}]',
                status=random.choice(["entwurf", "versendet", "bezahlt"]),
                created_at=invoice_date,
                updated_at=invoice_date
            )
            session.add(invoice)
        
        session.commit()
        print("Rechnungen erstellt")
    
    print("=" * 60)
    print("Alle Testdaten erfolgreich erstellt!")
    print()
    print("ZUSAMMENFASSUNG:")
    print("   3 Benutzer (admin, buchhalter, mitarbeiter1)")
    print("   3 Mitarbeiter")
    print("   3 Projekte")
    print("   10 Berichte")
    print("   5 Angebote")
    print("   20 Stundeneintraege")
    print("   8 Rechnungen")
    print()
    print("LOGIN-DATEN:")
    print("   Benutzername: admin")
    print("   Passwort: admin123")
    print()
    print("Die neue Datenbank ist: database_fresh.db")
    print("Kopieren Sie diese ueber database.db um sie zu verwenden!")

if __name__ == "__main__":
    create_fresh_database()
