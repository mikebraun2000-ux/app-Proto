@echo off
echo ========================================
echo   Bau-Dokumentations-App starten
echo ========================================
echo.

REM Prüfe ob Python verfügbar ist
python --version >nul 2>&1
if errorlevel 1 (
    echo FEHLER: Python ist nicht installiert oder nicht im PATH verfügbar.
    echo Bitte installieren Sie Python 3.8 oder höher.
    pause
    exit /b 1
)

REM Wechsle in das Backend-Verzeichnis
cd /d "%~dp0"

REM Aktiviere die virtuelle Umgebung falls vorhanden
if exist "venv311\Scripts\activate.bat" (
    echo Aktiviere virtuelle Umgebung...
    call venv311\Scripts\activate.bat
) else (
    echo Hinweis: Keine virtuelle Umgebung gefunden.
)

REM Prüfe ob alle Abhängigkeiten installiert sind
python -c "import uvicorn, fastapi, sqlmodel" >nul 2>&1
if errorlevel 1 (
    echo Installiere fehlende Abhängigkeiten...
    pip install -r requirements.txt
)

echo.
echo ========================================
echo   Server wird gestartet...
echo ========================================
echo.
echo Die App ist verfügbar unter:
echo   http://localhost:8000/app
echo.
echo Login-Daten:
echo   Benutzername: admin
echo   Passwort: admin123
echo.
echo Zum Stoppen drücken Sie Ctrl+C
echo ========================================
echo.

REM Starte den FastAPI-Server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

echo.
echo Server wurde beendet.
pause
