from django.db import models
from django.contrib.auth.models import User

class DeviceToken(models.Model):
    """
    Modelo para almacenar tokens FCM de dispositivos móviles
    """
    PLATFORM_CHOICES = [
        ('android', 'Android'),
        ('ios', 'iOS'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='device_tokens',
        help_text='Usuario propietario del dispositivo'
    )
    token = models.CharField(
        max_length=500, 
        unique=True,
        help_text='Token FCM del dispositivo'
    )
    platform = models.CharField(
        max_length=10, 
        choices=PLATFORM_CHOICES,
        default='android',
        help_text='Plataforma del dispositivo'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Indica si el token está activo'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha de registro del token'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Última actualización del token'
    )
    
    class Meta:
        db_table = 'device_tokens'
        verbose_name = 'Token de dispositivo'
        verbose_name_plural = 'Tokens de dispositivos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['token']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.platform} - {self.token[:20]}..."
