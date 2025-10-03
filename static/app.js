async function initializeApp() {
    authToken = localStorage.getItem('access_token');
    if (!authToken) {
        showLoginPrompt();
        return;
    }

    await hydrateThemeFromServer();
    if (!authToken) {
        return;
    }
    await loadUserData();

    const section = window.location.hash.replace('#', '') || 'dashboard';
    showSection(section);
}

async function loadUsers() {
    if (!authToken) {
        showLoginPrompt();
        return [];
    }

    try {
        const response = await fetch(`${API_BASE}/auth/users`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.ok) {
            usersCache = await response.json();
            return usersCache;
        } else if (response.status === 403) {
            console.warn('Keine Berechtigung für Benutzerverwaltung.');
            usersCache = [];
        } else {
            console.warn('Fehler beim Laden der Benutzerliste:', response.status);
            usersCache = [];
        }
    } catch (error) {
        console.error('Fehler beim Laden der Benutzer:', error);
        usersCache = [];
    }

    return usersCache;
}

function displayUsers(users) {
    const tbody = document.getElementById('users-table');
    if (!tbody) return;

    if (!Array.isArray(users) || users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Keine Benutzer gefunden</td></tr>';
        return;
    }

    tbody.innerHTML = users.map(user => {
        const lastLogin = user.last_login ? new Date(user.last_login).toLocaleString('de-DE') : 'Nie';
        const activeBadge = user.is_active ? '<span class="badge bg-success">Aktiv</span>' : '<span class="badge bg-secondary">Inaktiv</span>';
        return `
            <tr>
                <td>${user.full_name || user.name || '-'}</td>
                <td>${user.username}</td>
                <td>${user.email || '-'}</td>
                <td>${user.role}</td>
                <td>${activeBadge}</td>
                <td>${lastLogin}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="showUserModal(${user.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-warning me-1" onclick="resetUserPassword(${user.id})">
                        <i class="fas fa-key"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

function showUserModal(userId = null) {
    const modalElement = document.getElementById('userModal');
    if (!modalElement) return;

    const modal = new bootstrap.Modal(modalElement);
    const title = document.getElementById('userModalTitle');
    const form = document.getElementById('userForm');
    const passwordGroup = document.getElementById('userPasswordGroup');

    if (userId) {
        const user = usersCache.find(u => u.id === Number(userId));
        if (!user) {
            showAlert('Benutzer nicht gefunden.', 'warning');
            return;
        }

        title.textContent = 'Benutzer bearbeiten';
        document.getElementById('userId').value = user.id;
        document.getElementById('userFullName').value = user.full_name || user.name || '';
        document.getElementById('userUsername').value = user.username;
        document.getElementById('userEmail').value = user.email || '';
        document.getElementById('userRole').value = user.role;
        document.getElementById('userIsActive').checked = !!user.is_active;
        document.getElementById('userPassword').value = '';
        passwordGroup.querySelector('.form-text').textContent = 'Passwort leer lassen, um es nicht zu ändern.';
    } else {
        title.textContent = 'Neuen Benutzer anlegen';
        form.reset();
        document.getElementById('userId').value = '';
        document.getElementById('userIsActive').checked = true;
        passwordGroup.querySelector('.form-text').textContent = 'Mindestens 8 Zeichen.';
    }

    modal.show();
}

async function saveUser() {
    const id = document.getElementById('userId').value;
    const fullName = document.getElementById('userFullName').value.trim();
    const username = document.getElementById('userUsername').value.trim();
    const email = document.getElementById('userEmail').value.trim();
    const role = document.getElementById('userRole').value;
    const isActive = document.getElementById('userIsActive').checked;
    const password = document.getElementById('userPassword').value;

    if (!fullName) {
        showAlert('Name ist ein Pflichtfeld.', 'warning');
        return;
    }

    let url;
    let method;
    let body;

    if (id) {
        url = `${API_BASE}/auth/users/${id}`;
        method = 'PUT';
        body = {
            email,
            full_name: fullName,
            role,
            is_active: isActive
        };
    } else {
        if (!username) {
            showAlert('Benutzername ist ein Pflichtfeld.', 'warning');
            return;
        }

        if (!password || password.length < 8) {
            showAlert('Passwort muss mindestens 8 Zeichen haben.', 'warning');
            return;
        }

        url = `${API_BASE}/auth/register`;
        method = 'POST';
        body = {
            username,
            email,
            full_name: fullName,
            role,
            password
        };
    }

    try {
        const response = await fetch(url, {
            method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(body)
        });

        if (response.ok) {
            bootstrap.Modal.getInstance(document.getElementById('userModal')).hide();
            showAlert('Benutzer gespeichert.', 'success');
            loadUsers();
        } else {
            const error = await response.json().catch(() => ({}));
            showAlert(error.detail || 'Fehler beim Speichern des Benutzers.', 'danger');
        }
    } catch (error) {
        console.error('Fehler beim Speichern des Benutzers:', error);
        showAlert('Fehler beim Speichern des Benutzers.', 'danger');
    }
}

async function resetUserPassword(userId) {
    if (!confirm('Passwort für diesen Benutzer zurücksetzen?')) {
        return;
    }

    const newPassword = prompt('Neues Passwort eingeben (min. 8 Zeichen):');
    if (!newPassword) {
        showAlert('Passwort wurde nicht geändert.', 'info');
        return;
    }
    if (newPassword.length < 8) {
        showAlert('Passwort muss mindestens 8 Zeichen haben.', 'warning');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/auth/users/${userId}/reset-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ password: newPassword })
        });

        if (response.ok) {
            showAlert('Passwort wurde aktualisiert.', 'success');
        } else {
            const error = await response.json().catch(() => ({}));
            showAlert(error.detail || 'Fehler beim Zurücksetzen des Passworts.', 'danger');
        }
    } catch (error) {
        console.error('Fehler beim Zurücksetzen des Passworts:', error);
        showAlert('Fehler beim Zurücksetzen des Passworts.', 'danger');
    }
}
// Logo-Management laden
async function loadLogoManagement() {
    try {
        await Promise.all([loadCurrentLogo(), loadLogoHistory()]);
        setupLogoManagementHandlers();
    } catch (error) {
        console.error('Fehler beim Laden des Logo-Managements:', error);
        showAlert('Logo-Verwaltung konnte nicht geladen werden.', 'danger');
    }
}

async function loadCurrentLogo() {
    const container = document.getElementById('currentLogoContainer');
    if (!container) return;

    try {
        const response = await apiRequest(`${API_BASE}/company-logo/current`);

        if (response.ok) {
            const logo = await response.json();
            renderCurrentLogo(logo);
        } else if (response.status === 404) {
            renderNoLogo();
        } else {
            throw new Error(`HTTP ${response.status}`);
        }
    } catch (error) {
        console.error('Fehler beim Laden des Logos:', error);
        renderNoLogo('Logo konnte nicht geladen werden');
    }
}

function renderCurrentLogo(logo) {
    const container = document.getElementById('currentLogoContainer');
    if (!container) return;

    if (!logo) {
        renderNoLogo();
        return;
    }

    const createdAt = logo.created_at ? new Date(logo.created_at).toLocaleString('de-DE') : '-';
    const sizeKb = logo.file_size ? (logo.file_size / 1024).toFixed(1) : '0.0';

    container.innerHTML = `
        <div class="text-center">
            <img src="/company-logo/view?logo_id=${logo.id}&ts=${Date.now()}" alt="Firmenlogo" class="img-fluid mb-3 rounded shadow-sm" style="max-height: 180px; object-fit: contain;">
            <h6 class="fw-bold">${logo.original_filename || 'Logo'}</h6>
            <small class="text-muted d-block">${sizeKb} KB • ${createdAt}</small>
            <div class="mt-3">
                <button class="btn btn-sm btn-outline-danger" id="deleteLogoBtn">
                    <i class="fas fa-trash me-1"></i>Logo löschen
                </button>
            </div>
        </div>
    `;

    const deleteBtn = document.getElementById('deleteLogoBtn');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', async () => {
            if (!confirm('Möchten Sie das aktuelle Logo wirklich löschen?')) return;

            try {
                const response = await apiRequest(`${API_BASE}/company-logo/current`, {
                    method: 'DELETE'
                });

                if (!response.ok) {
                    const error = await response.json().catch(() => ({}));
                    throw new Error(error.detail || 'Fehler beim Löschen');
                }

                showAlert('Logo erfolgreich gelöscht.', 'success');
                await loadLogoManagement();
            } catch (error) {
                console.error('Fehler beim Löschen des Logos:', error);
                showAlert(error.message || 'Logo konnte nicht gelöscht werden.', 'danger');
            }
        });
    }
}

function renderNoLogo(message = 'Kein Logo hochgeladen') {
    const container = document.getElementById('currentLogoContainer');
    if (!container) return;

    container.innerHTML = `
        <div class="text-center text-muted">
            <i class="fas fa-image fa-3x mb-3"></i>
            <p>${message}</p>
        </div>
    `;
}

async function loadLogoHistory() {
    const container = document.getElementById('logoHistoryContainer');
    if (!container) return;

    try {
        const response = await apiRequest(`${API_BASE}/company-logo/history`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const history = await response.json();
        renderLogoHistory(history);
    } catch (error) {
        console.error('Fehler beim Laden der Logo-Historie:', error);
        container.innerHTML = `
            <div class="alert alert-danger mb-0" role="alert">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Historie konnte nicht geladen werden.
            </div>
        `;
    }
}

function renderLogoHistory(history) {
    const container = document.getElementById('logoHistoryContainer');
    if (!container) return;

    if (!history || history.length === 0) {
        container.innerHTML = `
            <div class="text-center text-muted">
                <i class="fas fa-history fa-2x mb-2"></i>
                <p>Noch keine Logos hochgeladen.</p>
            </div>
        `;
        return;
    }

    const rows = history.map((entry) => {
        const createdAt = entry.created_at ? new Date(entry.created_at).toLocaleString('de-DE') : '-';
        const sizeKb = entry.file_size ? (entry.file_size / 1024).toFixed(1) : '0.0';
        const badge = entry.is_active
            ? '<span class="badge bg-success">Aktiv</span>'
            : '<span class="badge bg-secondary">Inaktiv</span>';

        const previewBtn = `
            <a class="btn btn-sm btn-outline-primary" href="/company-logo/view?logo_id=${entry.id}" target="_blank" title="Anzeigen">
                <i class="fas fa-eye"></i>
            </a>
        `;

        const deleteBtn = entry.is_active
            ? ''
            : `
                <button
                    class="btn btn-sm btn-outline-danger ms-2"
                    data-logo-delete="${entry.id}"
                    title="Löschen"
                >
                    <i class="fas fa-trash"></i>
                </button>
            `;

        return `
            <tr>
                <td>${entry.original_filename || entry.filename}</td>
                <td>${sizeKb} KB</td>
                <td>${createdAt}</td>
                <td>${badge}</td>
                <td class="text-end">
                    ${previewBtn}
                    ${deleteBtn}
                </td>
            </tr>
        `;
    }).join('');

    container.innerHTML = `
        <div class="table-responsive">
            <table class="table table-striped align-middle mb-0">
                <thead class="table-light">
                    <tr>
                        <th>Datei</th>
                        <th>Größe</th>
                        <th>Hochgeladen am</th>
                        <th>Status</th>
                        <th class="text-end">Aktion</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows}
                </tbody>
            </table>
        </div>
    `;

    container.querySelectorAll('[data-logo-delete]').forEach((btn) => {
        btn.addEventListener('click', async () => {
            const logoId = btn.getAttribute('data-logo-delete');
            if (!logoId) return;
            if (!confirm('Logo endgültig löschen?')) return;

            try {
                const response = await apiRequest(`${API_BASE}/company-logo/${logoId}`, {
                    method: 'DELETE'
                });

                if (!response.ok) {
                    const error = await response.json().catch(() => ({}));
                    throw new Error(error.detail || 'Logo konnte nicht gelöscht werden');
                }

                showAlert('Logo gelöscht.', 'success');
                await loadLogoManagement();
            } catch (error) {
                console.error('Fehler beim Löschen des Logos:', error);
                showAlert(error.message || 'Logo konnte nicht gelöscht werden.', 'danger');
            }
        });
    });
}

function setupLogoManagementHandlers() {
    const form = document.getElementById('logoUploadForm');
    if (form && !form.dataset.bound) {
        form.dataset.bound = 'true';
        form.addEventListener('submit', handleLogoUpload);
    }
}

async function handleLogoUpload(event) {
    event.preventDefault();
    const form = event.target;
    const fileInput = document.getElementById('logoFile');

    if (!fileInput || !fileInput.files || !fileInput.files[0]) {
        showAlert('Bitte wählen Sie eine Logodatei aus.', 'warning');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        const response = await fetch(`${API_BASE}/company-logo/upload`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            },
            body: formData
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || 'Fehler beim Hochladen');
        }

        showAlert('Logo erfolgreich hochgeladen!', 'success');
        form.reset();
        await loadLogoManagement();
    } catch (error) {
        console.error('Fehler beim Hochladen des Logos:', error);
        showAlert(error.message || 'Logo konnte nicht hochgeladen werden.', 'danger');
    }
}

/**
 * Bau-Dokumentations-App - Frontend JavaScript
 * Verwaltet die Benutzeroberfläche und API-Kommunikation
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

// Cache für zuletzt geladene Angebote
let offersCache = [];
let invoicesCache = [];
let currentLogoCache = null;
let employeesCache = [];
let timeEntriesCache = [];
let usersCache = [];
let projects = [];
let billingInfo = null;
let tenantSettings = null;

const EMPLOYEE_USER_STORAGE_KEY = 'employeeUserAssignments';
let employeeUserAssignments = {};

if (typeof localStorage !== 'undefined') {
    try {
        const storedAssignments = localStorage.getItem(EMPLOYEE_USER_STORAGE_KEY);
        if (storedAssignments) {
            employeeUserAssignments = JSON.parse(storedAssignments) || {};
            }
        } catch (error) {
        console.warn('Konnte gespeicherte Mitarbeiter-Benutzer-Zuordnungen nicht laden:', error);
        employeeUserAssignments = {};
    }
}

// API Base URL
const API_BASE = window.location.origin.replace(/\/$/, '');
const USER_SETTINGS_ENDPOINT = `${API_BASE}/user/settings`;

async function createAutoOffer(projectId) {
    if (!authToken) {
        showAlert('Bitte melden Sie sich an', 'warning');
        return;
    }
    
    try {
        // Falls keine Projekt-ID übergeben wurde, nehme das erste verfügbare Projekt
        let selectedProjectId = projectId;
        
        if (!selectedProjectId) {
            const projectsResponse = await fetch(`${API_BASE}/projects`, {
                headers: { 'Authorization': `Bearer ${authToken}` }
            });
            
            if (projectsResponse.ok) {
                const projects = await projectsResponse.json();
                if (projects.length === 0) {
                    showAlert('Kein Projekt verfügbar. Bitte legen Sie zuerst ein Projekt an.', 'warning');
                    return;
                }
                selectedProjectId = projects[0].id;
            } else {
                throw new Error('Projekte konnten nicht geladen werden');
            }
        }
        
        // Automatisches Angebot erstellen über Backend
        const response = await fetch(`${API_BASE}/offers/auto`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                project_id: selectedProjectId,
                currency: 'EUR'
            })
        });
        
        if (response.ok) {
            const createdOffer = await response.json();
            showAlert('Automatisches Angebot erfolgreich erstellt!', 'success');
            
            // Automatische Angebote neu laden
            await loadAutoOffers();
        } else if (response.status === 401) {
            showLoginPrompt();
        } else if (response.status === 404) {
            showAlert('Projekt nicht gefunden', 'danger');
        } else {
            const errorData = await response.json().catch(() => ({}));
            showAlert(errorData.detail || 'Fehler beim Erstellen des automatischen Angebots', 'danger');
        }
    } catch (error) {
        console.error('Fehler beim automatischen Angebot:', error);
        showAlert('Fehler beim Erstellen des automatischen Angebots', 'danger');
    }
}

function getStatusText(status) {
    const statusMapping = {
        'entwurf': 'Entwurf',
        'gesendet': 'Gesendet',
        'genehmigt': 'Genehmigt',
        'abgelehnt': 'Abgelehnt',
        'bezahlt': 'Bezahlt',
        'überfällig': 'Überfällig'
    };
    return statusMapping[status] || status || 'Unbekannt';
}

// Initialisierung beim Laden der Seite
document.addEventListener('DOMContentLoaded', () => {
    initializeTheme();

    document.querySelectorAll('#mainNavigation [data-section]').forEach(link => {
        link.addEventListener('click', async (event) => {
            event.preventDefault();
            const section = link.getAttribute('data-section');
            await showSection(section);
        });
    });

    const logoModalTrigger = document.getElementById('openLogoModal');
    if (logoModalTrigger) {
        logoModalTrigger.addEventListener('click', async (event) => {
            event.preventDefault();
            await showLogoManagement();
        });
    }

    const checkoutBtn = document.getElementById('billing-checkout-btn');
    const refreshBtn = document.getElementById('billing-refresh-btn');
    if (checkoutBtn) checkoutBtn.addEventListener('click', startCheckout);
    if (refreshBtn) refreshBtn.addEventListener('click', loadBillingStatus);

    const tenantSaveBtn = document.getElementById('tenantSettingsSaveBtn');
    if (tenantSaveBtn) tenantSaveBtn.addEventListener('click', async (event) => {
        event.preventDefault();
        await saveTenantSettings();
        const alertContainer = document.getElementById('tenantSettingsPreview');
        if (alertContainer) {
            alertContainer.classList.add('border-success');
            setTimeout(() => alertContainer.classList.remove('border-success'), 2000);
        }
    });

    // Formular Event Listener registrieren
    setupFormEventListeners();

    initializeApp();
});

function getOrCreateModalInstance(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return null;
    if (!window.bootstrap || !window.bootstrap.Modal) {
        console.warn('Bootstrap Modal ist nicht verfügbar.');
        return null;
    }
    return window.bootstrap.Modal.getOrCreateInstance(element);
}

async function showTenantSettingsModal() {
    await loadTenantSettings();
    renderTenantSettingsPreview(tenantSettings);
}

function showLogoManagementModal() {
    if (!logoManagementModalInstance) {
        logoManagementModalInstance = getOrCreateModalInstance('logoManagementModal');
    }
    if (logoManagementModalInstance) {
        logoManagementModalInstance.show();
    }
}

// Event Listeners einrichten
function setupEventListeners() {
    // Progress Slider für Berichte
    const progressSlider = document.getElementById('reportProgress');
    if (progressSlider) {
        progressSlider.addEventListener('input', function() {
            document.getElementById('progressValue').textContent = this.value + '%';
        });
    }
    
    // Angebotspositionen berechnen
    document.addEventListener('input', function(e) {
        if (e.target.classList.contains('item-quantity') || 
            e.target.classList.contains('item-unit-price')) {
            calculateOfferTotal();
        }
    });
    
    // Stundenerfassung Validierung
    document.addEventListener('input', function(e) {
        if (e.target.id === 'timeEntryHours' || e.target.id === 'timeEntryDescription') {
            validateTimeEntry();
        }
    });
}

// Sektionen wechseln
async function showSection(sectionName) {
    if (showSection._active === sectionName) return;
    showSection._active = sectionName;

        if (!hasAccessToSection(sectionName)) {
        showSection._active = null;
        if (sectionName !== 'dashboard') await showSection('dashboard');
        else showLoginPrompt();
            return;
        }
    
    document.querySelectorAll('.section').forEach(section => {
        section.style.display = 'none';
        section.classList.remove('active');
    });
    
    document.querySelectorAll('#mainNavigation [data-section]').forEach(link => {
        link.classList.remove('active');
    });
    
    const targetSection = document.getElementById(`${sectionName}-section`);
    if (targetSection) {
        targetSection.style.display = 'block';
        targetSection.classList.add('active');
        const activeLink = document.querySelector(`#mainNavigation [data-section="${sectionName}"]`);
        if (activeLink) activeLink.classList.add('active');
        await loadSectionData(sectionName);
    }

    showSection._active = null;
}

// Sektionsspezifische Daten laden
async function loadSectionData(sectionName) {
    switch (sectionName) {
        case 'dashboard':
            await loadDashboardData();
            break;
        case 'projects':
            await loadProjects();
            break;
        case 'offers':
            await loadOffers();
            break;
        case 'auto-offers':
            await loadAutoOffers();
            break;
        case 'invoices':
            await loadInvoices();
            break;
        case 'billing':
            await loadBillingStatus();
            break;
        case 'reports':
            await loadReports();
            break;
        case 'time-tracking':
            await loadTimeTrackingData();
            break;
        case 'tenant-settings':
            await loadTenantSettings();
            break;
        case 'settings':
            await loadTenantSettings();
            await loadEmployees();
            await loadUsers();
            await loadInvitations();
            break;
        default:
            console.warn('Unbekannte Sektion:', sectionName);
    }
}

// Prüfen ob Benutzer Zugriff auf Sektion hat
function hasAccessToSection(sectionName) {
    // Wenn currentUser noch nicht geladen ist, erlaube Dashboard
    if (!currentUser) {
        console.log('currentUser noch nicht geladen, erlaube Dashboard');
        return sectionName === 'dashboard';
    }
    
    const role = currentUser.role;
    console.log('Prüfe Zugriff für Rolle:', role, 'auf Sektion:', sectionName);
    
    // Admin hat Zugriff auf alles
    if (role === 'admin') return true;
    
    // Buchhalter hat Zugriff auf alles außer Mitarbeiter
    if (role === 'buchhalter') {
        const allowed = ['dashboard', 'projects', 'offers', 'invoices', 'reports', 'billing', 'tenant-settings', 'settings'];
        return allowed.includes(sectionName);
    }
    
    // Mitarbeiter hat nur Zugriff auf bestimmte Bereiche
    if (role === 'mitarbeiter') {
        const allowedSections = ['dashboard', 'projects', 'time-tracking'];
        return allowedSections.includes(sectionName);
    }
    
    return false;
}

// Benutzerdaten laden
async function loadUserData() {
    if (!authToken) {
        showLoginPrompt();
        return;
    }

    try {
        console.log('Lade Benutzerdaten mit Token:', authToken ? 'Token vorhanden' : 'Kein Token');

        const response = await fetch(`${API_BASE}/auth/me`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        console.log('API Response Status:', response.status);

        if (response.ok) {
            const payload = await response.json();
            if (payload && typeof payload === 'object' && 'user' in payload) {
                currentUser = payload.user;
                tenantSettings = {
                    company_name: 'Trockenbau Stuttgart GmbH',
                    company_address: 'Musterstraße 123, 70173 Stuttgart',
                    company_phone: '0711-123456',
                    company_fax: '0711-123457',
                    company_email: 'info@trockenbau-stuttgart.de',
                    ...payload.tenant
                };
            } else {
                currentUser = payload;
            }
            console.log('Benutzerdaten geladen:', currentUser);
            updateUserDisplay();
            if (tenantSettings) fillTenantSettingsForm(tenantSettings);
            renderTenantSettingsPreview(tenantSettings);
            await loadInvitations();
        } else if (response.status === 401) {
            console.log('Token ungültig, zeige Login-Prompt');
            localStorage.removeItem('access_token');
            localStorage.removeItem('user_role');
            showLoginPrompt();
        } else {
            console.log('API-Fehler:', response.status);
            showLoginPrompt();
        }
    } catch (error) {
        console.error('Fehler beim Laden der Benutzerdaten:', error);
        showLoginPrompt();
    }
}

// Benutzeranzeige aktualisieren
function updateUserDisplay() {
    const userDisplay = document.getElementById('userDisplay');
    if (userDisplay && currentUser) {
        const displayName = currentUser.full_name || currentUser.name || currentUser.username || 'Unbekannter Benutzer';
        const displayRole = currentUser.role || 'unbekannt';
        const email = currentUser.email || '';
        const lastLogin = currentUser.last_login ? new Date(currentUser.last_login).toLocaleString('de-DE') : 'Noch keine Anmeldung';
        userDisplay.innerHTML = `
            <div class="text-primary fw-bold">
                <i class="fas fa-user me-2"></i>${displayName}
                <br><small class="text-primary text-opacity-75">${displayRole}</small>
                ${email ? `<br><small class="text-muted">${email}</small>` : ''}
                <br><small class="text-muted">Letzte Anmeldung: ${lastLogin}</small>
                <br><button class="btn btn-sm btn-outline-primary mt-2" onclick="logout()">
                    <i class="fas fa-sign-out-alt me-1"></i>Abmelden
                </button>
            </div>
        `;
        
        // Navigation basierend auf Benutzerrolle anpassen
        updateNavigationForRole(displayRole);
        
        // Admin-Benachrichtigungen anzeigen (nur für Admin)
        if (currentUser.role === 'admin') {
            document.getElementById('adminNotifications').style.display = 'block';
            loadAdminNotifications();
        } else {
            document.getElementById('adminNotifications').style.display = 'none';
        }
    }
}

// Navigation basierend auf Benutzerrolle anpassen
function updateNavigationForRole(role) {
    const navItems = {
        reports: document.querySelector('[data-section="reports"]'),
        offers: document.querySelector('[data-section="offers"]'),
        invoices: document.querySelector('[data-section="invoices"]'),
        timeTracking: document.querySelector('[data-section="time-tracking"]'),
        billing: document.getElementById('billing-nav'),
        settings: document.getElementById('settings-nav')
    };

    const setDisplay = (element, visible) => {
        if (!element) return;
        element.style.display = visible ? 'block' : 'none';
    };

    switch (role) {
        case 'mitarbeiter':
            setDisplay(navItems.reports, false);
            setDisplay(navItems.offers, false);
            setDisplay(navItems.invoices, false);
            setDisplay(navItems.billing, false);
            setDisplay(navItems.settings, false);
            break;
        case 'buchhalter':
            setDisplay(navItems.reports, true);
            setDisplay(navItems.offers, true);
            setDisplay(navItems.invoices, true);
            setDisplay(navItems.billing, true);
            setDisplay(navItems.settings, true);
            break;
        default: // admin
            Object.values(navItems).forEach(item => setDisplay(item, true));
            break;
    }
}

// Login-Prompt anzeigen
function showLoginPrompt() {
    const userDisplay = document.getElementById('userDisplay');
    if (userDisplay) {
        userDisplay.innerHTML = `
            <div class="text-center">
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <strong>Authentifizierung erforderlich</strong>
                    <br><small>Bitte melden Sie sich erneut an</small>
                    <br><button class="btn btn-sm btn-primary mt-2" onclick="window.location.href='/login'">
                        <i class="fas fa-sign-in-alt me-1"></i>Zur Anmeldung
                    </button>
                </div>
            </div>
        `;
    }
}

// Logout-Funktion
function logout() {
    // Token aus localStorage entfernen
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_role');
    
    // Zur Login-Seite weiterleiten
    window.location.href = '/login';
}

// Dashboard-Daten laden
async function loadDashboardData() {
    if (!authToken) {
        showLoginPrompt();
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/dashboard`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            renderDashboard(data);
        } else if (response.status === 401) {
            showLoginPrompt();
        } else {
            showAlert('Dashboard konnte nicht geladen werden', 'danger');
        }
    } catch (error) {
        console.error('Fehler beim Laden des Dashboards:', error);
        showAlert('Dashboard konnte nicht geladen werden', 'danger');
    }
}

function renderDashboard(data) {
    if (!data || typeof data !== 'object') {
        console.warn('Ungültige Dashboard-Daten:', data);
        return;
    }

    const projectsCount = document.getElementById('projects-count');
    const reportsCount = document.getElementById('reports-count');
    const offersCount = document.getElementById('offers-count');
    const totalRevenue = document.getElementById('total-revenue');
    const monthlyRevenue = document.getElementById('monthly-revenue');
    const weekHours = document.getElementById('hours-this-week');
    const totalHours = document.getElementById('total-hours');
    const activeProjects = document.getElementById('active-projects');
    const pendingOffers = document.getElementById('pending-offers');
    const openInvoices = document.getElementById('open-invoices');

    if (projectsCount) projectsCount.textContent = (data.projects?.total ?? 0) + '';
    if (reportsCount) reportsCount.textContent = (data.reports?.total ?? 0) + '';
    if (offersCount) offersCount.textContent = (data.offers?.total ?? 0) + '';

    if (totalRevenue) {
        const value = data.revenue?.total ?? 0;
        totalRevenue.textContent = `${value.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} €`;
    }

    if (monthlyRevenue) {
        const value = data.revenue?.this_month ?? 0;
        monthlyRevenue.textContent = `${value.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} €`;
    }

    if (weekHours) {
        const value = data.time_tracking?.hours_this_week ?? 0;
        weekHours.textContent = `${value.toFixed(2)} h`;
    }

    if (totalHours) {
        const value = data.time_tracking?.total_hours ?? 0;
        totalHours.textContent = `${value.toFixed(2)} h`;
    }

    if (activeProjects) activeProjects.textContent = (data.projects?.active ?? 0) + '';
    if (pendingOffers) pendingOffers.textContent = (data.offers?.pending ?? 0) + '';
    if (openInvoices) openInvoices.textContent = (data.invoices?.open ?? 0) + '';
}

// Projekte laden
async function loadProjects() {
    if (!authToken) {
        showLoginPrompt();
        return [];
    }

    try {
        const response = await fetch(`${API_BASE}/projects`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.ok) {
            projects = await response.json();
            displayProjects(projects);
            updateProjectDropdowns(projects);
            populateTimeEntryProjectSelect();
            populateInvoiceProjectSelect();
            return projects;
        } else if (response.status === 401) {
            showLoginPrompt();
        } else {
            showAlert('Fehler beim Laden der Projekte', 'danger');
        }
    } catch (error) {
        console.error('Fehler beim Laden der Projekte:', error);
        showAlert('Fehler beim Laden der Projekte', 'danger');
    }

    return [];
}

function populateInvoiceProjectSelect() {
    const projectSelect = document.getElementById('invoiceProject');
    if (!projectSelect) return;

    projectSelect.innerHTML = '<option value="">Projekt auswählen...</option>';

    if (Array.isArray(projects) && projects.length > 0) {
        projects.forEach(project => {
            const option = document.createElement('option');
            option.value = project.id;
            option.textContent = `${project.name} (${project.client_name || 'Kein Kunde'})`;
            projectSelect.appendChild(option);
        });
    }
}

// Projekte anzeigen
function displayProjects(projects) {
    const tbody = document.getElementById('projects-table');
    if (tbody) {
        if (projects.length > 0) {
            tbody.innerHTML = projects.map(project => `
                <tr style="cursor: pointer;" onclick="showProjectDetails(${project.id})" title="Klicken für Details">
                    <td><strong>${project.name}</strong></td>
                    <td>${project.client_name || '-'}</td>
                    <td><span class="badge bg-${getStatusColor(project.status)}">${project.status}</span></td>
                    <td>${formatDate(project.start_date)}</td>
                    <td>${formatDate(project.end_date)}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1" onclick="event.stopPropagation(); editProject(${project.id})" title="Projekt bearbeiten">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="event.stopPropagation(); deleteProject(${project.id})" title="Projekt löschen" id="delete-btn-${project.id}">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Keine Projekte vorhanden</td></tr>';
        }
    }
}

// Projekt-Dropdowns aktualisieren
function updateProjectDropdowns(projects) {
    const dropdowns = ['reportProject', 'offerProject', 'timeEntryProject', 'clockProject', 'autoInvoiceProject'];
    
    dropdowns.forEach(dropdownId => {
        const dropdown = document.getElementById(dropdownId);
        if (dropdown) {
            dropdown.innerHTML = '<option value="">Projekt auswählen...</option>' +
                projects.map(project => `<option value="${project.id}">${project.name}</option>`).join('');
        }
    });
}

// Mitarbeiter laden
async function loadEmployees() {
    if (!authToken) return;
    try {
        const response = await fetch(`${API_BASE}/employees`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (response.ok) {
            employeesCache = await response.json();
            displayEmployees(employeesCache);
        } else if (response.status === 401) {
            showLoginPrompt();
        } else {
            showAlert('Mitarbeiter konnten nicht geladen werden', 'danger');
        }
    } catch (error) {
        console.error('Fehler beim Laden der Mitarbeiter:', error);
        showAlert('Mitarbeiter konnten nicht geladen werden', 'danger');
    }
}

// Mitarbeiter anzeigen
function displayEmployees(employees) {
    const tbody = document.getElementById('employees-table');
    if (tbody) {
        if (employees.length > 0) {
            tbody.innerHTML = employees.map(employee => {
                const user = findUserForEmployee(employee);
                const usernameDisplay = formatEmployeeUsername(employee);
                const userId = user ? user.id : null;
                const resetTitle = userId !== null ? 'Passwort zurücksetzen' : 'Benutzer auswählen und Passwort zurücksetzen';
                return `
                <tr>
                    <td>${employee.full_name}</td>
                    <td>${usernameDisplay}</td>
                    <td>${employee.position || '-'}</td>
                    <td>${employee.hourly_rate ? employee.hourly_rate.toFixed(2) + ' €' : '-'}</td>
                    <td>${employee.phone || '-'}</td>
                    <td>${employee.email || '-'}</td>
                    <td><span class="badge bg-${employee.is_active ? 'success' : 'secondary'}">${employee.is_active ? 'Aktiv' : 'Inaktiv'}</span></td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1" onclick="editEmployee(${employee.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-warning me-1" onclick="handleEmployeePasswordReset(${employee.id}, ${userId !== null ? userId : 'null'})" data-employee-id="${employee.id}" data-user-id="${userId !== null ? userId : ''}" data-employee-name="${(employee.full_name || '').replace(/\\/g, '\\\\').replace(/"/g, '&quot;')}" title="${resetTitle}">
                            <i class="fas fa-key"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteEmployee(${employee.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>`;
            }).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted">Keine Mitarbeiter vorhanden</td></tr>';
        }
    }
}

function findUserForEmployee(employee) {
    if (!Array.isArray(usersCache) || usersCache.length === 0) {
        return null;
    }

    const assignmentKey = String(employee.id);
    const assignedUserId = employeeUserAssignments[assignmentKey];
    if (assignedUserId) {
        const assigned = usersCache.find(u => u.id === Number(assignedUserId));
        if (assigned) {
            return assigned;
        }
    }

    const email = (employee.email || '').trim().toLowerCase();
    if (email) {
        const byEmail = usersCache.find(u => (u.email || '').trim().toLowerCase() === email);
        if (byEmail) {
            return byEmail;
        }
    }

    const fullName = (employee.full_name || '').trim().toLowerCase();
    if (fullName) {
        const byName = usersCache.find(u => (u.full_name || u.name || '').trim().toLowerCase() === fullName);
        if (byName) {
            return byName;
        }
    }

    return null;
}

function formatEmployeeUsername(employee) {
    const fullName = (employee?.full_name || '').trim();
    if (!fullName) {
        return '-';
    }

    const parts = fullName.split(/\s+/).filter(Boolean);
    if (parts.length === 0) {
        return '-';
    }

    const firstName = sanitizeNamePart(parts[0]);
    const lastName = parts.length > 1 ? sanitizeNamePart(parts[parts.length - 1]) : '';

    if (lastName) {
        return `${lastName}.${firstName || 'user'}`;
    }

    return firstName || '-';
}

function sanitizeNamePart(part) {
    if (!part) {
        return '';
    }

    let normalized = part.trim().toLowerCase();
    const replacements = {
        'ä': 'ae',
        'ö': 'oe',
        'ü': 'ue',
        'ß': 'ss'
    };

    normalized = normalized.replace(/[äöüß]/g, match => replacements[match] || match);

    // Entferne diakritische Zeichen
    if (typeof normalized.normalize === 'function') {
        normalized = normalized.normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    }

    normalized = normalized.replace(/[^a-z0-9]/g, '');

    return normalized;
}

function initializeEmployeeTableEvents() {
    const tbody = document.getElementById('employees-table');
    if (!tbody || initializeEmployeeTableEvents._initialized) {
        return;
    }
    tbody.addEventListener('click', event => {
        const button = event.target.closest('button[data-action]');
        if (!button) return;
        const action = button.dataset.action;
        const employeeId = button.dataset.employeeId;
        switch (action) {
            case 'edit-employee':
                if (employeeId) {
                    editEmployee(Number(employeeId));
                }
                break;
            case 'delete-employee':
                if (employeeId) {
                    deleteEmployee(Number(employeeId));
                }
                break;
            case 'reset-password':
                const userId = button.dataset.userId;
                const fullName = button.dataset.fullName || '';
                if (userId) {
                    resetEmployeePassword(Number(userId), fullName || 'Benutzer');
                }
                break;
        }
    });
    initializeEmployeeTableEvents._initialized = true;
}

// Mitarbeiter-Dropdowns aktualisieren
function updateEmployeeDropdowns(employees) {
    const dropdown = document.getElementById('timeEntryEmployee');
    if (dropdown) {
        dropdown.innerHTML = '<option value="">Mitarbeiter auswählen...</option>' +
            employees.filter(emp => emp.is_active).map(employee => 
                `<option value="${employee.id}">${employee.full_name}</option>`
            ).join('');
    }
}

// Stundeneinträge laden
async function loadTimeEntries() {
    try {
        const response = await fetch(`${API_BASE}/time-entries`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            timeEntriesCache = await response.json();
            displayTimeEntries(timeEntriesCache);
        } else {
            showError('Fehler beim Laden der Stundeneinträge');
        }
    } catch (error) {
        console.error('Fehler beim Laden der Stundeneinträge:', error);
        showError('Fehler beim Laden der Stundeneinträge');
    }
}

// Stundeneinträge anzeigen
function displayTimeEntries(timeEntries) {
    const tbody = document.getElementById('time-entries-table');
    if (tbody) {
        if (Array.isArray(timeEntries) && timeEntries.length > 0) {
            tbody.innerHTML = timeEntries.map(entry => {
                const projectName = entry.project_name || getProjectName(entry.project_id) || 'Unbekannt';
                const employeeName = getEmployeeName(entry.employee_id) || 'Unbekannt';
                const hoursWorked = Number(entry.hours_worked || 0).toFixed(2);
                const breakMinutes = Number(entry.total_break_minutes || 0);

                return `
                <tr>
                    <td>${formatDate(entry.work_date)}</td>
                    <td>${projectName}</td>
                    <td>${employeeName}</td>
                    <td>${formatTime(entry.clock_in)}</td>
                    <td>${formatTime(entry.clock_out)}</td>
                    <td>${hoursWorked}h</td>
                    <td>${breakMinutes} Min</td>
                    <td><span class="badge bg-${entry.is_edited ? 'warning' : 'success'}">${entry.is_edited ? 'Bearbeitet' : 'Original'}</span></td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary me-1" onclick="editTimeEntry(${entry.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteTimeEntry(${entry.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>`;
            }).join('');
        } else {
            tbody.innerHTML = '<tr><td colspan="9" class="text-center text-muted">Keine Stundeneinträge vorhanden</td></tr>';
        }
    }
}

// Berichte laden
async function loadReports() {
    if (!authToken) return;
    try {
        const response = await fetch(`${API_BASE}/reports`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (response.ok) {
            const reports = await response.json();
            displayReports(reports);
        } else if (response.status === 401) {
            showLoginPrompt();
        } else {
            showAlert('Berichte konnten nicht geladen werden', 'danger');
        }
    } catch (error) {
        console.error('Fehler beim Laden der Berichte:', error);
        showAlert('Berichte konnten nicht geladen werden', 'danger');
    }
}

// Status Badge Klasse basierend auf Status bestimmen
function getStatusBadgeClass(status) {
    if (!status) return 'bg-primary';
    
    const statusLower = status.toLowerCase();
    
    // Abgeschlossen - Grün
    if (statusLower.includes('abgeschlossen') || statusLower.includes('fertig') || statusLower.includes('completed') || statusLower.includes('abnahme')) {
        return 'bg-success';
    }
    
    // Material/Verzögerung - Orange
    else if (statusLower.includes('material') || statusLower.includes('verzögerung') || statusLower.includes('wartend')) {
        return 'bg-warning';
    }
    
    // Fehler - Rot
    else if (statusLower.includes('fehler') || statusLower.includes('error') || statusLower.includes('probleme')) {
        return 'bg-danger';
    }
    
    // Qualitätskontrolle/Prüfung - Cyan
    else if (statusLower.includes('prüfung') || statusLower.includes('review') || statusLower.includes('kontroll') || statusLower.includes('qualität')) {
        return 'bg-info';
    }
    
    // Trockenbau-Arbeiten - Blau
    else if (statusLower.includes('gipskarton') || statusLower.includes('dämmung') || statusLower.includes('spachtel') || 
             statusLower.includes('schleif') || statusLower.includes('grundierung') || statusLower.includes('anstrich') || 
             statusLower.includes('reinigung')) {
        return 'bg-primary';
    }
    
    // Pausiert - Grau
    else if (statusLower.includes('pausiert') || statusLower.includes('paused')) {
        return 'bg-secondary';
    }
    
    // Standard - Blau
    else {
        return 'bg-primary';
    }
}

// Berichte anzeigen
async function displayReports(reports) {
    console.log('displayReports aufgerufen mit:', reports ? reports.length : 'undefined', 'Berichten');
    
    const tbody = document.getElementById('reports-table');
    console.log('reports-table Element gefunden:', !!tbody);
    
    if (tbody) {
        if (reports && reports.length > 0) {
            console.log('Rendere', reports.length, 'Berichte');
            
            try {
                // Projekt-Namen für alle Berichte nachladen
                const projectNames = await loadProjectNames();
                console.log('Projekt-Namen geladen:', Object.keys(projectNames).length);
                
                tbody.innerHTML = reports.map(report => {
                    const projectName = projectNames[report.project_id] || 'Unbekannt';
                    const statusBadgeClass = getStatusBadgeClass(report.status);
                    const statusText = report.status || 'In Bearbeitung';
                    
                    return `
                        <tr>
                            <td>
                                <div class="d-flex align-items-center">
                                    <span>${report.title || 'Kein Titel'}</span>
                                    <span class="badge bg-info ms-2" title="Fotos anzeigen" onclick="viewReportFiles(${report.id})" style="cursor: pointer;">
                                        <i class="fas fa-image me-1"></i>Fotos
                                    </span>
                                </div>
                            </td>
                            <td>${projectName}</td>
                            <td>${formatDate(report.report_date)}</td>
                            <td>
                                <span class="badge ${statusBadgeClass}">${statusText}</span>
                            </td>
                            <td>
                                <button class="btn btn-sm btn-outline-primary me-1" onclick="editReport(${report.id})">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-info me-1" onclick="viewReportFiles(${report.id})" title="Fotos anzeigen">
                                    <i class="fas fa-image"></i>
                                </button>
                                <button class="btn btn-sm btn-outline-danger" onclick="deleteReport(${report.id})">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </td>
                        </tr>
                    `;
                }).join('');
                
                console.log('Berichte erfolgreich gerendert');
            } catch (error) {
                console.error('Fehler beim Rendern der Berichte:', error);
                tbody.innerHTML = '<tr><td colspan="5" class="text-center text-danger">Fehler beim Laden der Berichte</td></tr>';
            }
        } else {
            console.log('Keine Berichte vorhanden');
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center text-muted py-4">
                        <i class="fas fa-clipboard-list fa-2x mb-3 d-block text-muted"></i>
                        <h5 class="text-muted">Keine Berichte vorhanden</h5>
                        <p class="text-muted mb-0">Erstellen Sie Ihren ersten Bericht, um loszulegen.</p>
                    </td>
                </tr>
            `;
        }
    } else {
        console.error('reports-table Element nicht gefunden!');
    }
}

// Projekt-Namen nachladen
async function loadProjectNames() {
    try {
        if (!authToken) {
            window.location.href = '/login';
            return;
        }

        const response = await fetch(`${API_BASE}/projects/`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const projects = await response.json();
            const projectNames = {};
            projects.forEach(project => {
                projectNames[project.id] = project.name;
            });
            return projectNames;
        }
        return {};
    } catch (error) {
        console.error('Fehler beim Laden der Projekt-Namen:', error);
        return {};
    }
}

// Dateien eines Berichts anzeigen
async function viewReportFiles(reportId) {
    try {
        const response = await fetch(`${API_BASE}/reports/${reportId}/files`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const files = await response.json();
            showReportFilesModal(files, reportId);
        } else {
            showAlert('Fehler beim Laden der Dateien', 'danger');
        }
    } catch (error) {
        console.error('Fehler beim Laden der Dateien:', error);
        showAlert('Fehler beim Laden der Dateien', 'danger');
    }
}

// Modal für Bericht-Dateien anzeigen
function showReportFilesModal(files, reportId) {
    const modalHtml = `
        <div class="modal fade" id="reportFilesModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Bericht-Fotos</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        ${files.length > 0 ? `
                            <div class="list-group">
                                ${files.map(file => `
                                    <div class="list-group-item d-flex justify-content-between align-items-center">
                                        <div>
                                            <i class="fas fa-image me-2 text-primary"></i>
                                            <span>${file.original_filename || file.filename}</span>
                                            <small class="text-muted ms-2">(${(file.size / 1024).toFixed(1)} KB)</small>
                                        </div>
                                        <div>
                                            <button class="btn btn-sm btn-outline-info me-1" onclick="previewReportFile(${reportId}, '${file.filename}')" title="Foto anzeigen">
                                                <i class="fas fa-eye"></i>
                                            </button>
                                            <button class="btn btn-sm btn-outline-primary me-1" onclick="downloadReportFile(${reportId}, '${file.filename}')" title="Herunterladen">
                                                <i class="fas fa-download"></i>
                                            </button>
                                            <button class="btn btn-sm btn-outline-danger" onclick="deleteReportFile(${reportId}, '${file.filename}')" title="Löschen">
                                                <i class="fas fa-trash"></i>
                                            </button>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        ` : '<p class="text-muted">Keine Fotos vorhanden</p>'}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Schließen</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Altes Modal entfernen
    const existingModal = document.getElementById('reportFilesModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Neues Modal hinzufügen und anzeigen
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = new bootstrap.Modal(document.getElementById('reportFilesModal'));
    modal.show();
    
    // Modal entfernen nach dem Schließen
    document.getElementById('reportFilesModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}

// Datei herunterladen
async function downloadReportFile(reportId, filename) {
    try {
        const response = await fetch(`${API_BASE}/reports/${reportId}/files/${filename}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } else {
            showAlert('Fehler beim Herunterladen der Datei', 'danger');
        }
    } catch (error) {
        console.error('Fehler beim Herunterladen der Datei:', error);
        showAlert('Fehler beim Herunterladen der Datei', 'danger');
    }
}

// Foto-Vorschau anzeigen
async function previewReportFile(reportId, filename) {
    try {
        const response = await fetch(`${API_BASE}/reports/${reportId}/files/${filename}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const blob = await response.blob();
            
            // Prüfe ob das Bild gültig ist
            if (blob.size === 0) {
                showAlert('Das Bild ist leer oder beschädigt', 'warning');
                return;
            }
            
            // Prüfe ob es ein gültiges Bild ist
            if (!blob.type.startsWith('image/')) {
                showAlert('Die Datei ist kein gültiges Bild', 'warning');
                return;
            }
            
            const imageUrl = URL.createObjectURL(blob);
            showImagePreviewModal(filename, imageUrl);
        } else if (response.status === 404) {
            showAlert('Das Bild wurde nicht gefunden', 'warning');
        } else {
            showAlert('Fehler beim Laden des Fotos', 'danger');
        }
    } catch (error) {
        console.error('Fehler beim Laden des Fotos:', error);
        if (error.message.includes('corrupt') || error.message.includes('truncated')) {
            showAlert('Das Bild ist beschädigt und kann nicht angezeigt werden', 'warning');
        } else {
            showAlert('Fehler beim Laden des Fotos', 'danger');
        }
    }
}

// Foto-Vorschau Modal anzeigen
function showImagePreviewModal(filename, imageUrl) {
    const modalHtml = `
        <div class="modal fade" id="imagePreviewModal" tabindex="-1">
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Foto-Vorschau</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body text-center">
                        <img src="${imageUrl}" class="img-fluid" style="max-height: 70vh; max-width: 100%;" alt="${filename}" 
                             onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                        <div style="display: none; padding: 2rem; color: #dc3545;">
                            <i class="fas fa-exclamation-triangle fa-3x mb-3"></i>
                            <h5>Bild kann nicht angezeigt werden</h5>
                            <p>Das Bild ist möglicherweise beschädigt oder wurde gelöscht.</p>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Schließen</button>
                        <button type="button" class="btn btn-primary" onclick="downloadFromPreview('${imageUrl}', '${filename}')">
                            <i class="fas fa-download me-1"></i>Herunterladen
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Altes Modal entfernen
    const existingModal = document.getElementById('imagePreviewModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Neues Modal hinzufügen und anzeigen
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = new bootstrap.Modal(document.getElementById('imagePreviewModal'));
    modal.show();
    
    // Modal entfernen nach dem Schließen und URL freigeben
    document.getElementById('imagePreviewModal').addEventListener('hidden.bs.modal', function() {
        URL.revokeObjectURL(imageUrl);
        this.remove();
    });
}

// Download aus der Vorschau
function downloadFromPreview(imageUrl, filename) {
    const a = document.createElement('a');
    a.href = imageUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
}

// Datei löschen
async function deleteReportFile(reportId, filename) {
    if (confirm('Möchten Sie diese Datei wirklich löschen?')) {
        try {
            const response = await fetch(`${API_BASE}/reports/${reportId}/files/${filename}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            });
            
            if (response.ok) {
                showAlert('Datei erfolgreich gelöscht', 'success');
                viewReportFiles(reportId); // Modal aktualisieren
            } else {
                showAlert('Fehler beim Löschen der Datei', 'danger');
            }
        } catch (error) {
            console.error('Fehler beim Löschen der Datei:', error);
            showAlert('Fehler beim Löschen der Datei', 'danger');
        }
    }
}

// Angebote laden
async function loadOffers() {
    if (!authToken) return;
    try {
        const response = await fetch(`${API_BASE}/offers`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (response.ok) {
            const offers = await response.json();
            displayOffers(offers);
        } else if (response.status === 401) {
            showLoginPrompt();
        } else {
            showAlert('Angebote konnten nicht geladen werden', 'danger');
        }
    } catch (error) {
        console.error('Fehler beim Laden der Angebote:', error);
        showAlert('Angebote konnten nicht geladen werden', 'danger');
    }
}

// Automatische Angebote laden
async function loadAutoOffers() {
    if (!authToken) return;
    try {
        // Backend-Filter: nur automatisch generierte Angebote abrufen
        const response = await fetch(`${API_BASE}/offers?auto_generated=true`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (response.ok) {
            const autoOffers = await response.json();
            console.log('Automatische Angebote geladen:', autoOffers.length);
            displayAutoOffers(autoOffers);
        } else if (response.status === 401) {
            showLoginPrompt();
        } else {
            showAlert('Automatische Angebote konnten nicht geladen werden', 'danger');
        }
    } catch (error) {
        console.error('Fehler beim Laden der automatischen Angebote:', error);
        showAlert('Automatische Angebote konnten nicht geladen werden', 'danger');
    }
}

// Automatische Angebote anzeigen
function displayAutoOffers(offers) {
    const tbody = document.getElementById('auto-offers-table');
    if (!tbody) return;

    if (!Array.isArray(offers) || offers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Keine automatischen Angebote vorhanden</td></tr>';
        return;
    }

    tbody.innerHTML = offers.map(offer => `
        <tr>
            <td>${offer.title || 'Kein Titel'}</td>
            <td>${offer.client_name || 'N/A'}</td>
            <td>${Number(offer.total_amount || 0).toFixed(2)} ${offer.currency || 'EUR'}</td>
            <td><span class="badge bg-${getStatusColor(offer.status || 'offen')}">${offer.status || 'offen'}</span></td>
            <td>${formatDate(offer.created_at)}</td>
            <td>
                <button class="btn btn-sm btn-outline-info me-1" onclick="viewOffer(${offer.id})" title="Ansehen">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-sm btn-outline-primary me-1" onclick="editOffer(${offer.id})">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn btn-sm btn-outline-success me-1" onclick="createInvoiceFromOffer(${offer.id})" title="Als Rechnung erstellen">
                    <i class="fas fa-file-invoice-dollar"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteOffer(${offer.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

// Angebote anzeigen
function displayOffers(offers) {
    const tbody = document.getElementById('offers-table');
    if (!tbody) return;

    if (!offers || offers.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">Keine Angebote vorhanden</td></tr>';
        return;
    }

    tbody.innerHTML = '';

    offers.forEach(offer => {
        const tr = document.createElement('tr');

        const tdTitle = document.createElement('td');
        tdTitle.textContent = offer.title;

        const tdClient = document.createElement('td');
        tdClient.textContent = offer.client_name || 'N/A';

        const tdAmount = document.createElement('td');
        const amount = Number(offer.total_amount || 0);
        tdAmount.textContent = `${amount.toFixed(2)} ${offer.currency || 'EUR'}`;

        const tdStatus = document.createElement('td');
        const badge = document.createElement('span');
        badge.className = `badge bg-${getStatusColor(offer.status || 'entwurf')}`;
        badge.textContent = offer.status || 'entwurf';
        tdStatus.appendChild(badge);

        const tdValid = document.createElement('td');
        tdValid.textContent = formatDate(offer.valid_until);

        const tdActions = document.createElement('td');

        // Edit-Button
        const editBtn = document.createElement('button');
        editBtn.className = 'btn btn-sm btn-outline-primary me-1';
        editBtn.innerHTML = '<i class="fas fa-edit"></i>';
        editBtn.onclick = () => editOffer(offer.id);

        // Rechnung erstellen Button (falls gewünscht)
        const invoiceBtn = document.createElement('button');
        invoiceBtn.className = 'btn btn-sm btn-outline-success me-1';
        invoiceBtn.title = 'Rechnung erstellen';
        invoiceBtn.innerHTML = '<i class="fas fa-file-invoice-dollar"></i>';
        if (typeof createInvoiceFromOffer === 'function') {
            invoiceBtn.onclick = () => createInvoiceFromOffer(offer.id);
        } else {
            invoiceBtn.classList.add('disabled');
            invoiceBtn.setAttribute('title', 'Funktion nicht verfügbar');
        }

        // Löschen-Button
        const delBtn = document.createElement('button');
        delBtn.className = 'btn btn-sm btn-outline-danger';
        delBtn.innerHTML = '<i class="fas fa-trash"></i>';
        delBtn.onclick = () => deleteOffer(offer.id);

        tdActions.appendChild(editBtn);
        tdActions.appendChild(invoiceBtn);
        tdActions.appendChild(delBtn);

        tr.appendChild(tdTitle);
        tr.appendChild(tdClient);
        tr.appendChild(tdAmount);
        tr.appendChild(tdStatus);
        tr.appendChild(tdValid);
        tr.appendChild(tdActions);

        tbody.appendChild(tr);
    });
}

// Rechnung aus Angebot erstellen (echter API-Call)
async function createInvoiceFromOffer(offerId) {
    if (!offerId) {
        console.warn('createInvoiceFromOffer ohne gültige ID aufgerufen');
        return;
    }

    if (typeof confirm === 'function') {
        const proceed = confirm('Möchten Sie wirklich aus diesem Angebot eine Rechnung erstellen?');
        if (!proceed) {
            return;
        }
    }

    if (!authToken) {
        console.error('Kein Auth-Token vorhanden, kann Rechnung nicht erstellen');
        if (typeof showAlert === 'function') {
            showAlert('Fehler: Kein Authentifizierungs-Token vorhanden.', 'danger');
        }
        return;
    }

    try {
        console.log('Starte Rechnungserstellung für Angebot', offerId);
        if (typeof showAlert === 'function') {
            showAlert('Rechnung wird erstellt...', 'info');
        }

        const response = await fetch(`${API_BASE}/offers/${offerId}/create-invoice`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            let result = {};
            try {
                result = await response.json();
            } catch (parseError) {
                console.warn('Antwort der Rechnungserstellung konnte nicht als JSON gelesen werden', parseError);
            }

            console.log('Rechnung erfolgreich erstellt:', result);
            if (typeof showAlert === 'function') {
                const message = result?.message || 'Rechnung erfolgreich erstellt!';
                showAlert(message, 'success');
            }

            // Listen aktualisieren
            try {
                await loadInvoices();
            } catch (loadError) {
                console.warn('Rechnungen konnten nach Erstellung nicht neu geladen werden:', loadError);
            }

            try {
                await loadOffers();
            } catch (loadError) {
                console.warn('Angebote konnten nach Rechnungserstellung nicht neu geladen werden:', loadError);
            }

            return result;
        }

        // Fehlerhafte Antwort verarbeiten
        let errorMessage = `HTTP ${response.status}`;
        try {
            const errorData = await response.json();
            errorMessage = errorData?.detail || JSON.stringify(errorData);
        } catch (jsonError) {
            console.warn('Fehlerantwort nicht als JSON lesbar:', jsonError);
            try {
                errorMessage = await response.text();
            } catch (textError) {
                console.warn('Fehlerantwort auch nicht als Text lesbar:', textError);
            }
        }

        console.error('Fehler beim Erstellen der Rechnung:', errorMessage);
        if (typeof showAlert === 'function') {
            showAlert(`Fehler beim Erstellen der Rechnung: ${errorMessage}`, 'danger');
        }

    } catch (error) {
        console.error('Netzwerk-/Runtime-Fehler bei Rechnungserstellung:', error);
        if (typeof showAlert === 'function') {
            showAlert(`Fehler beim Erstellen der Rechnung: ${error.message}`, 'danger');
        }
    }
}

// Rechnungen laden
async function loadInvoices() {
    if (!authToken) return;
    try {
        const response = await fetch(`${API_BASE}/invoices`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        if (response.ok) {
            const invoices = await response.json();
            invoicesCache = invoices; // Cache speichern!
            displayInvoices(invoices);
        } else if (response.status === 401) {
            showLoginPrompt();
        } else {
            showAlert('Rechnungen konnten nicht geladen werden', 'danger');
        }
    } catch (error) {
        console.error('Fehler beim Laden der Rechnungen:', error);
        showAlert('Rechnungen konnten nicht geladen werden', 'danger');
    }
}

// Rechnungen anzeigen
function displayInvoices(invoices) {
    const tbody = document.getElementById('invoices-table');
    if (!tbody) {
        console.warn('invoices-table Element nicht gefunden');
        return;
    }

    if (!Array.isArray(invoices) || invoices.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center text-muted">Keine Rechnungen vorhanden</td></tr>';
        return;
    }

    const rowsHtml = invoices.map(invoice => `
                <tr>
                    <td>${invoice.invoice_number}</td>
                    <td>${invoice.title}</td>
            <td>${invoice.client_name || 'N/A'}</td>
            <td>${Number(invoice.total_amount || 0).toFixed(2)} ${invoice.currency || 'EUR'}</td>
            <td><span class="badge bg-${getStatusColor(invoice.status || 'entwurf')}">${invoice.status || 'entwurf'}</span></td>
                    <td>${formatDate(invoice.invoice_date)}</td>
                    <td>${formatDate(invoice.due_date)}</td>
                    <td>
                <button class="btn btn-sm btn-outline-info me-1 preview-btn" data-invoice-id="${invoice.id}" title="Vorschau">
                    <i class="fas fa-eye"></i>
                </button>
                <button class="btn btn-sm btn-outline-success me-1" onclick="downloadInvoicePDF(${invoice.id})" title="PDF herunterladen">
                    <i class="fas fa-download"></i>
                </button>
                        <button class="btn btn-sm btn-outline-primary me-1" onclick="editInvoice(${invoice.id})">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="deleteInvoice(${invoice.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </td>
                </tr>
            `).join('');

    tbody.innerHTML = rowsHtml;

    tbody.querySelectorAll('.preview-btn').forEach(button => {
        button.addEventListener('click', () => {
            const invoiceId = Number(button.dataset.invoiceId);
            if (!isNaN(invoiceId)) {
                previewInvoice(invoiceId);
            }
        });
    });
}

// Rechnungsvorschau anzeigen
function previewInvoice(invoiceId) {
    if (!Array.isArray(invoicesCache) || invoicesCache.length === 0) {
        console.warn('Keine Rechnungen im Cache vorhanden');
        if (typeof showAlert === 'function') {
            showAlert('Keine Rechnungsdaten vorhanden', 'warning');
        }
        return;
    }

    const invoice = invoicesCache.find(inv => inv.id === Number(invoiceId));
    if (!invoice) {
        console.warn('Rechnung nicht im Cache gefunden:', invoiceId);
        loadInvoices().then(() => {
            const refreshed = invoicesCache.find(inv => inv.id === Number(invoiceId));
            if (refreshed) {
                showInvoicePreviewModal(refreshed);
        } else {
                if (typeof showAlert === 'function') {
                    showAlert('Rechnung nicht gefunden.', 'warning');
                }
            }
        });
        return;
    }

    showInvoicePreviewModal(invoice);
}

// Vorschau-Modal generieren und anzeigen
function showInvoicePreviewModal(invoice) {
    try {
        let items = [];
        if (typeof invoice.items === 'string') {
            try {
                items = JSON.parse(invoice.items);
            } catch (parseError) {
                console.warn('Items konnten nicht geparst werden:', parseError);
            }
        } else if (Array.isArray(invoice.items)) {
            items = invoice.items;
        }

        const settings = tenantSettings || {};
        const companyBlock = `
            <div class="invoice-company">
                <h5 class="fw-bold mb-1">${settings.company_name || 'Trockenbau Stuttgart GmbH'}</h5>
                <div>${(settings.company_address || 'Musterstraße 123, 70173 Stuttgart').replace(/\n/g, '<br>')}</div>
                <div>Tel: ${settings.company_phone || '0711-123456'}${settings.company_fax ? ` • Fax: ${settings.company_fax}` : ''}</div>
                <div>E-Mail: ${settings.company_email || 'info@trockenbau-stuttgart.de'}</div>
            </div>`;
        const taxBlock = `
            <div class="invoice-tax mt-3">
                <div>Steuernummer: ${settings.tax_number || '12/345/67890'}</div>
                <div>USt-IdNr.: ${settings.vat_id || 'DE123456789'}</div>
                <div>IBAN: ${settings.bank_iban || 'DE12 3456 7890 1234 5678 90'}</div>
                <div>BIC: ${settings.bank_bic || 'GENODEF1S02'}</div>
                <div>Bank: ${settings.bank_name || 'Musterbank Stuttgart'}</div>
            </div>`;

        const previewHtml = `
            <div class="modal fade" id="previewInvoiceModal" tabindex="-1">
                <div class="modal-dialog modal-xl modal-dialog-centered">
                    <div class="modal-content shadow-lg">
                        <div class="modal-header bg-light">
                            <h5 class="modal-title fw-bold">Rechnungsvorschau: ${invoice.invoice_number || '—'}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="invoice-preview" style="color: #000;">
                                <div class="row mb-4">
                                    <div class="col-md-6">
                                        <h4 class="fw-bold text-uppercase">Rechnung</h4>
                                        <p><strong>Rechnungsnummer:</strong> ${invoice.invoice_number || '—'}</p>
                                        <p><strong>Erstellt am:</strong> ${formatDate(invoice.invoice_date)}</p>
                                        <p><strong>Fällig am:</strong> ${formatDate(invoice.due_date)}</p>
                                    </div>
                                    <div class="col-md-6 text-md-end">
                                        <h5 class="fw-bold">Kunde</h5>
                                        <p><strong>${invoice.client_name || '—'}</strong></p>
                                        ${invoice.client_address ? `<p>${invoice.client_address.replace(/\n/g, '<br>')}</p>` : ''}
                                    </div>
                                </div>

                                <div class="table-responsive mb-4">
                                    <table class="table table-bordered">
                                        <thead class="table-light">
                                            <tr>
                                                <th>Beschreibung</th>
                                                <th class="text-end">Menge</th>
                                                <th class="text-end">Einheit</th>
                                                <th class="text-end">Einzelpreis</th>
                                                <th class="text-end">Gesamt</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${items.length > 0 ? items.map(item => `
                                                <tr>
                                                    <td>${item.description || '—'}</td>
                                                    <td class="text-end">${Number(item.quantity || 0).toFixed(2)}</td>
                                                    <td class="text-end">${item.unit || 'Stk'}</td>
                                                    <td class="text-end">${Number(item.unit_price || 0).toFixed(2)} EUR</td>
                                                    <td class="text-end">${Number(item.total_price || item.unit_price * item.quantity || 0).toFixed(2)} EUR</td>
                                                </tr>
                                            `).join('') : `
                                                <tr>
                                                    <td colspan="5" class="text-center text-muted">Keine Positionen vorhanden</td>
                                                </tr>
                                            `}
                                        </tbody>
                                    </table>
                                </div>

                                <div class="row g-3">
                                    <div class="col-md-6">
                                        <p><strong>Status:</strong> ${getStatusText(invoice.status)}</p>
                                        <p><strong>Währung:</strong> ${invoice.currency || 'EUR'}</p>
                                        ${invoice.description ? `<div><strong>Beschreibung:</strong><br>${invoice.description}</div>` : ''}
                                    </div>
                                    <div class="col-md-6">
                                        <table class="table table-borderless">
                                            <tbody>
                                                <tr>
                                                    <td><strong>Zwischensumme:</strong></td>
                                                    <td class="text-end">${Number(invoice.total_amount || 0 / 1.19).toFixed(2)} EUR</td>
                                                </tr>
                                                <tr>
                                                    <td><strong>USt (19%):</strong></td>
                                                    <td class="text-end">${Number((invoice.total_amount || 0) - ((invoice.total_amount || 0) / 1.19)).toFixed(2)} EUR</td>
                                                </tr>
                                                <tr class="table-light">
                                                    <td><strong>Gesamtbetrag:</strong></td>
                                                    <td class="text-end fw-bold">${Number(invoice.total_amount || 0).toFixed(2)} EUR</td>
                                                </tr>
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Schließen</button>
                            <button type="button" class="btn btn-primary" data-invoice-id="${invoice.id}" id="preview-download-btn">
                                <i class="fas fa-download me-2"></i>PDF herunterladen
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        const existingModal = document.getElementById('previewInvoiceModal');
        if (existingModal) {
            existingModal.remove();
        }

        document.body.insertAdjacentHTML('beforeend', previewHtml);
        const modalElement = document.getElementById('previewInvoiceModal');
        const modal = new bootstrap.Modal(modalElement);

        modalElement.addEventListener('hidden.bs.modal', () => {
            modalElement.remove();
        }, { once: true });

        modal.show();

        const downloadBtn = document.getElementById('preview-download-btn');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', () => downloadInvoicePDF(invoice.id));
        }

    } catch (error) {
        console.error('Fehler beim Anzeigen der Rechnungsvorschau:', error);
        if (typeof showAlert === 'function') {
            showAlert('Fehler beim Öffnen der Vorschau.', 'danger');
        }
    }
}

// PDF-Download aus Vorschau oder Liste
async function downloadInvoicePDF(invoiceId) {
    try {
        if (!authToken) {
            throw new Error('Kein Authentifizierungs-Token vorhanden');
        }

        const response = await fetch(`${API_BASE}/invoices/${invoiceId}/pdf`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (!response.ok) {
            let errorText = `HTTP ${response.status}`;
            try {
                errorText = await response.text();
            } catch (error) {
                console.warn('Fehlertext konnte nicht gelesen werden:', error);
            }
            throw new Error(errorText);
        }

        const blob = await response.blob();
        const downloadUrl = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = `Rechnung_${invoiceId}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(downloadUrl);

        if (typeof showAlert === 'function') {
            showAlert('PDF erfolgreich heruntergeladen.', 'success');
        }

    } catch (error) {
        console.error('Fehler beim PDF-Download:', error);
        if (typeof showAlert === 'function') {
            showAlert('Fehler beim Herunterladen des PDFs: ' + error.message, 'danger');
        }
    }
}


// Modal-Funktionen
function showProjectModal(projectId = null) {
    const modal = new bootstrap.Modal(document.getElementById('projectModal'));
    const title = document.getElementById('projectModalTitle');
    const form = document.getElementById('projectForm');
    
    if (projectId) {
        title.textContent = 'Projekt bearbeiten';
        form.dataset.projectId = projectId;
        // Projekt-Daten laden und Formular füllen
        loadProjectData(projectId);
    } else {
        title.textContent = 'Neues Projekt';
        form.dataset.projectId = '';
        form.reset();
    }
    
    modal.show();
}

function showReportModal(reportId = null) {
    const modal = new bootstrap.Modal(document.getElementById('reportModal'));
    const title = document.getElementById('reportModalTitle');
    const form = document.getElementById('reportForm');
    
    // Upload-Bereich zurücksetzen
    document.getElementById('uploadedFiles').style.display = 'none';
    document.getElementById('fileList').innerHTML = '';
    document.getElementById('reportFiles').value = '';
    
    if (reportId) {
        title.textContent = 'Bericht bearbeiten';
        form.dataset.reportId = reportId;
        // Bericht-Daten laden und Formular füllen
        loadReportData(reportId);
    } else {
        title.textContent = 'Neuer Bericht';
        form.dataset.reportId = '';
        form.reset();
        // Heutiges Datum setzen
        document.getElementById('reportDate').value = new Date().toISOString().split('T')[0];
    }
    
    modal.show();
}

// Foto-Upload Funktionen für Berichte
function handleFileUpload(event) {
    const files = event.target.files;
    const fileList = document.getElementById('fileList');
    const uploadedFiles = document.getElementById('uploadedFiles');
    
    if (files.length > 0) {
        // Überprüfe, ob alle Dateien Bilder sind
        const validFiles = Array.from(files).filter(file => file.type.startsWith('image/'));
        const invalidFiles = Array.from(files).filter(file => !file.type.startsWith('image/'));
        
        if (invalidFiles.length > 0) {
            showAlert('Nur Bilddateien sind erlaubt! Ungültige Dateien wurden entfernt.', 'warning');
        }
        
        if (validFiles.length > 0) {
            uploadedFiles.style.display = 'block';
            fileList.innerHTML = '';
            
            validFiles.forEach((file, index) => {
                const fileItem = document.createElement('div');
                fileItem.className = 'list-group-item d-flex justify-content-between align-items-center';
                fileItem.innerHTML = `
                    <div>
                        <i class="fas fa-image me-2 text-primary"></i>
                        <span>${file.name}</span>
                        <small class="text-muted ms-2">(${(file.size / 1024).toFixed(1)} KB)</small>
                    </div>
                    <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeFile(${index})">
                        <i class="fas fa-times"></i>
                    </button>
                `;
                fileList.appendChild(fileItem);
            });
        } else {
            uploadedFiles.style.display = 'none';
        }
    } else {
        uploadedFiles.style.display = 'none';
    }
}

function removeFile(index) {
    const fileInput = document.getElementById('reportFiles');
    const dt = new DataTransfer();
    
    Array.from(fileInput.files).forEach((file, i) => {
        if (i !== index) {
            dt.items.add(file);
        }
    });
    
    fileInput.files = dt.files;
    handleFileUpload({ target: fileInput });
}

// Event Listener für Datei-Upload hinzufügen
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('reportFiles');
    if (fileInput) {
        fileInput.addEventListener('change', handleFileUpload);
    }
});

function showOfferModal(offerId = null) {
    const modal = new bootstrap.Modal(document.getElementById('offerModal'));
    const title = document.getElementById('offerModalTitle');
    const form = document.getElementById('offerForm');
    
    if (offerId) {
        title.textContent = 'Angebot bearbeiten';
        form.dataset.offerId = offerId;
        // Angebot-Daten laden und Formular füllen
        loadOfferData(offerId);
    } else {
        title.textContent = 'Neues Angebot';
        form.dataset.offerId = '';
        form.reset();
    }
    
    modal.show();
}

// Projekt-Daten laden für Bearbeitung
async function loadProjectData(projectId) {
    try {
        const response = await fetch(`${API_BASE}/projects/${projectId}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const project = await response.json();
            // Formular mit Projekt-Daten füllen
            document.getElementById('projectName').value = project.name || '';
            document.getElementById('projectDescription').value = project.description || '';
            document.getElementById('projectStatus').value = project.status || 'planned';
            document.getElementById('projectStartDate').value = project.start_date ? project.start_date.split('T')[0] : '';
            document.getElementById('projectEndDate').value = project.end_date ? project.end_date.split('T')[0] : '';
            document.getElementById('projectBudget').value = project.budget || '';
        }
    } catch (error) {
        console.error('Fehler beim Laden der Projekt-Daten:', error);
    }
}

// Bericht-Daten laden für Bearbeitung
async function loadReportData(reportId) {
    try {
        const response = await fetch(`${API_BASE}/reports/${reportId}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const report = await response.json();
            // Status-Feld setzen
            const statusSelect = document.getElementById('reportStatus');
            if (statusSelect && report.status) {
                statusSelect.value = report.status;
            }
            // Formular mit Bericht-Daten füllen
            const titleElement = document.getElementById('reportTitle');
            const contentElement = document.getElementById('reportContent');
            const dateElement = document.getElementById('reportDate');
            const projectElement = document.getElementById('reportProject');
            
            if (titleElement) titleElement.value = report.title || '';
            if (contentElement) contentElement.value = report.content || '';
            if (dateElement) dateElement.value = report.report_date ? report.report_date.split('T')[0] : '';
            if (projectElement) projectElement.value = report.project_id || '';
        }
    } catch (error) {
        console.error('Fehler beim Laden der Bericht-Daten:', error);
    }
}

// Angebot-Daten laden für Bearbeitung
async function loadOfferData(offerId) {
    try {
        const response = await fetch(`${API_BASE}/offers/${offerId}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const offer = await response.json();
            // Formular mit Angebot-Daten füllen
            document.getElementById('offerTitle').value = offer.title || '';
            document.getElementById('offerDescription').value = offer.description || '';
            document.getElementById('offerAmount').value = offer.amount || '';
            document.getElementById('offerStatus').value = offer.status || 'draft';
            document.getElementById('offerValidUntil').value = offer.valid_until ? offer.valid_until.split('T')[0] : '';
        }
    } catch (error) {
        console.error('Fehler beim Laden der Angebot-Daten:', error);
    }
}

// Mitarbeiter-Daten laden für Bearbeitung
async function loadEmployeeData(employeeId) {
    try {
        const response = await fetch(`${API_BASE}/employees/${employeeId}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            const employee = await response.json();
            // Formular mit Mitarbeiter-Daten füllen
            document.getElementById('employeeName').value = employee.full_name || '';
            document.getElementById('employeeEmail').value = employee.email || '';
            document.getElementById('employeePhone').value = employee.phone || '';
            document.getElementById('employeePosition').value = employee.position || '';
            document.getElementById('employeeHourlyRate').value = employee.hourly_rate || '';
        }
    } catch (error) {
        console.error('Fehler beim Laden der Mitarbeiter-Daten:', error);
    }
}

function showEmployeeModal(employeeId = null) {
    const modal = new bootstrap.Modal(document.getElementById('employeeModal'));
    const title = document.getElementById('employeeModalTitle');
    const form = document.getElementById('employeeForm');
    
    if (employeeId) {
        title.textContent = 'Mitarbeiter bearbeiten';
        form.dataset.employeeId = employeeId;
        // Mitarbeiter-Daten laden und Formular füllen
        loadEmployeeData(employeeId);
    } else {
        title.textContent = 'Neuer Mitarbeiter';
        form.dataset.employeeId = '';
        form.reset();
    }
    
    modal.show();
}

function showTimeEntryModal(timeEntryId = null) {
    const modal = new bootstrap.Modal(document.getElementById('timeEntryModal'));
    const title = document.getElementById('timeEntryModalTitle');
    const form = document.getElementById('timeEntryForm');

    populateTimeEntryProjectSelect();
    populateEmployeeDropdown();
    
    if (timeEntryId) {
        title.textContent = 'Stundeneintrag bearbeiten';
        loadTimeEntryData(timeEntryId);
    } else {
        title.textContent = 'Neue Stundenerfassung';
        form.reset();
        document.getElementById('timeEntryDate').value = new Date().toISOString().split('T')[0];
        form.dataset.timeEntryId = '';
    }
    
    modal.show();
}

async function loadTimeEntryData(timeEntryId) {
    if (!timeEntryId) return;

    try {
        const response = await fetch(`${API_BASE}/time-entries/${timeEntryId}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        const entry = await response.json();
        if (!response.ok || !entry || entry.detail) {
            console.error('Fehler beim Laden des Stundeneintrags:', response.status);
            showAlert('Stundeneintrag konnte nicht geladen werden.', 'danger');
            const cachedEntry = timeEntriesCache.find(e => e.id === Number(timeEntryId));
            if (cachedEntry) {
                fillTimeEntryForm(cachedEntry);
            }
            return;
        }
        fillTimeEntryForm(entry);
    } catch (error) {
        console.error('Fehler beim Laden des Stundeneintrags:', error);
        showAlert('Stundeneintrag konnte nicht geladen werden.', 'danger');
        const cachedEntry = timeEntriesCache.find(e => e.id === Number(timeEntryId));
        if (cachedEntry) {
            fillTimeEntryForm(cachedEntry);
        }
    }
}

function fillTimeEntryForm(entry) {
    const form = document.getElementById('timeEntryForm');
    if (!form) return;

    form.dataset.timeEntryId = entry.id;

    const dateField = document.getElementById('timeEntryDate');
    if (dateField) {
        const workDate = entry.work_date || entry.date;
        dateField.value = workDate ? workDate.split('T')[0] : '';
    }

    const projectSelect = document.getElementById('timeEntryProject');
    if (projectSelect) {
        const projectId = entry.project_id || entry.project?.id;
        if (projectId && !Array.from(projectSelect.options).some(opt => Number(opt.value) === Number(projectId))) {
            const option = document.createElement('option');
            option.value = projectId;
            option.textContent = entry.project_name || entry.project?.name || `Projekt ${projectId}`;
            projectSelect.appendChild(option);
        }
        projectSelect.value = projectId ? String(projectId) : '';
    }

    const employeeSelect = document.getElementById('timeEntryEmployee');
    if (employeeSelect) {
        const employeeId = entry.employee_id || entry.employee?.id;
        if (employeeId && !Array.from(employeeSelect.options).some(opt => Number(opt.value) === Number(employeeId))) {
            const option = document.createElement('option');
            option.value = employeeId;
            option.textContent = entry.employee_name || entry.employee?.full_name || `Mitarbeiter ${employeeId}`;
            employeeSelect.appendChild(option);
        }
        employeeSelect.value = employeeId ? String(employeeId) : '';
    }

    const descriptionField = document.getElementById('timeEntryDescription');
    if (descriptionField) {
        descriptionField.value = entry.description || '';
    }

    const startField = document.getElementById('timeEntryStartTime');
    if (startField) {
        startField.value = entry.clock_in || entry.clock_in_time || '';
    }

    const endField = document.getElementById('timeEntryEndTime');
    if (endField) {
        endField.value = entry.clock_out || entry.clock_out_time || '';
    }

    const breakField = document.getElementById('timeEntryBreakMinutes');
    if (breakField) {
        breakField.value = entry.total_break_minutes || 0;
    }

    const hoursField = document.getElementById('timeEntryHours');
    if (hoursField) {
        hoursField.value = entry.hours_worked || 0;
    }
}

function populateTimeEntryProjectSelect() {
    const select = document.getElementById('timeEntryProject');
    if (!select) return;

    select.innerHTML = '<option value="">Projekt auswählen...</option>';

    if (Array.isArray(projects) && projects.length > 0) {
        projects.forEach(project => {
            const option = document.createElement('option');
            option.value = project.id;
            option.textContent = `${project.name} (${project.client_name || 'Kein Kunde'})`;
            select.appendChild(option);
        });
    }
}

function populateEmployeeDropdown() {
    const select = document.getElementById('timeEntryEmployee');
    if (!select) return;

    select.innerHTML = '<option value="">Mitarbeiter auswählen...</option>';

    if (Array.isArray(employeesCache) && employeesCache.length > 0) {
        employeesCache.forEach(emp => {
            const option = document.createElement('option');
            option.value = emp.id;
            option.textContent = emp.full_name;
            select.appendChild(option);
        });
    }
}

// Speicher-Funktionen
async function saveProject() {
    const form = document.getElementById('projectForm');
    const formData = new FormData(form);
    
    const projectData = {
        name: document.getElementById('projectName').value,
        description: document.getElementById('projectDescription').value,
        client_name: document.getElementById('projectClient').value,
        project_type: document.getElementById('projectType').value,
        status: document.getElementById('projectStatus').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/projects`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(projectData)
        });
        
        if (response.ok) {
            showSuccess('Projekt erfolgreich gespeichert');
            bootstrap.Modal.getInstance(document.getElementById('projectModal')).hide();
            loadProjects();
            
            // Admin-Benachrichtigung senden (falls Mitarbeiter)
            if (currentUser && currentUser.role === 'mitarbeiter') {
                await sendAdminNotification('Projekt bearbeitet', `Mitarbeiter ${currentUser.full_name} hat ein Projekt bearbeitet.`);
            }
        } else {
            showError('Fehler beim Speichern des Projekts');
        }
    } catch (error) {
        console.error('Fehler beim Speichern des Projekts:', error);
        showError('Fehler beim Speichern des Projekts');
    }
}

async function saveReport() {
    const reportData = {
        project_id: parseInt(document.getElementById('reportProject').value),
        title: document.getElementById('reportTitle').value,
        content: document.getElementById('reportContent').value,
        work_type: document.getElementById('reportWorkType').value,
        area_completed: parseFloat(document.getElementById('reportAreaCompleted').value) || null,
        materials_used: document.getElementById('reportMaterialsUsed').value,
        quality_check: document.getElementById('reportQualityCheck').value,
        issues_encountered: document.getElementById('reportIssues').value,
        next_steps: document.getElementById('reportNextSteps').value,
        progress_percentage: parseFloat(document.getElementById('reportProgress').value) || null
    };
    
    // Nur Datum hinzufügen wenn es nicht leer ist
    const reportDate = document.getElementById('reportDate').value;
    if (reportDate && reportDate.trim() !== '') {
        reportData.report_date = reportDate;
    }
    
    try {
        const response = await fetch(`${API_BASE}/reports`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(reportData)
        });
        
        if (response.ok) {
            showSuccess('Bericht erfolgreich gespeichert');
            bootstrap.Modal.getInstance(document.getElementById('reportModal')).hide();
            loadReports();
        } else {
            showError('Fehler beim Speichern des Berichts');
        }
    } catch (error) {
        console.error('Fehler beim Speichern des Berichts:', error);
        showError('Fehler beim Speichern des Berichts');
    }
}

async function saveEmployee() {
    const employeeData = {
        full_name: document.getElementById('employeeName').value,
        position: document.getElementById('employeePosition').value,
        hourly_rate: parseFloat(document.getElementById('employeeHourlyRate').value) || null,
        phone: document.getElementById('employeePhone').value,
        email: document.getElementById('employeeEmail').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/employees`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(employeeData)
        });
        
        if (response.ok) {
            showSuccess('Mitarbeiter erfolgreich gespeichert');
            bootstrap.Modal.getInstance(document.getElementById('employeeModal')).hide();
            loadEmployees();
            loadProjects();
        } else {
            showError('Fehler beim Speichern des Mitarbeiters');
        }
    } catch (error) {
        console.error('Fehler beim Speichern des Mitarbeiters:', error);
        showError('Fehler beim Speichern des Mitarbeiters');
    }
}

async function saveTimeEntry() {
    const timeEntryData = {
        project_id: parseInt(document.getElementById('timeEntryProject').value),
        employee_id: parseInt(document.getElementById('timeEntryEmployee').value),
        date: document.getElementById('timeEntryDate').value,
        clock_in: document.getElementById('timeEntryStartTime').value,
        clock_out: document.getElementById('timeEntryEndTime').value,
        total_break_minutes: parseInt(document.getElementById('timeEntryBreakMinutes').value) || 0,
        hours_worked: parseFloat(document.getElementById('timeEntryHours').value),
        description: document.getElementById('timeEntryDescription').value,
        hourly_rate: parseFloat(document.getElementById('timeEntryHourlyRate').value) || null
    };
    
    // Überlappungsprüfung vor dem Speichern
    const overlapCheck = await checkTimeOverlap(timeEntryData);
    if (overlapCheck.hasOverlap) {
        showAlert(`⚠️ Überlappende Zeiten erkannt!<br><br>Konflikt mit:<br>• ${overlapCheck.conflictingEntry.description}<br>• ${overlapCheck.conflictingEntry.date} ${overlapCheck.conflictingEntry.clock_in} - ${overlapCheck.conflictingEntry.clock_out}<br><br>Bitte korrigieren Sie die Zeiten.`, 'warning');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/time-entries`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(timeEntryData)
        });
        
        if (response.ok) {
            showSuccess('Stundeneintrag erfolgreich gespeichert');
            bootstrap.Modal.getInstance(document.getElementById('timeEntryModal')).hide();
            loadTimeEntries();
            
            // Admin-Benachrichtigung senden (falls Mitarbeiter)
            if (currentUser && currentUser.role === 'mitarbeiter') {
                await sendAdminNotification('Stundeneintrag erstellt', `Mitarbeiter ${currentUser.full_name} hat einen neuen Stundeneintrag erstellt.`);
            }
        } else {
            showError('Fehler beim Speichern des Stundeneintrags');
        }
    } catch (error) {
        console.error('Fehler beim Speichern des Stundeneintrags:', error);
        showError('Fehler beim Speichern des Stundeneintrags');
    }
}

// Überlappungsprüfung für Stundeneinträge
async function checkTimeOverlap(timeEntryData) {
    try {
        // Alle Stundeneinträge für den Mitarbeiter und das Datum laden
        const response = await fetch(`${API_BASE}/time-entries?employee_id=${timeEntryData.employee_id}&date=${timeEntryData.date}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (!response.ok) {
            return { hasOverlap: false };
        }
        
        const existingEntries = await response.json();
        const newStart = new Date(`${timeEntryData.date}T${timeEntryData.clock_in}`);
        const newEnd = new Date(`${timeEntryData.date}T${timeEntryData.clock_out}`);
        
        for (const entry of existingEntries) {
            if (entry.id === parseInt(document.getElementById('timeEntryForm')?.dataset.timeEntryId)) {
                continue; // Aktueller Eintrag wird bearbeitet, nicht prüfen
            }
            
            const existingStart = new Date(`${entry.date}T${entry.clock_in}`);
            const existingEnd = new Date(`${entry.date}T${entry.clock_out}`);
            
            // Überlappungsprüfung
            if ((newStart < existingEnd && newEnd > existingStart)) {
                return {
                    hasOverlap: true,
                    conflictingEntry: entry
                };
            }
        }
        
        return { hasOverlap: false };
    } catch (error) {
        console.error('Fehler bei Überlappungsprüfung:', error);
        return { hasOverlap: false };
    }
}

// Admin-Benachrichtigung senden
async function sendAdminNotification(title, message) {
    try {
        // Benachrichtigung in localStorage speichern (für Demo)
        const notifications = JSON.parse(localStorage.getItem('adminNotifications') || '[]');
        notifications.push({
            id: Date.now(),
            title: title,
            message: message,
            timestamp: new Date().toISOString(),
            read: false
        });
        localStorage.setItem('adminNotifications', JSON.stringify(notifications));
        
        console.log('Admin-Benachrichtigung gespeichert:', title);
    } catch (error) {
        console.error('Fehler beim Senden der Admin-Benachrichtigung:', error);
    }
}

// Admin-Benachrichtigungen laden und anzeigen
function loadAdminNotifications() {
    const notifications = JSON.parse(localStorage.getItem('adminNotifications') || '[]');
    const unreadCount = notifications.filter(n => !n.read).length;
    
    // Benachrichtigungs-Badge aktualisieren
    const badge = document.getElementById('notificationBadge');
    if (badge) {
        badge.textContent = unreadCount;
        badge.style.display = unreadCount > 0 ? 'inline' : 'none';
    }
    
    return notifications;
}

// Benachrichtigungen anzeigen
function showNotifications() {
    const notifications = loadAdminNotifications();
    
    if (notifications.length === 0) {
        showAlert('Keine Benachrichtigungen vorhanden.', 'info');
        return;
    }
    
    // Benachrichtigungen als HTML generieren
    const notificationsHtml = notifications.map(notification => `
        <div class="notification-item p-3 mb-2 border rounded ${notification.read ? 'bg-light' : 'bg-warning bg-opacity-10'}">
            <div class="d-flex justify-content-between align-items-start">
                <div>
                    <h6 class="mb-1 ${notification.read ? 'text-muted' : 'text-dark'}">${notification.title}</h6>
                    <p class="mb-1 small">${notification.message}</p>
                    <small class="text-muted">${new Date(notification.timestamp).toLocaleString('de-DE')}</small>
                </div>
                <div>
                    ${!notification.read ? '<span class="badge bg-danger">Neu</span>' : ''}
                </div>
            </div>
        </div>
    `).join('');
    
    // Modal für Benachrichtigungen erstellen
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
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <span>${notifications.length} Benachrichtigungen</span>
                            <button class="btn btn-sm btn-outline-primary" onclick="markAllAsRead()">
                                <i class="fas fa-check-double me-1"></i>Alle als gelesen markieren
                            </button>
                        </div>
                        <div class="notifications-list">
                            ${notificationsHtml}
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Schließen</button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Modal zur Seite hinzufügen und anzeigen
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    const modal = new bootstrap.Modal(document.getElementById('notificationsModal'));
    modal.show();
    
    // Modal entfernen nach dem Schließen
    document.getElementById('notificationsModal').addEventListener('hidden.bs.modal', function() {
        this.remove();
    });
}

// Alle Benachrichtigungen als gelesen markieren
function markAllAsRead() {
    const notifications = JSON.parse(localStorage.getItem('adminNotifications') || '[]');
    notifications.forEach(notification => {
        notification.read = true;
    });
    localStorage.setItem('adminNotifications', JSON.stringify(notifications));
    
    // Badge aktualisieren
    loadAdminNotifications();
    
    // Modal schließen und neu öffnen
    bootstrap.Modal.getInstance(document.getElementById('notificationsModal')).hide();
    setTimeout(() => showNotifications(), 300);
}

// Rechnungs-Funktionen
function showInvoiceModal() {
    const modal = new bootstrap.Modal(document.getElementById('invoiceModal'));
    modal.show();
}

function showAutoInvoiceModal() {
    const modal = new bootstrap.Modal(document.getElementById('autoInvoiceModal'));
    modal.show();
}

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
        total_amount: parseFloat(formData.get('total_amount')) || 0,
        currency: formData.get('currency') || 'EUR',
        status: formData.get('status') || 'entwurf',
        items: [] // Leere Items-Liste für jetzt
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

// Zeiterfassung-Funktionen
async function loadTimeTrackingData() {
    if (!authToken) {
        showLoginPrompt();
        return;
    }

    try {
        await loadProjects();
        
        // Projekte in Clock-Dropdown laden
        const clockSelect = document.getElementById('clockProject');
        if (clockSelect && Array.isArray(projectsCache)) {
            clockSelect.innerHTML = '<option value="">Projekt auswählen...</option>' +
                projectsCache.map(p => `<option value="${p.id}">${p.name || 'Unbenannt'}</option>`).join('');
        }

        const response = await fetch(`${API_BASE}/time-entries`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.ok) {
            timeEntriesCache = await response.json();
            displayTimeEntries(timeEntriesCache);
        } else if (response.status === 401) {
            showLoginPrompt();
        } else {
            showAlert('Fehler beim Laden der Stundenerfassung', 'danger');
        }
    } catch (error) {
        console.error('Fehler beim Laden der Stundenerfassung:', error);
        showAlert('Fehler beim Laden der Stundenerfassung', 'danger');
    }
}

function clockIn() {
    const projectId = document.getElementById('clockProject').value;
    console.log('ClockIn aufgerufen - Projekt ID:', projectId);
    
    if (!projectId) {
        showError('Bitte wählen Sie ein Projekt aus');
        return;
    }
    
    isClockedIn = true;
    workStartTime = new Date();
    
    // UI aktualisieren
    document.getElementById('clockInBtn').style.display = 'none';
    document.getElementById('clockOutBtn').style.display = 'block';
    
    const pauseBtn = document.getElementById('pauseBtn');
    if (pauseBtn) {
        pauseBtn.disabled = false;
        pauseBtn.style.display = 'block';
    }
    
    const clockStatus = document.getElementById('clockStatus');
    if (clockStatus) {
        clockStatus.style.display = 'block';
    }
    
    const statusText = document.getElementById('statusText');
    if (statusText) {
        statusText.textContent = 'Eingestempelt';
    }
    
    // Projektname aus der Auswahl holen
    const projectSelect = document.getElementById('clockProject');
    const selectedOption = projectSelect.selectedOptions[0];
    const selectedProjectName = selectedOption ? selectedOption.text : 'Unbekanntes Projekt';
    
    console.log('Ausgewähltes Projekt:', selectedProjectName);
    console.log('Selected Option:', selectedOption);
    
    // Projekt in der Vorschau anzeigen
    const currentProjectElement = document.getElementById('currentProject');
    if (currentProjectElement) {
        currentProjectElement.textContent = selectedProjectName;
        console.log('Projekt in Vorschau gesetzt:', selectedProjectName);
    } else {
        console.error('currentProject Element nicht gefunden!');
    }
    
    // Einstempelzeit anzeigen
    const clockInTimeElement = document.getElementById('clockInTime');
    if (clockInTimeElement) {
        clockInTimeElement.textContent = formatTime(workStartTime);
        console.log('Einstempelzeit gesetzt:', formatTime(workStartTime));
    } else {
        console.error('clockInTime Element nicht gefunden!');
    }
    
    // Timer starten
    startWorkTimer();
    
    showSuccess('Erfolgreich eingestempelt');
}


// Projektvorschau sofort aktualisieren
function updateProjectPreview() {
    const projectSelect = document.getElementById('clockProject');
    const selectedOption = projectSelect.selectedOptions[0];
    const selectedProjectName = selectedOption ? selectedOption.text : '-';
    
    // Dropdown visuell aktualisieren
    if (selectedOption) {
        selectedOption.selected = true;
    }
    
    const currentProjectElement = document.getElementById('currentProject');
    if (currentProjectElement) {
        currentProjectElement.textContent = selectedProjectName;
    }
    
    // Dropdown-Text visuell aktualisieren - speziell für Dark Mode
    setTimeout(() => {
        const currentValue = projectSelect.value;
        const isDarkMode = document.body.classList.contains('dark-mode');
        
        if (isDarkMode) {
            // Dark Mode: Spezielle Behandlung
            projectSelect.style.background = '#FFFFFF';
            projectSelect.style.color = '#1F2937';
            projectSelect.style.borderColor = 'rgba(96, 165, 250, 0.3)';
        }
        
        projectSelect.style.display = 'none';
        projectSelect.offsetHeight; // Trigger reflow
        projectSelect.style.display = 'block';
        projectSelect.value = currentValue;
    }, 100);
}

function clockOut() {
    if (!isClockedIn) return;
    
    const endTime = new Date();
    const workDuration = (endTime - workStartTime) / (1000 * 60 * 60); // Stunden
    
    // Stundeneintrag erstellen
    createTimeEntryFromClock(workDuration);
    
    // UI zurücksetzen
    isClockedIn = false;
    workStartTime = null;
    
    document.getElementById('clockInBtn').style.display = 'block';
    document.getElementById('clockOutBtn').style.display = 'none';
    
    const pauseBtn = document.getElementById('pauseBtn');
    if (pauseBtn) {
        pauseBtn.disabled = true;
        pauseBtn.style.display = 'block';
    }
    
    const clockStatus = document.getElementById('clockStatus');
    if (clockStatus) clockStatus.style.display = 'none';
    
    const workTimeDisplay = document.getElementById('workTimeDisplay');
    if (workTimeDisplay) workTimeDisplay.textContent = '00:00:00';
    
    const currentProject = document.getElementById('currentProject');
    if (currentProject) currentProject.textContent = '-';
    
    const clockInTime = document.getElementById('clockInTime');
    if (clockInTime) clockInTime.textContent = '-';
    
    const breakTime = document.getElementById('breakTime');
    if (breakTime) breakTime.textContent = '0 Min';
    
    // Timer stoppen
    if (workTimer) {
        clearInterval(workTimer);
        workTimer = null;
    }
    
    showSuccess('Erfolgreich ausgestempelt');
}

function startBreak() {
    if (!isClockedIn) return;
    
    breakStartTime = new Date();
    document.getElementById('breakStartBtn').style.display = 'none';
    document.getElementById('breakEndBtn').style.display = 'inline-block';
    document.getElementById('statusText').textContent = 'Pause';
}

function endBreak() {
    if (!breakStartTime) return;
    
    const breakDuration = Math.round((new Date() - breakStartTime) / (1000 * 60)); // Minuten
    const currentBreakTime = parseInt(document.getElementById('breakTime').textContent) || 0;
    document.getElementById('breakTime').textContent = (currentBreakTime + breakDuration) + ' Min';
    
    breakStartTime = null;
    document.getElementById('breakStartBtn').style.display = 'inline-block';
    document.getElementById('breakEndBtn').style.display = 'none';
    document.getElementById('statusText').textContent = 'Eingestempelt';
}

function startWorkTimer() {
    workTimer = setInterval(() => {
        if (isClockedIn && workStartTime) {
            const now = new Date();
            const elapsed = now - workStartTime;
            const hours = Math.floor(elapsed / (1000 * 60 * 60));
            const minutes = Math.floor((elapsed % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((elapsed % (1000 * 60)) / 1000);
            
            document.getElementById('workTimeDisplay').textContent = 
                `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
    }, 1000);
}

async function createTimeEntryFromClock(hoursWorked) {
    const projectId = document.getElementById('clockProject').value;
    const breakMinutes = parseInt(document.getElementById('breakTime').textContent) || 0;
    
    const timeEntryData = {
        project_id: parseInt(projectId),
        employee_id: 1, // Ersten verfügbaren Mitarbeiter verwenden
        date: new Date().toISOString().split('T')[0],
        clock_in: workStartTime.toISOString(),
        clock_out: new Date().toISOString(),
        total_break_minutes: breakMinutes,
        hours_worked: hoursWorked,
        description: 'Arbeitstag ' + new Date().toLocaleDateString('de-DE')
    };
    
    try {
        const response = await fetch(`${API_BASE}/time-entries`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(timeEntryData)
        });
        
        if (response.ok) {
            loadTimeEntries();
        } else {
            showError('Fehler beim Speichern des Stundeneintrags');
        }
    } catch (error) {
        console.error('Fehler beim Speichern des Stundeneintrags:', error);
        showError('Fehler beim Speichern des Stundeneintrags');
    }
}

// Validierung
function validateTimeEntry() {
    const hours = parseFloat(document.getElementById('timeEntryHours').value) || 0;
    const description = document.getElementById('timeEntryDescription').value.trim();
    const project = document.getElementById('timeEntryProject').value;
    const employee = document.getElementById('timeEntryEmployee').value;
    
    let isValid = true;
    let errors = [];
    
    // Überstunden-Warnung
    if (hours > 8) {
        errors.push('Warnung: Mehr als 8 Stunden erfasst');
    }
    
    // Pflichtfelder prüfen
    if (!project) {
        errors.push('Projekt ist erforderlich');
        isValid = false;
    }
    
    if (!employee) {
        errors.push('Mitarbeiter ist erforderlich');
        isValid = false;
    }
    
    if (!description) {
        errors.push('Arbeitsbeschreibung ist erforderlich');
        isValid = false;
    }
    
    if (hours <= 0) {
        errors.push('Arbeitszeit muss größer als 0 sein');
        isValid = false;
    }
    
    // Validierungs-Alerts anzeigen
    const alertsContainer = document.getElementById('timeEntryValidationAlerts');
    if (alertsContainer) {
        alertsContainer.innerHTML = errors.map(error => 
            `<div class="alert alert-warning alert-dismissible fade show" role="alert">
                <i class="fas fa-exclamation-triangle me-2"></i>${error}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>`
        ).join('');
    }
    
    // Speichern-Button aktivieren/deaktivieren
    const saveBtn = document.getElementById('saveTimeEntryBtn');
    if (saveBtn) {
        saveBtn.disabled = !isValid;
    }
    
    return isValid;
}

// Arbeitszeit berechnen
function calculateWorkTime() {
    const startTime = document.getElementById('timeEntryStartTime').value;
    const endTime = document.getElementById('timeEntryEndTime').value;
    const breakMinutes = parseInt(document.getElementById('timeEntryBreakMinutes').value) || 0;
    
    if (startTime && endTime) {
        const start = new Date('2000-01-01T' + startTime);
        const end = new Date('2000-01-01T' + endTime);
        const diffMs = end - start;
        const diffHours = (diffMs / (1000 * 60 * 60)) - (breakMinutes / 60);
        
        if (diffHours > 0) {
            document.getElementById('timeEntryHours').value = diffHours.toFixed(2);
        }
    }
}

// Angebotspositionen verwalten
function addOfferItem() {
    const container = document.getElementById('offerItems');
    const newItem = document.createElement('div');
    newItem.className = 'offer-item border p-3 mb-3 rounded';
    newItem.innerHTML = `
        <div class="row">
            <div class="col-md-4">
                <label class="form-label">Beschreibung</label>
                <input type="text" class="form-control item-description" placeholder="z.B. Maurerarbeiten">
            </div>
            <div class="col-md-2">
                <label class="form-label">Menge</label>
                <input type="number" class="form-control item-quantity" step="0.01" min="0">
            </div>
            <div class="col-md-2">
                <label class="form-label">Einheit</label>
                <input type="text" class="form-control item-unit" placeholder="z.B. m²">
            </div>
            <div class="col-md-2">
                <label class="form-label">Einzelpreis</label>
                <input type="number" class="form-control item-unit-price" step="0.01" min="0">
            </div>
            <div class="col-md-2">
                <label class="form-label">Gesamtpreis</label>
                <input type="number" class="form-control item-total-price" step="0.01" readonly>
            </div>
        </div>
    `;
    container.appendChild(newItem);
}

function calculateOfferTotal() {
    const items = document.querySelectorAll('.offer-item');
    let total = 0;
    
    items.forEach(item => {
        const quantity = parseFloat(item.querySelector('.item-quantity').value) || 0;
        const unitPrice = parseFloat(item.querySelector('.item-unit-price').value) || 0;
        const totalPrice = quantity * unitPrice;
        
        item.querySelector('.item-total-price').value = totalPrice.toFixed(2);
        total += totalPrice;
    });
    
    document.getElementById('offerTotalAmount').value = total.toFixed(2);
}

// Hilfsfunktionen
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('de-DE');
}

function formatTime(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' });
}

function getStatusColor(status) {
    const statusColors = {
        'aktiv': 'success',
        'pausiert': 'warning',
        'abgeschlossen': 'secondary',
        'entwurf': 'secondary',
        'versendet': 'info',
        'angenommen': 'success',
        'abgelehnt': 'danger'
    };
    return statusColors[status] || 'secondary';
}

function showSuccess(message) {
    showAlert(message, 'success');
}

function showError(message) {
    showAlert(message, 'danger');
}

function showAlert(message, type) {
    const alertContainer = document.getElementById('alertContainer');
    if (alertContainer) {
        const alertId = 'alert-' + Date.now();
        alertContainer.innerHTML += `
            <div id="${alertId}" class="alert alert-${type} alert-dismissible fade show" role="alert">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        // Alert nach 5 Sekunden automatisch entfernen
        setTimeout(() => {
            const alert = document.getElementById(alertId);
            if (alert) {
                alert.remove();
            }
        }, 5000);
    }
}

// Placeholder-Funktionen für Edit/Delete
function editProject(id) {
    console.log('Projekt bearbeiten:', id);
    showProjectModal(id);
}

async function deleteProject(id) {
    // Erweiterte Bestätigung mit Projekt-Details
    const project = await getProjectDetails(id);
    if (!project) {
        showAlert('Projekt nicht gefunden', 'danger');
        return;
    }
    
    const confirmMessage = `
        Möchten Sie das Projekt wirklich löschen?
        
        Projekt: ${project.name}
        Kunde: ${project.client_name || 'Nicht angegeben'}
        Status: ${project.status}
        
        ⚠️ WARNUNG: Diese Aktion kann nicht rückgängig gemacht werden!
        ⚠️ ALLE verknüpften Daten werden automatisch mitgelöscht:
        • Berichte und deren Anhänge
        • Stundeneinträge
        • Angebote
        • Rechnungen
        • Projektbilder
    `;
    
    if (confirm(confirmMessage)) {
        try {
            // Zeige Lade-Indikator
            showDeleteLoading(id);
            
            const response = await fetch(`${API_BASE}/projects/${id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${authToken}`,
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Erfolgreiche Löschung mit Details
                const deletedData = data.deleted_data || {};
                const details = [];
                if (deletedData.berichte > 0) details.push(`${deletedData.berichte} Berichte`);
                if (deletedData.stundeneintraege > 0) details.push(`${deletedData.stundeneintraege} Stundeneinträge`);
                if (deletedData.angebote > 0) details.push(`${deletedData.angebote} Angebote`);
                if (deletedData.rechnungen > 0) details.push(`${deletedData.rechnungen} Rechnungen`);
                if (deletedData.projektbilder > 0) details.push(`${deletedData.projektbilder} Projektbilder`);
                
                const detailText = details.length > 0 ? ` (${details.join(', ')})` : '';
                showAlert(`Projekt "${data.deleted_project}" wurde erfolgreich gelöscht${detailText}`, 'success');
                loadProjects();
                updateProjectDropdowns([]); // Dropdowns leeren
            } else {
                // Fehlerbehandlung mit detaillierter Meldung
                if (response.status === 400) {
                    showAlert(`Löschung nicht möglich: ${data.detail}`, 'warning');
                } else if (response.status === 403) {
                    showAlert('Sie haben keine Berechtigung, Projekte zu löschen', 'danger');
                } else if (response.status === 404) {
                    showAlert('Projekt nicht gefunden', 'danger');
                } else {
                    showAlert(`Fehler beim Löschen: ${data.detail || 'Unbekannter Fehler'}`, 'danger');
                }
            }
        } catch (error) {
            console.error('Fehler beim Löschen des Projekts:', error);
            showAlert('Netzwerkfehler beim Löschen des Projekts', 'danger');
        } finally {
            hideDeleteLoading(id);
        }
    }
}

// Hilfsfunktion: Projekt-Details abrufen
async function getProjectDetails(id) {
    try {
        const response = await fetch(`${API_BASE}/projects/${id}`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (response.ok) {
            return await response.json();
        }
        return null;
    } catch (error) {
        console.error('Fehler beim Laden der Projekt-Details:', error);
        return null;
    }
}

// Projekt-Details anzeigen
async function showProjectDetails(id) {
    try {
        const project = await getProjectDetails(id);
        if (!project) {
            showAlert('Projekt nicht gefunden', 'danger');
            return;
        }
        
        // Stundeneinträge für das Projekt abrufen
        const timeEntriesResponse = await fetch(`${API_BASE}/time-entries`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        let projectTimeEntries = [];
        let totalHours = 0;
        let totalCost = 0;
        
        if (timeEntriesResponse.ok) {
            const allTimeEntries = await timeEntriesResponse.json();
            projectTimeEntries = allTimeEntries.filter(entry => entry.project_id === id);
            
            // Berechne Gesamtstunden und -kosten
            totalHours = projectTimeEntries.reduce((sum, entry) => sum + (entry.hours_worked || 0), 0);
            totalCost = projectTimeEntries.reduce((sum, entry) => sum + (entry.total_cost || 0), 0);
        }
        
        // Modal-Inhalt erstellen
        const modalContent = `
            <div class="modal fade" id="projectDetailsModal" tabindex="-1" aria-labelledby="projectDetailsModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="projectDetailsModalLabel">
                                <i class="fas fa-project-diagram me-2"></i>${project.name}
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6 class="text-primary mb-3"><i class="fas fa-info-circle me-2"></i>Projekt-Informationen</h6>
                                    <table class="table table-sm">
                                        <tr>
                                            <td><strong>Name:</strong></td>
                                            <td>${project.name}</td>
                                        </tr>
                                        <tr>
                                            <td><strong>Status:</strong></td>
                                            <td><span class="badge bg-${getStatusColor(project.status)}">${project.status}</span></td>
                                        </tr>
                                        <tr>
                                            <td><strong>Typ:</strong></td>
                                            <td>${project.project_type || '-'}</td>
                                        </tr>
                                        <tr>
                                            <td><strong>Beschreibung:</strong></td>
                                            <td>${project.description || '-'}</td>
                                        </tr>
                                        <tr>
                                            <td><strong>Startdatum:</strong></td>
                                            <td>${formatDate(project.start_date)}</td>
                                        </tr>
                                        <tr>
                                            <td><strong>Enddatum:</strong></td>
                                            <td>${formatDate(project.end_date)}</td>
                                        </tr>
                                    </table>
                                </div>
                                <div class="col-md-6">
                                    <h6 class="text-primary mb-3"><i class="fas fa-user me-2"></i>Kunden-Informationen</h6>
                                    <table class="table table-sm">
                                        <tr>
                                            <td><strong>Kunde:</strong></td>
                                            <td>${project.client_name || '-'}</td>
                                        </tr>
                                        <tr>
                                            <td><strong>Telefon:</strong></td>
                                            <td>${project.client_phone || '-'}</td>
                                        </tr>
                                        <tr>
                                            <td><strong>E-Mail:</strong></td>
                                            <td>${project.client_email || '-'}</td>
                                        </tr>
                                        <tr>
                                            <td><strong>Adresse:</strong></td>
                                            <td>${project.address || '-'}</td>
                                        </tr>
                                    </table>
                                </div>
                            </div>
                            
                            <div class="row mt-4">
                                <div class="col-md-6">
                                    <h6 class="text-primary mb-3"><i class="fas fa-chart-line me-2"></i>Projekt-Daten</h6>
                                    <table class="table table-sm">
                                        <tr>
                                            <td><strong>Gesamtfläche:</strong></td>
                                            <td>${project.total_area ? project.total_area + ' m²' : '-'}</td>
                                        </tr>
                                        <tr>
                                            <td><strong>Geschätzte Stunden:</strong></td>
                                            <td>${project.estimated_hours || '-'}</td>
                                        </tr>
                                        <tr>
                                            <td><strong>Stundensatz:</strong></td>
                                            <td>${project.hourly_rate ? project.hourly_rate + ' €/h' : '-'}</td>
                                        </tr>
                                    </table>
                                </div>
                                <div class="col-md-6">
                                    <h6 class="text-primary mb-3"><i class="fas fa-clock me-2"></i>Zeitstempel</h6>
                                    <table class="table table-sm">
                                        <tr>
                                            <td><strong>Erstellt:</strong></td>
                                            <td>${formatDate(project.created_at)}</td>
                                        </tr>
                                        <tr>
                                            <td><strong>Zuletzt aktualisiert:</strong></td>
                                            <td>${formatDate(project.updated_at)}</td>
                                        </tr>
                                    </table>
                                </div>
                            </div>
                            
                            <div class="row mt-4">
                                <div class="col-12">
                                    <h6 class="text-primary mb-3"><i class="fas fa-clock me-2"></i>Arbeitsstunden</h6>
                                    <div class="row mb-3">
                                        <div class="col-md-4">
                                            <div class="card bg-light">
                                                <div class="card-body text-center">
                                                    <h5 class="card-title text-primary">${totalHours.toFixed(2)}</h5>
                                                    <p class="card-text">Gesamtstunden</p>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="col-md-4">
                                            <div class="card bg-light">
                                                <div class="card-body text-center">
                                                    <h5 class="card-title text-success">${totalCost.toFixed(2)} €</h5>
                                                    <p class="card-text">Gesamtkosten</p>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="col-md-4">
                                            <div class="card bg-light">
                                                <div class="card-body text-center">
                                                    <h5 class="card-title text-info">${projectTimeEntries.length}</h5>
                                                    <p class="card-text">Einträge</p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    ${projectTimeEntries.length > 0 ? `
                                        <div class="table-responsive">
                                            <table class="table table-sm table-striped">
                                                <thead>
                                                    <tr>
                                                        <th>Datum</th>
                                                        <th>Mitarbeiter</th>
                                                        <th>Stunden</th>
                                                        <th>Kosten</th>
                                                        <th>Beschreibung</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    ${projectTimeEntries.slice(0, 10).map(entry => `
                                                        <tr>
                                                            <td>${formatDate(entry.work_date)}</td>
                                                            <td>${entry.employee_name || 'Unbekannt'}</td>
                                                            <td>${entry.hours_worked || 0}h</td>
                                                            <td>${entry.total_cost ? entry.total_cost.toFixed(2) + ' €' : '-'}</td>
                                                            <td>${entry.description || '-'}</td>
                                                        </tr>
                                                    `).join('')}
                                                </tbody>
                                            </table>
                                        </div>
                                        ${projectTimeEntries.length > 10 ? `<p class="text-muted small">... und ${projectTimeEntries.length - 10} weitere Einträge</p>` : ''}
                                    ` : `
                                        <div class="alert alert-info">
                                            <i class="fas fa-info-circle me-2"></i>Noch keine Arbeitsstunden für dieses Projekt erfasst.
                                        </div>
                                    `}
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                                <i class="fas fa-times me-2"></i>Schließen
                            </button>
                            <button type="button" class="btn btn-primary" onclick="editProject(${project.id}); bootstrap.Modal.getInstance(document.getElementById('projectDetailsModal')).hide();">
                                <i class="fas fa-edit me-2"></i>Bearbeiten
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Modal entfernen falls vorhanden
        const existingModal = document.getElementById('projectDetailsModal');
        if (existingModal) {
            existingModal.remove();
        }
        
        // Modal hinzufügen
        document.body.insertAdjacentHTML('beforeend', modalContent);
        
        // Modal anzeigen
        const modal = new bootstrap.Modal(document.getElementById('projectDetailsModal'));
        modal.show();
        
    } catch (error) {
        console.error('Fehler beim Laden der Projekt-Details:', error);
        showAlert('Fehler beim Laden der Projekt-Details', 'danger');
    }
}

// Lade-Indikator für Löschung anzeigen
function showDeleteLoading(id) {
    const button = document.querySelector(`button[onclick="deleteProject(${id})"]`);
    if (button) {
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Lösche...';
        button.classList.add('btn-warning');
        button.classList.remove('btn-outline-danger');
    }
}

// Lade-Indikator für Löschung verstecken
function hideDeleteLoading(id) {
    const button = document.querySelector(`button[onclick="deleteProject(${id})"]`);
    if (button) {
        button.disabled = false;
        button.innerHTML = '<i class="fas fa-trash"></i>';
        button.classList.remove('btn-warning');
        button.classList.add('btn-outline-danger');
    }
}

function editReport(id) {
    console.log('Bericht bearbeiten:', id);
    showReportModal(id);
}

async function deleteReport(id) {
    if (confirm('Möchten Sie diesen Bericht wirklich löschen?')) {
        try {
            const response = await fetch(`${API_BASE}/reports/${id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            });
            
            if (response.ok) {
                loadReports();
                showAlert('Bericht erfolgreich gelöscht!', 'success');
            } else {
                showAlert('Fehler beim Löschen des Berichts', 'danger');
            }
        } catch (error) {
            console.error('Fehler beim Löschen des Berichts:', error);
            showAlert('Fehler beim Löschen des Berichts', 'danger');
        }
    }
}

function editOffer(id) {
    console.log('Angebot bearbeiten:', id);
    showOfferModal(id);
}

async function deleteOffer(id) {
    if (confirm('Möchten Sie dieses Angebot wirklich löschen?')) {
        try {
            const response = await fetch(`${API_BASE}/offers/${id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            });
            
            if (response.ok) {
                loadOffers();
                showAlert('Angebot erfolgreich gelöscht!', 'success');
            } else {
                showAlert('Fehler beim Löschen des Angebots', 'danger');
            }
        } catch (error) {
            console.error('Fehler beim Löschen des Angebots:', error);
            showAlert('Fehler beim Löschen des Angebots', 'danger');
        }
    }
}

function editEmployee(id) {
    console.log('Mitarbeiter bearbeiten:', id);
    showEmployeeModal(id);
}

async function deleteEmployee(id) {
    if (confirm('Möchten Sie diesen Mitarbeiter wirklich löschen?')) {
        try {
            const response = await fetch(`${API_BASE}/employees/${id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${authToken}`
                }
            });
            
            if (response.ok) {
                loadEmployees();
                showAlert('Mitarbeiter erfolgreich gelöscht!', 'success');
            } else {
                showAlert('Fehler beim Löschen des Mitarbeiters', 'danger');
            }
        } catch (error) {
            console.error('Fehler beim Löschen des Mitarbeiters:', error);
            showAlert('Fehler beim Löschen des Mitarbeiters', 'danger');
        }
    }
}

function editTimeEntry(id) {
    console.log('Stundeneintrag bearbeiten:', id);
    showTimeEntryModal(id);
}

function deleteTimeEntry(id) {
    if (confirm('Möchten Sie diesen Stundeneintrag wirklich löschen?')) {
        console.log('Stundeneintrag löschen:', id);
        fetch(`${API_BASE}/time-entries/${id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        }).then(response => {
            if (response.ok) {
                // Lokal entfernen, damit die UI sofort reagiert
                timeEntriesCache = timeEntriesCache.filter(entry => entry.id !== Number(id));
                displayTimeEntries(timeEntriesCache);
                showAlert('Stundeneintrag wurde gelöscht.', 'success');
            } else if (response.status === 404) {
                showAlert('Stundeneintrag nicht gefunden.', 'warning');
                timeEntriesCache = timeEntriesCache.filter(entry => entry.id !== Number(id));
                displayTimeEntries(timeEntriesCache);
            } else {
                showAlert('Fehler beim Löschen des Stundeneintrags.', 'danger');
            }
        }).catch(error => {
            console.error('Fehler beim Löschen des Stundeneintrags:', error);
            showAlert('Fehler beim Löschen des Stundeneintrags.', 'danger');
        });
    }
}

function editInvoice(id) {
    const invoice = Array.isArray(invoicesCache) ? invoicesCache.find(inv => inv.id === Number(id)) : null;
    if (!invoice) {
        console.warn('Rechnung nicht gefunden:', id);
        if (typeof showAlert === 'function') {
            showAlert('Rechnung nicht gefunden.', 'warning');
        }
        return;
    }

    console.log('Bearbeite Rechnung:', invoice);
    console.log('Total Amount:', invoice.total_amount, 'Type:', typeof invoice.total_amount);

    const form = document.getElementById('invoiceForm');
    if (!form) {
        console.error('invoiceForm nicht gefunden');
        return;
    }

    form.dataset.invoiceId = invoice.id;
    document.getElementById('invoiceModalTitle').textContent = 'Rechnung bearbeiten';

    populateInvoiceProjectSelect();

    const projectSelect = document.getElementById('invoiceProject');
    if (projectSelect) {
        projectSelect.value = invoice.project_id || '';
    }

    document.getElementById('invoiceNumber').value = invoice.invoice_number || '';
    document.getElementById('invoiceTitle').value = invoice.title || '';
    document.getElementById('invoiceDescription').value = invoice.description || '';
    document.getElementById('invoiceClientName').value = invoice.client_name || '';
    document.getElementById('invoiceClientAddress').value = invoice.client_address || '';
    
    // Betrag explizit als Number setzen
    const totalAmountField = document.getElementById('invoiceTotalAmount');
    const totalAmount = Number(invoice.total_amount) || 0;
    totalAmountField.value = totalAmount.toFixed(2);
    console.log('Setze Total Amount Feld auf:', totalAmountField.value);
    
    document.getElementById('invoiceCurrency').value = invoice.currency || 'EUR';
    document.getElementById('invoiceStatus').value = invoice.status || 'entwurf';

    const modal = new bootstrap.Modal(document.getElementById('invoiceModal'));
    modal.show();
}

function deleteInvoice(id) {
    if (confirm('Möchten Sie diese Rechnung wirklich löschen?')) {
        console.log('Rechnung löschen:', id);
        (async () => {
            if (!authToken) {
                showLoginPrompt();
                return;
            }

            try {
                const response = await fetch(`${API_BASE}/invoices/${id}`, {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Bearer ${authToken}`
                    }
                });

                if (response.ok) {
                    showAlert('Rechnung wurde gelöscht.', 'success');

                    if (typeof loadInvoices === 'function') {
                        await loadInvoices();
                    }

                    const modalElement = document.getElementById('invoiceModal');
                    if (modalElement && window.bootstrap && window.bootstrap.Modal) {
                        const modalInstance = window.bootstrap.Modal.getInstance(modalElement);
                        if (modalInstance) {
                            modalInstance.hide();
                        }
                    }
                } else if (response.status === 401) {
                    showLoginPrompt();
                } else if (response.status === 404) {
                    showAlert('Rechnung wurde nicht gefunden.', 'warning');
                } else {
                    const error = await response.json().catch(() => ({}));
                    showAlert(error.detail || 'Rechnung konnte nicht gelöscht werden.', 'danger');
                }
            } catch (error) {
                console.error('Fehler beim Löschen der Rechnung:', error);
                showAlert('Rechnung konnte nicht gelöscht werden.', 'danger');
            }
        })();
    }
}

// Auto-Invoice Funktionen
function showAutoInvoiceModal() {
    const modal = new bootstrap.Modal(document.getElementById('autoInvoiceModal'));
    modal.show();
}

function createAutoInvoice() {
    const projectId = document.getElementById('autoInvoiceProject').value;
    if (!projectId) {
        showError('Bitte wählen Sie ein Projekt aus');
        return;
    }
    
    console.log('Auto-Rechnung erstellen für Projekt:', projectId);
    // Auto-Invoice API-Aufruf hier implementieren
}

// Mobile Menu Funktionen
function toggleMobileMenu() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        sidebar.classList.toggle('show');
    }
}

// Mobile Menu schließen beim Klick außerhalb
document.addEventListener('click', function(e) {
    const sidebar = document.querySelector('.sidebar');
    const menuButton = document.querySelector('[onclick="toggleMobileMenu()"]');
    
    if (window.innerWidth < 768 && sidebar && sidebar.classList.contains('show')) {
        if (!sidebar.contains(e.target) && !menuButton.contains(e.target)) {
            sidebar.classList.remove('show');
        }
    }
});

// Responsive Design Verbesserungen
function handleResize() {
    const sidebar = document.querySelector('.sidebar');
    
    if (window.innerWidth < 768) {
        // Mobile-Ansicht
        if (sidebar) {
            sidebar.classList.add('mobile-sidebar');
            sidebar.classList.remove('show');
        }
    } else {
        // Desktop-Ansicht
        if (sidebar) {
            sidebar.classList.remove('mobile-sidebar', 'show');
        }
    }
}

// Resize-Event-Listener
window.addEventListener('resize', handleResize);

// Initiale Größe prüfen
handleResize();

// Touch-Gesten für Mobile
let touchStartX = 0;
let touchStartY = 0;

document.addEventListener('touchstart', function(e) {
    touchStartX = e.touches[0].clientX;
    touchStartY = e.touches[0].clientY;
});

document.addEventListener('touchmove', function(e) {
    if (window.innerWidth < 768) {
        const touchEndX = e.touches[0].clientX;
        const touchEndY = e.touches[0].clientY;
        const diffX = touchStartX - touchEndX;
        const diffY = Math.abs(touchStartY - touchEndY);
        
        // Swipe von links nach rechts zum Öffnen des Menüs
        if (diffX > 50 && diffY < 100 && touchStartX < 50) {
            const sidebar = document.querySelector('.sidebar');
            if (sidebar && !sidebar.classList.contains('show')) {
                sidebar.classList.add('show');
            }
        }
        
        // Swipe von rechts nach links zum Schließen des Menüs
        if (diffX < -50 && diffY < 100) {
            const sidebar = document.querySelector('.sidebar');
            if (sidebar && sidebar.classList.contains('show')) {
                sidebar.classList.remove('show');
            }
        }
    }
});

// Dark Mode Funktionen
const DARK_MODE_FLAG_KEY = 'darkMode';
const LEGACY_THEME_KEY = 'theme';
const DARK_MODE_CLASS_NAME = 'dark-mode';
const DARK_THEME_VALUE = 'dark';
const LIGHT_THEME_VALUE = 'light';
const BOOTSTRAP_THEME_ATTRIBUTE = 'data-bs-theme';
let systemThemeListenerRegistered = false;
let serverThemePreference = null;

/**
 * Liefert das gespeicherte Theme oder {@code null}, wenn keine Einstellung existiert.
 */
function getStoredThemePreference() {
    try {
        const storedFlag = localStorage.getItem(DARK_MODE_FLAG_KEY);
        if (storedFlag === 'true') {
            return DARK_THEME_VALUE;
        }
        if (storedFlag === 'false') {
            return LIGHT_THEME_VALUE;
        }

        const legacyTheme = localStorage.getItem(LEGACY_THEME_KEY);
        if (legacyTheme === DARK_THEME_VALUE || legacyTheme === LIGHT_THEME_VALUE) {
            return legacyTheme;
        }
    } catch (error) {
        console.warn('Konnte gespeicherte Theme-Einstellung nicht lesen:', error);
    }

    return null;
}

/**
 * Persistiert eine Theme-Wahl kompatibel zu alten und neuen lokalen Storage-Keys.
 */
function persistThemePreference(theme) {
    const isDarkTheme = theme === DARK_THEME_VALUE;

    try {
        localStorage.setItem(DARK_MODE_FLAG_KEY, isDarkTheme ? 'true' : 'false');
        localStorage.setItem(LEGACY_THEME_KEY, theme);
    } catch (error) {
        console.warn('Konnte Theme-Einstellung nicht speichern:', error);
    }
}

/**
 * Überträgt die Theme-Präferenz an das Backend, sofern ein Token vorhanden ist.
 */
async function persistThemePreferenceToServer(theme) {
    if (!authToken) {
        return false;
    }

    if (theme !== DARK_THEME_VALUE && theme !== LIGHT_THEME_VALUE) {
        return false;
    }

    try {
        const response = await fetch(USER_SETTINGS_ENDPOINT, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ theme_preference: theme })
        });

        if (!response.ok) {
            console.warn('Server konnte Theme-Präferenz nicht speichern:', response.status);
            return false;
        }

        serverThemePreference = theme;
        return true;
    } catch (error) {
        console.warn('Konnte Theme-Präferenz nicht zum Server synchronisieren:', error);
        return false;
    }
}

/**
 * Holt die gespeicherte Theme-Präferenz vom Backend.
 */
async function fetchThemePreferenceFromServer() {
    if (!authToken) {
        return null;
    }

    try {
        const response = await fetch(USER_SETTINGS_ENDPOINT, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.status === 401) {
            console.warn('Nicht autorisiert beim Laden der Theme-Präferenz.');
            authToken = null;
            localStorage.removeItem('access_token');
            localStorage.removeItem('user_role');
            showLoginPrompt();
            return null;
        }

        if (!response.ok) {
            console.warn('Konnte Theme-Präferenz nicht laden:', response.status);
            return null;
        }

        const payload = await response.json();
        const serverTheme = payload?.theme_preference || null;
        if (serverTheme === DARK_THEME_VALUE || serverTheme === LIGHT_THEME_VALUE) {
            serverThemePreference = serverTheme;
            return serverTheme;
        }

        return null;
    } catch (error) {
        console.warn('Fehler beim Laden der Theme-Präferenz vom Server:', error);
        return null;
    }
}

/**
 * Wendet das gewünschte Theme auf DOM, UI-Controls und gespeicherte Werte an.
 */
function applyTheme(theme, { persistPreference = true, syncServer = false } = {}) {
    isDarkMode = theme === DARK_THEME_VALUE;

    if (document.body) {
        document.body.classList.toggle(DARK_MODE_CLASS_NAME, isDarkMode);
    }

    if (document.documentElement) {
        document.documentElement.setAttribute(BOOTSTRAP_THEME_ATTRIBUTE, isDarkMode ? 'dark' : 'light');
    }

    if (persistPreference) {
        persistThemePreference(theme);
    }

    if (syncServer) {
        persistThemePreferenceToServer(theme);
    }

    updateDarkModeToggle();
    updateProjectNamesColor();
}

/**
 * Reagiert auf System-Theme-Änderungen solange der Nutzer keine eigene Wahl getroffen hat.
 */
function handleSystemThemeChange(mediaQueryList) {
    const storedTheme = getStoredThemePreference();
    if (storedTheme) {
        return; // Benutzerpräferenz überschreibt System-Einstellung.
    }

    const nextTheme = mediaQueryList.matches ? DARK_THEME_VALUE : LIGHT_THEME_VALUE;
    applyTheme(nextTheme, { persistPreference: false });
}

/**
 * Aktiviert Listener für System-Theme-Änderungen (Prefers-Color-Scheme).
 */
function registerSystemThemeListener() {
    if (systemThemeListenerRegistered || !window.matchMedia) {
        return;
    }

    const mediaQueryList = window.matchMedia('(prefers-color-scheme: dark)');

    if (typeof mediaQueryList.addEventListener === 'function') {
        mediaQueryList.addEventListener('change', handleSystemThemeChange);
    } else if (typeof mediaQueryList.addListener === 'function') {
        mediaQueryList.addListener(handleSystemThemeChange);
    }

    systemThemeListenerRegistered = true;
}

/**
 * Initialisiert den Dark-/Light-Mode anhand gespeicherter Werte oder Systempräferenz.
 */
function initializeTheme() {
    const storedTheme = getStoredThemePreference();
    if (storedTheme) {
        applyTheme(storedTheme, { persistPreference: true });
    } else {
        const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        applyTheme(prefersDark ? DARK_THEME_VALUE : LIGHT_THEME_VALUE, { persistPreference: false });
    }

    registerSystemThemeListener();
}

/**
 * Synchronisiert die Theme-Präferenz mit dem Backend und berücksichtigt lokale Fallbacks.
 */
async function hydrateThemeFromServer() {
    if (!authToken) {
        return;
    }

    const localTheme = getStoredThemePreference();
    const serverTheme = await fetchThemePreferenceFromServer();

    if (serverTheme && serverTheme !== (isDarkMode ? DARK_THEME_VALUE : LIGHT_THEME_VALUE)) {
        applyTheme(serverTheme, { persistPreference: true, syncServer: false });
        return;
    }

    if (!serverTheme && localTheme) {
        await persistThemePreferenceToServer(localTheme);
    }
}

function toggleDarkMode() {
    const nextTheme = isDarkMode ? LIGHT_THEME_VALUE : DARK_THEME_VALUE;
    applyTheme(nextTheme, { persistPreference: true, syncServer: true });

    // Force reload dashboard data to update project names
    loadDashboardData();
}

function toggleTheme() {
    /**
     * Legacy wrapper to keep the existing HTML `onclick="toggleTheme()"` attribute functional.
     */
    toggleDarkMode();
}

function updateProjectNamesColor() {
    const projectNames = document.querySelectorAll('.project-name');
    projectNames.forEach(name => {
        if (isDarkMode) {
            name.style.setProperty('color', '#FFFFFF', 'important');
            name.style.setProperty('font-weight', '700', 'important');
        } else {
            name.style.setProperty('color', '#374151', 'important');
            name.style.setProperty('font-weight', '500', 'important');
        }
    });
}

// Force project names to have correct color - runs every 2 seconds
setInterval(() => {
    const projectNames = document.querySelectorAll('.project-name');
    projectNames.forEach(name => {
        if (isDarkMode) {
            if (name.style.color !== 'rgb(255, 255, 255)') {
                name.style.setProperty('color', '#FFFFFF', 'important');
                name.style.setProperty('font-weight', '700', 'important');
            }
        } else if (name.style.color !== 'rgb(55, 65, 81)') {
            name.style.setProperty('color', '#374151', 'important');
            name.style.setProperty('font-weight', '500', 'important');
        }
    });
}, 2000);

// Formular Event Listener einrichten
function setupFormEventListeners() {
    // Projekt-Formular
    const projectForm = document.getElementById('projectForm');
    if (projectForm) {
        projectForm.addEventListener('submit', handleProjectSubmit);
    }
    
    // Bericht-Formular
    const reportForm = document.getElementById('reportForm');
    if (reportForm) {
        console.log('Registriere Event-Listener für reportForm');
        reportForm.addEventListener('submit', handleReportSubmit);
    } else {
        console.log('FEHLER: reportForm nicht gefunden!');
    }
    
    // Angebot-Formular
    const offerForm = document.getElementById('offerForm');
    if (offerForm) {
        console.log('Registriere Event-Listener für offerForm');
        offerForm.addEventListener('submit', handleOfferSubmit);
    } else {
        console.log('FEHLER: offerForm nicht gefunden!');
    }
    
    // Mitarbeiter-Formular
    const employeeForm = document.getElementById('employeeForm');
    if (employeeForm) {
        console.log('Registriere Event-Listener für employeeForm');
        employeeForm.addEventListener('submit', handleEmployeeSubmit);
    } else {
        console.log('FEHLER: employeeForm nicht gefunden!');
    }
    
    // Stundeneintrag-Formular
    const timeEntryForm = document.getElementById('timeEntryForm');
    if (timeEntryForm) {
        console.log('Registriere Event-Listener für timeEntryForm');
        timeEntryForm.addEventListener('submit', handleTimeEntrySubmit);
    } else {
        console.log('FEHLER: timeEntryForm nicht gefunden!');
    }
    
    // Rechnungs-Formular
    const invoiceForm = document.getElementById('invoiceForm');
    if (invoiceForm) {
        console.log('Registriere Event-Listener für invoiceForm');
        invoiceForm.addEventListener('submit', handleInvoiceSubmit);
    } else {
        console.log('FEHLER: invoiceForm nicht gefunden!');
    }

    const userForm = document.getElementById('userForm');
    if (userForm) {
        console.log('Registriere Event-Listener für userForm');
        userForm.addEventListener('submit', event => {
            event.preventDefault();
            saveUser();
        });
    } else {
        console.log('FEHLER: userForm nicht gefunden!');
    }
}

// Projekt-Formular Handler
async function handleProjectSubmit(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const projectData = {
        name: formData.get('projectName'),
        description: formData.get('projectDescription'),
        client_name: formData.get('projectClient'),
        project_type: formData.get('projectType'),
        status: formData.get('projectStatus'),
        start_date: formData.get('projectStartDate'),
        end_date: formData.get('projectEndDate'),
        budget: parseFloat(formData.get('projectBudget')) || 0
    };
    
    try {
        const projectId = event.target.dataset.projectId;
        const url = projectId ? `${API_BASE}/projects/${projectId}` : `${API_BASE}/projects`;
        const method = projectId ? 'PUT' : 'POST';
        
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
            loadProjects();
            showAlert('Projekt erfolgreich gespeichert!', 'success');
        } else {
            showAlert('Fehler beim Speichern des Projekts', 'danger');
        }
    } catch (error) {
        console.error('Fehler beim Speichern des Projekts:', error);
        showAlert('Fehler beim Speichern des Projekts', 'danger');
    }
}

// Bericht-Formular Handler
async function handleReportSubmit(event) {
    console.log('handleReportSubmit aufgerufen!');
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const reportData = {
        project_id: parseInt(formData.get('project_id')) || 1, // Fallback zu Projekt 1
        title: formData.get('title'),
        content: formData.get('content'),
        work_type: formData.get('work_type'),
        status: formData.get('status')
    };
    
    // Nur Datum hinzufügen wenn es nicht leer ist
    const reportDate = formData.get('report_date');
    if (reportDate && reportDate.trim() !== '') {
        reportData.report_date = reportDate;
    }
    
    // Dateien verarbeiten
    const files = formData.getAll('files');
    if (files.length > 0) {
        reportData.attachments = files.map(file => ({
            filename: file.name,
            size: file.size,
            type: file.type
        }));
    }
    
    try {
        const reportId = event.target.dataset.reportId;
        const url = reportId ? `${API_BASE}/reports/${reportId}` : `${API_BASE}/reports`;
        const method = reportId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(reportData)
        });
        
        if (response.ok) {
            // Dateien hochladen, wenn vorhanden
            if (files.length > 0) {
                await uploadReportFiles(reportId || (await response.json()).id, files);
            }
            
            const modal = bootstrap.Modal.getInstance(document.getElementById('reportModal'));
            if (modal) {
                modal.hide();
            }
            loadReports();
            showAlert('Bericht erfolgreich gespeichert!', 'success');
        } else {
            showAlert('Fehler beim Speichern des Berichts', 'danger');
        }
    } catch (error) {
        console.error('Fehler beim Speichern des Berichts:', error);
        showAlert('Fehler beim Speichern des Berichts', 'danger');
    }
}

// Dateien für Berichte hochladen
async function uploadReportFiles(reportId, files) {
    try {
        for (const file of files) {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('report_id', reportId);
            
            const response = await fetch(`${API_BASE}/reports/${reportId}/upload`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${authToken}`
                },
                body: formData
            });
            
            if (!response.ok) {
                console.error('Fehler beim Hochladen der Datei:', file.name);
            }
        }
    } catch (error) {
        console.error('Fehler beim Hochladen der Dateien:', error);
    }
}

// Angebot-Berechnung
function calculateOfferTotal() {
    const netAmount = parseFloat(document.getElementById('offerNetAmount').value) || 0;
    const taxRate = parseFloat(document.getElementById('offerTaxRate').value) || 0;
    const taxAmount = (netAmount * taxRate) / 100;
    const totalAmount = netAmount + taxAmount;
    
    document.getElementById('offerTotalAmount').value = totalAmount.toFixed(2);
}

// Angebot-Formular Handler
async function handleOfferSubmit(event) {
    console.log('handleOfferSubmit aufgerufen!');
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const offerData = {
        project_id: parseInt(formData.get('project_id')) || 1, // Fallback zu Projekt 1
        title: formData.get('title'),
        description: formData.get('description'),
        client_name: formData.get('client_name'),
        client_address: formData.get('client_address'),
        total_amount: parseFloat(formData.get('total_amount')) || 0,
        valid_until: formData.get('valid_until'),
        items: [] // Leere Items-Liste für jetzt
    };
    
    try {
        const offerId = event.target.dataset.offerId;
        const url = offerId ? `${API_BASE}/offers/${offerId}` : `${API_BASE}/offers`;
        const method = offerId ? 'PUT' : 'POST';
        
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
        hourly_rate: parseFloat(formData.get('hourly_rate')) || 0
    };
    
    try {
        const employeeId = event.target.dataset.employeeId;
        const url = employeeId ? `${API_BASE}/employees/${employeeId}` : `${API_BASE}/employees`;
        const method = employeeId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
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
        project_id: parseInt(formData.get('project_id')),
        employee_id: parseInt(formData.get('employee_id')),
        work_date: formData.get('work_date'),
        clock_in: formData.get('clock_in'),
        clock_out: formData.get('clock_out'),
        total_break_minutes: parseInt(formData.get('total_break_minutes')) || 0,
        hours_worked: parseFloat(formData.get('hours_worked')),
        description: formData.get('description'),
        hourly_rate: parseFloat(formData.get('hourly_rate')) || null
    };
    
    try {
        const timeEntryId = event.target.dataset.timeEntryId;
        const url = timeEntryId ? `${API_BASE}/time-entries/${timeEntryId}` : `${API_BASE}/time-entries`;
        const method = timeEntryId ? 'PUT' : 'POST';
        
        if (method === 'PUT') {
            Object.entries(timeEntryData).forEach(([key, value]) => {
                if (value === '' || value === null || Number.isNaN(value)) {
                    delete timeEntryData[key];
                }
            });
        }
        
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
            loadTimeEntries();
            showAlert('Stundeneintrag erfolgreich gespeichert!', 'success');
        } else {
            showAlert('Fehler beim Speichern des Stundeneintrags', 'danger');
        }
    } catch (error) {
        console.error('Fehler beim Speichern des Stundeneintrags:', error);
        showAlert('Fehler beim Speichern des Stundeneintrags', 'danger');
    }
}

// Alert-Funktion
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alertContainer') || document.body;
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.appendChild(alertDiv);
    
    // Auto-remove nach 5 Sekunden
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function updateDarkModeToggle() {
    const icon = document.getElementById('darkModeIcon');
    const text = document.getElementById('darkModeText');

    if (icon) {
        icon.className = isDarkMode ? 'fas fa-sun' : 'fas fa-moon';
    }

    if (text) {
        text.textContent = isDarkMode ? 'Light Mode' : 'Dark Mode';
    }
}

function apiRequest(url, options = {}) {
    const defaultHeaders = options.headers || {};
    if (authToken && !('Authorization' in defaultHeaders)) {
        defaultHeaders['Authorization'] = `Bearer ${authToken}`;
    }

    const finalOptions = Object.assign({
        headers: defaultHeaders
    }, options);

    return fetch(url, finalOptions);
}

// Hilfsfunktionen für Projekt-/Mitarbeiterdaten
function getProjectName(projectId) {
    if (!Array.isArray(projects)) return '';
    const project = projects.find(p => p.id === Number(projectId));
    return project ? project.name : '';
}

function getEmployeeName(employeeId) {
    if (!Array.isArray(employeesCache)) return '';
    const employee = employeesCache.find(e => e.id === Number(employeeId));
    return employee ? employee.full_name : '';
}

function toggleUserManagement(isVisible) {
    const section = document.getElementById('user-management-section');
    const button = document.getElementById('userManagementButton');
    if (section) section.style.display = isVisible ? 'block' : 'none';
    if (button) button.style.display = isVisible ? 'inline-block' : 'none';
}

async function resetEmployeePassword(userId, fullName) {
    if (!authToken) {
        showAlert('Keine Berechtigung vorhanden.', 'warning');
        return;
    }

    if (!confirm(`Passwort für ${fullName} zurücksetzen?`)) {
        return;
    }

    const newPassword = prompt('Neues Passwort (min. 8 Zeichen):');
    if (!newPassword) {
        showAlert('Passwort wurde nicht geändert.', 'info');
        return;
    }
    if (newPassword.length < 8) {
        showAlert('Passwort muss mindestens 8 Zeichen haben.', 'warning');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/auth/users/${userId}/reset-password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ password: newPassword })
        });

        if (response.ok) {
            showAlert(`Passwort für ${fullName} wurde aktualisiert.`, 'success');
        } else {
            const error = await response.json().catch(() => ({}));
            showAlert(error.detail || 'Fehler beim Zurücksetzen des Passworts.', 'danger');
        }
    } catch (error) {
        console.error('Fehler beim Zurücksetzen des Mitarbeiter-Passworts:', error);
        showAlert('Fehler beim Zurücksetzen des Passworts.', 'danger');
    }
}

async function handleEmployeePasswordReset(employeeId, initialUserId = null) {
    if (!authToken) {
        showAlert('Keine Berechtigung vorhanden.', 'warning');
        return;
    }

    if (!Array.isArray(employeesCache) || employeesCache.length === 0) {
        await loadEmployees();
    }

    if (!Array.isArray(usersCache) || usersCache.length === 0) {
        await loadUsers();
    } else {
        await loadUsers();
    }

    const employee = employeesCache.find(e => e.id === Number(employeeId));
    if (!employee) {
        showAlert('Mitarbeiter nicht gefunden.', 'danger');
        return;
    }

    let targetUser = null;

    if (initialUserId !== null) {
        targetUser = usersCache.find(u => u.id === Number(initialUserId)) || null;
    }

    if (!targetUser) {
        targetUser = findUserForEmployee(employee);
    }

    if (!targetUser) {
        const userList = usersCache.map(u => `${u.username}${u.full_name ? ` (${u.full_name})` : ''}`).join('\n');
        const userInput = prompt(
            userList
                ? `Kein Benutzer direkt verknüpft. Bitte Benutzernamen oder ID eingeben:\n\n${userList}`
                : 'Kein Benutzer geladen. Bitte Benutzernamen eingeben:'
        );

        if (!userInput) {
            showAlert('Passwort wurde nicht geändert.', 'info');
            return;
        }

        const trimmedInput = userInput.trim();
        const normalizedInput = trimmedInput.toLowerCase();
        const simplifiedInput = normalizedInput.split(/[\s(]/)[0];

        targetUser = usersCache.find(u => {
            if (!u) return false;
            const username = (u.username || '').trim().toLowerCase();
            const email = (u.email || '').trim().toLowerCase();
            if (String(u.id) === trimmedInput) {
                return true;
            }
            return username === normalizedInput || email === normalizedInput ||
                   username === simplifiedInput || email === simplifiedInput;
        });

        if (!targetUser && trimmedInput) {
            const idFromInput = Number(trimmedInput);
            if (!Number.isNaN(idFromInput)) {
                targetUser = usersCache.find(u => u.id === idFromInput);
            }
        }

        if (!targetUser) {
            showAlert('Benutzer nicht gefunden.', 'warning');
            return;
        }

        employeeUserAssignments[String(employee.id)] = targetUser.id;
        persistEmployeeUserAssignments();
    } else {
        employeeUserAssignments[String(employee.id)] = targetUser.id;
        persistEmployeeUserAssignments();
    }

    await resetEmployeePassword(targetUser.id, targetUser.full_name || targetUser.username || 'Benutzer');
}

function persistEmployeeUserAssignments() {
    if (typeof localStorage === 'undefined') {
        return;
    }

    try {
        localStorage.setItem(EMPLOYEE_USER_STORAGE_KEY, JSON.stringify(employeeUserAssignments));
    } catch (error) {
        console.warn('Konnte Mitarbeiter-Benutzer-Zuordnungen nicht speichern:', error);
    }
}

const invitationsTableBody = document.getElementById('invitations-table');
let invitationsCache = [];

async function loadInvitations() {
    if (!authToken) return;

    try {
        const response = await apiCall(`${API_BASE}/auth/invitations`);
        if (!response.ok) {
            throw new Error('Einladungen konnten nicht geladen werden.');
        }
        invitationsCache = await response.json();
        displayInvitations();
    } catch (error) {
        console.error('Fehler beim Laden der Einladungen:', error);
        showAlert(error.message || 'Fehler beim Laden der Einladungen.', 'danger');
    }
}

function displayInvitations() {
    if (!invitationsTableBody) return;

    if (!Array.isArray(invitationsCache) || invitationsCache.length === 0) {
        invitationsTableBody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">Keine aktiven Einladungen</td></tr>';
        return;
    }

    invitationsTableBody.innerHTML = invitationsCache.map(invite => {
        const expiresAt = invite.expires_at ? new Date(invite.expires_at).toLocaleString('de-DE') : '-';
        const createdAt = invite.created_at ? new Date(invite.created_at).toLocaleString('de-DE') : '-';
        const statusBadge = invite.accepted_at
            ? '<span class="badge bg-success">Akzeptiert</span>'
            : '<span class="badge bg-warning text-dark">Offen</span>';

        return `
            <tr>
                <td>${invite.email}</td>
                <td>${invite.role || '-'}</td>
                <td>${invite.invited_by_name || '-'}</td>
                <td>${createdAt}</td>
                <td>${expiresAt}</td>
                <td>${statusBadge}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="resendInvitation('${invite.email}')">
                        <i class="fas fa-sync-alt"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteInvitation(${invite.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

function showInviteModal() {
    const modal = new bootstrap.Modal(document.getElementById('inviteModal'));
    document.getElementById('inviteForm').reset();
    modal.show();
}

async function submitInvitation() {
    const email = document.getElementById('inviteEmail').value.trim();
    const role = document.getElementById('inviteRole').value;
    const ttlDays = Number(document.getElementById('inviteTtl').value) || 7;

    if (!email) {
        showAlert('Bitte eine E-Mail-Adresse angeben.', 'warning');
        return;
    }

    try {
        const response = await apiCall(`${API_BASE}/auth/invite`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, role, ttl_hours: ttlDays * 24 })
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || 'Einladung konnte nicht erstellt werden.');
        }

        const result = await response.json();
        const modalElement = document.getElementById('inviteModal');
        bootstrap.Modal.getInstance(modalElement)?.hide();

        const acceptLink = `${window.location.origin}/invite/accept?token=${encodeURIComponent(result.token)}`;
        document.getElementById('inviteTokenLink').value = acceptLink;
        document.getElementById('inviteExpiresLabel').innerText = `Link gültig bis ${new Date(result.expires_at).toLocaleString('de-DE')}`;

        const tokenModal = new bootstrap.Modal(document.getElementById('inviteTokenModal'));
        tokenModal.show();

        showAlert('Einladung wurde erstellt.', 'success');
        await loadInvitations();
    } catch (error) {
        console.error('Fehler beim Einladen:', error);
        showAlert(error.message || 'Einladung konnte nicht erstellt werden.', 'danger');
    }
}

async function resendInvitation(email) {
    try {
        const response = await apiCall(`${API_BASE}/auth/invite/resend`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || 'Einladung konnte nicht erneut versendet werden.');
        }

        const result = await response.json();
        const acceptLink = `${window.location.origin}/invite/accept?token=${encodeURIComponent(result.token)}`;
        document.getElementById('inviteTokenLink').value = acceptLink;
        document.getElementById('inviteExpiresLabel').innerText = `Link gültig bis ${new Date(result.expires_at).toLocaleString('de-DE')}`;
        const tokenModal = new bootstrap.Modal(document.getElementById('inviteTokenModal'));
        tokenModal.show();

        showAlert('Einladung wurde erneut versendet.', 'success');
        await loadInvitations();
    } catch (error) {
        console.error('Fehler beim erneuten Versenden:', error);
        showAlert(error.message || 'Einladung konnte nicht erneut versendet werden.', 'danger');
    }
}

async function deleteInvitation(invitationId) {
    if (!confirm('Einladung wirklich löschen?')) return;

    try {
        const response = await apiCall(`${API_BASE}/auth/invitations/${invitationId}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || 'Einladung konnte nicht gelöscht werden.');
        }

        showAlert('Einladung gelöscht.', 'success');
        await loadInvitations();
    } catch (error) {
        console.error('Fehler beim Löschen der Einladung:', error);
        showAlert(error.message || 'Einladung konnte nicht gelöscht werden.', 'danger');
    }
}

function copyInviteLink() {
    const input = document.getElementById('inviteTokenLink');
    input.select();
    input.setSelectionRange(0, 99999);
    document.execCommand('copy');
    showAlert('Link kopiert!', 'success');
}

async function loadInvitationSummary() {
    await loadInvitations();
}

async function loadBillingStatus() {
    if (!authToken) {
        updateBillingUI({ status: 'unauthenticated' });
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/billing/status`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (response.ok) {
            const data = await response.json();
            billingInfo = data || {};
            updateBillingUI(billingInfo);
        } else if (response.status === 401) {
            showLoginPrompt();
        } else {
            updateBillingUI({ status: 'error' });
        }
    } catch (error) {
        console.error('Fehler beim Laden des Billing-Status:', error);
        updateBillingUI({ status: 'error', error: error.message });
    }
}

function updateBillingUI(info) {
    const container = document.getElementById('billing-status-container');
    
    if (!container) {
        console.error('Billing-Status-Container nicht gefunden!');
        return;
    }

    const status = info.subscription_status || info.status || 'inactive';
    const statusMap = {
        active: { text: 'Aktiv', badge: 'success', icon: 'check-circle' },
        trialing: { text: 'Testphase', badge: 'info', icon: 'clock' },
        past_due: { text: 'Zahlung überfällig', badge: 'warning', icon: 'exclamation-triangle' },
        canceled: { text: 'Gekündigt', badge: 'secondary', icon: 'times-circle' },
        suspended: { text: 'Gesperrt', badge: 'danger', icon: 'ban' },
        inactive: { text: 'Inaktiv', badge: 'secondary', icon: 'minus-circle' },
        unauthenticated: { text: 'Nicht angemeldet', badge: 'secondary', icon: 'user-slash' },
        error: { text: 'Fehler beim Laden', badge: 'danger', icon: 'exclamation-circle' }
    };

    const badgeInfo = statusMap[status] || statusMap.inactive;
    
    let html = `
        <div class="row">
            <div class="col-md-6 mb-3">
                <div class="p-3 border rounded" style="background-color: var(--card-bg); border-color: var(--border-color) !important;">
                    <h6 class="mb-2" style="color: var(--text-primary); font-weight: 600;">
                        <i class="fas fa-${badgeInfo.icon} me-2"></i>Status
                    </h6>
                    <h4 class="mb-0">
                        <span class="badge bg-${badgeInfo.badge}">${badgeInfo.text}</span>
                    </h4>
                </div>
            </div>
            <div class="col-md-6 mb-3">
                <div class="p-3 border rounded" style="background-color: var(--card-bg); border-color: var(--border-color) !important;">
                    <h6 class="mb-2" style="color: var(--text-primary); font-weight: 600;">
                        <i class="fas fa-tag me-2"></i>Plan
                    </h6>
                    <h4 class="mb-0" style="color: var(--text-primary);">${info.plan_name || 'Kein Plan'}</h4>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-12">
                <div class="p-3 border rounded" style="background-color: var(--card-bg); border-color: var(--border-color) !important;">
                    <h6 class="mb-2" style="color: var(--text-primary); font-weight: 600;">
                        <i class="fas fa-calendar-alt me-2"></i>Nächste Abbuchung
                    </h6>
                    <p class="mb-0" style="color: var(--text-primary);">
                        ${info.current_period_end ? new Date(info.current_period_end).toLocaleDateString('de-DE') : 'Keine aktive Abbuchung geplant'}
                    </p>
                </div>
            </div>
        </div>
    `;
    
    if (status === 'suspended' || status === 'past_due') {
        html += `
            <div class="alert alert-warning mt-3" style="background-color: var(--warning-bg); border-color: var(--warning-border); color: var(--text-primary);">
                <i class="fas fa-exclamation-triangle me-2"></i>
                <strong>Achtung:</strong> Ihr Zugriff ist eingeschränkt. Bitte aktualisieren Sie Ihre Zahlungsinformationen.
            </div>
        `;
    }
    
    if (info.message && (status === 'inactive' || status === 'error')) {
        html += `
            <div class="alert alert-info mt-3" style="background-color: var(--info-bg); border-color: var(--info-border); color: var(--text-primary);">
                <i class="fas fa-info-circle me-2"></i>
                ${escapeHtml(info.message)}
            </div>
        `;
    }
    
    container.innerHTML = html;
    
    const checkoutBtn = document.getElementById('billing-checkout-btn');
    if (checkoutBtn) {
        checkoutBtn.disabled = status === 'unauthenticated';
    }
}

async function startCheckout() {
    if (!authToken) {
        showAlert('Bitte melde dich zuerst an.', 'warning');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/billing/checkout`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || 'Checkout konnte nicht gestartet werden');
        }

        const data = await response.json();
        if (data.checkout_url) {
            window.location.href = data.checkout_url;
        } else {
            throw new Error('Keine Checkout-URL erhalten');
        }
    } catch (error) {
        console.error('Stripe-Checkout-Fehler:', error);
        showAlert(error.message || 'Checkout konnte nicht gestartet werden.', 'danger');
    }
}

async function loadTenantSettings() {
    if (!authToken) {
        showAlert('Nicht angemeldet.', 'warning');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/auth/tenant/settings`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        if (!response.ok) {
            throw new Error('Stammdaten konnten nicht geladen werden');
        }

        const payload = await response.json();
        tenantSettings = payload.tenant || payload;
        fillTenantSettingsForm(tenantSettings);
        renderTenantSettingsPreview(tenantSettings);
    } catch (error) {
        console.error('Fehler beim Laden der Firmenstammdaten:', error);
        showAlert(error.message || 'Stammdaten konnten nicht geladen werden.', 'danger');
    }
}

function fillTenantSettingsForm(settings) {
    const values = settings || {};

    const inputs = {
        company_name: document.getElementById('settingsCompanyName'),
        company_address: document.getElementById('settingsCompanyAddress'),
        company_phone: document.getElementById('settingsCompanyPhone'),
        company_fax: document.getElementById('settingsCompanyFax'),
        company_email: document.getElementById('settingsCompanyEmail'),
        company_website: document.getElementById('settingsCompanyWebsite'),
        bank_name: document.getElementById('settingsBankName'),
        bank_iban: document.getElementById('settingsBankIban'),
        bank_bic: document.getElementById('settingsBankBic'),
        tax_number: document.getElementById('settingsTaxNumber'),
        vat_id: document.getElementById('settingsVatId')
    };

    Object.entries(inputs).forEach(([key, input]) => {
        if (input) {
            const value = values[key];
            input.value = value === null || value === undefined ? '' : value;
        }
    });
}

function collectTenantSettingsForm() {
    return {
        company_name: document.getElementById('settingsCompanyName').value.trim(),
        company_address: document.getElementById('settingsCompanyAddress').value.trim(),
        company_phone: document.getElementById('settingsCompanyPhone').value.trim(),
        company_fax: document.getElementById('settingsCompanyFax').value.trim(),
        company_email: document.getElementById('settingsCompanyEmail').value.trim(),
        company_website: document.getElementById('settingsCompanyWebsite').value.trim(),
        bank_name: document.getElementById('settingsBankName').value.trim(),
        bank_iban: document.getElementById('settingsBankIban').value.trim(),
        bank_bic: document.getElementById('settingsBankBic').value.trim(),
        tax_number: document.getElementById('settingsTaxNumber').value.trim(),
        vat_id: document.getElementById('settingsVatId').value.trim(),
    };
}

// Preview während der Eingabe aktualisieren
function updateTenantSettingsPreview() {
    const settings = collectTenantSettingsForm();
    renderTenantSettingsPreview(settings);
}

async function saveTenantSettings() {
    if (!authToken) {
        showAlert('Nicht angemeldet.', 'warning');
        return;
    }

    const payload = collectTenantSettingsForm();

    try {
        const response = await fetch(`${API_BASE}/auth/tenant/settings`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || 'Stammdaten konnten nicht gespeichert werden');
        }

        const data = await response.json();
        tenantSettings = data.tenant || data;
        showAlert('Stammdaten wurden gespeichert.', 'success');
        fillTenantSettingsForm(tenantSettings);
        renderTenantSettingsPreview(tenantSettings);
    } catch (error) {
        console.error('Fehler beim Speichern der Firmenstammdaten:', error);
        showAlert(error.message || 'Stammdaten konnten nicht gespeichert werden.', 'danger');
    }
}

// Hilfsfunktionen
function escapeHtml(value) {
    if (value === null || value === undefined) {
        return '';
    }
    return String(value)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

async function apiCall(url, options = {}) {
    if (!options.headers) options.headers = {};
    if (authToken) {
        options.headers['Authorization'] = `Bearer ${authToken}`;
    }
    options.headers['Content-Type'] = options.headers['Content-Type'] || 'application/json';
    const response = await fetch(url, options);
    return response;
}

function renderTenantSettingsPreview(settings) {
    const container = document.getElementById('tenantSettingsPreview');
    const content = document.getElementById('tenantSettingsPreviewContent');
    if (!container || !content) return;

    if (!settings) {
        container.style.display = 'none';
        return;
    }

    container.style.display = 'block';

    const companyName = escapeHtml(settings.company_name || 'DC trockenbau');
    const rawAddress = settings.company_address || 'Dannys Zuhause\nTel: 01637841519\nE-Mail: Dannys@email.de';
    const addressLines = rawAddress
        .split(/\n|,/)
        .map(item => item.trim())
        .filter(Boolean)
        .map(line => escapeHtml(line))
        .join('<br>');

    const contactLines = [];
    if (settings.company_phone) contactLines.push(`Tel: ${escapeHtml(settings.company_phone)}`);
    if (settings.company_email) contactLines.push(`E-Mail: ${escapeHtml(settings.company_email)}`);
    if (settings.company_website) contactLines.push(`Web: ${escapeHtml(settings.company_website)}`);

    const taxLines = [];
    if (settings.tax_number) taxLines.push(`Steuernummer: ${escapeHtml(settings.tax_number)}`);
    if (settings.vat_id) taxLines.push(`USt-IdNr.: ${escapeHtml(settings.vat_id)}`);

    const bankLines = [];
    if (settings.bank_iban) bankLines.push(`IBAN: ${escapeHtml(settings.bank_iban)}`);
    if (settings.bank_bic) bankLines.push(`BIC: ${escapeHtml(settings.bank_bic)}`);
    if (settings.bank_name) bankLines.push(`Bank: ${escapeHtml(settings.bank_name)}`);

    const taxAndBankLines = [...taxLines, ...bankLines];

    const paymentDays = settings.payment_terms_days ?? 30;
    const invoiceDate = new Date();
    const dueDate = new Date(invoiceDate.getTime());
    dueDate.setDate(invoiceDate.getDate() + paymentDays);
    const formatDate = (date) => new Intl.DateTimeFormat('de-DE').format(date);

    const demoTotal = 5000;
    const demoNet = demoTotal / 1.19;
    const demoVat = demoTotal - demoNet;
    const formatCurrency = (value) => value.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' €';

    const footerParts = [companyName, addressLines.replace(/<br>/g, ' • ')];
    if (contactLines.length) footerParts.push(contactLines.join(' • '));

    content.innerHTML = `
        <div class="invoice-preview">
            <div class="invoice-header">
                <div>
                    <div class="company-name">${companyName}</div>
                    <div class="company-contact">
                        ${addressLines.split('<br>').map(line => `<span class="line">${line}</span>`).join('')}
                        ${contactLines.length ? contactLines.map(line => `<span class="line">${line}</span>`).join('') : ''}
                    </div>
                    ${taxAndBankLines.length ? `<div class="company-tax">${taxAndBankLines.map(line => `<span class="line">${line}</span>`).join('')}</div>` : ''}
                </div>
                <div>
                    <div class="logo-box">Logo-Vorschau</div>
                </div>
            </div>

            <div class="invoice-title">RECHNUNG</div>

            <div class="meta-section">
                <div class="meta-block">
                    <span class="meta-title">Rechnungsempfänger:</span>
                    <table class="meta-table">
                        <tr><td>N.N.</td></tr>
                    </table>
                </div>
                <div class="meta-block">
                    <span class="meta-title">Rechnungsdetails:</span>
                    <table class="meta-table">
                        <tr><td class="label">Rechnungs-Nr.</td><td>RE-20251003-002</td></tr>
                        <tr><td class="label">Kunden-Nr.</td><td>00000001</td></tr>
                        <tr><td class="label">Rechnungsdatum</td><td>${formatDate(invoiceDate)}</td></tr>
                        <tr><td class="label">Fälligkeitsdatum</td><td>${formatDate(dueDate)}</td></tr>
                        <tr><td class="label">Seite</td><td>1 / 1</td></tr>
                    </table>
                </div>
            </div>

            <table class="invoice-items">
                <thead>
                    <tr>
                        <th style="width: 10%;">Pos.</th>
                        <th>Bezeichnung</th>
                        <th style="width: 12%;">Menge</th>
                        <th style="width: 12%;">Einh.</th>
                        <th style="width: 13%;">E-Preis €</th>
                        <th style="width: 13%;">G-Preis €</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>00001</td>
                        <td>Bauleistungen</td>
                        <td>1,0</td>
                        <td>Pauschal</td>
                        <td>${formatCurrency(demoTotal)}</td>
                        <td>${formatCurrency(demoTotal)}</td>
                    </tr>
                </tbody>
            </table>

            <div class="invoice-summary">
                <div class="summary-lines">
                    <div class="row"><span class="label">Zwischensumme</span><span>${formatCurrency(demoNet)}</span></div>
                    <div class="row"><span class="label">USt (19 %)</span><span>${formatCurrency(demoVat)}</span></div>
                </div>
                <div class="summary-total"><span>Gesamtbetrag</span><span>${formatCurrency(demoTotal)}</span></div>
            </div>

            <div class="invoice-footer">${footerParts.join(' • ')}</div>
        </div>
    `;
}

let logoManagementModalInstance = null;

// Initialisierung beim Laden der Seite
document.addEventListener('DOMContentLoaded', () => {
    initializeTheme();

    document.querySelectorAll('#mainNavigation [data-section]').forEach(link => {
        link.addEventListener('click', async (event) => {
            event.preventDefault();
            const section = link.getAttribute('data-section');
            await showSection(section);
        });
    });

    const logoModalTrigger = document.getElementById('openLogoModal');
    if (logoModalTrigger) {
        logoModalTrigger.addEventListener('click', async (event) => {
            event.preventDefault();
            await showLogoManagement();
        });
    }

    const checkoutBtn = document.getElementById('billing-checkout-btn');
    const refreshBtn = document.getElementById('billing-refresh-btn');
    if (checkoutBtn) checkoutBtn.addEventListener('click', startCheckout);
    if (refreshBtn) refreshBtn.addEventListener('click', loadBillingStatus);

    const tenantSaveBtn = document.getElementById('tenantSettingsSaveBtn');
    if (tenantSaveBtn) tenantSaveBtn.addEventListener('click', async (event) => {
        event.preventDefault();
        await saveTenantSettings();
        const alertContainer = document.getElementById('tenantSettingsPreview');
        if (alertContainer) {
            alertContainer.classList.add('border-success');
            setTimeout(() => alertContainer.classList.remove('border-success'), 2000);
        }
    });

    // Formular Event Listener registrieren
    setupFormEventListeners();

    initializeApp();
});

function showLogoManagementModal() {
    if (!logoManagementModalInstance) {
        logoManagementModalInstance = getOrCreateModalInstance('logoManagementModal');
    }
    if (logoManagementModalInstance) {
        logoManagementModalInstance.show();
    }
}

async function showLogoManagement() {
    await loadLogoManagement();
    showLogoManagementModal();
}
