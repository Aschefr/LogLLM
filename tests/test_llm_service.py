import unittest
import sys
sys.path.insert(0, '/app')

from llm_service import LLMService
from config_manager import ConfigManager

class TestLLMService(unittest.TestCase):
    def setUp(self):
        self.config_manager = ConfigManager('/tmp/test_config.db')
        self.llm_service = LLMService(self.config_manager)
    
    def test_get_settings(self):
        """Test retrieval of settings"""
        settings = self.llm_service.get_settings()
        self.assertIn('llm_provider', settings)
        self.assertIn('llm_endpoint', settings)
    
    def test_analyze_log_format(self):
        """Test that analyze_log returns a string"""
        settings = self.llm_service.get_settings()
        result = self.llm_service.analyze_log(
            "Test error message",
            "Test context",
            settings
        )
        self.assertIsInstance(result, str)

if __name__ == '__main__':
    unittest.main()
