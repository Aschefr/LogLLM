import requests
import apprise
from apprise import Apprise

class NotificationService:
    def __init__(self, config_manager):
        self.config_manager = config_manager
    
    def get_settings(self):
        return self.config_manager.get_all_settings()
    
    def test_notification(self, data):
        provider = data.get('provider', 'none')
        endpoint = data.get('endpoint', '')
        
        try:
            if provider == 'discord':
                url = endpoint
                payload = {
                    "content": "🔔 LogLLM Test Notification\nThis is a test notification from LogLLM."
                }
                response = requests.post(url, json=payload, timeout=10)
                
                if response.status_code in [200, 204]:
                    return {'success': True, 'message': 'Test notification sent successfully'}
                else:
                    return {'success': False, 'message': f'Error: {response.status_code}'}
            
            elif provider == 'telegram':
                # Telegram requires bot token and chat ID
                bot_token = endpoint.split(':')[0] if ':' in endpoint else endpoint
                chat_id = endpoint.split(':')[1] if ':' in endpoint else ''
                
                if not bot_token or not chat_id:
                    return {'success': False, 'message': 'Invalid endpoint format. Use: bot_token:chat_id'}
                
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                payload = {
                    "chat_id": chat_id,
                    "text": "🔔 LogLLM Test Notification\nThis is a test notification from LogLLM."
                }
                response = requests.post(url, json=payload, timeout=10)
                
                if response.status_code == 200:
                    return {'success': True, 'message': 'Test notification sent successfully'}
                else:
                    return {'success': False, 'message': f'Error: {response.status_code}'}
            
            elif provider == 'email':
                # Email format: smtp://user:pass@smtp.server.com:port
                apobj = Apprise()
                if apobj.add(endpoint):
                    apobj.notify(
                        body="🔔 LogLLM Test Notification\nThis is a test notification from LogLLM.",
                        title="LogLLM Test"
                    )
                    return {'success': True, 'message': 'Test notification sent successfully'}
                else:
                    return {'success': False, 'message': 'Invalid email endpoint'}
            
            elif provider == 'apprise':
                # Apprise supports multiple services
                apobj = Apprise()
                if apobj.add(endpoint):
                    apobj.notify(
                        body="🔔 LogLLM Test Notification\nThis is a test notification from LogLLM.",
                        title="LogLLM Test"
                    )
                    return {'success': True, 'message': 'Test notification sent successfully'}
                else:
                    return {'success': False, 'message': 'Invalid Apprise endpoint'}
            
            else:
                return {'success': False, 'message': 'Unknown notification provider'}
        
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    def send_notification(self, title, message, settings, log_settings=None):
        provider = settings.get('notification_provider', 'none')
        
        # Check if notifications are enabled for this log
        if log_settings:
            if not log_settings.get('notifications_enabled'):
                return {'success': False, 'message': 'Notifications disabled for this log'}
        
        if provider == 'none':
            return {'success': False, 'message': 'No notification provider configured'}
        
        endpoint = settings.get('notification_endpoint', '')
        
        try:
            if provider == 'discord':
                url = endpoint
                payload = {
                    "content": f"🔔 **{title}**\n\n{message}"
                }
                response = requests.post(url, json=payload, timeout=10)
                
                if response.status_code in [200, 204]:
                    return {'success': True}
                else:
                    return {'success': False, 'message': f'Error: {response.status_code}'}
            
            elif provider == 'telegram':
                bot_token = endpoint.split(':')[0] if ':' in endpoint else endpoint
                chat_id = endpoint.split(':')[1] if ':' in endpoint else ''
                
                if not bot_token or not chat_id:
                    return {'success': False, 'message': 'Invalid endpoint format'}
                
                url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                payload = {
                    "chat_id": chat_id,
                    "text": f"🔔 **{title}**\n\n{message}",
                    "parse_mode": "Markdown"
                }
                response = requests.post(url, json=payload, timeout=10)
                
                if response.status_code == 200:
                    return {'success': True}
                else:
                    return {'success': False, 'message': f'Error: {response.status_code}'}
            
            elif provider in ['email', 'apprise']:
                apobj = Apprise()
                if apobj.add(endpoint):
                    apobj.notify(
                        body=message,
                        title=title
                    )
                    return {'success': True}
                else:
                    return {'success': False, 'message': 'Invalid endpoint'}
            
            else:
                return {'success': False, 'message': 'Unknown provider'}
        
        except Exception as e:
            return {'success': False, 'message': f'Error: {str(e)}'}
