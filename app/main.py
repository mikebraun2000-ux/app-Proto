"""
Hauptanwendung für die Bau-Dokumentations-App.
FastAPI-Anwendung mit allen Routen und Middleware.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import logging
import os
from .database import create_db_and_tables
from .routers import (
    projects,
    reports,
    offers,
    employees,
    time_entries,
    project_images,
    invoices,
    auth,
    invoice_generation,
    billing,
    company_logo,
    user_settings,
)
from .utils.feature_flags import FEATURE_FLAGS
from app.utils.db_compat import ensure_tenant_settings_columns

FEATURE_FLAGS.setdefault("multi_tenant_enabled", False)

logger = logging.getLogger(__name__)

# Startup-Event
def startup_event():
    """Wird beim Start der Anwendung ausgeführt."""
    create_db_and_tables()
    try:
        ensure_tenant_settings_columns()
    except Exception as e:
        logger.warning(f"Konnte tenant_settings nicht aktualisieren: {e}")

# FastAPI-Anwendung erstellen
app = FastAPI(
    title="Bau-Dokumentations-App",
    description="Backend-API für eine lokale Bau-Dokumentations-Anwendung",
    version="1.0.0"
)

# Startup-Event registrieren
app.add_event_handler("startup", startup_event)

# CORS-Middleware für Frontend-Kommunikation
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8080", "http://localhost:8000", "http://127.0.0.1:8000"],  # Frontend-URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Globaler Exception Handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP Exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unerwarteter Fehler: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Interner Serverfehler", "status_code": 500}
    )

# Static Files für Frontend
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Router einbinden
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(reports.router)
app.include_router(offers.router)
app.include_router(employees.router)
app.include_router(time_entries.router)
app.include_router(project_images.router)
app.include_router(invoices.router)
app.include_router(invoice_generation.router)
app.include_router(billing.router)
app.include_router(company_logo.router)
app.include_router(user_settings.router)

# Dashboard
from app.routers import dashboard
app.include_router(dashboard.router)

@app.get("/")
def read_root():
    """
    Root-Endpoint für die API.
    
    Returns:
        dict: Willkommensnachricht und API-Informationen
    """
    return {
        "message": "Willkommen zur Bau-Dokumentations-App API",
        "version": "1.0.0",
        "docs": "/docs",
        "frontend": "/app",
        "endpoints": {
            "projects": "/projects",
            "reports": "/reports", 
            "offers": "/offers",
            "employees": "/employees",
            "time_entries": "/time-entries",
            "project_images": "/project-images",
            "invoices": "/invoices"
        }
    }

@app.get("/login", response_class=HTMLResponse)
def serve_login():
    """
    Login-Seite ausliefern.
    
    Returns:
        HTML: Login-Interface
    """
    if os.path.exists("static/login.html"):
        with open("static/login.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    else:
        return HTMLResponse(content="<h1>Login-Seite nicht gefunden</h1>", status_code=404)

@app.get("/app", response_class=HTMLResponse)
def serve_frontend():
    """
    Frontend-Anwendung ausliefern.
    
    Returns:
        HTML: Frontend-Interface
    """
    if os.path.exists("static/index.html"):
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    else:
        return HTMLResponse(content="<h1>Frontend nicht gefunden</h1>", status_code=404)

@app.get("/app_simple.js", response_class=HTMLResponse)
def serve_js():
    """
    JavaScript-Datei ausliefern.
    
    Returns:
        JavaScript: Frontend-JavaScript
    """
    if os.path.exists("static/app_simple.js"):
        with open("static/app_simple.js", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), media_type="application/javascript")
    else:
        return HTMLResponse(content="// JavaScript-Datei nicht gefunden", status_code=404)

@app.get("/health")
def health_check():
    """
    Health-Check-Endpoint für die API.
    
    Returns:
        dict: Status der Anwendung
    """
    return {"status": "healthy", "message": "API ist erreichbar"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

