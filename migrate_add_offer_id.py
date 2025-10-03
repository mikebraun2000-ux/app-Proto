#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

DATABASE_URL = "database.db"

def add_offer_id_to_invoices():
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()

    try:
        # Spalte hinzufügen, falls nicht vorhanden
        cursor.execute("ALTER TABLE invoice ADD COLUMN offer_id INTEGER REFERENCES offer(id)")
        print("+ offer_id Spalte erfolgreich hinzugefügt")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("- offer_id Spalte existiert bereits.")
        else:
            print(f"- Fehler beim Hinzufügen der offer_id Spalte: {e}")
            conn.close()
            return

    conn.commit()
    conn.close()
    print("+ Migration erfolgreich abgeschlossen")

if __name__ == "__main__":
    print("=== Migration: offer_id Spalte hinzufügen ===")
    add_offer_id_to_invoices()


