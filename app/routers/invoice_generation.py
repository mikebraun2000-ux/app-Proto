"""
Router für automatische Rechnungsgenerierung.
Separater Router um Konflikte mit {invoice_id} zu vermeiden.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from ..database import get_session
from ..schemas import InvoiceGenerationRequest, InvoiceCalculationResult
from ..services.invoice_generator import InvoiceGenerator
from ..auth import get_current_user, require_buchhalter_or_admin

router = APIRouter(prefix="/invoice-generation", tags=["invoice-generation"])

@router.get("/methods")
def get_generation_methods(current_user = Depends(get_current_user)):
    """
    Gibt verfügbare Rechnungsgenerierungs-Methoden zurück.
    
    Returns:
        dict: Verfügbare Methoden und deren Beschreibungen
    """
    return {
        "methods": {
            "time_entries": {
                "name": "Stundeneinträge",
                "description": "Generiert Rechnung basierend auf Arbeitsstunden und Stundensätzen",
                "features": ["Lohnanteil-Berechnung", "Mitarbeiter-spezifische Abrechnung"]
            },
            "reports": {
                "name": "Berichte",
                "description": "Generiert Rechnung basierend auf erstellten Berichten",
                "features": ["Leistungsnachweis", "Arbeitsart-spezifische Abrechnung"]
            },
            "offers": {
                "name": "Angebote",
                "description": "Generiert Rechnung basierend auf akzeptierten Angeboten",
                "features": ["Angebotspositionen", "Vordefinierte Preise"]
            },
            "hybrid": {
                "name": "Hybrid (Empfohlen)",
                "description": "Kombiniert alle Datenquellen für umfassende Rechnungsgenerierung",
                "features": ["Stundeneinträge", "Materialverbrauch", "Berichte", "Lohnanteil"]
            }
        },
        "ustg_requirements": {
            "section_14": "UStG §14 konforme Rechnungsstellung",
            "labor_cost_display": "Lohnanteil gesondert ausweisen",
            "tax_calculation": "Automatische USt-Berechnung",
            "invoice_numbering": "Fortlaufende Rechnungsnummerierung"
        }
    }

@router.post("/generate", response_model=InvoiceCalculationResult)
def generate_invoice_calculation(
    request: InvoiceGenerationRequest, 
    session: Session = Depends(get_session), 
    current_user = Depends(require_buchhalter_or_admin)
):
    """
    Generiert eine Rechnungsberechnung basierend auf verschiedenen Datenquellen.
    
    Args:
        request: Rechnungsgenerierungs-Anfrage
        
    Returns:
        InvoiceCalculationResult: Berechnungsergebnis
    """
    try:
        generator = InvoiceGenerator(session, current_user.tenant_id)
        result = generator.generate_invoice(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler bei der Rechnungsgenerierung: {str(e)}")

@router.post("/create-from-calculation")
def create_invoice_from_calculation(
    request_data: dict,
    session: Session = Depends(get_session),
    current_user = Depends(require_buchhalter_or_admin)
):
    """
    Erstellt eine tatsächliche Rechnung aus einem Berechnungsergebnis.
    
    Args:
        request_data: Dict mit project_id, calculation, invoice_number, client_name, client_address
        
    Returns:
        Invoice: Erstellte Rechnung
    """
    try:
        print(f"DEBUG: Empfangene Daten: {request_data}")
        
        # Extrahiere Parameter aus request_data
        project_id = request_data.get('project_id')
        calculation = request_data.get('calculation')
        invoice_number = request_data.get('invoice_number')
        client_name = request_data.get('client_name')
        client_address = request_data.get('client_address')
        
        print(f"DEBUG: Extrahierte Parameter:")
        print(f"  - project_id: {project_id}")
        print(f"  - invoice_number: {invoice_number}")
        print(f"  - client_name: {client_name}")
        print(f"  - calculation vorhanden: {calculation is not None}")
        
        if not all([project_id, calculation, invoice_number, client_name]):
            missing = []
            if not project_id: missing.append('project_id')
            if not calculation: missing.append('calculation')
            if not invoice_number: missing.append('invoice_number')
            if not client_name: missing.append('client_name')
            raise HTTPException(status_code=400, detail=f"Fehlende erforderliche Parameter: {missing}")
        
        generator = InvoiceGenerator(session, current_user.tenant_id)
        invoice = generator.create_invoice_from_calculation(
            project_id, calculation, invoice_number, client_name, client_address
        )
        print(f"DEBUG: Rechnung erfolgreich erstellt: {invoice.id}")
        return invoice
    except Exception as e:
        print(f"DEBUG: Fehler beim Erstellen der Rechnung: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Erstellen der Rechnung: {str(e)}")
