"""Tests für die Rechnungs-Router-Konfiguration."""

import os
import sys
from pathlib import Path

from fastapi.routing import APIRoute

# Minimal erforderliche Settings setzen, damit der Auth-Stack geladen werden kann.
os.environ.setdefault("SECRET_KEY", "test-secret-key")

# Sicherstellen, dass das Projektverzeichnis im Python-Pfad liegt.
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.main import app  # noqa: E402  # Import nach Setzen der Umgebung


def test_create_invoice_from_calculation_route_uses_project_path() -> None:
    """Stellt sicher, dass der Endpunkt den erwarteten Pfad mit Projekt-ID nutzt."""
    route_paths = {
        route.path
        for route in app.routes
        if isinstance(route, APIRoute) and route.name == "create_invoice_from_calculation"
    }
    assert "/invoices/create-from-calculation/{project_id}" in route_paths
