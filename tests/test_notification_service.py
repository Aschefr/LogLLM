import unittest
import sys
sys.path.insert(0, '/app')

from notification_service import NotificationService
from config_manager import ConfigManager

class TestNotificationService(unittest.TestCase):
    def setUp(self):
        self.config_manager = ConfigManager('/tmp/test_config.db')
        self.notification_service = NotificationService(self.config_manager)
    
    def test_get_settings(self):
        """Test retrieval of settings"""
        settings = self.notification_service.get_settings()
        self.assertIn('notification_provider', settings)
    
    def test_test_notification_none_provider(self):
        """Test notification with no provider"""
        result = self.notification_service.test_notification({
            'provider': 'none',
            'endpoint': ''
        })
        self.assertFalse(result['success'])
    
    def test_test_notification_invalid_provider(self):
        """Test notification with invalid provider"""
        result = self.notification_service.test_notification({
            'provider': 'invalid',
            'endpoint': ''
        })
        self.assertFalse(result['success'])

if __name__ == '__main__':
    unittest.main()
