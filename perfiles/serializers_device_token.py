from rest_framework import serializers
from .models_device_token import DeviceToken


class DeviceTokenSerializer(serializers.ModelSerializer):
    """
    Serializer para tokens FCM de dispositivos
    """
    class Meta:
        model = DeviceToken
        fields = ['id', 'token', 'platform', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """
        Crear o actualizar token FCM
        Si el token ya existe, lo actualiza y lo marca como activo
        """
        user = self.context['request'].user
        token = validated_data.get('token')
        
        # Buscar si el token ya existe
        device_token, created = DeviceToken.objects.update_or_create(
            token=token,
            defaults={
                'user': user,
                'platform': validated_data.get('platform', 'android'),
                'is_active': True
            }
        )
        
        return device_token
