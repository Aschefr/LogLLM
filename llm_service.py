import requests
import json
from config_manager import ConfigManager

class LLMService:
    def __init__(self, config_manager):
        self.config_manager = config_manager
    
    def get_settings(self):
        return self.config_manager.get_all_settings()
    
    def test_connection(self):
        settings = self.get_settings()
        provider = settings.get('llm_provider', 'ollama')
        endpoint = settings.get('llm_endpoint', 'http://localhost:11434')
        model = settings.get('llm_model', 'llama2')
        
        try:
            if provider == 'ollama':
                # Test Ollama API
                url = f"{endpoint}/api/generate"
                payload = {
                    "model": model,
                    "prompt": "Test",
                    "stream": False
                }
                response = requests.post(url, json=payload, timeout=10)
                
                if response.status_code == 200:
                    return {
                        'success': True,
                        'message': 'Connection successful',
                        'provider': provider
                    }
                else:
                    return {
                        'success': False,
                        'message': f'Error: {response.status_code}',
                        'provider': provider
                    }
            
            elif provider == 'localai':
                # Test LocalAI API (OpenAI compatible)
                url = f"{endpoint}/v1/chat/completions"
                payload = {
                    "model": model,
                    "messages": [{"role": "user", "content": "Test"}]
                }
                response = requests.post(url, json=payload, timeout=10)
                
                if response.status_code == 200:
                    return {
                        'success': True,
                        'message': 'Connection successful',
                        'provider': provider
                    }
                else:
                    return {
                        'success': False,
                        'message': f'Error: {response.status_code}',
                        'provider': provider
                    }
            
            else:
                return {
                    'success': False,
                    'message': 'Unknown provider',
                    'provider': provider
                }
        
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': f'Connection failed: {str(e)}',
                'provider': provider
            }
    
    def analyze_log(self, log_entry, context, settings, log_settings=None):
        provider = settings.get('llm_provider', 'ollama')
        endpoint = settings.get('llm_endpoint', 'http://localhost:11434')
        
        # Use log-specific settings if provided
        model = log_settings.get('llm_model') if log_settings and log_settings.get('llm_model') else settings.get('llm_model', 'llama2')
        system_prompt = log_settings.get('system_prompt') if log_settings and log_settings.get('system_prompt') else settings.get('system_prompt')
        user_prompt = log_settings.get('user_prompt') if log_settings and log_settings.get('user_prompt') else settings.get('default_prompt')
        
        # Build the prompt
        full_prompt = f"{user_prompt}\n\nContext (last lines before entry):\n{context}\n\nLog Entry:\n{log_entry}"
        
        try:
            if provider == 'ollama':
                url = f"{endpoint}/api/generate"
                payload = {
                    "model": model,
                    "prompt": full_prompt,
                    "system": system_prompt,
                    "stream": False
                }
                response = requests.post(url, json=payload, timeout=60)
                
                if response.status_code == 200:
                    result = response.json()
                    self.config_manager.increment_llm_usage()
                    return result.get('response', 'No response from LLM')
                else:
                    return f"Error: {response.status_code}"
            
            elif provider == 'localai':
                url = f"{endpoint}/v1/chat/completions"
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": full_prompt}
                    ]
                }
                response = requests.post(url, json=payload, timeout=60)
                
                if response.status_code == 200:
                    result = response.json()
                    self.config_manager.increment_llm_usage()
                    return result['choices'][0]['message']['content']
                else:
                    return f"Error: {response.status_code}"
            
            else:
                return "Unknown LLM provider"
        
        except requests.exceptions.RequestException as e:
            return f"Connection error: {str(e)}"
        except Exception as e:
            return f"Error: {str(e)}"
