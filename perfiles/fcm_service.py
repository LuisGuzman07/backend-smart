"""
Helper para enviar notificaciones push usando Firebase Cloud Messaging (FCM)
"""
import json
import logging
import requests
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from django.conf import settings

logger = logging.getLogger(__name__)


class FCMService:
    """
    Servicio para enviar notificaciones push mediante Firebase Cloud Messaging
    """
    
    # Alcances necesarios para FCM
    SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']
    
    def __init__(self):
        """
        Inicializa el servicio FCM con las credenciales de Firebase
        """
        self.project_id = getattr(settings, 'FIREBASE_PROJECT_ID', None)
        self.service_account_json = getattr(settings, 'FIREBASE_SERVICE_ACCOUNT_JSON', None)
        
        if not self.project_id or not self.service_account_json:
            logger.error("Firebase credentials not configured in settings")
            self.credentials = None
        else:
            try:
                # Cargar credenciales desde JSON
                service_account_info = json.loads(self.service_account_json)
                self.credentials = service_account.Credentials.from_service_account_info(
                    service_account_info,
                    scopes=self.SCOPES
                )
            except Exception as e:
                logger.error(f"Error loading Firebase credentials: {e}")
                self.credentials = None
    
    def _get_access_token(self):
        """
        Obtiene el access token de Google para FCM
        
        Returns:
            str: Access token
        """
        if not self.credentials:
            raise ValueError("Firebase credentials not configured")
        
        # Refrescar el token si es necesario
        if not self.credentials.valid:
            self.credentials.refresh(Request())
        
        return self.credentials.token
    
    def send_push_notification(self, token, title, body, data=None):
        """
        Envía una notificación push a un token FCM específico
        
        Args:
            token (str): Token FCM del dispositivo
            title (str): Título de la notificación
            body (str): Cuerpo del mensaje
            data (dict): Datos adicionales (opcional)
        
        Returns:
            dict: Respuesta de FCM
        """
        if not self.credentials:
            logger.error("Cannot send notification: Firebase not configured")
            return {
                'success': False,
                'error': 'Firebase not configured'
            }
        
        try:
            access_token = self._get_access_token()
            
            # URL del endpoint de FCM
            url = f'https://fcm.googleapis.com/v1/projects/{self.project_id}/messages:send'
            
            # Headers
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json; UTF-8',
            }
            
            # Construir el mensaje
            message = {
                'message': {
                    'token': token,
                    'notification': {
                        'title': title,
                        'body': body,
                    },
                }
            }
            
            # Agregar datos adicionales si existen
            if data:
                message['message']['data'] = data
            
            # Enviar la notificación
            response = requests.post(url, headers=headers, json=message, timeout=10)
            
            if response.status_code == 200:
                logger.info(f"Push notification sent successfully to token: {token[:20]}...")
                return {
                    'success': True,
                    'message_id': response.json().get('name')
                }
            else:
                logger.error(f"FCM Error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': response.text
                }
        
        except Exception as e:
            logger.error(f"Error sending push notification: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_push_to_user(self, user, title, body, data=None):
        """
        Envía notificación push a todos los dispositivos activos de un usuario
        
        Args:
            user: Instancia del modelo User
            title (str): Título de la notificación
            body (str): Cuerpo del mensaje
            data (dict): Datos adicionales (opcional)
        
        Returns:
            dict: Resumen del envío
        """
        from perfiles.models_device_token import DeviceToken
        
        # Obtener todos los tokens activos del usuario
        tokens = DeviceToken.objects.filter(user=user, is_active=True)
        
        if not tokens.exists():
            logger.info(f"No active tokens found for user: {user.username}")
            return {
                'success': False,
                'message': 'No active tokens found'
            }
        
        results = {
            'total': tokens.count(),
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        # Enviar a cada token
        for device_token in tokens:
            result = self.send_push_notification(
                token=device_token.token,
                title=title,
                body=body,
                data=data
            )
            
            if result['success']:
                results['successful'] += 1
            else:
                results['failed'] += 1
                results['errors'].append({
                    'token': device_token.token[:20] + '...',
                    'error': result.get('error', 'Unknown error')
                })
                
                # Si el token es inválido, marcarlo como inactivo
                if 'NOT_FOUND' in str(result.get('error', '')) or \
                   'UNREGISTERED' in str(result.get('error', '')):
                    device_token.is_active = False
                    device_token.save()
                    logger.info(f"Token marked as inactive: {device_token.token[:20]}...")
        
        logger.info(f"Push notifications sent to user {user.username}: "
                   f"{results['successful']} successful, {results['failed']} failed")
        
        return results


# Instancia global del servicio
fcm_service = FCMService()


# Funciones de conveniencia
def send_push_to_token(token, title, body, data=None):
    """
    Función helper para enviar notificación a un token específico
    """
    return fcm_service.send_push_notification(token, title, body, data)


def send_push_to_user(user, title, body, data=None):
    """
    Función helper para enviar notificación a un usuario
    """
    return fcm_service.send_push_to_user(user, title, body, data)
