"""
Prüft die Datenbankstruktur.
"""

import sqlite3

def check_database():
    """Prüft die Datenbankstruktur."""
    print("Prüfe Datenbankstruktur...")
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    try:
        # Tabellen auflisten
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("Tabellen:", [table[0] for table in tables])
        
        # User-Tabelle prüfen
        if 'user' in [table[0] for table in tables]:
            cursor.execute("SELECT * FROM user LIMIT 3")
            users = cursor.fetchall()
            print("User-Daten:", users)
            
            # Spalten der User-Tabelle
            cursor.execute("PRAGMA table_info(user)")
            columns = cursor.fetchall()
            print("User-Spalten:", [col[1] for col in columns])
        
    except Exception as e:
        print(f"Fehler: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_database()

