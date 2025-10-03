#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

DATABASE_URL = "database.db"

def add_status_column_to_reports():
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()

    try:
        # Spalte hinzufügen, falls nicht vorhanden
        cursor.execute("ALTER TABLE report ADD COLUMN status VARCHAR(20) DEFAULT 'BERICHT'")
        print("+ Status-Spalte erfolgreich hinzugefügt")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("- Status-Spalte existiert bereits.")
        else:
            print(f"- Fehler beim Hinzufügen der Status-Spalte: {e}")
            conn.close()
            return

    # Bestehende Berichte aktualisieren, falls sie noch keinen Status haben
    cursor.execute("UPDATE report SET status = 'BERICHT' WHERE status IS NULL")
    updated_rows = cursor.rowcount
    print(f"+ {updated_rows} Berichte aktualisiert")

    conn.commit()
    conn.close()
    print("+ Migration erfolgreich abgeschlossen")

if __name__ == "__main__":
    print("=== Migration: Status-Spalte hinzufügen ===")
    add_status_column_to_reports()


