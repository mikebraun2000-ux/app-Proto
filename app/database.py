"""
Datenbankverbindung und Session-Management für die Bau-Dokumentations-App.
Verwendet SQLite mit SQLModel für die Datenmodellierung.
"""

from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
import os
# Hinweis: Legacy-Datenbanken werden über Alembic/Kompatibilitätsskripte aktualisiert

# SQLite-Datenbankpfad
DATABASE_URL = "sqlite:///./database.db"

# Engine erstellen mit check_same_thread=False für SQLite
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False  # SQL-Queries in der Konsole anzeigen (für Entwicklung)
)

def create_db_and_tables() -> None:
    """
    Erstellt die Datenbank und alle Tabellen basierend auf den SQLModel-Modellen.
    """
    SQLModel.metadata.create_all(engine)
    # Legacy-Datenbanken sollten vorab migriert werden (siehe Alembic)

def get_session() -> Generator[Session, None, None]:
    """
    FastAPI Dependency für Datenbank-Sessions.
    Erstellt eine neue Session für jeden Request und schließt sie automatisch.
    """
    with Session(engine) as session:
        yield session

