import unittest
import sys
import os
import tempfile
sys.path.insert(0, '/app')

from config_manager import ConfigManager

class TestConfigManager(unittest.TestCase):
    def setUp(self):
        self.test_db = '/tmp/test_config_manager.db'
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        self.config_manager = ConfigManager(self.test_db)
    
    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
    
    def test_init_default_settings(self):
        """Test that default settings are initialized"""
        settings = self.config_manager.get_all_settings()
        self.assertIn('llm_provider', settings)
        self.assertIn('system_prompt', settings)
        self.assertIn('default_prompt', settings)
    
    def test_save_and_get_settings(self):
        """Test saving and retrieving settings"""
        test_settings = {
            'test_key': 'test_value',
            'test_number': 123
        }
        self.config_manager.save_settings(test_settings)
        
        settings = self.config_manager.get_all_settings()
        self.assertEqual(settings['test_key'], 'test_value')
        self.assertEqual(settings['test_number'], 123)
    
    def test_create_log(self):
        """Test creating a new log entry"""
        log_data = {
            'name': 'Test Log',
            'path': '/logs/test.log',
            'context_window': 50,
            'severity': 'Warning'
        }
        log_id = self.config_manager.create_log(log_data)
        self.assertIsNotNone(log_id)
        self.assertIsInstance(log_id, int)
    
    def test_get_logs(self):
        """Test retrieving logs"""
        log_data = {
            'name': 'Test Log 2',
            'path': '/logs/test2.log',
            'context_window': 100,
            'severity': 'Error'
        }
        self.config_manager.create_log(log_data)
        
        logs = self.config_manager.get_logs()
        self.assertGreater(len(logs), 0)
    
    def test_delete_log(self):
        """Test deleting a log"""
        log_data = {
            'name': 'Test Log 3',
            'path': '/logs/test3.log',
            'context_window': 50,
            'severity': 'Info'
        }
        log_id = self.config_manager.create_log(log_data)
        self.config_manager.delete_log(log_id)
        
        logs = self.config_manager.get_logs()
        log_names = [log['name'] for log in logs]
        self.assertNotIn('Test Log 3', log_names)
    
    def test_save_analysis(self):
        """Test saving an analysis"""
        log_data = {
            'name': 'Test Log 4',
            'path': '/logs/test4.log',
            'context_window': 50,
            'severity': 'Warning'
        }
        log_id = self.config_manager.create_log(log_data)
        
        analysis_data = {
            'severity': 'Error',
            'log_message': 'Test error',
            'llm_response': 'Test analysis',
            'context': 'Test context'
        }
        analysis_id = self.config_manager.save_analysis(log_id, analysis_data)
        self.assertIsNotNone(analysis_id)
    
    def test_get_analyses(self):
        """Test retrieving analyses"""
        log_data = {
            'name': 'Test Log 5',
            'path': '/logs/test5.log',
            'context_window': 50,
            'severity': 'Warning'
        }
        log_id = self.config_manager.create_log(log_data)
        
        analysis_data = {
            'severity': 'Critical',
            'log_message': 'Critical error',
            'llm_response': 'Critical analysis',
            'context': 'Critical context'
        }
        self.config_manager.save_analysis(log_id, analysis_data)
        
        analyses = self.config_manager.get_analyses(log_id)
        self.assertEqual(len(analyses), 1)
        self.assertEqual(analyses[0]['severity'], 'Critical')

if __name__ == '__main__':
    unittest.main()
