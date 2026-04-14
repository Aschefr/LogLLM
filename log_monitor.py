import os
import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

class LogMonitor:
    def __init__(self, config_manager, llm_service, notification_service):
        self.config_manager = config_manager
        self.llm_service = llm_service
        self.notification_service = notification_service
        self.monitors = {}
        self.is_running = False
    
    def scan_available_files(self):
        files = []
        logs_dir = '/logs'
        
        if os.path.exists(logs_dir):
            for root, dirs, filenames in os.walk(logs_dir):
                for filename in filenames:
                    file_path = os.path.join(root, filename)
                    if os.path.isfile(file_path) and not filename.startswith('.'):
                        files.append({
                            'path': file_path,
                            'name': filename,
                            'size': os.path.getsize(file_path),
                            'modified': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                        })
        
        return files
    
    def start_monitoring(self, log_id):
        log = self.config_manager.get_logs()
        log = next((l for l in log if l['id'] == log_id), None)
        
        if not log:
            return
        
        if log_id in self.monitors:
            self.stop_monitoring(log_id)
        
        file_path = log['path']
        
        if not os.path.exists(file_path):
            return
        
        class LogHandler(FileSystemEventHandler):
            def __init__(self, log_id, config_manager, llm_service, notification_service):
                self.log_id = log_id
                self.config_manager = config_manager
                self.llm_service = llm_service
                self.notification_service = notification_service
                self.last_position = 0
                self.buffer = []
            
            def on_modified(self, event):
                if event.is_directory:
                    return
                
                try:
                    self.process_file(event.src_path)
                except Exception as e:
                    print(f"Error processing file: {e}")
            
            def process_file(self, file_path):
                log = self.config_manager.get_logs()
                log = next((l for l in log if l['id'] == self.log_id), None)
                
                if not log:
                    return
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        f.seek(self.last_position)
                        new_lines = f.readlines()
                        self.last_position = f.tell()
                        
                        if new_lines:
                            self.analyze_lines(new_lines, log)
                
                except Exception as e:
                    print(f"Error reading file: {e}")
            
            def analyze_lines(self, lines, log):
                settings = self.config_manager.get_all_settings()
                context_window = log.get('context_window', 50)
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Check if this line contains an error
                    error_keywords = ['error', 'exception', 'failed', 'critical', 'fatal', 'panic']
                    if not any(keyword in line.lower() for keyword in error_keywords):
                        continue
                    
                    # Get context
                    context = self.get_context(file_path, context_window)
                    
                    # Analyze with LLM
                    llm_response = self.llm_service.analyze_log(line, context, settings, log)
                    
                    # Determine severity
                    severity = log.get('severity', 'Warning')
                    if any(k in line.lower() for k in ['critical', 'fatal', 'panic']):
                        severity = 'Critical'
                    elif any(k in line.lower() for k in ['error', 'exception']):
                        severity = 'Error'
                    
                    # Save analysis
                    analysis_data = {
                        'severity': severity,
                        'log_message': line,
                        'llm_response': llm_response,
                        'context': context
                    }
                    
                    self.config_manager.save_analysis(self.log_id, analysis_data)
                    
                    # Send notification if configured
                    if severity in ['Error', 'Critical']:
                        notification = self.notification_service.send_notification(
                            f"Log Alert: {log['name']}",
                            f"Severity: {severity}\n\nLog: {line}\n\nAnalysis: {llm_response[:200]}...",
                            settings,
                            log
                        )
            
            def get_context(self, file_path, lines_count):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        all_lines = f.readlines()
                        current_pos = self.last_position
                        
                        # Find current line number
                        line_num = 0
                        pos = 0
                        for i, line in enumerate(all_lines):
                            if pos >= current_pos:
                                line_num = i
                                break
                            pos += len(line.encode('utf-8'))
                        
                        # Get context lines
                        start = max(0, line_num - lines_count)
                        context_lines = all_lines[start:line_num]
                        
                        return ''.join(context_lines[-lines_count:])
                
                except Exception as e:
                    return f"Error getting context: {e}"
        
        event_handler = LogHandler(log_id, self.config_manager, self.llm_service, self.notification_service)
        observer = Observer()
        observer.schedule(event_handler, os.path.dirname(file_path), recursive=False)
        observer.start()
        
        self.monitors[log_id] = {
            'observer': observer,
            'handler': event_handler
        }
        
        self.is_running = True
    
    def stop_monitoring(self, log_id):
        if log_id in self.monitors:
            monitor = self.monitors[log_id]
            monitor['observer'].stop()
            monitor['observer'].join()
            del self.monitors[log_id]
    
    def restart_monitoring(self, log_id):
        self.stop_monitoring(log_id)
        self.start_monitoring(log_id)
    
    def scan_log(self, log_id):
        log = self.config_manager.get_logs()
        log = next((l for l in log if l['id'] == log_id), None)
        
        if not log:
            return
        
        file_path = log['path']
        
        if not os.path.exists(file_path):
            return
        
        # Create a temporary handler to scan the file
        handler = LogHandler(log_id, self.config_manager, self.llm_service, self.notification_service)
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                handler.analyze_lines(lines, log)
        except Exception as e:
            print(f"Error scanning file: {e}")
