// API Base URL
const API_BASE = '';

// Current page state
let currentPage = 'dashboard';
let currentLogId = null;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    loadDashboard();
});

// Navigation
function initNavigation() {
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const page = link.dataset.page;
            showPage(page);
        });
    });
}

function showPage(page) {
    document.querySelectorAll('.page-section').forEach(section => {
        section.classList.remove('active');
    });
    
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.dataset.page === page) {
            link.classList.add('active');
        }
    });
    
    const pageElement = document.getElementById(page);
    if (pageElement) {
        pageElement.classList.add('active');
        currentPage = page;
        
        switch(page) {
            case 'dashboard':
                loadDashboard();
                break;
            case 'logs':
                loadLogs();
                break;
            case 'settings':
                loadSettings();
                break;
        }
    }
}

function showToast(title, message, type = 'info') {
    const toastEl = document.getElementById('toast');
    document.getElementById('toast-title').textContent = title;
    document.getElementById('toast-message').textContent = message;
    const toast = new bootstrap.Toast(toastEl);
    toast.show();
}

async function loadDashboard() {
    try {
        const response = await fetch(`${API_BASE}/api/dashboard`);
        const data = await response.json();
        
        document.getElementById('stat-monitoring-status').textContent = 
            data.monitoring_status === 'active' ? 'Active' : 'Stopped';
        document.getElementById('stat-monitoring-status').className = 
            data.monitoring_status === 'active' ? 'stat-value' : 'stat-value text-danger';
        
        document.getElementById('stat-active-logs').textContent = data.active_logs;
        document.getElementById('stat-errors-today').textContent = data.errors_today;
        document.getElementById('stat-llm-usage').textContent = data.llm_usage;
        
        renderRecentAlerts(data.recent_analyses);
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showToast('Error', 'Failed to load dashboard data');
    }
}

function renderRecentAlerts(analyses) {
    const tbody = document.getElementById('recent-alerts-table');
    
    if (!analyses || analyses.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No recent alerts</td></tr>';
        return;
    }
    
    tbody.innerHTML = analyses.map(analysis => `
        <tr>
            <td>${new Date(analysis.timestamp).toLocaleString()}</td>
            <td>${escapeHtml(analysis.log_name || 'Unknown')}</td>
            <td><span class="severity-${analysis.severity}">${analysis.severity}</span></td>
            <td>${escapeHtml(analysis.log_message?.substring(0, 50) || '')}...</td>
            <td>${escapeHtml(analysis.llm_response?.substring(0, 80) || '')}...</td>
        </tr>
    `).join('');
}

async function loadLogs() {
    try {
        const response = await fetch(`${API_BASE}/api/logs`);
        const logs = await response.json();
        
        const container = document.getElementById('logs-list');
        
        if (!logs || logs.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="bi bi-file-earmark-text"></i>
                    <h4>No Logs Configured</h4>
                    <p>Use the "Add Log" wizard to start monitoring your first log file.</p>
                    <button class="btn btn-primary" onclick="showPage('wizard')">Add Log</button>
                </div>
            `;
            return;
        }
        
        container.innerHTML = logs.map(log => `
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h5 class="card-title mb-0">${escapeHtml(log.name)}</h5>
                    <span class="badge ${log.is_active ? 'badge-success' : 'badge-secondary'}">
                        ${log.is_active ? 'Active' : 'Inactive'}
                    </span>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <p class="mb-2"><strong>Path:</strong> ${escapeHtml(log.path)}</p>
                            <p class="mb-2"><strong>Context Window:</strong> ${log.context_window} lines</p>
                            <p class="mb-2"><strong>Severity:</strong> ${log.severity}</p>
                        </div>
                        <div class="col-md-6">
                            <p class="mb-2"><strong>Notifications:</strong> ${log.notifications_enabled ? 'Enabled' : 'Disabled'}</p>
                            <p class="mb-2"><strong>Created:</strong> ${new Date(log.created_at).toLocaleString()}</p>
                        </div>
                    </div>
                    <div class="d-flex gap-2">
                        <button class="btn btn-sm btn-primary" onclick="viewLogDetail(${log.id})">
                            <i class="bi bi-eye"></i> View Details
                        </button>
                        <button class="btn btn-sm btn-warning" onclick="scanLog(${log.id})">
                            <i class="bi bi-search"></i> Scan Now
                        </button>
                        <button class="btn btn-sm btn-danger" onclick="deleteLog(${log.id})">
                            <i class="bi bi-trash"></i> Delete
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading logs:', error);
        showToast('Error', 'Failed to load logs');
    }
}

async function viewLogDetail(logId) {
    currentLogId = logId;
    
    try {
        const logsResponse = await fetch(`${API_BASE}/api/logs`);
        const logs = await logsResponse.json();
        const log = logs.find(l => l.id === logId);
        
        if (!log) {
            showToast('Error', 'Log not found');
            return;
        }
        
        document.getElementById('log-detail-title').textContent = log.name;
        
        const analysesResponse = await fetch(`${API_BASE}/api/logs/${logId}/analyses`);
        const analyses = await analysesResponse.json();
        
        let analysesHtml = '';
        if (analyses && analyses.length > 0) {
            analysesHtml = `
                <div class="card mb-4">
                    <div class="card-header">
                        <h5 class="card-title"><i class="bi bi-list-ul"></i> Analyses</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>Time</th>
                                        <th>Severity</th>
                                        <th>Log Message</th>
                                        <th>LLM Response</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${analyses.map(analysis => `
                                        <tr class="${analysis.is_read ? '' : 'table-warning'}">
                                            <td>${new Date(analysis.timestamp).toLocaleString()}</td>
                                            <td><span class="severity-${analysis.severity}">${analysis.severity}</span></td>
                                            <td>${escapeHtml(analysis.log_message?.substring(0, 60) || '')}...</td>
                                            <td>${escapeHtml(analysis.llm_response?.substring(0, 100) || '')}...</td>
                                            <td>
                                                <button class="btn btn-sm btn-info" onclick="showAnalysisDetail(${analysis.id})">
                                                    <i class="bi bi-eye"></i>
                                                </button>
                                                ${!analysis.is_read ? `<button class="btn btn-sm btn-success" onclick="markAsRead(${analysis.id})">
                                                    <i class="bi bi-check"></i>
                                                </button>` : ''}
                                                <button class="btn btn-sm btn-secondary" onclick="markAsIgnored(${analysis.id})">
                                                    <i class="bi bi-eye-slash"></i>
                                                </button>
                                            </td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `;
        } else {
            analysesHtml = '<div class="alert alert-info">No analyses found for this log.</div>';
        }
        
        document.getElementById('log-detail-content').innerHTML = `
            <div class="card mb-4">
                <div class="card-header">
                    <h5 class="card-title"><i class="bi bi-info-circle"></i> Log Information</h5>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>Path:</strong> ${escapeHtml(log.path)}</p>
                            <p><strong>Context Window:</strong> ${log.context_window} lines</p>
                            <p><strong>Default Severity:</strong> ${log.severity}</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Notifications:</strong> ${log.notifications_enabled ? 'Enabled' : 'Disabled'}</p>
                            <p><strong>Created:</strong> ${new Date(log.created_at).toLocaleString()}</p>
                            <p><strong>Updated:</strong> ${new Date(log.updated_at).toLocaleString()}</p>
                        </div>
                    </div>
                    <div class="d-flex gap-2">
                        <button class="btn btn-warning" onclick="scanLog(${log.id})">
                            <i class="bi bi-search"></i> Scan Now
                        </button>
                        <button class="btn btn-danger" onclick="deleteLog(${log.id})">
                            <i class="bi bi-trash"></i> Delete Log
                        </button>
                    </div>
                </div>
            </div>
            ${analysesHtml}
        `;
        
        showPage('log-detail');
    } catch (error) {
        console.error('Error loading log detail:', error);
        showToast('Error', 'Failed to load log details');
    }
}

function showAnalysisDetail(analysisId) {
    const logsResponse = fetch(`${API_BASE}/api/logs`);
    const analysesResponse = fetch(`${API_BASE}/api/logs/${currentLogId}/analyses`);
    
    Promise.all([logsResponse, analysesResponse]).then(([logsRes, analysesRes]) => {
        return Promise.all([logsRes.json(), analysesRes.json()]);
    }).then(([logs, analyses]) => {
        const analysis = analyses.find(a => a.id === analysisId);
        if (!analysis) return;
        
        const modalHtml = `
            <div class="modal fade" id="analysisModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Analysis Detail</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="mb-3">
                                <strong>Time:</strong> ${new Date(analysis.timestamp).toLocaleString()}
                            </div>
                            <div class="mb-3">
                                <strong>Severity:</strong> <span class="severity-${analysis.severity}">${analysis.severity}</span>
                            </div>
                            <div class="mb-3">
                                <strong>Log Message:</strong>
                                <p class="context-box">${escapeHtml(analysis.log_message)}</p>
                            </div>
                            <div class="mb-3">
                                <strong>Context:</strong>
                                <p class="context-box">${escapeHtml(analysis.context || 'No context available')}</p>
                            </div>
                            <div class="mb-3">
                                <strong>LLM Analysis:</strong>
                                <div class="llm-response-box">${escapeHtml(analysis.llm_response || 'No analysis available')}</div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        const modal = new bootstrap.Modal(document.getElementById('analysisModal'));
        modal.show();
    });
}

async function markAsRead(analysisId) {
    try {
        await fetch(`${API_BASE}/api/analyses/${analysisId}/read`, { method: 'POST' });
        showToast('Success', 'Analysis marked as read');
        viewLogDetail(currentLogId);
    } catch (error) {
        console.error('Error marking as read:', error);
        showToast('Error', 'Failed to mark analysis as read');
    }
}

async function markAsIgnored(analysisId) {
    try {
        await fetch(`${API_BASE}/api/analyses/${analysisId}/ignore`, { method: 'POST' });
        showToast('Success', 'Analysis marked as ignored');
        viewLogDetail(currentLogId);
    } catch (error) {
        console.error('Error marking as ignored:', error);
        showToast('Error', 'Failed to mark analysis as ignored');
    }
}

async function scanLog(logId) {
    try {
        showToast('Scanning', 'Scanning log file...');
        await fetch(`${API_BASE}/api/logs/${logId}/scan`);
        showToast('Complete', 'Log scan complete');
        if (currentPage === 'log-detail' && currentLogId === logId) {
            viewLogDetail(logId);
        } else {
            loadLogs();
        }
    } catch (error) {
        console.error('Error scanning log:', error);
        showToast('Error', 'Failed to scan log');
    }
}

async function deleteLog(logId) {
    if (!confirm('Are you sure you want to delete this log monitor?')) {
        return;
    }
    
    try {
        await fetch(`${API_BASE}/api/logs/${logId}`, { method: 'DELETE' });
        showToast('Success', 'Log monitor deleted');
        if (currentPage === 'log-detail') {
            showPage('logs');
        } else {
            loadLogs();
        }
    } catch (error) {
        console.error('Error deleting log:', error);
        showToast('Error', 'Failed to delete log');
    }
}

// Wizard
let wizardCurrentStep = 1;

function nextWizardStep(step) {
    document.querySelectorAll('.wizard-step').forEach(s => s.classList.remove('active'));
    document.querySelector(`.wizard-step[data-step="${step}"]`).classList.add('active');
    
    document.querySelectorAll('.wizard-step-indicator').forEach((ind, idx) => {
        if (idx + 1 < step) {
            ind.classList.add('completed');
            ind.classList.remove('active');
        } else if (idx + 1 === step) {
            ind.classList.add('active');
            ind.classList.remove('completed');
        } else {
            ind.classList.remove('active', 'completed');
        }
    });
    
    wizardCurrentStep = step;
}

function prevWizardStep(step) {
    nextWizardStep(step);
}

async function scanFiles() {
    try {
        const response = await fetch(`${API_BASE}/api/files/scan`);
        const files = await response.json();
        
        const select = document.getElementById('wizard-file-path');
        select.innerHTML = '<option value="">Select a file...</option>';
        
        files.forEach(file => {
            const option = document.createElement('option');
            option.value = file.path;
            option.textContent = file.path;
            select.appendChild(option);
        });
        
        if (files.length === 0) {
            showToast('Info', 'No files found in /logs directory');
        }
    } catch (error) {
        console.error('Error scanning files:', error);
        showToast('Error', 'Failed to scan files');
    }
}

async function submitWizard() {
    const settings = await getSettings();
    
    const data = {
        name: document.getElementById('wizard-log-name').value,
        path: document.getElementById('wizard-file-path').value,
        context_window: parseInt(document.getElementById('wizard-context-window').value),
        severity: document.getElementById('wizard-severity').value,
        notifications_enabled: document.getElementById('wizard-notifications-enabled').checked,
        notification_channel: document.getElementById('wizard-notification-channel').value
    };
    
    const systemPrompt = document.getElementById('wizard-system-prompt').value;
    const userPrompt = document.getElementById('wizard-user-prompt').value;
    
    if (systemPrompt) data.system_prompt = systemPrompt;
    if (userPrompt) data.user_prompt = userPrompt;
    
    if (!data.name || !data.path) {
        showToast('Error', 'Please fill in all required fields');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/logs`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showToast('Success', 'Log monitor created successfully');
            showPage('logs');
        } else {
            showToast('Error', 'Failed to create log monitor');
        }
    } catch (error) {
        console.error('Error creating log:', error);
        showToast('Error', 'Failed to create log monitor');
    }
}

// Settings
async function loadSettings() {
    try {
        const settings = await getSettings();
        
        document.getElementById('setting-llm-provider').value = settings.llm_provider || 'ollama';
        document.getElementById('setting-llm-endpoint').value = settings.llm_endpoint || '';
        document.getElementById('setting-llm-model').value = settings.llm_model || '';
        document.getElementById('setting-system-prompt').value = settings.system_prompt || '';
        document.getElementById('setting-default-prompt').value = settings.default_prompt || '';
        document.getElementById('setting-notification-provider').value = settings.notification_provider || 'none';
        document.getElementById('setting-notification-endpoint').value = settings.notification_endpoint || '';
    } catch (error) {
        console.error('Error loading settings:', error);
        showToast('Error', 'Failed to load settings');
    }
}

async function getSettings() {
    const response = await fetch(`${API_BASE}/api/settings`);
    return await response.json();
}

async function saveSettings() {
    const data = {
        llm_provider: document.getElementById('setting-llm-provider').value,
        llm_endpoint: document.getElementById('setting-llm-endpoint').value,
        llm_model: document.getElementById('setting-llm-model').value,
        system_prompt: document.getElementById('setting-system-prompt').value,
        default_prompt: document.getElementById('setting-default-prompt').value,
        notification_provider: document.getElementById('setting-notification-provider').value,
        notification_endpoint: document.getElementById('setting-notification-endpoint').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/api/settings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showToast('Success', 'Settings saved successfully');
        } else {
            showToast('Error', 'Failed to save settings');
        }
    } catch (error) {
        console.error('Error saving settings:', error);
        showToast('Error', 'Failed to save settings');
    }
}

async function testLLM() {
    try {
        showToast('Testing', 'Testing LLM connection...');
        const response = await fetch(`${API_BASE}/api/llm/test`);
        const result = await response.json();
        
        if (result.success) {
            showToast('Success', result.message);
        } else {
            showToast('Error', result.message);
        }
    } catch (error) {
        console.error('Error testing LLM:', error);
        showToast('Error', 'Failed to test LLM connection');
    }
}

async function testNotification() {
    const data = {
        provider: document.getElementById('setting-notification-provider').value,
        endpoint: document.getElementById('setting-notification-endpoint').value
    };
    
    try {
        showToast('Testing', 'Sending test notification...');
        const response = await fetch(`${API_BASE}/api/notification/test`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showToast('Success', result.message);
        } else {
            showToast('Error', result.message);
        }
    } catch (error) {
        console.error('Error testing notification:', error);
        showToast('Error', 'Failed to test notification');
    }
}

// Utility
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Auto-refresh dashboard every 30 seconds
setInterval(loadDashboard, 30000);
