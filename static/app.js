document.addEventListener('DOMContentLoaded', function() {
    // Fetch and display stats
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            document.getElementById('active-logs').textContent = data.active_logs || 0;
            document.getElementById('analyses-today').textContent = data.analyses_today || 0;
            document.getElementById('llm-requests').textContent = data.llm_requests || 0;
        })
        .catch(error => console.error('Error fetching stats:', error));

    // Fetch and display logs
    fetch('/api/logs')
        .then(response => response.json())
        .then(data => {
            const logsList = document.getElementById('logs-list');
            if (data.logs && data.logs.length > 0) {
                logsList.innerHTML = data.logs.map(log => `
                    <div class="log-item">
                        <h4>${log.name}</h4>
                        <p>${log.path}</p>
                        <span class="status ${log.is_active ? 'active' : 'inactive'}">
                            ${log.is_active ? '✓ Active' : '✗ Inactive'}
                        </span>
                    </div>
                `).join('');
            } else {
                logsList.innerHTML = '<p>No logs configured yet.</p>';
            }
        })
        .catch(error => console.error('Error fetching logs:', error));

    // Fetch and display analyses
    fetch('/api/analyses')
        .then(response => response.json())
        .then(data => {
            const analysesList = document.getElementById('analyses-list');
            if (data.analyses && data.analyses.length > 0) {
                analysesList.innerHTML = data.analyses.map(analysis => `
                    <div class="analysis-item">
                        <h4>${analysis.log_name}</h4>
                        <p><strong>Severity:</strong> ${analysis.severity}</p>
                        <p><strong>Message:</strong> ${analysis.log_message}</p>
                        <p><strong>Analysis:</strong> ${analysis.llm_response || 'No analysis yet'}</p>
                        <small>${new Date(analysis.timestamp).toLocaleString()}</small>
                    </div>
                `).join('');
            } else {
                analysesList.innerHTML = '<p>No analyses yet.</p>';
            }
        })
        .catch(error => console.error('Error fetching analyses:', error));
});
