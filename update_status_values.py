#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

DATABASE_URL = "database.db"

def update_report_status_values():
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()

    status_mapping = {
        'bericht': 'BERICHT',
        'meldung': 'MELDUNG',
        'schaden': 'SCHADEN',
        'verzoegerung': 'VERZOEGERUNG',
        'qualitaet': 'QUALITAET',
        'sicherheit': 'SICHERHEIT',
        'material': 'MATERIAL',
        'sonstiges': 'SONSTIGES'
    }

    print("=== Aktualisiere Status-Werte ===")

    for old_status, new_status in status_mapping.items():
        cursor.execute("UPDATE report SET status = ? WHERE status = ?", (new_status, old_status))
        updated_rows = cursor.rowcount
        if updated_rows > 0:
            print(f"+ {updated_rows} Berichte von '{old_status}' zu '{new_status}' aktualisiert")
    
    conn.commit()
    print("+ Alle Status-Werte erfolgreich korrigiert")

    # Überprüfe einige aktualisierte Berichte
    print("\nAktualisierte Berichte:")
    cursor.execute("SELECT id, title, status FROM report ORDER BY id DESC LIMIT 10")
    for row in cursor.fetchall():
        print(f"  ID {row[0]}: {row[1]} - Status: {row[2]}")

    conn.close()

if __name__ == "__main__":
    update_report_status_values()


