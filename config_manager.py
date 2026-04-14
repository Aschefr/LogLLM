import sqlite3
import json
from datetime import datetime, timedelta

class ConfigManager:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_default_settings()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_default_settings(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        defaults = {
            'llm_provider': 'ollama',
            'llm_endpoint': 'http://host.docker.internal:11434',
            'llm_model': 'llama2',
            'system_prompt': 'You are a log analysis assistant. Analyze the following log entry and determine if it represents an error or issue that requires attention.',
            'default_prompt': 'Analyze this log entry and explain what might have caused it:',
            'default_severity': 'Warning',
            'notification_provider': 'none',
            'notification_endpoint': '',
            'notification_channel': ''
        }
        
        for key, value in defaults.items():
            cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', (key, json.dumps(value)))
        
        conn.commit()
        conn.close()
    
    def get_all_settings(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT key, value FROM settings')
        rows = cursor.fetchall()
        conn.close()
        
        settings = {}
        for row in rows:
            try:
                settings[row['key']] = json.loads(row['value'])
            except json.JSONDecodeError:
                settings[row['key']] = row['value']
        
        return settings
    
    def save_settings(self, settings):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        for key, value in settings.items():
            cursor.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', 
                         (key, json.dumps(value)))
        
        conn.commit()
        conn.close()
    
    def get_logs(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM logs ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_active_logs(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM logs WHERE is_active = 1')
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def create_log(self, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO logs (name, path, context_window, llm_model, system_prompt, 
                            user_prompt, severity, notifications_enabled, notification_channel, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
        ''', (
            data['name'],
            data['path'],
            data.get('context_window', 50),
            data.get('llm_model'),
            data.get('system_prompt'),
            data.get('user_prompt'),
            data.get('severity', 'Warning'),
            1 if data.get('notifications_enabled') else 0,
            data.get('notification_channel')
        ))
        
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return log_id
    
    def update_log(self, log_id, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE logs SET 
                name = ?, path = ?, context_window = ?, llm_model = ?,
                system_prompt = ?, user_prompt = ?, severity = ?,
                notifications_enabled = ?, notification_channel = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            data['name'],
            data['path'],
            data.get('context_window', 50),
            data.get('llm_model'),
            data.get('system_prompt'),
            data.get('user_prompt'),
            data.get('severity', 'Warning'),
            1 if data.get('notifications_enabled') else 0,
            data.get('notification_channel'),
            log_id
        ))
        
        conn.commit()
        conn.close()
    
    def delete_log(self, log_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM logs WHERE id = ?', (log_id,))
        cursor.execute('DELETE FROM analyses WHERE log_id = ?', (log_id,))
        
        conn.commit()
        conn.close()
    
    def get_analyses(self, log_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT a.*, l.name as log_name 
            FROM analyses a 
            JOIN logs l ON a.log_id = l.id 
            WHERE a.log_id = ? 
            ORDER BY a.timestamp DESC
        ''', (log_id,))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def save_analysis(self, log_id, data):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analyses (log_id, timestamp, severity, log_message, llm_response, context)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            log_id,
            datetime.now().isoformat(),
            data['severity'],
            data['log_message'],
            data['llm_response'],
            data['context']
        ))
        
        analysis_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return analysis_id
    
    def mark_analysis_read(self, analysis_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE analyses SET is_read = 1 WHERE id = ?', (analysis_id,))
        conn.commit()
        conn.close()
    
    def mark_analysis_ignored(self, analysis_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE analyses SET is_ignored = 1 WHERE id = ?', (analysis_id,))
        conn.commit()
        conn.close()
    
    def get_recent_analyses(self, limit=10):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT a.*, l.name as log_name 
            FROM analyses a 
            JOIN logs l ON a.log_id = l.id 
            ORDER BY a.timestamp DESC 
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_errors_today(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        today = datetime.now().date()
        cursor.execute('''
            SELECT COUNT(*) FROM analyses 
            WHERE date(timestamp) = date(?) 
            AND severity IN ('Error', 'Critical')
        ''', (today.isoformat(),))
        count = cursor.fetchone()[0]
        conn.close()
        
        return count
    
    def get_llm_usage(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT SUM(llm_requests) as total FROM usage_stats')
        result = cursor.fetchone()[0]
        conn.close()
        
        return result or 0
    
    def increment_llm_usage(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO usage_stats (timestamp, llm_requests)
            VALUES (CURRENT_TIMESTAMP, 1)
        ''')
        conn.commit()
        conn.close()
