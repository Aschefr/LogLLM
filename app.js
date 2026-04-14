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
    // Hide all pages
    document.querySelectorAll('.page-section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Update nav
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.dataset.page === page) {
            link.classList.add('active');
        }
    });
    
    // Show selected page
    const pageElement = document.getElementById(page);
    if (pageElement) {
        pageElement.classList.add('active');
        currentPage = page;
        
        // Load page data
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

// Toast notifications
function showToast(title, message, type = 'info') {
    const toastEl = document.getElementById('toast');
    document.getElementById('toast-title').textContent = title;
    document.getElementById('toast-message').textContent = message;
    
    const toast = new bootstrap.Toast(toastEl);
    toast.show();
}

// Dashboard
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

// Logs
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
        // Get log info
        const logsResponse = await fetch(`${API_BASE}/api/logs`);
        const logs = await logsResponse.json();
        const log = logs.find(l => l.id === logId);
        
        if (!log) {
            showToast('Error', 'Log not found');
            return;
        }
        
        document.getElementById('log-detail-title').textContent = log.name;
        
        // Get analyses
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
                                                <button class="btn btn-sm btn-info" onclick="showAnalysisDetail(${analysis.id}, ${JSON.stringify(analysis).replace(/"/g, '&quot;')})">
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