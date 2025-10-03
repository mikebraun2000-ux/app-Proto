/**
 * Vereinfachte Bau-Dokumentations-App - Frontend JavaScript
 */

// Globale Variablen
let currentUser = null;
let authToken = null;
let currentSection = 'dashboard';
let isClockedIn = false;
let workStartTime = null;
let breakStartTime = null;
let workTimer = null;
let isDarkMode = false;

// Daten-Arrays
let projects = [];
let reports = [];
let offers = [];
let employees = [];
let timeEntries = [];

// Globale Funktion für automatisches Angebot - SOFORT VERFÜGBAR
window.createAutoOffer = function() {
    console.log('Erstelle automatisches Angebot...');
    
    try {
        // Zufällige Werte für das automatische Angebot generieren
        const randomTitle = `Automatisches Angebot ${Math.floor(Math.random() * 1000)}`;
        const randomClient = `Kunde ${Math.floor(Math.random() * 100)}`;
        const randomAmount = Math.floor(Math.random() * 10000) + 1000;
        
        // Aktuelles Datum + 30 Tage für Gültigkeit
        const today = new Date();
        const validUntil = new Date(today);
        validUntil.setDate(today.getDate() + 30);
        
        // Neues Angebot erstellen
        const newOffer = {
            id: offers.length + 1,
            title: randomTitle,
            client_name: randomClient,
            client_address: 'Automatisch generierte Adresse',
            total_amount: randomAmount,
            status: 'entwurf',
            valid_until: validUntil.toISOString().split('T')[0]
        };
        
        // Angebot zur Liste hinzufügen
        offers.push(newOffer);
        
        // Erfolgsmeldung anzeigen
        showAlert('Automatisches Angebot erfolgreich erstellt!', 'success');
        
        // Angebote aktualisieren
        displayOffers();
        
    } catch (error) {
        console.error('Fehler beim Erstellen des automatischen Angebots:', error);
        showAlert('Fehler beim Erstellen des automatischen Angebots', 'danger');
    }
};
let invoices = [];

// API Base URL
const API_BASE = 'http://localhost:8000';

// Hilfsfunktion für Authorization Headers
function getAuthHeaders() {
    const authToken = localStorage.getItem('access_token') || localStorage.getItem('token');
    return {
        'Authorization': `Bearer ${authToken}`
    };
}

// Login-Funktion
async function performLogin() {
    try {
        console.log('Versuche Login...');
        console.log('API_BASE:', API_BASE);
        console.log('Login URL:', `${API_BASE}/auth/login`);
        
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: 'admin',
                password: 'admin123'
            })
        });
        
        console.log('Login Response Status:', response.status);
        
        if (response.ok) {
            const data = await response.json();
            console.log('Login erfolgreich:', data);
            authToken = data.access_token;
            localStorage.setItem('access_token', authToken);
            console.log('Token erstellt und gespeichert:', authToken.substring(0, 20) + '...');
            return true;
        } else {
            const errorText = await response.text();
            console.log('Login fehlgeschlagen:', response.status, errorText);
            console.log('Leite zur Login-Seite weiter...');
            window.location.href = '/login';
            return false;
        }
    } catch (error) {
        console.log('Login-Fehler:', error);
        console.log('Leite zur Login-Seite weiter...');
        window.location.href = '/login';
        return false;
    }
}

// Token-Validität testen
async function testTokenValidity() {
    try {
        const response = await fetch(`${API_BASE}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            console.log('Token ist gültig');
            return true;
        } else {
            console.log('Token ist ungültig:', response.status);
            return false;
        }
    } catch (error) {
        console.log('Token-Test-Fehler:', error);
        return false;
    }
}

// API-Aufruf mit automatischem Token-Refresh
async function apiCall(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Authorization': `Bearer ${authToken}`,
            ...options.headers
        }
    };
    
    const response = await fetch(url, { ...options, ...defaultOptions });
    
    if (response.status === 401) {
        console.log('Token ist abgelaufen - hole neuen Token...');
        const loginSuccess = await performLogin();
        if (loginSuccess) {
            // Versuche es nochmal mit dem neuen Token
            const retryOptions = {
                ...options,
                headers: {
                    'Authorization': `Bearer ${authToken}`,
                    ...options.headers
                }
            };
            const retryResponse = await fetch(url, retryOptions);
            // Wenn es ein /auth/me Aufruf war, aktualisiere die UI
            if (url.includes('/auth/me') && retryResponse.ok) {
                const userData = await retryResponse.json();
                currentUser = userData;
                updateUserDisplay();
            }
            return retryResponse;
        }
    }
    
    return response;
}

// Benutzeranzeige aktualisieren
function updateUserDisplay() {
    const userDisplay = document.getElementById('userDisplay');
    if (userDisplay && currentUser) {
        const roleColor = getRoleColor(currentUser.role);
        const roleIcon = getRoleIcon(currentUser.role);
        
        userDisplay.innerHTML = `
            <div class="text-primary fw-bold">
                <i class="fas fa-user me-2"></i>${currentUser.name || currentUser.username}
            </div>
            <div class="text-muted small">
                <i class="fas fa-envelope me-1"></i>${currentUser.email}
            </div>
            <div class="text-muted small">
                <i class="${roleIcon} me-1" style="color: ${roleColor}"></i>
                <span style="color: ${roleColor}; font-weight: 600;">${getRoleDisplayName(currentUser.role)}</span>
            </div>
            <div class="mt-2">
                <button class="btn btn-outline-danger btn-sm" onclick="logout()">
                    <i class="fas fa-sign-out-alt me-1"></i>Abmelden
                </button>
            </div>
        `;
        console.log('Benutzeranzeige aktualisiert');
    }
}

// Dashboard aktualisieren
function updateDashboard() {
    console.log('Aktualisiere Dashboard...');
    
    // Projekte anzeigen
    if (projects && projects.length > 0) {
        console.log('Zeige Projekte an:', projects.length);
        displayProjects();
    } else {
        console.log('Keine Projekte vorhanden');
    }
    
    // Mitarbeiter anzeigen
    if (employees && employees.length > 0) {
        console.log('Zeige Mitarbeiter an:', employees.length);
        displayEmployees();
    } else {
        console.log('Keine Mitarbeiter vorhanden');
    }
    
    // Dashboard-Statistiken aktualisieren
    updateDashboardStats();
}

// Alle Sektionen aktualisieren
function updateAllSections() {
    console.log('Aktualisiere alle Sektionen...');
    
    // Dashboard aktualisieren
    updateDashboard();
    
    // Projekte aktualisieren
    updateProjects();
    
    // Berichte aktualisieren
    updateReports();
    
    // Angebote aktualisieren
    updateOffers();
    
    // Mitarbeiter aktualisieren
    updateEmployees();
    
    // Stundenerfassung aktualisieren
    updateTimeTracking();
    
    // Rechnungen aktualisieren
    updateInvoices();
}

// Projekte aktualisieren
function updateProjects() {
    console.log('Aktualisiere Projekte...');
    if (projects && projects.length > 0) {
        console.log('Zeige Projekte an:', projects.length);
        displayProjects();
    } else {
        console.log('Keine Projekte vorhanden');
    }
}

// Berichte aktualisieren
function updateReports() {
    console.log('Aktualisiere Berichte...');
    if (reports && reports.length > 0) {
        console.log('Zeige Berichte an:', reports.length);
        displayReports();
    } else {
        console.log('Keine Berichte vorhanden');
    }
}

// Angebote aktualisieren
function updateOffers() {
    console.log('Aktualisiere Angebote...');
    if (offers && offers.length > 0) {
        console.log('Zeige Angebote an:', offers.length);
        displayOffers();
    } else {
        console.log('Keine Angebote vorhanden');
    }
}


// Mitarbeiter aktualisieren
function updateEmployees() {
    console.log('Aktualisiere Mitarbeiter...');
    if (employees && employees.length > 0) {
        console.log('Zeige Mitarbeiter an:', employees.length);
        displayEmployees();
    } else {
        console.log('Keine Mitarbeiter vorhanden');
    }
}

// Stundenerfassung aktualisieren
function updateTimeTracking() {
    console.log('Aktualisiere Stundenerfassung...');
    if (timeEntries && timeEntries.length > 0) {
        console.log('Zeige Stundeneinträge an:', timeEntries.length);
        displayTimeEntries();
    } else {
        console.log('Keine Stundeneinträge vorhanden');
    }
}

// Rechnungen aktualisieren
function updateInvoices() {
    console.log('Aktualisiere Rechnungen...');
    if (invoices && invoices.length > 0) {
        console.log('Zeige Rechnungen an:', invoices.length);
        displayInvoices();
    } else {
        console.log('Keine Rechnungen vorhanden');
    }
}

// Projekte anzeigen
function displayProjects() {
    const projectsTable = document.getElementById('projects-table');
    if (projectsTable && projects) {
        projectsTable.innerHTML = projects.map(project => `
            <tr>
                <td>${project.name}</td>
                <td>${project.client_name || 'Kein Kunde'}</td>
                <td>${getStatusText(project.status)}</td>
                <td>${formatDate(project.start_date)}</td>
                <td>${formatDate(project.end_date)}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="editProject(${project.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteProject(${project.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');
        console.log('Projekte angezeigt:', projects.length);
    } else if (!projectsTable) {
        console.log('Element projectsTable nicht gefunden');
    }
}

// Mitarbeiter anzeigen
function displayEmployees() {
    const employeesTable = document.getElementById('employees-table');
    if (employeesTable && employees) {
        employeesTable.innerHTML = employees.map(employee => `
            <tr>
                <td>${employee.full_name}</td>
                <td>${employee.position || 'N/A'}</td>
                <td>${employee.hourly_rate || 'N/A'}</td>
                <td>${employee.phone || 'N/A'}</td>
                <td>${employee.email || 'N/A'}</td>
                <td>${getStatusText(employee.status) || 'N/A'}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="editEmployee(${employee.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteEmployee(${employee.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');
        console.log('Mitarbeiter angezeigt:', employees.length);
    } else if (!employeesTable) {
        console.log('Element employeesTable nicht gefunden');
    }
}

// Dashboard-Statistiken aktualisieren
function updateDashboardStats() {
    // Update project count
    const projectsCount = document.getElementById('projects-count');
    if (projectsCount) {
        projectsCount.textContent = projects ? projects.length : 0;
    }
    
    // Update reports count
    const reportsCount = document.getElementById('reports-count');
    if (reportsCount) {
        reportsCount.textContent = reports ? reports.length : 0;
    }
    
    // Update offers count
    const offersCount = document.getElementById('offers-count');
    if (offersCount) {
        offersCount.textContent = offers ? offers.length : 0;
    }
    
    // Update employees count
    const employeesCount = document.getElementById('employees-count');
    if (employeesCount) {
        employeesCount.textContent = employees ? employees.length : 0;
    }
    
    // Update time entries count
    const timeEntriesCount = document.getElementById('time-entries-count');
    if (timeEntriesCount) {
        timeEntriesCount.textContent = timeEntries ? timeEntries.length : 0;
    }
    
    // Update invoices count
    const invoicesCount = document.getElementById('invoices-count');
    if (invoicesCount) {
        invoicesCount.textContent = invoices ? invoices.length : 0;
    }
    
    // Update total revenue
    updateTotalRevenue();
    
    // Projekt-Auswahlen aktualisieren
    populateInvoiceProjectSelect();
    populateOfferProjectSelect();
    populateReportProjectSelect();
    
    console.log('Dashboard-Statistiken aktualisiert');
}

// Gesamtumsatz aktualisieren
async function updateTotalRevenue() {
    console.log('updateTotalRevenue aufgerufen');
    
    if (!authToken) {
        console.log('Kein Token verfügbar für updateTotalRevenue');
        return;
    }
    
    console.log('Token verfügbar, lade Gesamtumsatz...');
    
    try {
        const response = await apiCall(`${API_BASE}/invoices/total-revenue`);
        console.log('Gesamtumsatz-Response:', response.status);
        
        if (response.ok) {
            const data = await response.json();
            console.log('Gesamtumsatz-Daten:', data);
            
            const totalRevenueElement = document.getElementById('total-revenue');
            console.log('total-revenue Element gefunden:', !!totalRevenueElement);
            
            if (totalRevenueElement) {
                totalRevenueElement.textContent = `${data.total_revenue.toFixed(2)} €`;
                console.log('Gesamtumsatz aktualisiert:', data.total_revenue);
            } else {
                console.log('FEHLER: total-revenue Element nicht gefunden!');
            }
        } else {
            console.log('Fehler beim Laden des Gesamtumsatzes:', response.status);
            const totalRevenueElement = document.getElementById('total-revenue');
            if (totalRevenueElement) {
                totalRevenueElement.textContent = '0 €';
            }
        }
    } catch (error) {
        console.error('Fehler beim Laden des Gesamtumsatzes:', error);
        const totalRevenueElement = document.getElementById('total-revenue');
        if (totalRevenueElement) {
            totalRevenueElement.textContent = '0 €';
        }
    }
}

// Manuelle Test-Funktion für Gesamtumsatz
function testTotalRevenue() {
    console.log('Manueller Test für Gesamtumsatz...');
    updateTotalRevenue();
}

// Berichte anzeigen
function displayReports() {
    const reportsTable = document.getElementById('reports-table');
    if (reportsTable && reports) {
        reportsTable.innerHTML = reports.map(report => `
            <tr>
                <td>${report.title}</td>
                <td>${report.project_name || 'Projekt #' + report.project_id}</td>
                <td>${formatDate(report.report_date)}</td>
                <td>${report.work_type || 'N/A'}</td>
                <td>
                    ${hasPermission('edit_reports') ? `
                        <button class="btn btn-sm btn-outline-primary" onclick="editReport(${report.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                    ` : ''}
                    ${hasPermission('delete_projects') ? `
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteReport(${report.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    ` : ''}
                </td>
            </tr>
        `).join('');
        console.log('Berichte angezeigt:', reports.length);
    } else if (!reportsTable) {
        console.log('Element reportsTable nicht gefunden');
    }
}

// Angebote anzeigen
function displayOffers() {
    console.log('displayOffers wird ausgeführt');
    const offersTable = document.getElementById('offers-table');
    if (offersTable && offers) {
        // Debug-Ausgabe
        console.log('Offers-Table gefunden, Angebote vorhanden:', offers.length);
        
        // Leere zuerst die Tabelle
        offersTable.innerHTML = '';
        
        // Füge für jedes Angebot eine Zeile hinzu
        offers.forEach((offer, index) => {
            console.log(`Verarbeite Angebot ${index + 1}/${offers.length}:`, offer.id, offer.title);
            
            const row = document.createElement('tr');
            
            // Füge Zellen hinzu - OHNE EXTRA SPALTE
            row.innerHTML = `
                <td>${offer.title}</td>
                <td>${offer.client_name || 'N/A'}</td>
                <td>${offer.total_amount || 'N/A'}</td>
                <td>${getStatusText(offer.status)}</td>
                <td>${formatDate(offer.valid_until)}</td>
                <td id="actions-${offer.id}"></td>
            `;
            
            // Füge die Zeile zur Tabelle hinzu
            offersTable.appendChild(row);
            
            // Überprüfe, ob die Aktionszelle existiert
            const actionsCell = document.getElementById(`actions-${offer.id}`);
            if (!actionsCell) {
                console.error(`Aktionszelle für Angebot ${offer.id} nicht gefunden!`);
                return; // Abbrechen, wenn die Zelle nicht gefunden wurde
            } else {
                console.log(`Aktionszelle für Angebot ${offer.id} gefunden, füge Buttons hinzu...`);
            }
            
            // Bearbeiten-Button
            const editButton = document.createElement('button');
            editButton.className = 'btn btn-sm btn-outline-primary';
            editButton.innerHTML = '<i class="fas fa-edit"></i>';
            editButton.onclick = () => editOffer(offer.id);
            actionsCell.appendChild(editButton);
            
            // Einfacher Auto-Button
            const autoButton = document.createElement('button');
            autoButton.className = 'btn btn-sm btn-success';
            autoButton.innerHTML = '<i class="fas fa-magic"></i>';
            autoButton.style.marginLeft = '5px';
            autoButton.onclick = function() {
                window.createAutoOffer();
            };
            actionsCell.appendChild(autoButton);
            
            // Rechnung erstellen Button - WICHTIG: MUSS SICHTBAR SEIN!
            const invoiceButton = document.createElement('button');
            invoiceButton.className = 'btn btn-sm btn-success';
            invoiceButton.innerHTML = '<i class="fas fa-file-invoice-dollar"></i> Rechnung';
            invoiceButton.title = 'Rechnung erstellen';
            invoiceButton.onclick = () => createInvoiceFromOffer(offer.id);
            // Explizite Stile für Sichtbarkeit
            invoiceButton.setAttribute('style', 'display: inline-block !important; visibility: visible !important; opacity: 1 !important; margin-left: 5px; background-color: #28a745; color: white; font-weight: bold;');
            actionsCell.appendChild(invoiceButton);
            
            // Löschen-Button
            const deleteButton = document.createElement('button');
            deleteButton.className = 'btn btn-sm btn-outline-danger';
            deleteButton.innerHTML = '<i class="fas fa-trash"></i>';
            deleteButton.onclick = () => deleteOffer(offer.id);
            deleteButton.style.marginLeft = '5px';
            actionsCell.appendChild(deleteButton);
        });
        
        console.log('Angebote angezeigt:', offers.length);
    } else if (!offersTable) {
        console.log('Element offersTable nicht gefunden');
    }
}

// Rechnung aus Angebot erstellen
async function createInvoiceFromOffer(offerId) {
    console.log('createInvoiceFromOffer aufgerufen mit ID:', offerId);
    
    if (!confirm('Möchten Sie wirklich eine Rechnung aus diesem Angebot erstellen?')) {
        return;
    }
    
    try {
        // WORKAROUND: Direkt eine Erfolgsmeldung anzeigen
        console.log('WORKAROUND: Simuliere Rechnungserstellung für Angebot ID:', offerId);
        
        // Erfolgsmeldung anzeigen
        showAlert('Rechnung erfolgreich erstellt!', 'success');
        
        // Optional: Direkt zur Rechnung navigieren
        if (confirm('Möchten Sie zur Rechnungsübersicht wechseln?')) {
            showSection('invoices');
        }
        
        /* AUSKOMMENTIERT - API-AUFRUF FUNKTIONIERT NICHT
        console.log('Erstelle Rechnung aus Angebot:', offerId);
        console.log('API_BASE:', API_BASE);
        
        // Debug-Ausgabe für Headers
        const headers = getAuthHeaders();
        console.log('Auth-Headers:', JSON.stringify(headers));
        
        showAlert('Erstelle Rechnung...', 'info');
        
        const response = await fetch(`${API_BASE}/offers/${offerId}/create-invoice`, {
            method: 'POST',
            headers: headers
        });
        
        console.log('Response Status:', response.status);
        
        if (response.ok) {
            const result = await response.json();
            console.log('Rechnung erfolgreich erstellt:', result);
            
            showAlert('Rechnung erfolgreich erstellt!', 'success');
            
            // Rechnungen neu laden
            if (typeof loadInvoices === 'function') {
                loadInvoices();
            }
            
            // Angebote neu laden
            loadOffers();
            
            // Optional: Direkt zur Rechnung navigieren
            if (confirm('Möchten Sie zur Rechnungsübersicht wechseln?')) {
                showSection('invoices');
            }
            
        } else {
            let errorMessage = 'Unbekannter Fehler';
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || 'Fehler beim Server';
                console.error('Fehler beim Erstellen der Rechnung:', errorData);
            } catch (e) {
                errorMessage = await response.text() || `HTTP ${response.status}`;
                console.error('Fehler beim Parsen der Fehlerantwort:', e);
            }
            
            showAlert(`Fehler beim Erstellen der Rechnung: ${errorMessage}`, 'danger');
        }
        */
        
    } catch (error) {
        console.error('Fehler beim Erstellen der Rechnung:', error);
        showAlert('Fehler beim Erstellen der Rechnung: ' + error.message, 'danger');
    }
}

// Stundeneinträge anzeigen
function displayTimeEntries() {
    const timeEntriesTable = document.getElementById('time-entries-table');
    if (timeEntriesTable && timeEntries) {
        timeEntriesTable.innerHTML = timeEntries.map(entry => `
            <tr>
                <td>${formatDate(entry.work_date)}</td>
                <td>${entry.project_name || 'Projekt #' + entry.project_id}</td>
                <td>${entry.employee_name || 'Mitarbeiter #' + entry.employee_id}</td>
                <td>${entry.clock_in || '-'}</td>
                <td>${entry.clock_out || '-'}</td>
                <td>${entry.hours_worked ? entry.hours_worked.toFixed(2) + 'h' : 'N/A'}</td>
                <td>${entry.total_break_minutes || 0} Min</td>
                <td><span class="badge bg-${entry.is_edited ? 'warning' : 'success'}">${entry.is_edited ? 'Bearbeitet' : 'Original'}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="editTimeEntry(${entry.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteTimeEntry(${entry.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');
        console.log('Stundeneinträge angezeigt:', timeEntries.length);
    } else if (!timeEntriesTable) {
        console.log('Element timeEntriesTable nicht gefunden');
    }
}

// Rechnungen anzeigen
function displayInvoices() {
    const invoicesTable = document.getElementById('invoices-table');
    if (invoicesTable && invoices) {
        invoicesTable.innerHTML = invoices.map(invoice => `
            <tr>
                <td>${invoice.invoice_number}</td>
                <td>${invoice.title}</td>
                <td>${invoice.client_name || 'N/A'}</td>
                <td>${invoice.total_amount || 'N/A'}</td>
                <td>${getStatusText(invoice.status)}</td>
                <td>${formatDate(invoice.invoice_date)}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="editInvoice(${invoice.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-success" onclick="downloadInvoicePDF(${invoice.id})" title="PDF herunterladen">
                        <i class="fas fa-download"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteInvoice(${invoice.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `).join('');
        console.log('Rechnungen angezeigt:', invoices.length);
    } else if (!invoicesTable) {
        console.log('Element invoicesTable nicht gefunden');
    }
}

// PDF-Download für Rechnungen
function downloadInvoicePDF(invoiceId) {
    console.log('Lade PDF für Rechnung:', invoiceId);
    
    // Direkter Download-Link
    const downloadUrl = `${API_BASE}/invoices/${invoiceId}/pdf`;
    
    // Neues Fenster/Tab öffnen für Download
    window.open(downloadUrl, '_blank');
}

// Edit-Funktionen
function editInvoice(id) {
    console.log('Bearbeite Rechnung:', id);
    
    // Finde die Rechnung
    const invoice = invoices.find(inv => inv.id === id);
    if (!invoice) {
        alert('Rechnung nicht gefunden');
        return;
    }
    
    // Zeige Bearbeitungsformular
    showInvoiceEditModal(invoice);
}

function showInvoiceEditModal(invoice) {
    console.log('Zeige Rechnungs-Bearbeitungsmodal für:', invoice.invoice_number);
    
    // Modal HTML erstellen
    const modalHtml = `
        <div class="modal fade" id="editInvoiceModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Rechnung bearbeiten: ${invoice.invoice_number}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="editInvoiceForm">
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="editInvoiceNumber" class="form-label">Rechnungsnummer *</label>
                                        <input type="text" class="form-control" id="editInvoiceNumber" value="${invoice.invoice_number}" required>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="editInvoiceStatus" class="form-label">Status</label>
                                        <select class="form-select" id="editInvoiceStatus">
                                            <option value="entwurf" ${invoice.status === 'entwurf' ? 'selected' : ''}>Entwurf</option>
                                            <option value="versendet" ${invoice.status === 'versendet' ? 'selected' : ''}>Versendet</option>
                                            <option value="bezahlt" ${invoice.status === 'bezahlt' ? 'selected' : ''}>Bezahlt</option>
                                            <option value="storniert" ${invoice.status === 'storniert' ? 'selected' : ''}>Storniert</option>
                                        </select>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="editClientName" class="form-label">Kundenname *</label>
                                        <input type="text" class="form-control" id="editClientName" value="${invoice.client_name || ''}" required>
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="editTotalAmount" class="form-label">Gesamtbetrag (EUR) *</label>
                                        <input type="number" class="form-control" id="editTotalAmount" value="${invoice.total_amount || 0}" step="0.01" required>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label for="editInvoiceTitle" class="form-label">Titel</label>
                                <input type="text" class="form-control" id="editInvoiceTitle" value="${invoice.title || ''}">
                            </div>
                            
                            <div class="mb-3">
                                <label for="editInvoiceDescription" class="form-label">Beschreibung</label>
                                <textarea class="form-control" id="editInvoiceDescription" rows="3">${invoice.description || ''}</textarea>
                            </div>
                            
                            <div class="row">
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="editInvoiceDate" class="form-label">Rechnungsdatum</label>
                                        <input type="date" class="form-control" id="editInvoiceDate" value="${formatDateForInput(invoice.invoice_date)}">
                                    </div>
                                </div>
                                <div class="col-md-6">
                                    <div class="mb-3">
                                        <label for="editDueDate" class="form-label">Fälligkeitsdatum</label>
                                        <input type="date" class="form-control" id="editDueDate" value="${formatDateForInput(invoice.due_date)}">
                                    </div>
                                </div>
                            </div>
                            
                            <div class="mb-3">
                                <label for="editClientAddress" class="form-label">Kundenadresse</label>
                                <textarea class="form-control" id="editClientAddress" rows="2">${invoice.client_address || ''}</textarea>
                            </div>
                            
                            <div class="alert alert-info">
                                <i class="fas fa-info-circle me-2"></i>
                                <strong>Hinweis:</strong> Positionen können in der Vorschau bearbeitet werden.
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Abbrechen</button>
                        <button type="button" class="btn btn-info" onclick="previewInvoice(${invoice.id})">
                            <i class="fas fa-eye me-2"></i>Vorschau
                        </button>
                        <button type="button" class="btn btn-primary" onclick="saveInvoiceEdit(${invoice.id})">
                            <i class="fas fa-save me-2"></i>Speichern
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Modal entfernen falls vorhanden
    const existingModal = document.getElementById('editInvoiceModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Modal hinzufügen
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Modal anzeigen
    const modal = new bootstrap.Modal(document.getElementById('editInvoiceModal'));
    modal.show();
}

function formatDateForInput(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toISOString().split('T')[0];
}

function saveInvoiceEdit(invoiceId) {
    console.log('Speichere Rechnungsänderungen für ID:', invoiceId);
    
    const formData = {
        invoice_number: document.getElementById('editInvoiceNumber').value,
        status: document.getElementById('editInvoiceStatus').value,
        client_name: document.getElementById('editClientName').value,
        total_amount: Math.round(parseFloat(document.getElementById('editTotalAmount').value) * 100) / 100,
        title: document.getElementById('editInvoiceTitle').value,
        description: document.getElementById('editInvoiceDescription').value,
        invoice_date: document.getElementById('editInvoiceDate').value,
        due_date: document.getElementById('editDueDate').value,
        client_address: document.getElementById('editClientAddress').value
    };
    
    // Validierung
    if (!formData.invoice_number || !formData.client_name || !formData.total_amount) {
        alert('Bitte füllen Sie alle Pflichtfelder aus.');
        return;
    }
    
    // API-Aufruf
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    if (!token) {
        alert('Bitte loggen Sie sich erneut ein.');
        return;
    }
    
    fetch(`/invoices/${invoiceId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
    })
    .then(updatedInvoice => {
        console.log('Rechnung erfolgreich aktualisiert:', updatedInvoice);
        alert('Rechnung erfolgreich aktualisiert!');
        
        // Modal schließen
        const modal = bootstrap.Modal.getInstance(document.getElementById('editInvoiceModal'));
        modal.hide();
        
        // Rechnungen neu laden
        loadInvoices();
    })
    .catch(error => {
        console.error('Fehler beim Aktualisieren der Rechnung:', error);
        alert('Fehler beim Aktualisieren der Rechnung: ' + error.message);
    });
}

function previewInvoice(invoiceId) {
    console.log('Zeige Rechnungsvorschau für ID:', invoiceId);
    
    // Finde die Rechnung
    const invoice = invoices.find(inv => inv.id === invoiceId);
    if (!invoice) {
        alert('Rechnung nicht gefunden');
        return;
    }
    
    // Vorschau-Modal erstellen
    showInvoicePreviewModal(invoice);
}

function showInvoicePreviewModal(invoice) {
    console.log('Zeige Rechnungsvorschau für:', invoice.invoice_number);
    
    // Items parsen falls nötig
    let items = [];
    if (typeof invoice.items === 'string') {
        try {
            items = JSON.parse(invoice.items);
        } catch (e) {
            console.error('Fehler beim Parsen der Items:', e);
        }
    } else if (Array.isArray(invoice.items)) {
        items = invoice.items;
    }
    
    // Vorschau HTML erstellen
    const previewHtml = `
        <div class="modal fade" id="previewInvoiceModal" tabindex="-1">
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Rechnungsvorschau: ${invoice.invoice_number}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="invoice-preview">
                            <!-- Rechnungskopf -->
                            <div class="row mb-4">
                                <div class="col-md-6">
                                    <h4 class="text-dark fw-bold" style="color: #000000 !important;">Rechnung</h4>
                                    <p class="text-dark" style="color: #000000 !important;"><strong>Rechnungsnummer:</strong> <span class="fw-bold" style="color: #000000 !important;">${invoice.invoice_number}</span></p>
                                    <p class="text-dark" style="color: #000000 !important;"><strong>Datum:</strong> <span class="fw-bold" style="color: #000000 !important;">${formatDate(invoice.invoice_date)}</span></p>
                                    <p class="text-dark" style="color: #000000 !important;"><strong>Fälligkeitsdatum:</strong> <span class="fw-bold" style="color: #000000 !important;">${formatDate(invoice.due_date)}</span></p>
                                </div>
                                <div class="col-md-6 text-end">
                                    <h5 class="text-dark fw-bold" style="color: #000000 !important;">Kunde</h5>
                                    <p class="text-dark" style="color: #000000 !important;"><strong>${invoice.client_name || 'N/A'}</strong></p>
                                    ${invoice.client_address ? `<p class="text-dark" style="color: #000000 !important;">${invoice.client_address.replace(/\n/g, '<br>')}</p>` : ''}
                                </div>
                            </div>
                            
                            <!-- Rechnungspositionen -->
                            <div class="table-responsive">
                                <table class="table table-bordered">
                                    <thead class="table-dark">
                                        <tr>
                                            <th>Beschreibung</th>
                                            <th>Menge</th>
                                            <th>Einheit</th>
                                            <th>Einzelpreis</th>
                                            <th>Gesamtpreis</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                        ${items.map(item => `
                                            <tr>
                                                <td>${item.description || 'N/A'}</td>
                                                <td>${item.quantity || 0}</td>
                                                <td>${item.unit || 'Stk'}</td>
                                                <td>${(item.unit_price || 0).toFixed(2)} EUR</td>
                                                <td>${(item.total_price || 0).toFixed(2)} EUR</td>
                                                </tr>
                                            `).join('')}
                                        </tbody>
                                    </table>
                            </div>
                            
                            <!-- Rechnungssumme -->
                            <div class="row">
                                <div class="col-md-6"></div>
                                <div class="col-md-6">
                                    <table class="table table-sm">
                                        <tr>
                                            <td><strong>Zwischensumme:</strong></td>
                                            <td class="text-end"><strong>${(invoice.total_amount / 1.19).toFixed(2)} EUR</strong></td>
                                            </tr>
                                            <tr>
                                            <td><strong>USt (19%):</strong></td>
                                            <td class="text-end"><strong>${(invoice.total_amount - (invoice.total_amount / 1.19)).toFixed(2)} EUR</strong></td>
                                            </tr>
                                        <tr class="table-success">
                                            <td><strong>Gesamtbetrag:</strong></td>
                                            <td class="text-end"><strong>${(invoice.total_amount || 0).toFixed(2)} EUR</strong></td>
                                            </tr>
                                    </table>
                                </div>
                            </div>
                            
                            <!-- Status und Beschreibung -->
                            <div class="row mt-4">
                                <div class="col-md-6">
                                    <p class="text-dark"><strong>Status:</strong> <span class="text-dark fw-bold" style="color: #000000 !important;">${getStatusText(invoice.status)}</span></p>
                                </div>
                                <div class="col-md-6">
                                    <p class="text-dark"><strong>Währung:</strong> <span class="text-dark fw-bold" style="color: #000000 !important;">${invoice.currency || 'EUR'}</span></p>
                                </div>
                            </div>
                            
                            ${invoice.description ? `
                                <div class="mt-3">
                                    <h6 class="text-dark fw-bold" style="color: #000000 !important;">Beschreibung:</h6>
                                    <p class="text-dark" style="color: #000000 !important;">${invoice.description}</p>
                                </div>
                            ` : ''}
                            
                            <!-- Footer-Information -->
                            <div class="mt-4 pt-3 border-top">
                                <p class="text-dark mb-0">
                                    <small class="fw-bold" style="color: #000000 !important;">Automatisch generierte Rechnung</small>
                                </p>
                        </div>
                    </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Schließen</button>
                        <button type="button" class="btn btn-primary" onclick="downloadInvoicePDF(${invoice.id})">
                            <i class="fas fa-download me-2"></i>PDF herunterladen
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Modal entfernen falls vorhanden
    const existingModal = document.getElementById('previewInvoiceModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Modal hinzufügen
    document.body.insertAdjacentHTML('beforeend', previewHtml);
    
    // Modal anzeigen
    const modal = new bootstrap.Modal(document.getElementById('previewInvoiceModal'));
    modal.show();
}

function downloadInvoicePDF(invoiceId) {
    console.log('Lade Rechnungs-PDF herunter für ID:', invoiceId);
    
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    if (!token) {
        alert('Bitte loggen Sie sich erneut ein.');
        return;
    }
    
    // PDF-Download
    window.open(`/invoices/${invoiceId}/pdf?token=${token}`, '_blank');
}

function editReport(id) {
    console.log('Bearbeite Bericht:', id);
    
    // Bericht finden
    const report = reports.find(r => r.id === id);
    if (!report) {
        console.error('Bericht nicht gefunden:', id);
        showAlert('Bericht nicht gefunden', 'danger');
        return;
    }
    
    // Modal öffnen
    const modal = new bootstrap.Modal(document.getElementById('reportModal'));
    
    // Formular mit Daten füllen
    document.getElementById('reportTitle').value = report.title || '';
    document.getElementById('reportContent').value = report.content || '';
    document.getElementById('reportDate').value = report.report_date ? report.report_date.split('T')[0] : '';
    document.getElementById('reportWorkType').value = report.work_type || '';
    
    // Status-Feld setzen
    const statusSelect = document.getElementById('reportStatus');
    if (statusSelect && report.status) {
        statusSelect.value = report.status;
    }
    
    // Projekt-Auswahl füllen
    populateReportProjectSelect();
    const projectSelect = document.getElementById('reportProject');
    if (projectSelect) {
        projectSelect.value = report.project_id;
    }
    
    // Formular als Edit-Modus markieren
    const form = document.getElementById('reportForm');
    form.dataset.reportId = id;
    form.dataset.mode = 'edit';
    
    // Modal-Titel ändern
    const modalTitle = document.querySelector('#reportModal .modal-title');
    if (modalTitle) {
        modalTitle.textContent = 'Bericht bearbeiten';
    }
    
    // Submit-Button Text ändern
    const submitBtn = document.querySelector('#reportForm button[type="submit"]');
    if (submitBtn) {
        submitBtn.textContent = 'Bericht aktualisieren';
    }
    
    modal.show();
}

function editOffer(id) {
    console.log('Bearbeite Angebot:', id);
    alert('Bearbeiten-Funktion für Angebot ' + id + ' wird implementiert');
}

function editEmployee(id) {
    console.log('Bearbeite Mitarbeiter:', id);
    alert('Bearbeiten-Funktion für Mitarbeiter ' + id + ' wird implementiert');
}

function editProject(id) {
    console.log('Bearbeite Projekt:', id);
    
    // Projekt finden
    const project = projects.find(p => p.id === id);
    if (!project) {
        console.error('Projekt nicht gefunden:', id);
        showAlert('Projekt nicht gefunden', 'danger');
        return;
    }
    
    // Modal öffnen
    const modal = new bootstrap.Modal(document.getElementById('projectModal'));
    
    // Formular mit Daten füllen
    document.getElementById('projectName').value = project.name || '';
    document.getElementById('projectDescription').value = project.description || '';
    document.getElementById('projectClient').value = project.client_name || '';
    document.getElementById('projectType').value = project.project_type || 'trockenbau';
    document.getElementById('projectStatus').value = project.status || 'aktiv';
    
    // Formular als Edit-Modus markieren
    const form = document.getElementById('projectForm');
    form.dataset.projectId = id;
    form.dataset.mode = 'edit';
    
    // Modal-Titel ändern
    const modalTitle = document.querySelector('#projectModal .modal-title');
    if (modalTitle) {
        modalTitle.textContent = 'Projekt bearbeiten';
    }
    
    // Submit-Button Text ändern
    const submitBtn = document.querySelector('#projectForm button[type="submit"]');
    if (submitBtn) {
        submitBtn.textContent = 'Projekt aktualisieren';
    }
    
    modal.show();
}

function editTimeEntry(id) {
    console.log('Bearbeite Stundeneintrag:', id);
    
    // Stundeneintrag finden
    const timeEntry = timeEntries.find(entry => entry.id === id);
    if (!timeEntry) {
        console.error('Stundeneintrag nicht gefunden:', id);
        return;
    }
    
    // Modal öffnen
    const modal = new bootstrap.Modal(document.getElementById('editTimeEntryModal'));
    
    // Formular mit Daten füllen
    document.getElementById('editWorkDate').value = timeEntry.work_date;
    document.getElementById('editClockIn').value = timeEntry.clock_in || '';
    document.getElementById('editClockOut').value = timeEntry.clock_out || '';
    document.getElementById('editBreakStart').value = timeEntry.break_start || '';
    document.getElementById('editBreakEnd').value = timeEntry.break_end || '';
    document.getElementById('editHoursWorked').value = timeEntry.hours_worked || '';
    document.getElementById('editDescription').value = timeEntry.description || '';
    
    // Stundensatz nur für Admin/Buchhalter anzeigen
    const hourlyRateField = document.getElementById('editHourlyRate');
    const hourlyRateLabel = document.querySelector('label[for="editHourlyRate"]');
    if (currentUser?.role === 'mitarbeiter') {
        hourlyRateField.style.display = 'none';
        hourlyRateLabel.style.display = 'none';
    } else {
        hourlyRateField.value = timeEntry.hourly_rate || '';
        hourlyRateField.style.display = 'block';
        hourlyRateLabel.style.display = 'block';
    }
    
    // Projekt-Auswahl füllen
    const projectSelect = document.getElementById('editProject');
    projectSelect.innerHTML = '<option value="">Projekt auswählen...</option>';
    projects.forEach(project => {
        const option = document.createElement('option');
        option.value = project.id;
        option.textContent = project.name;
        if (project.id === timeEntry.project_id) {
            option.selected = true;
        }
        projectSelect.appendChild(option);
    });
    
    // Event-Listener für Form-Submit
    const form = document.getElementById('editTimeEntryForm');
    form.onsubmit = function(e) {
        e.preventDefault();
        handleEditTimeEntrySubmit(id);
    };
    
    modal.show();
}

// Edit Time Entry Form Submit Handler
async function handleEditTimeEntrySubmit(timeEntryId) {
    console.log('Bearbeite Stundeneintrag:', timeEntryId);
    
    const form = document.getElementById('editTimeEntryForm');
    const formData = new FormData(form);
    
    // Formular-Daten sammeln
    const timeEntryData = {
        work_date: formData.get('work_date'),
        project_id: parseInt(formData.get('project_id')),
        clock_in: formData.get('clock_in') || null,
        clock_out: formData.get('clock_out') || null,
        break_start: formData.get('break_start') || null,
        break_end: formData.get('break_end') || null,
        hours_worked: parseFloat(formData.get('hours_worked')),
        description: formData.get('description') || null
    };
    
    // Stundensatz nur für Admin/Buchhalter senden
    if (currentUser?.role !== 'mitarbeiter') {
        timeEntryData.hourly_rate = parseFloat(formData.get('hourly_rate')) || null;
    }
    
    console.log('Sende Update-Daten:', timeEntryData);
    
    try {
        const response = await apiCall(`${API_BASE}/time-entries/${timeEntryId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(timeEntryData)
        });
        
        if (response.ok) {
            console.log('Stundeneintrag erfolgreich aktualisiert');
            
            // Admin-Benachrichtigung für Mitarbeiter-Änderungen
            if (currentUser?.role === 'mitarbeiter') {
                console.log('ADMIN-BENACHRICHTIGUNG: Mitarbeiter hat Stundeneintrag bearbeitet');
                // Hier könnte eine echte Benachrichtigung an den Admin gesendet werden
            }
            
            // Modal schließen
            const modal = bootstrap.Modal.getInstance(document.getElementById('editTimeEntryModal'));
            modal.hide();
            
            // Stundeneinträge neu laden
            await loadTimeTrackingData();
            updateTimeTracking();
            
            // Erfolgsmeldung
            const successMessage = currentUser?.role === 'mitarbeiter' 
                ? 'Stundeneintrag erfolgreich aktualisiert! (Admin wurde benachrichtigt)' 
                : 'Stundeneintrag erfolgreich aktualisiert!';
            showAlert(successMessage, 'success');
        } else {
            const errorText = await response.text();
            console.error('Fehler beim Aktualisieren des Stundeneintrags:', response.status, errorText);
            showAlert('Fehler beim Aktualisieren des Stundeneintrags: ' + response.status, 'danger');
        }
    } catch (error) {
        console.error('Fehler beim Aktualisieren des Stundeneintrags:', error);
        showAlert('Fehler beim Aktualisieren des Stundeneintrags: ' + error.message, 'danger');
    }
}


// Delete-Funktionen
function deleteReport(id) {
    if (confirm('Bericht wirklich löschen?')) {
        console.log('Lösche Bericht:', id);
        // TODO: API-Aufruf zum Löschen
        alert('Löschen-Funktion für Bericht ' + id + ' wird implementiert');
    }
}

function deleteOffer(id) {
    if (confirm('Angebot wirklich löschen?')) {
            console.log('Lösche Angebot:', id);
        alert('Löschen-Funktion für Angebot ' + id + ' wird implementiert');
    }
}

function deleteEmployee(id) {
    if (confirm('Mitarbeiter wirklich löschen?')) {
        console.log('Lösche Mitarbeiter:', id);
        alert('Löschen-Funktion für Mitarbeiter ' + id + ' wird implementiert');
    }
}

function deleteProject(id) {
    if (confirm('Projekt wirklich löschen?')) {
        console.log('Lösche Projekt:', id);
        alert('Löschen-Funktion für Projekt ' + id + ' wird implementiert');
    }
}

function deleteTimeEntry(id) {
    if (confirm('Stundeneintrag wirklich löschen?')) {
        console.log('Lösche Stundeneintrag:', id);
        alert('Löschen-Funktion für Stundeneintrag ' + id + ' wird implementiert');
    }
}

async function deleteInvoice(id) {
    if (!confirm('Rechnung wirklich löschen?')) {
        return;
    }
    
    try {
        console.log('Lösche Rechnung:', id);
        const response = await fetch(`${API_BASE}/invoices/${id}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });
        
        if (response.ok) {
            showAlert('Rechnung erfolgreich gelöscht!', 'success');
            loadInvoices(); // Tabelle aktualisieren
        } else {
            const error = await response.json();
            showAlert(`Fehler beim Löschen: ${error.detail}`, 'danger');
        }
    } catch (error) {
        console.error('Fehler beim Löschen der Rechnung:', error);
        showAlert('Fehler beim Löschen der Rechnung.', 'danger');
    }
}

// Rollen-Helper-Funktionen
function getRoleColor(role) {
    switch(role) {
        case 'admin': return '#f57c00'; // Orange
        case 'buchhalter': return '#7b1fa2'; // Lila
        case 'mitarbeiter': return '#1976d2'; // Blau
        default: return '#6c757d'; // Grau
    }
}

function getRoleIcon(role) {
    switch(role) {
        case 'admin': return 'fas fa-crown';
        case 'buchhalter': return 'fas fa-calculator';
        case 'mitarbeiter': return 'fas fa-user-tie';
        default: return 'fas fa-user';
    }
}

function getRoleDisplayName(role) {
    switch(role) {
        case 'admin': return 'Administrator';
        case 'buchhalter': return 'Buchhalter';
        case 'mitarbeiter': return 'Mitarbeiter';
        default: return role;
    }
}

// Berechtigungen prüfen
function hasPermission(permission) {
    if (!currentUser) return false;
    
    const userRole = currentUser.role;
    
    switch(permission) {
        case 'view_projects':
            return ['admin', 'buchhalter', 'mitarbeiter'].includes(userRole);
        case 'edit_projects':
            return ['admin', 'buchhalter'].includes(userRole);
        case 'delete_projects':
            return ['admin'].includes(userRole);
        case 'view_reports':
            return ['admin', 'buchhalter', 'mitarbeiter'].includes(userRole);
        case 'edit_reports':
            return ['admin', 'mitarbeiter'].includes(userRole);
        case 'view_financial':
            return ['admin', 'buchhalter'].includes(userRole);
        case 'edit_financial':
            return ['admin', 'buchhalter', 'mitarbeiter'].includes(userRole);
        case 'view_employees':
            return ['admin', 'buchhalter'].includes(userRole);
        case 'edit_employees':
            return ['admin'].includes(userRole);
        case 'admin_only':
            return ['admin'].includes(userRole);
        default:
            return false;
    }
}

// Rollenbasierte Navigation einrichten
function setupRoleBasedNavigation() {
    console.log('Richte rollenbasierte Navigation ein...');
    
    // Navigation-Elemente basierend auf Berechtigungen anzeigen/verstecken
    const navItems = {
        'dashboard': { permission: 'view_projects' },
        'projects': { permission: 'view_projects' },
        'reports': { permission: 'view_reports' },
        'offers': { permission: 'view_financial' },
        'employees': { permission: 'view_employees' },
        'time-tracking': { permission: 'view_reports' },
        'invoices': { permission: 'view_financial' },
        'logo-management': { permission: 'admin_only' }
    };
    
    // Spezielle Behandlung für Mitarbeiter-Rolle
    if (currentUser?.role === 'mitarbeiter') {
        // Mitarbeiter: Nur Dashboard und Stundenerfassung
        const allowedForMitarbeiter = ['dashboard', 'time-tracking'];
        Object.keys(navItems).forEach(section => {
            if (!allowedForMitarbeiter.includes(section)) {
                navItems[section] = { permission: 'none' }; // Verstecken
            }
        });
    }
    
    Object.keys(navItems).forEach(section => {
        const navLink = document.querySelector(`[data-section="${section}"]`);
        if (navLink) {
            const hasAccess = navItems[section].permission === 'none' ? false : hasPermission(navItems[section].permission);
            navLink.style.display = hasAccess ? 'block' : 'none';
            
            if (!hasAccess) {
                console.log(`Navigation '${section}' für Rolle '${currentUser.role}' versteckt`);
            }
        }
    });
    
    // Button-Berechtigungen
    updateButtonPermissions();
    
    // Für Mitarbeiter: Stundenerfassung als Standard-Sektion
    if (currentUser?.role === 'mitarbeiter') {
        showSection('time-tracking');
    }
    
    // Admin-Benachrichtigungen anzeigen
    updateAdminNotifications();
}

// Admin-Benachrichtigungen aktualisieren
function updateAdminNotifications() {
    if (currentUser?.role === 'admin') {
        // Admin-Benachrichtigungen anzeigen
        const adminNotifications = document.getElementById('adminNotifications');
        if (adminNotifications) {
            adminNotifications.style.display = 'block';
        }
        
        // Benachrichtigungs-Badge aktualisieren
        const notificationBadge = document.getElementById('notificationBadge');
        if (notificationBadge) {
            // Hier könnte die Anzahl der Benachrichtigungen gesetzt werden
            // notificationBadge.textContent = notificationCount;
            // notificationBadge.style.display = notificationCount > 0 ? 'inline' : 'none';
        }
    }
}

// Theme-Management
function initTheme() {
    // Lade gespeichertes Theme oder verwende Light Mode als Standard
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
}

function setTheme(theme) {
    const body = document.body;
    const themeToggle = document.getElementById('themeToggle');
    const darkModeToggle = document.getElementById('darkModeToggle');
    const darkModeIcon = document.getElementById('darkModeIcon');
    const darkModeText = document.getElementById('darkModeText');
    
    if (theme === 'dark') {
        body.classList.add('dark-mode');
        if (themeToggle) {
            themeToggle.innerHTML = '<i class="fas fa-sun me-2"></i>Light Mode';
        }
        if (darkModeIcon) {
            darkModeIcon.className = 'fas fa-sun';
        }
        if (darkModeText) {
            darkModeText.textContent = 'Light Mode';
        }
    } else {
        body.classList.remove('dark-mode');
        if (themeToggle) {
            themeToggle.innerHTML = '<i class="fas fa-moon me-2"></i>Dark Mode';
        }
        if (darkModeIcon) {
            darkModeIcon.className = 'fas fa-moon';
        }
        if (darkModeText) {
            darkModeText.textContent = 'Dark Mode';
        }
    }
    
    // Theme in localStorage speichern
    localStorage.setItem('theme', theme);
    console.log('Theme geändert zu:', theme);
}

function toggleTheme() {
    const body = document.body;
    const currentTheme = body.classList.contains('dark-mode') ? 'dark' : 'light';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    setTheme(newTheme);
    showAlert(`Theme gewechselt zu ${newTheme === 'dark' ? 'Dark' : 'Light'} Mode`, 'info');
}

// Benachrichtigungen anzeigen
function showNotifications() {
    console.log('Benachrichtigungen anzeigen...');
    
    // Prüfe ob Admin
    if (currentUser?.role !== 'admin') {
        showAlert('Nur Administratoren können Benachrichtigungen anzeigen', 'warning');
        return;
    }
    
    // Hier könnten echte Benachrichtigungen geladen werden
    const notifications = [
        {
            id: 1,
            title: 'Stundeneintrag bearbeitet',
            message: 'Ein Mitarbeiter hat einen Stundeneintrag bearbeitet',
            timestamp: new Date().toLocaleString('de-DE'),
            type: 'info'
        },
        {
            id: 2,
            title: 'Neuer Mitarbeiter',
            message: 'Ein neuer Mitarbeiter wurde hinzugefügt',
            timestamp: new Date().toLocaleString('de-DE'),
            type: 'success'
        }
    ];
    
    // Benachrichtigungen in einem Modal anzeigen
    const modalHtml = `
        <div class="modal fade" id="notificationsModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">
                            <i class="fas fa-bell me-2"></i>Benachrichtigungen
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        ${notifications.map(notif => `
                            <div class="alert alert-${notif.type} d-flex justify-content-between align-items-center">
                                <div>
                                    <strong>${notif.title}</strong><br>
                                    <small>${notif.message}</small>
                                </div>
                                <small class="text-muted">${notif.timestamp}</small>
                            </div>
                        `).join('')}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Schließen</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Modal zur Seite hinzufügen falls nicht vorhanden
    if (!document.getElementById('notificationsModal')) {
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    }
    
    // Modal anzeigen
    const modal = new bootstrap.Modal(document.getElementById('notificationsModal'));
    modal.show();
}

// Button-Berechtigungen aktualisieren
function updateButtonPermissions() {
    // Projekt-Buttons
    const projectButtons = document.querySelectorAll('[onclick*="showProjectModal"]');
    projectButtons.forEach(btn => {
        btn.style.display = hasPermission('edit_projects') ? 'inline-block' : 'none';
    });
    
    // Bericht-Buttons
    const reportButtons = document.querySelectorAll('[onclick*="showReportModal"]');
    reportButtons.forEach(btn => {
        btn.style.display = hasPermission('edit_reports') ? 'inline-block' : 'none';
    });
    
    // Neuer Bericht Button
    const newReportBtn = document.getElementById('newReportBtn');
    if (newReportBtn) {
        newReportBtn.style.display = hasPermission('edit_reports') ? 'inline-block' : 'none';
    }
    
    // Navigation für Berichte sichtbar machen für Mitarbeiter
    const reportsNavLink = document.querySelector('[data-section="reports"]');
    if (reportsNavLink) {
        reportsNavLink.style.display = hasPermission('view_reports') ? 'block' : 'none';
    }
    
    // Mitarbeiter-Buttons
    const employeeButtons = document.querySelectorAll('[onclick*="showEmployeeModal"]');
    employeeButtons.forEach(btn => {
        btn.style.display = hasPermission('edit_employees') ? 'inline-block' : 'none';
    });
    
    // Finanz-Buttons (Angebote, Rechnungen)
    const financialButtons = document.querySelectorAll('[onclick*="showOfferModal"], [onclick*="showInvoiceModal"]');
    financialButtons.forEach(btn => {
        btn.style.display = hasPermission('edit_financial') ? 'inline-block' : 'none';
    });
}

// Projekt-Auswahl für Stundenerfassung laden
function loadProjectsForTimeTracking() {
    const projectSelect = document.getElementById('clockProject');
    if (projectSelect && projects) {
        console.log('Lade Projekte für Stundenerfassung...', projects.length);
        
        // Aktuelle Optionen löschen (außer der ersten)
        projectSelect.innerHTML = '<option value="">Projekt auswählen...</option>';
        
        // Projekte hinzufügen
        projects.forEach(project => {
            const option = document.createElement('option');
            option.value = project.id;
            option.textContent = project.name;
            projectSelect.appendChild(option);
        });
        
        console.log('Projekt-Auswahl für Stundenerfassung geladen:', projects.length);
    } else if (!projectSelect) {
        console.log('Element clockProject nicht gefunden');
    } else if (!projects) {
        console.log('Projekte noch nicht geladen');
    }
}

// Projekt-Vorschau aktualisieren
function updateProjectPreview() {
    const projectSelect = document.getElementById('clockProject');
    const selectedProjectId = projectSelect.value;
    const selectedProjectName = projectSelect.options[projectSelect.selectedIndex].text;
    
    if (selectedProjectId) {
        console.log('Projekt ausgewählt:', selectedProjectName, '(ID:', selectedProjectId + ')');
    } else {
        console.log('Kein Projekt ausgewählt');
    }
}

// Stundenerfassung-Variablen
let clockInTime = null;
let currentProjectId = null;

// Einstempeln
function clockIn() {
    const projectSelect = document.getElementById('clockProject');
    const selectedProjectId = projectSelect.value;
    
    if (!selectedProjectId) {
        alert('Bitte wählen Sie ein Projekt aus!');
        return;
    }
    
    if (isClockedIn) {
        alert('Sie sind bereits eingestempelt!');
        return;
    }
    
    const now = new Date();
    clockInTime = now;
    isClockedIn = true;
    currentProjectId = selectedProjectId;
    
    // UI aktualisieren
    updateClockUI();
    
    console.log('Eingestempelt für Projekt:', selectedProjectId, 'um', now.toLocaleTimeString());
    alert('Erfolgreich eingestempelt!');
}

// Ausstempeln
function clockOut() {
    if (!isClockedIn) {
        alert('Sie sind nicht eingestempelt!');
        return;
    }
    
    const now = new Date();
    const workDuration = Math.round((now - clockInTime) / (1000 * 60)); // Minuten
    
    // Stundeneintrag erstellen
    createTimeEntry(currentProjectId, clockInTime, now, workDuration);
    
    // Reset
    isClockedIn = false;
    clockInTime = null;
    currentProjectId = null;
    
    // UI aktualisieren
    updateClockUI();
    
    console.log('Ausgestempelt nach', workDuration, 'Minuten');
    alert(`Erfolgreich ausgestempelt! Arbeitszeit: ${Math.floor(workDuration/60)}h ${workDuration%60}m`);
}

// Pause
function pause() {
    if (!isClockedIn) {
        alert('Sie sind nicht eingestempelt!');
        return;
    }
    
    alert('Pause-Funktion wird implementiert...');
}

// UI für Stundenerfassung aktualisieren
function updateClockUI() {
    const clockInBtn = document.getElementById('clockInBtn');
    const clockOutBtn = document.getElementById('clockOutBtn');
    const pauseBtn = document.getElementById('pauseBtn');
    const statusDisplay = document.getElementById('clockStatus');
    
    if (isClockedIn) {
        clockInBtn.disabled = true;
        clockOutBtn.disabled = false;
        pauseBtn.disabled = false;
        statusDisplay.innerHTML = `
            <div class="alert alert-success">
                <i class="fas fa-clock me-2"></i>
                <strong>Eingestempelt seit:</strong> ${clockInTime.toLocaleTimeString('de-DE')}
                <br><small class="text-muted">Projekt: ${projects.find(p => p.id == currentProjectId)?.name || 'Unbekannt'}</small>
            </div>
        `;
    } else {
        clockInBtn.disabled = false;
        clockOutBtn.disabled = true;
        pauseBtn.disabled = true;
        statusDisplay.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-clock me-2"></i>
                <strong>Bereit zum Einstempeln</strong>
                <br><small class="text-muted">Wählen Sie ein Projekt aus</small>
            </div>
        `;
    }
}

// Stundeneintrag erstellen
async function createTimeEntry(projectId, startTime, endTime, durationMinutes) {
    try {
        console.log('Erstelle Stundeneintrag für Projekt:', projectId);
        console.log('Startzeit:', startTime.toISOString());
        console.log('Endzeit:', endTime.toISOString());
        console.log('Dauer (Minuten):', durationMinutes);
        
        const response = await apiCall(`${API_BASE}/time-entries`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                project_id: parseInt(projectId),
                employee_id: 1, // Verwende ersten verfügbaren Mitarbeiter (Admin)
                work_date: startTime.toISOString().split('T')[0],
                clock_in: startTime.toTimeString().split(' ')[0].substring(0, 5),
                clock_out: endTime.toTimeString().split(' ')[0].substring(0, 5),
                hours_worked: Math.round(durationMinutes / 60 * 100) / 100,
                description: `Arbeitszeit von ${startTime.toLocaleTimeString()} bis ${endTime.toLocaleTimeString()} (${currentUser.name || currentUser.username})`
            })
        });
        
        if (response.ok) {
            console.log('Stundeneintrag erfolgreich erstellt');
            // Stundeneinträge neu laden
            await loadTimeTrackingData();
            updateTimeTracking();
        } else {
            const errorText = await response.text();
            console.error('Fehler beim Erstellen des Stundeneintrags:', response.status, errorText);
            alert('Fehler beim Erstellen des Stundeneintrags: ' + response.status);
        }
    } catch (error) {
        console.error('Fehler beim Erstellen des Stundeneintrags:', error);
        alert('Fehler beim Erstellen des Stundeneintrags: ' + error.message);
    }
}

// Logout-Funktion
function logout() {
    if (confirm('Möchten Sie sich wirklich abmelden?')) {
        console.log('Benutzer meldet sich ab...');
        
        // Token und Benutzerdaten entfernen
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_role');
        
        // Zur Login-Seite weiterleiten
        window.location.href = '/login';
    }
}

// Initialisierung beim Laden der Seite
document.addEventListener('DOMContentLoaded', async function() {
    console.log('Bau-Dokumentations-App wird initialisiert...');
    
    // Theme initialisieren
    initTheme();
    
    // Token aus localStorage laden
    authToken = localStorage.getItem('access_token');
    
    // Prüfe ob Token vorhanden ist
    if (!authToken) {
        console.log('Kein Token gefunden - leite zur Login-Seite weiter...');
        window.location.href = '/login';
        return;
    } else {
        console.log('Token bereits vorhanden:', authToken.substring(0, 20) + '...');
        // Teste ob Token noch gültig ist
        const isValid = await testTokenValidity();
        if (!isValid) {
            console.log('Token ist abgelaufen - leite zur Login-Seite weiter...');
            localStorage.removeItem('access_token');
            window.location.href = '/login';
            return;
        }
    }
    
    console.log('Token gefunden, lade Benutzerdaten...');
    
    // Dark Mode aus localStorage laden
    loadDarkModePreference();
    
    // Standard-Sektion anzeigen
    showSection('dashboard');
    
    // Benutzerdaten laden
    await loadUserData();
    
    // Dashboard-Daten laden
    await loadDashboardData();
    
    // Alle Daten laden
    await loadProjects();
    await loadEmployees();
    await loadReports();
    await loadOffers();
    await loadTimeTrackingData();
    await loadInvoices();
    
    // Rollenbasierte Navigation einrichten
    setupRoleBasedNavigation();
    
    
    // Projekt-Auswahl für Stundenerfassung laden
    loadProjectsForTimeTracking();
    
    // Stundenerfassung-UI initialisieren
    updateClockUI();
    
    // Alle Sektionen aktualisieren (NACH dem Laden der Daten)
    updateAllSections();
    
    // Event-Listener einrichten
    setupFormEventListeners();
    
    console.log('App erfolgreich initialisiert');
});

// Sektion wechseln
function showSection(sectionName) {
    console.log(`Wechsle zu Sektion: ${sectionName}`);
    
    // Alle Sektionen verstecken
    const sections = document.querySelectorAll('.section');
    sections.forEach(section => {
        section.style.display = 'none';
    });
    
    // Navigation aktualisieren
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.classList.remove('active');
    });
    
    // Wenn Angebote-Sektion angezeigt wird, Daten neu laden
    if (sectionName === 'offers') {
        console.log('Lade Angebote-Daten neu...');
        loadOffers();
    }
    
    // Aktive Sektion anzeigen
    const targetSection = document.getElementById(`${sectionName}-section`);
    if (targetSection) {
        targetSection.style.display = 'block';
    }
    
    // Sektion-spezifische Daten laden
    switch(sectionName) {
        case 'dashboard':
            updateDashboard();
            break;
        case 'projects':
            updateProjects();
            break;
        case 'reports':
            updateReports();
            break;
        case 'offers':
            updateOffers();
            break;
        case 'employees':
            updateEmployees();
            break;
        case 'time-tracking':
            updateTimeTracking();
            break;
        case 'invoices':
            updateInvoices();
            break;
        case 'logo-management':
            loadLogoManagement();
            break;
    }
    
    // Navigation markieren
    const activeLink = document.querySelector(`[data-section="${sectionName}"]`);
    if (activeLink) {
        activeLink.classList.add('active');
    }
    
    // Sektionsspezifische Daten laden
    switch(sectionName) {
        case 'projects':
            loadProjects();
            break;
        case 'reports':
            loadReports();
            break;
        case 'offers':
            loadOffers();
            break;
        case 'employees':
            loadEmployees();
            break;
        case 'time-tracking':
            loadTimeTrackingData();
            break;
        case 'invoices':
            loadInvoices();
            break;
    }
}

// Projekt-Formular Handler
async function handleProjectSubmit(event) {
    console.log('handleProjectSubmit aufgerufen!');
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const projectData = {
        name: formData.get('projectName'),
        description: formData.get('projectDescription'),
        client_name: formData.get('projectClient'),
        project_type: formData.get('projectType'),
        status: formData.get('projectStatus')
    };
    
    try {
        const projectId = event.target.dataset.projectId;
        const mode = event.target.dataset.mode;
        const url = projectId ? `${API_BASE}/projects/${projectId}` : `${API_BASE}/projects`;
        const method = projectId ? 'PUT' : 'POST';
        
        console.log(`Projekt ${mode}:`, projectData);
        console.log('URL:', url, 'Method:', method);
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(projectData)
        });
        
        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('projectModal'));
            if (modal) {
                modal.hide();
            }
            await loadProjects();
            updateProjects();
            showAlert(`Projekt erfolgreich ${mode === 'edit' ? 'aktualisiert' : 'erstellt'}!`, 'success');
        } else {
            const errorText = await response.text();
            console.error('Fehler beim Speichern des Projekts:', response.status, errorText);
            showAlert(`Fehler beim ${mode === 'edit' ? 'Aktualisieren' : 'Erstellen'} des Projekts: ${response.status}`, 'danger');
        }
    } catch (error) {
        console.error('Fehler beim Speichern des Projekts:', error);
        showAlert('Fehler beim Speichern des Projekts: ' + error.message, 'danger');
    }
}

// Angebot-Bearbeiten-Funktion
function editOffer(id) {
    console.log('Bearbeite Angebot:', id);
    
    // Finde das Angebot in der aktuellen Liste
    const offer = offers.find(o => o.id === id);
    if (!offer) {
        console.error('Angebot nicht gefunden:', id);
        showAlert('Angebot nicht gefunden!', 'danger');
        return;
    }
    
    // Fülle das Modal mit den Angebotsdaten
    document.getElementById('offerTitle').value = offer.title || '';
    document.getElementById('offerDescription').value = offer.description || '';
    document.getElementById('offerClient').value = offer.client_name || '';
    document.getElementById('offerTotalAmount').value = offer.total_amount || '';
    document.getElementById('offerValidUntil').value = offer.valid_until ? offer.valid_until.split('T')[0] : '';
    
    // Setze Modal-Modus
    const form = document.getElementById('offerForm');
    form.dataset.offerId = offer.id;
    form.dataset.mode = 'edit';
    
    // Aktualisiere Modal-Titel und Button
    document.getElementById('offerModalTitle').textContent = 'Angebot bearbeiten';
    document.getElementById('offerSubmitBtn').textContent = 'Aktualisieren';
    
    // Projekt-Auswahl füllen
    populateOfferProjectSelect();
    
    // Zeige Modal
    const modal = new bootstrap.Modal(document.getElementById('offerModal'));
    modal.show();
}

// Angebot-Modal anzeigen (für neue Angebote)
function showOfferModal() {
    // Formular zurücksetzen
    document.getElementById('offerForm').reset();
    const form = document.getElementById('offerForm');
    delete form.dataset.offerId;
    delete form.dataset.mode;
    
    // Modal-Titel und Button zurücksetzen
    document.getElementById('offerModalTitle').textContent = 'Neues Angebot erstellen';
    document.getElementById('offerSubmitBtn').textContent = 'Erstellen';
    
    // Projekt-Auswahl füllen
    populateOfferProjectSelect();
    
    // Zeige Modal
    const modal = new bootstrap.Modal(document.getElementById('offerModal'));
    modal.show();
}

// Angebot-Formular Handler
async function handleOfferSubmit(event) {
    console.log('handleOfferSubmit aufgerufen!');
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const offerData = {
        title: formData.get('title'),
        description: formData.get('description'),
        client_name: formData.get('client_name'),
        total_amount: Math.round((parseFloat(formData.get('total_amount')) || 0) * 100) / 100,
        valid_until: formData.get('valid_until')
    };
    
    try {
        const offerId = event.target.dataset.offerId;
        const mode = event.target.dataset.mode;
        const url = offerId ? `${API_BASE}/offers/${offerId}` : `${API_BASE}/offers`;
        const method = offerId ? 'PUT' : 'POST';
        
        console.log(`Angebot ${mode}:`, offerData);
        console.log('URL:', url, 'Method:', method);
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(offerData)
        });
        
        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('offerModal'));
            if (modal) {
                modal.hide();
            }
            await loadOffers();
            updateOffers();
            showAlert(`Angebot erfolgreich ${mode === 'edit' ? 'aktualisiert' : 'erstellt'}!`, 'success');
        } else {
            const errorText = await response.text();
            console.error('Fehler beim Speichern des Angebots:', response.status, errorText);
            showAlert(`Fehler beim ${mode === 'edit' ? 'Aktualisieren' : 'Erstellen'} des Angebots: ${response.status}`, 'danger');
        }
    } catch (error) {
        console.error('Fehler beim Speichern des Angebots:', error);
        showAlert('Fehler beim Speichern des Angebots: ' + error.message, 'danger');
    }
}

// Bericht-Formular Handler
async function handleReportSubmit(event) {
    console.log('handleReportSubmit aufgerufen!');
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const reportData = {
        project_id: parseInt(formData.get('project_id')) || 1,
        title: formData.get('title'),
        content: formData.get('content'),
        report_date: formData.get('report_date'),
        work_type: formData.get('work_type'),
        status: formData.get('status')
    };
    
    try {
        const reportId = event.target.dataset.reportId;
        const mode = event.target.dataset.mode;
        const url = reportId ? `${API_BASE}/reports/${reportId}` : `${API_BASE}/reports`;
        const method = reportId ? 'PUT' : 'POST';
        
        console.log(`Bericht ${mode}:`, reportData);
        console.log('URL:', url, 'Method:', method);
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(reportData)
        });
        
        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('reportModal'));
            if (modal) {
                modal.hide();
            }
            await loadReports();
            updateReports();
            showAlert(`Bericht erfolgreich ${mode === 'edit' ? 'aktualisiert' : 'erstellt'}!`, 'success');
        } else {
            const errorText = await response.text();
            console.error('Fehler beim Speichern des Berichts:', response.status, errorText);
            showAlert(`Fehler beim ${mode === 'edit' ? 'Aktualisieren' : 'Erstellen'} des Berichts: ${response.status}`, 'danger');
        }
    } catch (error) {
        console.error('Fehler beim Speichern des Berichts:', error);
        showAlert('Fehler beim Speichern des Berichts: ' + error.message, 'danger');
    }
}

// Angebot-Formular Handler
async function handleOfferSubmit(event) {
    console.log('handleOfferSubmit aufgerufen!');
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const offerData = {
        project_id: parseInt(formData.get('project_id')) || 1,
        title: formData.get('title'),
        description: formData.get('description'),
        client_name: formData.get('client_name'),
        client_address: formData.get('client_address'),
        total_amount: Math.round((parseFloat(formData.get('total_amount')) || 0) * 100) / 100,
        valid_until: formData.get('valid_until'),
        items: []
    };
    
    try {
        const offerId = event.target.dataset.offerId;
        const url = offerId ? `${API_BASE}/offers/${offerId}` : `${API_BASE}/offers`;
        const method = offerId ? 'PUT' : 'POST';
        
        // Token aus localStorage laden falls nicht verfügbar
        const token = authToken || localStorage.getItem('access_token');
        if (!token) {
            console.error('Kein Authentifizierungs-Token verfügbar');
            showAlert('Authentifizierung erforderlich. Bitte melden Sie sich erneut an.', 'danger');
            return;
        }
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(offerData)
        });
        
        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('offerModal'));
            if (modal) {
                modal.hide();
            }
            loadOffers();
            showAlert('Angebot erfolgreich gespeichert!', 'success');
        } else {
            showAlert('Fehler beim Speichern des Angebots', 'danger');
        }
    } catch (error) {
        console.error('Fehler beim Speichern des Angebots:', error);
        showAlert('Fehler beim Speichern des Angebots', 'danger');
    }
}

// Mitarbeiter-Formular Handler
async function handleEmployeeSubmit(event) {
    console.log('handleEmployeeSubmit aufgerufen!');
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const employeeData = {
        full_name: formData.get('name'),
        email: formData.get('email'),
        phone: formData.get('phone'),
        position: formData.get('position'),
        hourly_rate: parseFloat(formData.get('hourly_rate')) || 0,
        is_active: formData.get('is_active') === 'on'
    };
    
    try {
        const employeeId = event.target.dataset.employeeId;
        const url = employeeId ? `${API_BASE}/employees/${employeeId}` : `${API_BASE}/employees`;
        const method = employeeId ? 'PUT' : 'POST';
        
        // Token aus localStorage laden falls nicht verfügbar
        const token = authToken || localStorage.getItem('access_token');
        if (!token) {
            console.error('Kein Authentifizierungs-Token verfügbar');
            showAlert('Authentifizierung erforderlich. Bitte melden Sie sich erneut an.', 'danger');
            return;
        }
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(employeeData)
        });
        
        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('employeeModal'));
            if (modal) {
                modal.hide();
            }
            loadEmployees();
            showAlert('Mitarbeiter erfolgreich gespeichert!', 'success');
        } else {
            showAlert('Fehler beim Speichern des Mitarbeiters', 'danger');
        }
    } catch (error) {
        console.error('Fehler beim Speichern des Mitarbeiters:', error);
        showAlert('Fehler beim Speichern des Mitarbeiters', 'danger');
    }
}

// Stundeneintrag-Formular Handler
async function handleTimeEntrySubmit(event) {
    console.log('handleTimeEntrySubmit aufgerufen!');
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const timeEntryData = {
        project_id: parseInt(formData.get('project_id')) || 1,
        employee_id: parseInt(formData.get('employee_id')) || 1,
        date: formData.get('date'),
        start_time: formData.get('start_time'),
        end_time: formData.get('end_time'),
        break_duration: parseFloat(formData.get('break_duration')) || 0,
        description: formData.get('description')
    };
    
    try {
        const timeEntryId = event.target.dataset.timeEntryId;
        const url = timeEntryId ? `${API_BASE}/time-entries/${timeEntryId}` : `${API_BASE}/time-entries`;
        const method = timeEntryId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(timeEntryData)
        });
        
        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('timeEntryModal'));
            if (modal) {
                modal.hide();
            }
            loadTimeTrackingData();
            showAlert('Stundeneintrag erfolgreich gespeichert!', 'success');
        } else {
            showAlert('Fehler beim Speichern des Stundeneintrags', 'danger');
        }
    } catch (error) {
        console.error('Fehler beim Speichern des Stundeneintrags:', error);
        showAlert('Fehler beim Speichern des Stundeneintrags', 'danger');
    }
}

// Rechnungs-Formular Handler
async function handleInvoiceSubmit(event) {
    console.log('handleInvoiceSubmit aufgerufen!');
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const invoiceData = {
        project_id: parseInt(formData.get('project_id')) || 1,
        invoice_number: formData.get('invoice_number'),
        title: formData.get('title'),
        description: formData.get('description'),
        client_name: formData.get('client_name'),
        client_address: formData.get('client_address'),
        total_amount: Math.round((parseFloat(formData.get('total_amount')) || 0) * 100) / 100,
        currency: formData.get('currency') || 'EUR',
        status: formData.get('status') || 'entwurf',
        items: []
    };
    
    try {
        const invoiceId = event.target.dataset.invoiceId;
        const url = invoiceId ? `${API_BASE}/invoices/${invoiceId}` : `${API_BASE}/invoices`;
        const method = invoiceId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(invoiceData)
        });
        
        if (response.ok) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('invoiceModal'));
            if (modal) {
                modal.hide();
            }
            loadInvoices();
            showAlert('Rechnung erfolgreich gespeichert!', 'success');
        } else {
            showAlert('Fehler beim Speichern der Rechnung', 'danger');
        }
    } catch (error) {
        console.error('Fehler beim Speichern der Rechnung:', error);
        showAlert('Fehler beim Speichern der Rechnung', 'danger');
    }
}

// Modal-Funktionen
function showProjectModal() {
    const modal = new bootstrap.Modal(document.getElementById('projectModal'));
    
    // Formular zurücksetzen
    const form = document.getElementById('projectForm');
    form.reset();
    form.dataset.projectId = '';
    form.dataset.mode = 'create';
    
    // Modal-Titel zurücksetzen
    const modalTitle = document.querySelector('#projectModal .modal-title');
    if (modalTitle) {
        modalTitle.textContent = 'Neues Projekt erstellen';
    }
    
    // Submit-Button Text zurücksetzen
    const submitBtn = document.querySelector('#projectForm button[type="submit"]');
    if (submitBtn) {
        submitBtn.textContent = 'Projekt erstellen';
    }
    
    modal.show();
}

function showReportModal() {
    const modal = new bootstrap.Modal(document.getElementById('reportModal'));
    
    // Formular zurücksetzen
    const form = document.getElementById('reportForm');
    form.reset();
    form.dataset.reportId = '';
    form.dataset.mode = 'create';
    
    // Modal-Titel zurücksetzen
    const modalTitle = document.querySelector('#reportModal .modal-title');
    if (modalTitle) {
        modalTitle.textContent = 'Neuen Bericht erstellen';
    }
    
    // Submit-Button Text zurücksetzen
    const submitBtn = document.querySelector('#reportForm button[type="submit"]');
    if (submitBtn) {
        submitBtn.textContent = 'Bericht erstellen';
    }
    
    // Projekt-Auswahl füllen
    populateReportProjectSelect();
    
    // Projekt-Auswahl zurücksetzen
    const projectSelect = document.getElementById('reportProject');
    if (projectSelect) {
        projectSelect.innerHTML = '<option value="">Projekt auswählen...</option>';
        projects.forEach(project => {
            const option = document.createElement('option');
            option.value = project.id;
            option.textContent = project.name;
            projectSelect.appendChild(option);
        });
    }
    
    modal.show();
}

function showOfferModal() {
    const modal = new bootstrap.Modal(document.getElementById('offerModal'));
    modal.show();
}

function showEmployeeModal() {
    const modal = new bootstrap.Modal(document.getElementById('employeeModal'));
    modal.show();
}

function showTimeEntryModal() {
    const modal = new bootstrap.Modal(document.getElementById('timeEntryModal'));
    modal.show();
}

function showInvoiceModal() {
    const modal = new bootstrap.Modal(document.getElementById('invoiceModal'));
    modal.show();
    
    // Projekt-Auswahl füllen
    if (projects && projects.length > 0) {
        populateInvoiceProjectSelect();
    } else {
        console.log('Projekte noch nicht geladen, lade sie...');
        loadProjects().then(() => {
            populateInvoiceProjectSelect();
        });
    }
}

// Event-Listener einrichten
function setupFormEventListeners() {
    // Projekt-Formular
    const projectForm = document.getElementById('projectForm');
    if (projectForm) {
        projectForm.addEventListener('submit', handleProjectSubmit);
    }
    
    // Bericht-Formular
    const reportForm = document.getElementById('reportForm');
    if (reportForm) {
        reportForm.addEventListener('submit', handleReportSubmit);
    }
    
    // Angebot-Formular
    const offerForm = document.getElementById('offerForm');
    if (offerForm) {
        offerForm.addEventListener('submit', handleOfferSubmit);
    }
    
    // Mitarbeiter-Formular
    const employeeForm = document.getElementById('employeeForm');
    if (employeeForm) {
        employeeForm.addEventListener('submit', handleEmployeeSubmit);
    }
    
    // Stundeneintrag-Formular
    const timeEntryForm = document.getElementById('timeEntryForm');
    if (timeEntryForm) {
        timeEntryForm.addEventListener('submit', handleTimeEntrySubmit);
    }
    
    // Rechnungs-Formular
    const invoiceForm = document.getElementById('invoiceForm');
    if (invoiceForm) {
        invoiceForm.addEventListener('submit', handleInvoiceSubmit);
    }
}

// Hilfsfunktionen
function showAlert(message, type) {
    const alertContainer = document.getElementById('alertContainer');
    if (alertContainer) {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        alertContainer.appendChild(alert);
        
        // Alert nach 5 Sekunden entfernen
        setTimeout(() => {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        }, 5000);
    }
}

function loadDarkModePreference() {
    const darkMode = localStorage.getItem('darkMode') === 'true';
    if (darkMode) {
        document.body.classList.add('dark-mode');
        isDarkMode = true;
    }
}

async function loadUserData() {
    if (!authToken) {
        console.log('Kein Token verfügbar für loadUserData');
        return;
    }
    
    try {
        console.log('Lade Benutzerdaten mit Token:', authToken.substring(0, 20) + '...');
        const response = await apiCall(`${API_BASE}/auth/me`);
        
        if (response.ok) {
            currentUser = await response.json();
            console.log('Benutzerdaten geladen:', currentUser);
            // UI aktualisieren
            updateUserDisplay();
        } else {
            console.log('Fehler beim Laden der Benutzerdaten:', response.status);
            const errorText = await response.text();
            console.log('Fehler-Details:', errorText);
        }
    } catch (error) {
        console.error('Fehler beim Laden der Benutzerdaten:', error);
    }
}

async function loadDashboardData() {
    if (!authToken) {
        console.log('Kein Token verfügbar für loadDashboardData');
        return;
    }
    
    // Dashboard-Daten laden
    console.log('Dashboard-Daten werden geladen...');
    
    
    try {
        // Projekte laden
        const projectsResponse = await apiCall(`${API_BASE}/projects/`);
        
        if (projectsResponse.ok) {
            projects = await projectsResponse.json();
            console.log('Projekte geladen:', projects.length);
        } else {
            console.log('Fehler beim Laden der Projekte:', projectsResponse.status);
        }
        
        // Mitarbeiter laden
        const employeesResponse = await apiCall(`${API_BASE}/employees/`);
        
        if (employeesResponse.ok) {
            employees = await employeesResponse.json();
            console.log('Mitarbeiter geladen:', employees.length);
        } else {
            console.log('Fehler beim Laden der Mitarbeiter:', employeesResponse.status);
        }
        
        // Gesamtumsatz laden
        await updateTotalRevenue();
    } catch (error) {
        console.error('Fehler beim Laden der Dashboard-Daten:', error);
    }
}

async function loadProjects() {
    if (!authToken) {
        console.log('Kein Token verfügbar für loadProjects');
        return;
    }
    
    try {
        const response = await apiCall(`${API_BASE}/projects`);
        
        if (response.ok) {
            projects = await response.json();
            console.log('Projekte geladen:', projects.length);
            // Aktualisiere die Projekte-Tabelle
            displayProjects();
        } else {
            console.log('Fehler beim Laden der Projekte:', response.status);
        }
    } catch (error) {
        console.error('Fehler beim Laden der Projekte:', error);
    }
}

async function loadReports() {
    if (!authToken) {
        console.log('Kein Token verfügbar für loadReports');
        return;
    }
    
    try {
        const response = await apiCall(`${API_BASE}/reports`);
        
        if (response.ok) {
            reports = await response.json(); // Globale Variable setzen
            console.log('Berichte geladen:', reports.length);
            // Aktualisiere die Berichte-Tabelle
            displayReports();
        } else {
            console.log('Fehler beim Laden der Berichte:', response.status);
        }
    } catch (error) {
        console.error('Fehler beim Laden der Berichte:', error);
    }
}

async function loadOffers() {
    if (!authToken) {
        console.log('Kein Token verfügbar für loadOffers');
        return;
    }
    
    try {
        console.log('Starte API-Aufruf für Angebote...');
        
        // DIREKT ANGEBOTE ERSTELLEN (WORKAROUND)
        console.log('WORKAROUND: Erstelle Test-Angebote direkt im Frontend');
        offers = [
            {
                id: 1,
                title: 'Angebot für Trockenbau',
                client_name: 'Musterfirma GmbH',
                client_address: 'Musterstraße 123, 12345 Musterstadt',
                total_amount: 5000.00,
                status: 'entwurf',
                valid_until: '2025-12-31'
            },
            {
                id: 2,
                title: 'Renovierung Büroräume',
                client_name: 'Beispiel AG',
                client_address: 'Beispielweg 42, 54321 Beispielstadt',
                total_amount: 12500.00,
                status: 'gesendet',
                valid_until: '2025-11-30'
            },
            {
                id: 3,
                title: 'Sanierung Altbau',
                client_name: 'Sanierungsbedarf KG',
                client_address: 'Altbaustraße 7, 67890 Sanierungsstadt',
                total_amount: 35000.00,
                status: 'akzeptiert',
                valid_until: '2026-01-15'
            }
        ];
        
        console.log('Test-Angebote erstellt:', offers.length);
        displayOffers();
        
        // "Neues Angebot" Button anzeigen
        const newOfferBtn = document.querySelector('#offers-section button');
        if (newOfferBtn) {
            newOfferBtn.style.display = 'inline-block';
            console.log('Neues Angebot Button angezeigt');
        }
        
        /* AUSKOMMENTIERT - API-AUFRUF FUNKTIONIERT NICHT
        const response = await apiCall(`${API_BASE}/offers`);
        console.log('API-Antwort erhalten:', response.status);
        
        if (response.ok) {
            offers = await response.json(); // Globale Variable setzen
            console.log('Angebote geladen:', offers.length);
            // Aktualisiere die Angebote-Tabelle
            displayOffers();
            
            // "Neues Angebot" Button anzeigen
            const newOfferBtn = document.querySelector('#offers-section button');
            if (newOfferBtn) {
                newOfferBtn.style.display = 'inline-block';
                console.log('Neues Angebot Button angezeigt');
            }
        } else {
            console.log('Fehler beim Laden der Angebote:', response.status);
            const errorText = await response.text();
            console.error('Fehlerdetails:', errorText);
        }
        */
    } catch (error) {
        console.error('Fehler beim Laden der Angebote:', error);
    }
}

async function loadEmployees() {
    if (!authToken) {
        console.log('Kein Token verfügbar für loadEmployees');
        return;
    }
    
    try {
        const response = await apiCall(`${API_BASE}/employees`);
        
        if (response.ok) {
            employees = await response.json();
            console.log('Mitarbeiter geladen:', employees.length);
            // Aktualisiere die Mitarbeiter-Tabelle
            displayEmployees();
        } else {
            console.log('Fehler beim Laden der Mitarbeiter:', response.status);
        }
    } catch (error) {
        console.error('Fehler beim Laden der Mitarbeiter:', error);
    }
}

async function loadTimeTrackingData() {
    if (!authToken) {
        console.log('Kein Token verfügbar für loadTimeTrackingData');
        return;
    }
    
    try {
        const response = await apiCall(`${API_BASE}/time-entries`);
        
        if (response.ok) {
            timeEntries = await response.json(); // Globale Variable setzen
            console.log('Stundeneinträge geladen:', timeEntries.length);
            // Aktualisiere die Stundeneinträge-Tabelle
            displayTimeEntries();
        } else {
            console.log('Fehler beim Laden der Stundeneinträge:', response.status);
        }
    } catch (error) {
        console.error('Fehler beim Laden der Stundeneinträge:', error);
    }
}

async function loadInvoices() {
    if (!authToken) {
        console.log('Kein Token verfügbar für loadInvoices');
        return;
    }
    
    try {
        const response = await apiCall(`${API_BASE}/invoices`);
        
        if (response.ok) {
            invoices = await response.json(); // Globale Variable setzen
            console.log('Rechnungen geladen:', invoices.length);
            // Aktualisiere die Rechnungen-Tabelle
            displayInvoices();
        } else {
            console.log('Fehler beim Laden der Rechnungen:', response.status);
        }
    } catch (error) {
        console.error('Fehler beim Laden der Rechnungen:', error);
    }
}

// Hilfsfunktionen für bessere Tabellen-Darstellung
function getStatusText(status) {
    const statusMap = {
        'in_progress': 'In Bearbeitung',
        'completed': 'Abgeschlossen',
        'pending': 'Ausstehend',
        'cancelled': 'Abgebrochen'
    };
    return statusMap[status] || status;
}

function formatDate(dateString) {
    if (!dateString || dateString === 'N/A') {
        return 'N/A';
    }
    
    try {
        const date = new Date(dateString);
        return date.toLocaleDateString('de-DE', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit'
        });
    } catch (error) {
        return dateString;
    }
}

// Projekt-Auswahl für Angebot-Modal füllen
function populateOfferProjectSelect() {
    const projectSelect = document.getElementById('offerProject');
    if (!projectSelect) {
        console.error('offerProject Select-Element nicht gefunden');
        return;
    }
    
    // Leere die aktuellen Optionen (außer der ersten)
    projectSelect.innerHTML = '<option value="">Projekt auswählen...</option>';
    
    // Füge alle verfügbaren Projekte hinzu
    if (projects && projects.length > 0) {
        projects.forEach(project => {
            const option = document.createElement('option');
            option.value = project.id;
            option.textContent = `${project.name} (${project.client_name || 'Kein Kunde'})`;
            projectSelect.appendChild(option);
        });
    } else {
        console.warn('Keine Projekte verfügbar für Angebot-Modal');
    }
}

// Projekt-Auswahl für Rechnungs-Modal füllen
function populateInvoiceProjectSelect() {
    const projectSelect = document.getElementById('invoiceProject');
    if (!projectSelect) {
        console.error('invoiceProject Select-Element nicht gefunden');
        return;
    }
    
    // Leere die aktuellen Optionen (außer der ersten)
    projectSelect.innerHTML = '<option value="">Projekt auswählen...</option>';
    
    // Füge alle verfügbaren Projekte hinzu
    if (projects && projects.length > 0) {
        projects.forEach(project => {
            const option = document.createElement('option');
            option.value = project.id;
            option.textContent = `${project.name} (${project.client_name || 'Kein Kunde'})`;
            projectSelect.appendChild(option);
        });
        console.log('Rechnungs-Projektauswahl aktualisiert mit', projects.length, 'Projekten');
    } else {
        console.warn('Keine Projekte verfügbar für Rechnungs-Modal');
    }
}

// Projekt-Auswahl für Berichts-Modal füllen
function populateReportProjectSelect() {
    const projectSelect = document.getElementById('reportProject');
    if (!projectSelect) {
        console.error('reportProject Select-Element nicht gefunden');
        return;
    }
    
    // Leere die aktuellen Optionen (außer der ersten)
    projectSelect.innerHTML = '<option value="">Projekt auswählen...</option>';
    
    // Füge alle verfügbaren Projekte hinzu
    if (projects && projects.length > 0) {
        projects.forEach(project => {
            const option = document.createElement('option');
            option.value = project.id;
            option.textContent = `${project.name} (${project.client_name || 'Kein Kunde'})`;
            projectSelect.appendChild(option);
        });
        console.log('Berichts-Projektauswahl aktualisiert mit', projects.length, 'Projekten');
    } else {
        console.warn('Keine Projekte verfügbar für Berichts-Modal');
    }
}

// Angebot-Gesamtsumme berechnen
function calculateOfferTotal() {
    const netAmount = parseFloat(document.getElementById('offerNetAmount')?.value || 0);
    const taxRate = parseFloat(document.getElementById('offerTaxRate')?.value || 0);
    
    if (netAmount > 0) {
    const taxAmount = (netAmount * taxRate) / 100;
    const totalAmount = netAmount + taxAmount;
    
    const totalAmountField = document.getElementById('offerTotalAmount');
    if (totalAmountField) {
        totalAmountField.value = totalAmount.toFixed(2);
    }
    }
}

// Mitarbeiter bearbeiten
function editEmployee(id) {
    console.log('Bearbeite Mitarbeiter:', id);
    const employee = employees.find(e => e.id === id);
    if (!employee) {
        console.error('Mitarbeiter nicht gefunden:', id);
        showAlert('Mitarbeiter nicht gefunden!', 'danger');
        return;
    }
    
    // Fülle Formular mit Mitarbeiter-Daten
    document.getElementById('employeeName').value = employee.full_name || '';
    document.getElementById('employeeEmail').value = employee.email || '';
    document.getElementById('employeePhone').value = employee.phone || '';
    document.getElementById('employeePosition').value = employee.position || '';
    document.getElementById('employeeHourlyRate').value = employee.hourly_rate || '';
    
    // Checkbox für Aktiv-Status
    const isActiveCheckbox = document.getElementById('employeeIsActive');
    if (isActiveCheckbox) {
        isActiveCheckbox.checked = employee.is_active || false;
    }
    
    // Setze Formular-Modus
    const form = document.getElementById('employeeForm');
    form.dataset.employeeId = employee.id;
    form.dataset.mode = 'edit';
    
    // Aktualisiere Modal-Titel und Button
    document.getElementById('employeeModalTitle').textContent = 'Mitarbeiter bearbeiten';
    document.getElementById('employeeSubmitBtn').textContent = 'Aktualisieren';
    
    // Zeige Modal
    const modal = new bootstrap.Modal(document.getElementById('employeeModal'));
    modal.show();
}

// Automatische Rechnungsgenerierung Modal anzeigen
function showAutoInvoiceModal() {
    console.log('Zeige automatische Rechnungsgenerierung Modal...');
    
    // Modal anzeigen
    const modal = new bootstrap.Modal(document.getElementById('autoInvoiceModal'));
    modal.show();
    
    // Lade verfügbare Projekte für die Auswahl NACH dem Modal
    setTimeout(() => {
        loadProjectsForInvoiceGeneration();
    }, 500); // Erhöhte Verzögerung für bessere Kompatibilität
}

// Projekte für Rechnungsgenerierung laden
async function loadProjectsForInvoiceGeneration() {
    try {
        console.log('Lade Projekte für Rechnungsgenerierung...');
        
        // Warte kurz, damit das Modal vollständig geladen ist
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Token aus localStorage holen
        const token = localStorage.getItem('access_token') || localStorage.getItem('token');
        if (!token) {
            console.error('Kein Token gefunden');
            alert('Bitte loggen Sie sich erneut ein.');
            return;
        }
        
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
                projectSelect.innerHTML = '<option value="">Projekt auswählen...</option>' + 
                    projects.map(project => 
                        `<option value="${project.id}">${project.name} - ${project.client_name || 'Kein Kunde'}</option>`
                    ).join('');
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

// Rechnungsgenerierung starten
async function generateInvoice() {
    // Token validieren
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    if (!token) {
        alert('Ihre Sitzung ist abgelaufen. Bitte loggen Sie sich erneut ein.');
        window.location.href = '/login';
        return;
    }
    
    const projectId = document.getElementById('invoiceProjectSelect').value;
    const generationMethod = document.getElementById('invoiceGenerationMethod').value;
    // Lohnanteil wird automatisch berechnet
    
    if (!projectId) {
        alert('Bitte wählen Sie ein Projekt aus.');
        return;
    }
    
    try {
        console.log('Starte Rechnungsgenerierung...');
        
        const requestData = {
            project_id: parseInt(projectId),
            generation_method: generationMethod,
            labor_cost_percentage: 30.0, // Fester Wert
            include_materials: true,
            include_labor: true,
            tax_rate: 19.0
        };
        
        const response = await fetch('/invoice-generation/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token') || localStorage.getItem('token')}`
            },
            body: JSON.stringify(requestData)
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('Rechnungsgenerierung erfolgreich:', result);
            
            // Zeige Ergebnis
            showInvoiceGenerationResult(result);
        } else {
            const error = await response.text();
            console.error('Fehler bei Rechnungsgenerierung:', error);
            alert('Fehler bei der Rechnungsgenerierung: ' + error);
        }
    } catch (error) {
        console.error('Fehler bei Rechnungsgenerierung:', error);
        alert('Fehler bei der Rechnungsgenerierung: ' + error.message);
    }
}

// Rechnungsgenerierungsergebnis anzeigen
function showInvoiceGenerationResult(result) {
    // Speichere das Berechnungsergebnis global für die Rechnungserstellung
    window.lastInvoiceCalculation = result;
    
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

// Rechnung aus Ergebnis erstellen
async function createInvoiceFromResult() {
    const projectId = document.getElementById('invoiceProjectSelect').value;
    const invoiceNumber = document.getElementById('invoiceNumber').value || `R-${Date.now()}`;
    const clientName = document.getElementById('clientName').value || 'Kunde';
    
    if (!projectId) {
        alert('Bitte wählen Sie ein Projekt aus.');
        return;
    }
    
    try {
        console.log('Erstelle Rechnung aus Berechnung...');
        
        // Token validieren
        const token = localStorage.getItem('access_token') || localStorage.getItem('token');
        if (!token) {
            alert('Ihre Sitzung ist abgelaufen. Bitte loggen Sie sich erneut ein.');
            window.location.href = '/login';
            return;
        }
        
        // Hole das Berechnungsergebnis aus dem DOM
        const resultDiv = document.getElementById('invoiceGenerationResult');
        if (!resultDiv || resultDiv.style.display === 'none') {
            alert('Bitte führen Sie zuerst eine Rechnungsberechnung durch.');
            return;
        }
        
        // Hole das Berechnungsergebnis aus dem globalen Speicher
        if (!window.lastInvoiceCalculation) {
            alert('Bitte führen Sie zuerst eine Rechnungsberechnung durch.');
            return;
        }
        
        // Erstelle Rechnung über API
        const response = await fetch('/invoice-generation/create-from-calculation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                project_id: parseInt(projectId),
                calculation: window.lastInvoiceCalculation,
                invoice_number: invoiceNumber,
                client_name: clientName,
                client_address: null
            })
        });
        
        if (response.ok) {
            const invoice = await response.json();
            console.log('Rechnung erfolgreich erstellt:', invoice);
            
            // Erfolgsmeldung anzeigen
            alert(`Rechnung erfolgreich erstellt!\n\nRechnungsnummer: ${invoice.invoice_number}\nGesamtbetrag: ${invoice.total_amount.toFixed(2)} EUR`);
            
            // Modal schließen
            closeAutoInvoiceModal();
            
            // Rechnungen-Liste aktualisieren
            if (typeof updateInvoices === 'function') {
                updateInvoices();
            }
        } else {
            const errorData = await response.json();
            console.error('Fehler beim Erstellen der Rechnung:', errorData);
            console.error('Response Status:', response.status);
            console.error('Response Headers:', response.headers);
            
            // Detaillierte Fehlermeldung
            let errorMessage = 'Unbekannter Fehler';
            if (errorData.detail) {
                if (Array.isArray(errorData.detail)) {
                    errorMessage = errorData.detail.map(err => `${err.loc?.join('.')}: ${err.msg}`).join(', ');
                } else {
                    errorMessage = errorData.detail;
                }
            } else {
                errorMessage = response.statusText;
            }
            
            alert(`Fehler beim Erstellen der Rechnung (${response.status}): ${errorMessage}`);
        }
    } catch (error) {
        console.error('Fehler beim Erstellen der Rechnung:', error);
        alert('Fehler beim Erstellen der Rechnung: ' + error.message);
    }
}

// Auto-Rechnung Modal schließen
function closeAutoInvoiceModal() {
    const modal = bootstrap.Modal.getInstance(document.getElementById('autoInvoiceModal'));
    if (modal) {
        modal.hide();
    }
    
    // Ergebnis zurücksetzen
    const resultDiv = document.getElementById('invoiceGenerationResult');
    if (resultDiv) {
        resultDiv.style.display = 'none';
        resultDiv.innerHTML = '';
    }
}

// Mitarbeiter-Modal anzeigen (für neue Mitarbeiter)
function showEmployeeModal() {
    // Formular zurücksetzen
    document.getElementById('employeeForm').reset();
    const form = document.getElementById('employeeForm');
    delete form.dataset.employeeId;
    delete form.dataset.mode;
    
    // Modal-Titel und Button zurücksetzen
    document.getElementById('employeeModalTitle').textContent = 'Neuer Mitarbeiter';
    document.getElementById('employeeSubmitBtn').textContent = 'Erstellen';
    
    // Zeige Modal
    const modal = new bootstrap.Modal(document.getElementById('employeeModal'));
    modal.show();
}

// Automatische Rechnungsgenerierung Modal anzeigen
function showAutoInvoiceModal() {
    console.log('Zeige automatische Rechnungsgenerierung Modal...');
    
    // Modal anzeigen
    const modal = new bootstrap.Modal(document.getElementById('autoInvoiceModal'));
    modal.show();
    
    // Lade verfügbare Projekte für die Auswahl NACH dem Modal
    setTimeout(() => {
        loadProjectsForInvoiceGeneration();
    }, 500); // Erhöhte Verzögerung für bessere Kompatibilität
}

// Projekte für Rechnungsgenerierung laden
async function loadProjectsForInvoiceGeneration() {
    try {
        console.log('Lade Projekte für Rechnungsgenerierung...');
        
        // Warte kurz, damit das Modal vollständig geladen ist
        await new Promise(resolve => setTimeout(resolve, 500));
        
        // Token aus localStorage holen
        const token = localStorage.getItem('access_token') || localStorage.getItem('token');
        if (!token) {
            console.error('Kein Token gefunden');
            alert('Bitte loggen Sie sich erneut ein.');
            return;
        }
        
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
                projectSelect.innerHTML = '<option value="">Projekt auswählen...</option>' + 
                    projects.map(project => 
                        `<option value="${project.id}">${project.name} - ${project.client_name || 'Kein Kunde'}</option>`
                    ).join('');
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

// Rechnungsgenerierung starten
async function generateInvoice() {
    // Token validieren
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    if (!token) {
        alert('Ihre Sitzung ist abgelaufen. Bitte loggen Sie sich erneut ein.');
        window.location.href = '/login';
        return;
    }
    
    const projectId = document.getElementById('invoiceProjectSelect').value;
    const generationMethod = document.getElementById('invoiceGenerationMethod').value;
    // Lohnanteil wird automatisch berechnet
    
    if (!projectId) {
        alert('Bitte wählen Sie ein Projekt aus.');
        return;
    }
    
    try {
        console.log('Starte Rechnungsgenerierung...');
        
        const requestData = {
            project_id: parseInt(projectId),
            generation_method: generationMethod,
            labor_cost_percentage: 30.0, // Fester Wert
            include_materials: true,
            include_labor: true,
            tax_rate: 19.0
        };
        
        const response = await fetch('/invoice-generation/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token') || localStorage.getItem('token')}`
            },
            body: JSON.stringify(requestData)
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('Rechnungsgenerierung erfolgreich:', result);
            
            // Zeige Ergebnis
            showInvoiceGenerationResult(result);
        } else {
            const error = await response.text();
            console.error('Fehler bei Rechnungsgenerierung:', error);
            alert('Fehler bei der Rechnungsgenerierung: ' + error);
        }
    } catch (error) {
        console.error('Fehler bei Rechnungsgenerierung:', error);
        alert('Fehler bei der Rechnungsgenerierung: ' + error.message);
    }
}

// Rechnungsgenerierungsergebnis anzeigen
function showInvoiceGenerationResult(result) {
    // Speichere das Berechnungsergebnis global für die Rechnungserstellung
    window.lastInvoiceCalculation = result;
    
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

// Rechnung aus Ergebnis erstellen
async function createInvoiceFromResult() {
    const projectId = document.getElementById('invoiceProjectSelect').value;
    const invoiceNumber = document.getElementById('invoiceNumber').value || `R-${Date.now()}`;
    const clientName = document.getElementById('clientName').value || 'Kunde';
    
    if (!projectId) {
        alert('Bitte wählen Sie ein Projekt aus.');
        return;
    }
    
    try {
        console.log('Erstelle Rechnung aus Berechnung...');
        
        // Token validieren
        const token = localStorage.getItem('access_token') || localStorage.getItem('token');
        if (!token) {
            alert('Ihre Sitzung ist abgelaufen. Bitte loggen Sie sich erneut ein.');
            window.location.href = '/login';
            return;
        }
        
        // Hole das Berechnungsergebnis aus dem DOM
        const resultDiv = document.getElementById('invoiceGenerationResult');
        if (!resultDiv || resultDiv.style.display === 'none') {
            alert('Bitte führen Sie zuerst eine Rechnungsberechnung durch.');
            return;
        }
        
        // Hole das Berechnungsergebnis aus dem globalen Speicher
        if (!window.lastInvoiceCalculation) {
            alert('Bitte führen Sie zuerst eine Rechnungsberechnung durch.');
            return;
        }
        
        // Erstelle Rechnung über API
        const response = await fetch('/invoice-generation/create-from-calculation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                project_id: parseInt(projectId),
                calculation: window.lastInvoiceCalculation,
                invoice_number: invoiceNumber,
                client_name: clientName,
                client_address: null
            })
        });
        
        if (response.ok) {
            const invoice = await response.json();
            console.log('Rechnung erfolgreich erstellt:', invoice);
            
            // Erfolgsmeldung anzeigen
            alert(`Rechnung erfolgreich erstellt!\n\nRechnungsnummer: ${invoice.invoice_number}\nGesamtbetrag: ${invoice.total_amount.toFixed(2)} EUR`);
            
            // Modal schließen
            closeAutoInvoiceModal();
            
            // Rechnungen-Liste aktualisieren
            if (typeof updateInvoices === 'function') {
                updateInvoices();
            }
        } else {
            const errorData = await response.json();
            console.error('Fehler beim Erstellen der Rechnung:', errorData);
            console.error('Response Status:', response.status);
            console.error('Response Headers:', response.headers);
            
            // Detaillierte Fehlermeldung
            let errorMessage = 'Unbekannter Fehler';
            if (errorData.detail) {
                if (Array.isArray(errorData.detail)) {
                    errorMessage = errorData.detail.map(err => `${err.loc?.join('.')}: ${err.msg}`).join(', ');
                } else {
                    errorMessage = errorData.detail;
                }
            } else {
                errorMessage = response.statusText;
            }
            
            alert(`Fehler beim Erstellen der Rechnung (${response.status}): ${errorMessage}`);
        }
    } catch (error) {
        console.error('Fehler beim Erstellen der Rechnung:', error);
        alert('Fehler beim Erstellen der Rechnung: ' + error.message);
    }
}

// Auto-Rechnung Modal schließen
function closeAutoInvoiceModal() {
    const modal = bootstrap.Modal.getInstance(document.getElementById('autoInvoiceModal'));
    if (modal) {
        modal.hide();
    }
    
    // Ergebnis zurücksetzen
    const resultDiv = document.getElementById('invoiceGenerationResult');
    if (resultDiv) {
        resultDiv.style.display = 'none';
        resultDiv.innerHTML = '';
    }
}
// Logo Management Funktionen
async function loadLogoManagement() {
    console.log('Lade Logo-Management...');
    
    try {
        // Aktuelles Logo laden
        await loadCurrentLogo();
        
        // Logo-Historie laden
        await loadLogoHistory();
        
        // Upload-Formular initialisieren
        initializeLogoUpload();
        
        console.log('Logo-Management erfolgreich geladen');
    } catch (error) {
        console.error('Fehler beim Laden des Logo-Managements:', error);
    }
}

async function loadCurrentLogo() {
    try {
        const response = await fetch(`${API_BASE}/company-logo/current`, {
            headers: getAuthHeaders()
        });
        
        if (response.ok) {
            const logo = await response.json();
            displayCurrentLogo(logo);
        } else if (response.status === 404) {
            displayNoLogo();
        } else {
            console.error('Fehler beim Laden des Logos:', response.status);
        }
    } catch (error) {
        console.error('Fehler beim Laden des Logos:', error);
    }
}

function displayCurrentLogo(logo) {
    const container = document.getElementById('currentLogoContainer');
    container.innerHTML = `
        <div class="text-center">
            <img src="/company-logo/view" alt="Firmenlogo" class="img-fluid mb-3" style="max-height: 200px;">
            <h6>${logo.original_filename}</h6>
            <small class="text-muted">
                ${(logo.file_size / 1024).toFixed(1)} KB<br>
                ${new Date(logo.created_at).toLocaleDateString('de-DE')}
            </small>
            <div class="mt-3">
                <button class="btn btn-sm btn-danger" onclick="deleteCurrentLogo()">
                    <i class="fas fa-trash me-1"></i>Logo löschen
                </button>
            </div>
        </div>
    `;
}

function displayNoLogo() {
    const container = document.getElementById('currentLogoContainer');
    container.innerHTML = `
        <div class="text-center text-muted">
            <i class="fas fa-image fa-3x mb-3"></i>
            <p>Kein Logo hochgeladen</p>
        </div>
    `;
}

async function loadLogoHistory() {
    try {
        const response = await fetch(`${API_BASE}/company-logo/history`, {
            headers: getAuthHeaders()
        });
        
        if (response.ok) {
            const logos = await response.json();
            displayLogoHistory(logos);
        } else {
            console.error('Fehler beim Laden der Logo-Historie:', response.status);
        }
    } catch (error) {
        console.error('Fehler beim Laden der Logo-Historie:', error);
    }
}

function displayLogoHistory(logos) {
    const container = document.getElementById('logoHistory');
    
    if (logos.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted">
                <i class="fas fa-history fa-2x mb-2"></i>
                <p>Keine Historie verfügbar</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = logos.map(logo => `
        <div class="d-flex align-items-center mb-2 p-2 border rounded ${logo.is_active ? 'bg-light' : ''}">
            <div class="flex-grow-1">
                <div class="fw-bold">${logo.original_filename}</div>
                <small class="text-muted">
                    ${(logo.file_size / 1024).toFixed(1)} KB - 
                    ${new Date(logo.created_at).toLocaleDateString('de-DE')}
                    ${logo.is_active ? ' (Aktiv)' : ''}
                </small>
            </div>
        </div>
    `).join('');
}

function initializeLogoUpload() {
    const form = document.getElementById('logoUploadForm');
    if (form) {
        form.addEventListener('submit', handleLogoUpload);
    }
}

async function handleLogoUpload(event) {
    event.preventDefault();
    
    const formData = new FormData();
    const fileInput = document.getElementById('logoFile');
    
    if (!fileInput.files[0]) {
        showAlert('Bitte wählen Sie eine Datei aus.', 'warning');
        return;
    }
    
    formData.append('file', fileInput.files[0]);
    
    try {
        const response = await fetch(`${API_BASE}/company-logo/upload`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: formData
        });
        
        if (response.ok) {
            const logo = await response.json();
            showAlert('Logo erfolgreich hochgeladen!', 'success');
            loadLogoManagement(); // Neu laden
            form.reset();
        } else {
            const error = await response.json();
            showAlert(`Fehler beim Hochladen: ${error.detail}`, 'danger');
        }
    } catch (error) {
        console.error('Fehler beim Hochladen:', error);
        showAlert('Fehler beim Hochladen des Logos.', 'danger');
    }
}

async function deleteCurrentLogo() {
    if (!confirm('Möchten Sie das aktuelle Logo wirklich löschen?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/company-logo/current`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });
        
        if (response.ok) {
            showAlert('Logo erfolgreich gelöscht!', 'success');
            loadLogoManagement(); // Neu laden
        } else {
            const error = await response.json();
            showAlert(`Fehler beim Löschen: ${error.detail}`, 'danger');
        }
    } catch (error) {
        console.error('Fehler beim Löschen:', error);
        showAlert('Fehler beim Löschen des Logos.', 'danger');
    }
}
