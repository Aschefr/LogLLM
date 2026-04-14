import sqlite3
import json
import os
from datetime import datetime

class ConfigManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_db()
        self.init_default_settings()
    
    def init_db(self):
        """Initialize database and create tables"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                context_window INTEGER DEFAULT 50,
                severity TEXT DEFAULT 'Warning',
                system_prompt TEXT,
                user_prompt TEXT,
                notifications_enabled INTEGER DEFAULT 0,
                notification_channel TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create analyses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_id INTEGER NOT NULL,
                severity TEXT NOT NULL,
                log_message TEXT NOT NULL,
                llm_response TEXT,
                context TEXT,
                is_read INTEGER DEFAULT 0,
                is_ignored INTEGER DEFAULT 0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (log_id) REFERENCES logs (id)
            )
        ''')
        
        # Create usage_stats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                llm_requests INTEGER DEFAULT 0,
                notifications_sent INTEGER DEFAULT 0,
                errors_detected INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def init_default_settings(self):
        """Initialize default settings if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        default_settings = {
            'llm_provider': 'ollama',
            'llm_endpoint': 'http://host.docker.internal:11434',
            'llm_model': 'llama2',
            'system_prompt': 'You are a log analysis assistant. Analyze the provided log error and provide a concise explanation of what might have caused it and how to fix it.',
            'default_prompt': 'Analyze this log error and provide actionable insights.',
            'default_severity': 'Warning',
            'notification_provider': 'none',
            'notification_endpoint': ''
        }
        
        for key, value in default_settings.items():
            cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', 
                         (key, json.dumps(value)))
        
        # Initialize usage stats if not exists
        cursor.execute('SELECT COUNT(*) FROM usage_stats')
        if cursor.fetchone()[0] == 0:
            cursor.execute('INSERT INTO usage_stats (llm_requests, notifications_sent, errors_detected) VALUES (0, 0, 0)')
        
        conn.commit()
        conn.close()
    
    def get_setting(self, key):
        """Get a single setting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return json.loads(result[0])
        return None
    
    def set_setting(self, key, value):
        """Set a single setting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value, updated_at) 
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (key, json.dumps(value)))
        conn.commit()
        conn.close()
    
    def get_all_settings(self):
        """Get all settings as a dictionary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT key, value FROM settings')
        results = cursor.fetchall()
        conn.close()
        
        return {key: json.loads(value) for key, value in results}
    
    def save_settings(self, settings_dict):
        """Save multiple settings at once"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for key, value in settings_dict.items():
            cursor.execute('''
                INSERT OR REPLACE INTO settings (key, value, updated_at) 
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (key, json.dumps(value)))
        
        conn.commit()
        conn.close()
    
    def create_log(self, log_data):
        """Create a new log entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO logs (name, path, context_window, severity, system_prompt, 
                            user_prompt, notifications_enabled, notification_channel)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            log_data['name'],
            log_data['path'],
            log_data.get('context_window', 50),
            log_data.get('severity', 'Warning'),
            log_data.get('system_prompt'),
            log_data.get('user_prompt'),
            1 if log_data.get('notifications_enabled') else 0,
            log_data.get('notification_channel')
        ))
        
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return log_id
    
    def get_logs(self):
        """Get all logs"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM logs ORDER BY created_at DESC')
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    def get_active_logs(self):
        """Get all active logs"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM logs WHERE is_active = 1 ORDER BY created_at DESC')
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    def get_log(self, log_id):
        """Get a single log by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM logs WHERE id = ?', (log_id,))
        result = cursor.fetchone()
        conn.close()
        
        return dict(result) if result else None
    
    def update_log(self, log_id, log_data):
        """Update a log entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE logs SET
                name = ?,
                path = ?,
                context_window = ?,
                severity = ?,
                system_prompt = ?,
                user_prompt = ?,
                notifications_enabled = ?,
                notification_channel = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            log_data.get('name'),
            log_data.get('path'),
            log_data.get('context_window', 50),
            log_data.get('severity', 'Warning'),
            log_data.get('system_prompt'),
            log_data.get('user_prompt'),
            1 if log_data.get('notifications_enabled') else 0,
            log_data.get('notification_channel'),
            log_id
        ))
        
        conn.commit()
        conn.close()
    
    def delete_log(self, log_id):
        """Delete a log and its analyses"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM analyses WHERE log_id = ?', (log_id,))
        cursor.execute('DELETE FROM logs WHERE id = ?', (log_id,))
        
        conn.commit()
        conn.close()
    
    def save_analysis(self, log_id, analysis_data):
        """Save an analysis result"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analyses (log_id, severity, log_message, llm_response, context)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            log_id,
            analysis_data['severity'],
            analysis_data['log_message'],
            analysis_data.get('llm_response'),
            analysis_data.get('context')
        ))
        
        analysis_id = cursor.lastrowid
        
        # Update usage stats
        cursor.execute('UPDATE usage_stats SET errors_detected = errors_detected + 1, last_updated = CURRENT_TIMESTAMP')
        
        conn.commit()
        conn.close()
        
        return analysis_id
    
    def get_analyses(self, log_id, limit=100):
        """Get analyses for a specific log"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM analyses 
            WHERE log_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (log_id, limit))
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    def get_recent_analyses(self, limit=10):
        """Get recent analyses across all logs"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT a.*, l.name as log_name
            FROM analyses a
            JOIN logs l ON a.log_id = l.id
            ORDER BY a.timestamp DESC
            LIMIT ?
        ''', (limit,))
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    def mark_analysis_read(self, analysis_id):
        """Mark an analysis as read"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE analyses SET is_read = 1 WHERE id = ?', (analysis_id,))
        conn.commit()
        conn.close()
    
    def mark_analysis_ignored(self, analysis_id):
        """Mark an analysis as ignored"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE analyses SET is_ignored = 1 WHERE id = ?', (analysis_id,))
        conn.commit()
        conn.close()
    
    def get_usage_stats(self):
        """Get usage statistics"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usage_stats LIMIT 1')
        result = cursor.fetchone()
        conn.close()
        
        return dict(result) if result else {
            'llm_requests': 0,
            'notifications_sent': 0,
            'errors_detected': 0
        }
    
    def increment_llm_requests(self):
        """Increment LLM request counter"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE usage_stats SET llm_requests = llm_requests + 1, last_updated = CURRENT_TIMESTAMP')
        conn.commit()
        conn.close()
    
    def increment_notifications_sent(self):
        """Increment notifications sent counter"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('UPDATE usage_stats SET notifications_sent = notifications_sent + 1, last_updated = CURRENT_TIMESTAMP')
        conn.commit()
        conn.close()
