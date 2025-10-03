"""
Repariert Frontend-Probleme systematisch.
"""

def create_improved_modal_script():
    """Erstellt ein verbessertes Modal-Script."""
    return '''
// VERBESSERTE MODAL-FUNKTIONALITÄT
// =================================

// Modal anzeigen mit verbesserter Projektauswahl
function showAutoInvoiceModal() {
    console.log('Zeige automatische Rechnungsgenerierung Modal...');
    
    // Modal anzeigen
    const modal = new bootstrap.Modal(document.getElementById('autoInvoiceModal'));
    modal.show();
    
    // Projekte NACH Modal-Öffnung laden (mit Verzögerung)
    setTimeout(() => {
        loadProjectsForInvoiceGeneration();
    }, 300); // Erhöhte Verzögerung für bessere Kompatibilität
}

// Verbesserte Projektauswahl
async function loadProjectsForInvoiceGeneration() {
    try {
        console.log('Lade Projekte für Rechnungsgenerierung...');
        
        // Token aus localStorage holen
        const token = localStorage.getItem('token');
        if (!token) {
            console.error('Kein Token gefunden');
            alert('Bitte loggen Sie sich erneut ein.');
            return;
        }
        
        // Projekte laden
        const response = await fetch('/projects/', {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });
        
        console.log('Projekte-Response Status:', response.status);
        
        if (response.ok) {
            const projects = await response.json();
            console.log('Projekte geladen:', projects.length);
            
            const projectSelect = document.getElementById('invoiceProjectSelect');
            if (projectSelect) {
                // Dropdown leeren und Standard-Option hinzufügen
                projectSelect.innerHTML = '<option value="">Projekt auswählen...</option>';
                
                // Projekte hinzufügen
                projects.forEach(project => {
                    const option = document.createElement('option');
                    option.value = project.id;
                    option.textContent = `${project.name} - ${project.client_name || 'Kein Kunde'}`;
                    projectSelect.appendChild(option);
                });
                
                console.log('Projektauswahl aktualisiert mit', projects.length, 'Projekten');
            } else {
                console.error('Element invoiceProjectSelect nicht gefunden');
            }
        } else {
            console.error('Fehler beim Laden der Projekte:', response.status, response.statusText);
            const errorText = await response.text();
            console.error('Fehler-Details:', errorText);
        }
    } catch (error) {
        console.error('Fehler beim Laden der Projekte:', error);
    }
}

// Verbesserte Rechnungsgenerierung
async function generateInvoice() {
    const projectId = document.getElementById('invoiceProjectSelect').value;
    const generationMethod = document.getElementById('invoiceGenerationMethod').value;
    
    if (!projectId) {
        alert('Bitte wählen Sie ein Projekt aus.');
        return;
    }
    
    try {
        console.log('Starte Rechnungsgenerierung...');
        
        const token = localStorage.getItem('token');
        if (!token) {
            alert('Bitte loggen Sie sich erneut ein.');
            return;
        }
        
        const requestData = {
            project_id: parseInt(projectId),
            generation_method: generationMethod,
            labor_cost_percentage: 30.0, // Fester Wert
            include_materials: true,
            include_labor: true,
            tax_rate: 19.0
        };
        
        console.log('Sende Anfrage:', requestData);
        
        const response = await fetch('/invoice-generation/generate', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        console.log('Rechnungsgenerierung-Response:', response.status);
        
        if (response.ok) {
            const result = await response.json();
            console.log('Rechnungsgenerierung erfolgreich:', result);
            showInvoiceGenerationResult(result);
        } else {
            const errorText = await response.text();
            console.error('Rechnungsgenerierung-Fehler:', errorText);
            alert('Fehler bei der Rechnungsgenerierung: ' + errorText);
        }
    } catch (error) {
        console.error('Fehler bei der Rechnungsgenerierung:', error);
        alert('Fehler bei der Rechnungsgenerierung: ' + error.message);
    }
}

// Verbesserte Ergebnisanzeige
function showInvoiceGenerationResult(result) {
    const resultDiv = document.getElementById('invoiceGenerationResult');
    if (resultDiv) {
        resultDiv.innerHTML = `
            <div class="alert alert-success">
                <h5>Rechnungsberechnung erfolgreich!</h5>
                <p><strong>Gesamtbetrag:</strong> ${result.total_amount.toFixed(2)} EUR</p>
                <p><strong>Personalkosten gesamt:</strong> ${result.total_labor_cost.toFixed(2)} EUR</p>
                <p><strong>Materialkosten:</strong> ${result.total_material_cost.toFixed(2)} EUR</p>
                <p><strong>USt-Betrag:</strong> ${result.tax_amount.toFixed(2)} EUR</p>
                <p><strong>Anzahl Positionen:</strong> ${result.items.length}</p>
            </div>
            <div class="mt-3">
                <button class="btn btn-primary" onclick="createInvoiceFromResult()">
                    <i class="fas fa-save me-2"></i>Rechnung erstellen
                </button>
                <button class="btn btn-secondary" onclick="closeAutoInvoiceModal()">
                    <i class="fas fa-times me-2"></i>Abbrechen
                </button>
            </div>
        `;
        resultDiv.style.display = 'block';
    }
}

// Modal schließen
function closeAutoInvoiceModal() {
    const modal = bootstrap.Modal.getInstance(document.getElementById('autoInvoiceModal'));
    if (modal) {
        modal.hide();
    }
}

// Rechnung aus Ergebnis erstellen
async function createInvoiceFromResult() {
    // Implementierung für Rechnungserstellung
    console.log('Rechnung erstellen...');
    alert('Rechnungserstellung wird implementiert...');
}
'''

def main():
    """Hauptfunktion für Frontend-Reparatur."""
    print("FRONTEND-REPARATUR")
    print("=" * 20)
    
    # Verbessertes Script erstellen
    improved_script = create_improved_modal_script()
    
    # Script in Datei schreiben
    with open('improved_modal_functions.js', 'w', encoding='utf-8') as f:
        f.write(improved_script)
    
    print("Verbesserte Modal-Funktionen erstellt: improved_modal_functions.js")
    print("\nDiese Funktionen sollten in app_simple.js integriert werden:")
    print("1. showAutoInvoiceModal() - mit verbesserter Timing-Logik")
    print("2. loadProjectsForInvoiceGeneration() - mit besserer Fehlerbehandlung")
    print("3. generateInvoice() - mit verbesserter Token-Behandlung")
    print("4. showInvoiceGenerationResult() - mit korrekter Anzeige")

if __name__ == "__main__":
    main()

