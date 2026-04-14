from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sqlite3
import json
import os
from datetime import datetime
import threading
import time
from log_monitor import LogMonitor
from llm_service import LLMService
from notification_service import NotificationService
from config_manager import ConfigManager

app = Flask(__name__, template_folder='dist', static_folder='dist')
CORS(app)

# Initialize services
config_manager = ConfigManager('/app/appdata/config.db')
llm_service = LLMService(config_manager)
notification_service = NotificationService(config_manager)
log_monitor = LogMonitor(config_manager, llm_service, notification_service)

# Database initialization
def init_db():
    conn = sqlite3.connect('/app/appdata/config.db')
    cursor = conn.cursor()
    
    # Settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    # Logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            path TEXT,
            context_window INTEGER DEFAULT 50,
            llm_model TEXT,
            system_prompt TEXT,
            user_prompt TEXT,
            severity TEXT DEFAULT 'Warning',
            notifications_enabled INTEGER DEFAULT 0,
            notification_channel TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Analyses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_id INTEGER,
            timestamp TIMESTAMP,
            severity TEXT,
            log_message TEXT,
            llm_response TEXT,
            context TEXT,
            is_read INTEGER DEFAULT 0,
            is_ignored INTEGER DEFAULT 0,
            FOREIGN KEY (log_id) REFERENCES logs (id)
        )
    ''')
    
    # Usage stats table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP,
            llm_requests INTEGER DEFAULT 0,
            notifications_sent INTEGER DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<path:path>')
def catch_all(path):
    return render_template('index.html')

# API Routes
@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/settings')
def get_settings():
    return jsonify(config_manager.get_all_settings())

@app.route('/api/settings', methods=['POST'])
def save_settings():
    data = request.json
    config_manager.save_settings(data)
    return jsonify({'success': True})

@app.route('/api/logs')
def get_logs():
    logs = config_manager.get_logs()
    return jsonify(logs)

@app.route('/api/logs', methods=['POST'])
def create_log():
    data = request.json
    log_id = config_manager.create_log(data)
    log_monitor.start_monitoring(log_id)
    return jsonify({'success': True, 'id': log_id})

@app.route('/api/logs/<int:log_id>', methods=['PUT'])
def update_log(log_id):
    data = request.json
    config_manager.update_log(log_id, data)
    log_monitor.restart_monitoring(log_id)
    return jsonify({'success': True})

@app.route('/api/logs/<int:log_id>', methods=['DELETE'])
def delete_log(log_id):
    log_monitor.stop_monitoring(log_id)
    config_manager.delete_log(log_id)
    return jsonify({'success': True})

@app.route('/api/logs/<int:log_id>/analyses')
def get_analyses(log_id):
    analyses = config_manager.get_analyses(log_id)
    return jsonify(analyses)

@app.route('/api/logs/<int:log_id>/scan')
def scan_log(log_id):
    log_monitor.scan_log(log_id)
    return jsonify({'success': True})

@app.route('/api/analyses/<int:analysis_id>/read', methods=['POST'])
def mark_as_read(analysis_id):
    config_manager.mark_analysis_read(analysis_id)
    return jsonify({'success': True})

@app.route('/api/analyses/<int:analysis_id>/ignore', methods=['POST'])
def mark_as_ignored(analysis_id):
    config_manager.mark_analysis_ignored(analysis_id)
    return jsonify({'success': True})

@app.route('/api/dashboard')
def get_dashboard():
    stats = {
        'monitoring_status': 'active' if log_monitor.is_running else 'stopped',
        'active_logs': len([l for l in config_manager.get_logs() if l['is_active']]),
        'errors_today': config_manager.get_errors_today(),
        'recent_analyses': config_manager.get_recent_analyses(10),
        'llm_usage': config_manager.get_llm_usage()
    }
    return jsonify(stats)

@app.route('/api/llm/test')
def test_llm():
    result = llm_service.test_connection()
    return jsonify(result)

@app.route('/api/notification/test', methods=['POST'])
def test_notification():
    data = request.json
    result = notification_service.test_notification(data)
    return jsonify(result)

@app.route('/api/files/scan')
def scan_files():
    files = log_monitor.scan_available_files()
    return jsonify(files)

# Start monitoring on startup
def start_monitoring():
    time.sleep(2)  # Wait for server to start
    active_logs = config_manager.get_active_logs()
    for log in active_logs:
        log_monitor.start_monitoring(log['id'])

# Run the app
if __name__ == '__main__':
    threading.Thread(target=start_monitoring, daemon=True).start()
    app.run(host='0.0.0.0', port=8080, debug=False)
