
// DEBUG-SCRIPT FÜR BERICHT-FORMULAR
console.log('🔍 BERICHT-FORMULAR DEBUG STARTET...');

// 1. Prüfe ob reportForm existiert
const reportForm = document.getElementById('reportForm');
console.log('📋 reportForm gefunden:', !!reportForm);

if (reportForm) {
    // 2. Prüfe alle Felder
    const fields = ['project_id', 'title', 'content', 'report_date'];
    fields.forEach(fieldName => {
        const field = reportForm.querySelector(`[name="${fieldName}"]`);
        console.log(`📝 Feld ${fieldName}:`, !!field, field ? field.value : 'NICHT GEFUNDEN');
    });
    
    // 3. Prüfe Event-Listener
    console.log('🎯 Event-Listener Status:');
    console.log('- Form hat submit Event:', reportForm.onsubmit !== null);
    
    // 4. Teste Form-Submit manuell
    console.log('🧪 Teste manuellen Submit...');
    
    // Fülle Formular aus
    const projectSelect = reportForm.querySelector('[name="project_id"]');
    const titleInput = reportForm.querySelector('[name="title"]');
    const contentInput = reportForm.querySelector('[name="content"]');
    const dateInput = reportForm.querySelector('[name="report_date"]');
    
    if (projectSelect) projectSelect.value = '1';
    if (titleInput) titleInput.value = 'Debug Test';
    if (contentInput) contentInput.value = 'Debug Inhalt';
    if (dateInput) dateInput.value = '2025-09-27';
    
    console.log('📝 Formular ausgefüllt');
    
    // 5. Simuliere Submit
    const submitEvent = new Event('submit', { bubbles: true, cancelable: true });
    reportForm.dispatchEvent(submitEvent);
    
    console.log('🚀 Submit-Event ausgelöst');
}

// 6. Prüfe API_BASE
console.log('🌐 API_BASE:', window.API_BASE || 'NICHT GESETZT');

// 7. Prüfe authToken
console.log('🔑 authToken:', window.authToken ? 'VORHANDEN' : 'NICHT VORHANDEN');

console.log('✅ DEBUG-SCRIPT ABGESCHLOSSEN');
