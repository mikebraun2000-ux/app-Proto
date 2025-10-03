
// REPARIERTE PROJEKTAUSWAHL
// =========================

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
                
                // Zusätzliche Validierung
                if (projects.length === 0) {
                    console.warn('Keine Projekte verfügbar');
                    projectSelect.innerHTML = '<option value="">Keine Projekte verfügbar</option>';
                }
            } else {
                console.error('Element invoiceProjectSelect nicht gefunden');
                // Versuche alternative Selektoren
                const alternativeSelect = document.querySelector('select[id*="project"], select[id*="Project"]');
                if (alternativeSelect) {
                    console.log('Alternative Projektauswahl gefunden:', alternativeSelect.id);
                }
            }
        } else {
            console.error('Fehler beim Laden der Projekte:', response.status, response.statusText);
            const errorText = await response.text();
            console.error('Fehler-Details:', errorText);
            
            // Benutzer informieren
            alert('Fehler beim Laden der Projekte. Bitte versuchen Sie es erneut.');
        }
    } catch (error) {
        console.error('Fehler beim Laden der Projekte:', error);
        alert('Fehler beim Laden der Projekte: ' + error.message);
    }
}

// Verbesserte Modal-Anzeige
function showAutoInvoiceModal() {
    console.log('Zeige automatische Rechnungsgenerierung Modal...');
    
    // Modal anzeigen
    const modal = new bootstrap.Modal(document.getElementById('autoInvoiceModal'));
    modal.show();
    
    // Projekte NACH Modal-Öffnung laden (mit erhöhter Verzögerung)
    setTimeout(() => {
        loadProjectsForInvoiceGeneration();
    }, 500); // Erhöhte Verzögerung für bessere Kompatibilität
}

// Token-Validierung verbessern
function validateToken() {
    const token = localStorage.getItem('token');
    if (!token) {
        console.error('Kein Token gefunden');
        return false;
    }
    
    try {
        // Token dekodieren (einfache Validierung)
        const payload = JSON.parse(atob(token.split('.')[1]));
        const now = Math.floor(Date.now() / 1000);
        
        if (payload.exp && payload.exp < now) {
            console.error('Token abgelaufen');
            localStorage.removeItem('token');
            return false;
        }
        
        return true;
    } catch (error) {
        console.error('Token-Validierung fehlgeschlagen:', error);
        localStorage.removeItem('token');
        return false;
    }
}

// Verbesserte Rechnungsgenerierung
async function generateInvoice() {
    // Token validieren
    if (!validateToken()) {
        alert('Ihre Sitzung ist abgelaufen. Bitte loggen Sie sich erneut ein.');
        window.location.href = '/login';
        return;
    }
    
    const projectId = document.getElementById('invoiceProjectSelect').value;
    const generationMethod = document.getElementById('invoiceGenerationMethod').value;
    
    if (!projectId) {
        alert('Bitte wählen Sie ein Projekt aus.');
        return;
    }
    
    try {
        console.log('Starte Rechnungsgenerierung...');
        
        const token = localStorage.getItem('token');
        const requestData = {
            project_id: parseInt(projectId),
            generation_method: generationMethod,
            labor_cost_percentage: 30.0,
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
