"""
Automatische Rechnungsgenerierung Service.
Implementiert verschiedene Methoden zur Erstellung von UStG §14 konformen Rechnungen.
Erweitert um erweiterte Funktionen für Trockenbau-Projekte.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from sqlmodel import Session, select
from app.models import Project, TimeEntry, Report, Offer, MaterialUsage, Employee, Invoice
from app.schemas import InvoiceGenerationRequest, InvoiceGenerationData, InvoiceCalculationResult, InvoiceItem as InvoiceItemSchema

# Logger konfigurieren
logger = logging.getLogger(__name__)


class InvoiceGenerator:
    """Service für automatische Rechnungsgenerierung mit erweiterten Funktionen."""
    
    def __init__(self, session: Session):
        self.session = session
        self.default_tax_rate = 19.0
        self.default_labor_percentage = 0.0
        self.default_currency = "EUR"
    
    def generate_invoice(self, request: InvoiceGenerationRequest) -> InvoiceCalculationResult:
        """
        Generiert eine Rechnung basierend auf verschiedenen Datenquellen.
        
        Args:
            request: Rechnungsgenerierungs-Anfrage
            
        Returns:
            InvoiceCalculationResult: Berechnungsergebnis
        """
        try:
            logger.info(f"Starte Rechnungsgenerierung für Projekt {request.project_id}")
            
            # 1. Daten sammeln
            data = self._collect_invoice_data(request)
            logger.info(f"Daten gesammelt: {len(data.time_entries)} Stundeneinträge, {len(data.reports)} Berichte, {len(data.offers)} Angebote")
            
            # 2. Rechnungspositionen generieren
            items = self._generate_invoice_items(data, request)
            logger.info(f"Generiert {len(items)} Rechnungspositionen")
            
            # 3. Berechnungen durchführen
            result = self._calculate_invoice_totals(items, request)
            logger.info(f"Berechnung abgeschlossen: Gesamtbetrag {result.total_amount}€")
            
            return result
            
        except Exception as e:
            logger.error(f"Fehler bei der Rechnungsgenerierung: {str(e)}")
            raise
    
    def _collect_invoice_data(self, request: InvoiceGenerationRequest) -> InvoiceGenerationData:
        """Sammelt alle relevanten Daten für die Rechnungsgenerierung."""
        
        # Projekt laden
        project = self.session.get(Project, request.project_id)
        if not project:
            raise ValueError(f"Projekt mit ID {request.project_id} nicht gefunden")
        
        # Zeitraum definieren
        start_date = request.start_date or datetime.now() - timedelta(days=30)
        end_date = request.end_date or datetime.now()
        
        # Stundeneinträge laden
        time_entries_query = select(TimeEntry).where(
            TimeEntry.project_id == request.project_id,
            TimeEntry.work_date >= start_date,
            TimeEntry.work_date <= end_date
        )
        time_entries = self.session.exec(time_entries_query).all()
        
        # Berichte laden
        reports_query = select(Report).where(
            Report.project_id == request.project_id,
            Report.report_date >= start_date,
            Report.report_date <= end_date
        )
        reports = self.session.exec(reports_query).all()
        
        # Angebote laden
        offers_query = select(Offer).where(Offer.project_id == request.project_id)
        offers = self.session.exec(offers_query).all()
        
        # Materialverbrauch laden
        materials_query = select(MaterialUsage).where(
            MaterialUsage.project_id == request.project_id,
            MaterialUsage.usage_date >= start_date,
            MaterialUsage.usage_date <= end_date
        )
        materials = self.session.exec(materials_query).all()
        
        # Mitarbeiter laden
        employees_query = select(Employee)
        employees = self.session.exec(employees_query).all()
        
        return InvoiceGenerationData(
            project=project.__dict__,
            time_entries=[entry.__dict__ for entry in time_entries],
            reports=[report.__dict__ for report in reports],
            offers=[offer.__dict__ for offer in offers],
            materials=[material.__dict__ for material in materials],
            employees=[employee.__dict__ for employee in employees]
        )
    
    def _generate_invoice_items(self, data: InvoiceGenerationData, request: InvoiceGenerationRequest) -> List[InvoiceItemSchema]:
        """Generiert Rechnungspositionen basierend auf der gewählten Methode."""
        
        items = []
        
        if request.generation_method == "time_entries":
            items.extend(self._generate_from_time_entries(data, request))
        elif request.generation_method == "reports":
            items.extend(self._generate_from_reports(data, request))
        elif request.generation_method == "offers":
            items.extend(self._generate_from_offers(data, request))
        elif request.generation_method == "hybrid":
            items.extend(self._generate_hybrid_items(data, request))
        
        return items
    
    def _generate_from_time_entries(self, data: InvoiceGenerationData, request: InvoiceGenerationRequest) -> List[InvoiceItemSchema]:
        """Generiert Rechnungspositionen aus Stundeneinträgen."""
        items = []
        
        # Gruppiere Stundeneinträge nach Mitarbeiter
        employee_hours = {}
        for entry in data.time_entries:
            employee_id = entry.get('employee_id')
            if employee_id not in employee_hours:
                employee_hours[employee_id] = {
                    'total_hours': 0,
                    'total_cost': 0,
                    'employee': None
                }
            
            hours = entry.get('hours_worked', 0)
            hourly_rate = entry.get('hourly_rate', 0)
            
            employee_hours[employee_id]['total_hours'] += hours
            employee_hours[employee_id]['total_cost'] += hours * hourly_rate
            
            # Finde Mitarbeiter
            for emp in data.employees:
                if emp['id'] == employee_id:
                    employee_hours[employee_id]['employee'] = emp
                    break
        
        # Erstelle Rechnungspositionen
        for employee_id, data_emp in employee_hours.items():
            if data_emp['total_hours'] > 0:
                employee = data_emp['employee']
                employee_name = employee['full_name'] if employee else f"Mitarbeiter {employee_id}"
                
                # Lohnanteil berechnen
                labor_cost = data_emp['total_cost'] * (request.labor_cost_percentage / 100)
                service_cost = data_emp['total_cost'] - labor_cost
                
                items.append(InvoiceItemSchema(
                    description=f"Arbeitsstunden - {employee_name}",
                    quantity=round(data_emp['total_hours'], 2),
                    unit="Std",
                    unit_price=round(data_emp['total_cost'] / data_emp['total_hours'] if data_emp['total_hours'] > 0 else 0, 2),
                    total_price=round(data_emp['total_cost'], 2),
                    item_type="service",
                    labor_cost=round(labor_cost, 2),
                    service_cost=round(service_cost, 2)
                ))
        
        return items
    
    def _generate_from_reports(self, data: InvoiceGenerationData, request: InvoiceGenerationRequest) -> List[InvoiceItemSchema]:
        """Generiert Rechnungspositionen aus Berichten."""
        items = []
        
        for report in data.reports:
            # Gruppiere Berichte nach Arbeitsart
            work_type = report.get('work_type', 'Allgemeine Arbeiten')
            
            items.append(InvoiceItemSchema(
                description=f"Bericht: {work_type}",
                quantity=1,
                unit="Stk",
                unit_price=0,  # Wird später berechnet
                total_price=0,
                item_type="service"
            ))
        
        return items
    
    def _generate_from_offers(self, data: InvoiceGenerationData, request: InvoiceGenerationRequest) -> List[InvoiceItemSchema]:
        """Generiert Rechnungspositionen aus Angeboten."""
        items = []
        
        for offer in data.offers:
            if offer.get('status') == 'accepted':
                # Parse Angebotspositionen
                try:
                    offer_items = json.loads(offer.get('items', '[]'))
                    for item in offer_items:
                        items.append(InvoiceItemSchema(
                            description=item.get('description', ''),
                            quantity=round(item.get('quantity', 1), 2),
                            unit=item.get('unit', 'Stk'),
                            unit_price=round(item.get('unit_price', 0), 2),
                            total_price=round(item.get('total_price', 0), 2),
                            item_type=item.get('item_type', 'service')
                        ))
                except json.JSONDecodeError:
                    # Fallback: Einzelposition
                    items.append(InvoiceItemSchema(
                        description=offer.get('title', 'Angebot'),
                        quantity=1,
                        unit="Stk",
                        unit_price=round(offer.get('total_amount', 0), 2),
                        total_price=round(offer.get('total_amount', 0), 2),
                        item_type="service"
                    ))
        
        return items
    
    def _generate_hybrid_items(self, data: InvoiceGenerationData, request: InvoiceGenerationRequest) -> List[InvoiceItemSchema]:
        """Generiert Rechnungspositionen aus verschiedenen Datenquellen (Hybrid)."""
        items = []
        
        # 1. Stundeneinträge (Arbeitsleistung)
        if request.include_labor:
            items.extend(self._generate_from_time_entries(data, request))
        
        # 2. Materialverbrauch
        if request.include_materials:
            for material in data.materials:
                items.append(InvoiceItemSchema(
                    description=f"Material: {material.get('material_name', '')}",
                    quantity=round(material.get('quantity', 0), 2),
                    unit=material.get('unit', 'Stk'),
                    unit_price=round(material.get('unit_price', 0), 2),
                    total_price=round(material.get('total_cost', 0), 2),
                    item_type="material",
                    material_cost=round(material.get('total_cost', 0), 2)
                ))
        
        # 3. Berichte (zusätzliche Leistungen)
        for report in data.reports:
            items.append(InvoiceItemSchema(
                description=f"Zusätzliche Leistung: {report.get('title', 'Bericht')}",
                quantity=1,
                unit="Stk",
                unit_price=0,
                total_price=0,
                item_type="service"
            ))
        
        return items
    
    def _calculate_invoice_totals(self, items: List[InvoiceItemSchema], request: InvoiceGenerationRequest) -> InvoiceCalculationResult:
        """Berechnet die Rechnungssummen."""
        
        total_labor_cost = round(sum(item.labor_cost or 0 for item in items), 2)
        total_material_cost = round(sum(item.material_cost or 0 for item in items), 2)
        total_service_cost = round(sum(item.service_cost or 0 for item in items), 2)
        
        subtotal = round(total_labor_cost + total_material_cost + total_service_cost, 2)
        tax_amount = round(subtotal * (request.tax_rate / 100), 2)
        total_amount = round(subtotal + tax_amount, 2)
        
        # Lohnanteil in Prozent
        labor_percentage = round((total_labor_cost / subtotal * 100) if subtotal > 0 else 0, 2)
        
        return InvoiceCalculationResult(
            total_labor_cost=total_labor_cost,
            total_material_cost=total_material_cost,
            total_service_cost=total_service_cost,
            subtotal=subtotal,
            tax_amount=tax_amount,
            total_amount=total_amount,
            labor_percentage=labor_percentage,
            items=items
        )
    
    def create_invoice_from_calculation(self, project_id: int, calculation: dict, 
                                      invoice_number: str, client_name: str, client_address: str = None) -> Invoice:
        """Erstellt eine tatsächliche Rechnung aus dem Berechnungsergebnis."""
        
        # Rechnung erstellen
        invoice = Invoice(
            project_id=project_id,
            invoice_number=invoice_number,
            title=f"Rechnung {invoice_number}",
            description="Automatisch generierte Rechnung",
            client_name=client_name,
            client_address=client_address,
            total_amount=round(float(calculation.get('total_amount', 0.0)), 2),
            currency="EUR",
            invoice_date=datetime.now(),
            due_date=datetime.now() + timedelta(days=30),
            items=json.dumps(calculation.get('items', [])),
            status="entwurf"
        )
        
        self.session.add(invoice)
        self.session.commit()
        self.session.refresh(invoice)
        
        return invoice
    
    def generate_invoice_number(self, project_id: int, prefix: str = "RE") -> str:
        """
        Generiert eine eindeutige Rechnungsnummer.
        
        Args:
            project_id: Projekt-ID
            prefix: Präfix für Rechnungsnummer
            
        Returns:
            str: Eindeutige Rechnungsnummer
        """
        # Aktuelle Rechnungsnummern für das Projekt zählen
        existing_invoices = self.session.exec(
            select(Invoice).where(Invoice.project_id == project_id)
        ).all()
        
        invoice_count = len(existing_invoices) + 1
        date_str = datetime.now().strftime("%Y%m%d")
        
        return f"{prefix}-{date_str}-{project_id:03d}-{invoice_count:03d}"
    
    def validate_invoice_data(self, data: InvoiceGenerationData) -> Tuple[bool, List[str]]:
        """
        Validiert die Rechnungsdaten auf Vollständigkeit.
        
        Args:
            data: Rechnungsgenerierungs-Daten
            
        Returns:
            Tuple[bool, List[str]]: (Ist gültig, Liste der Fehler)
        """
        errors = []
        
        # Projekt validieren
        if not data.project:
            errors.append("Kein Projekt gefunden")
        
        # Mindestens eine Datenquelle vorhanden
        if not data.time_entries and not data.reports and not data.offers:
            errors.append("Keine abrechenbaren Daten gefunden")
        
        # Stundeneinträge validieren
        for entry in data.time_entries:
            if not entry.get('hours_worked', 0) > 0:
                errors.append(f"Ungültige Arbeitsstunden in Eintrag {entry.get('id')}")
        
        return len(errors) == 0, errors
    
    def get_invoice_summary(self, result: InvoiceCalculationResult) -> Dict[str, Any]:
        """
        Erstellt eine Zusammenfassung der Rechnungsberechnung.
        
        Args:
            result: Berechnungsergebnis
            
        Returns:
            Dict[str, Any]: Zusammenfassung
        """
        return {
            "summary": {
                "total_items": len(result.items),
                "labor_cost": result.total_labor_cost,
                "material_cost": result.total_material_cost,
                "service_cost": result.total_service_cost,
                "subtotal": result.subtotal,
                "tax_amount": result.tax_amount,
                "total_amount": result.total_amount,
                "labor_percentage": result.labor_percentage
            },
            "breakdown": {
                "labor_items": [item for item in result.items if item.item_type == "labor"],
                "material_items": [item for item in result.items if item.item_type == "material"],
                "service_items": [item for item in result.items if item.item_type == "service"]
            }
        }
    
    def export_invoice_data(self, result: InvoiceCalculationResult, format: str = "json") -> str:
        """
        Exportiert Rechnungsdaten in verschiedenen Formaten.
        
        Args:
            result: Berechnungsergebnis
            format: Export-Format ("json", "csv")
            
        Returns:
            str: Exportierte Daten
        """
        if format == "json":
            return json.dumps({
                "items": [item.dict() for item in result.items],
                "totals": {
                    "subtotal": result.subtotal,
                    "tax_amount": result.tax_amount,
                    "total_amount": result.total_amount
                }
            }, indent=2, ensure_ascii=False)
        
        elif format == "csv":
            csv_lines = ["Beschreibung,Menge,Einheit,Einzelpreis,Gesamtpreis,Typ"]
            for item in result.items:
                csv_lines.append(f"{item.description},{item.quantity},{item.unit},{item.unit_price},{item.total_price},{item.item_type}")
            return "\n".join(csv_lines)
        
        else:
            raise ValueError(f"Unbekanntes Format: {format}")
