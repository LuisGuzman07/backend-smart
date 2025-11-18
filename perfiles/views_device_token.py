from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from .models_device_token import DeviceToken
from .serializers_device_token import DeviceTokenSerializer


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def register_device_token(request):
    """
    Registrar token FCM de un dispositivo
    
    Body:
    {
        "token": "FCM_TOKEN_STRING",
        "platform": "android" // o "ios"
    }
    """
    token = request.data.get('token')
    platform = request.data.get('platform', 'android')
    
    if not token:
        return Response({
            'message': 'Token es requerido'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Usar update_or_create para evitar error de token duplicado
    device_token, created = DeviceToken.objects.update_or_create(
        token=token,
        defaults={
            'user': request.user,
            'platform': platform,
            'is_active': True
        }
    )
    
    serializer = DeviceTokenSerializer(device_token)
    
    return Response({
        'message': 'Token registrado exitosamente' if created else 'Token actualizado exitosamente',
        'data': serializer.data
    }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unregister_device_token(request):
    """
    Desactivar token FCM de un dispositivo
    
    Body:
    {
        "token": "FCM_TOKEN_STRING"
    }
    """
    token = request.data.get('token')
    
    if not token:
        return Response({
            'message': 'Token es requerido'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        device_token = DeviceToken.objects.get(
            token=token,
            user=request.user
        )
        device_token.is_active = False
        device_token.save()
        
        return Response({
            'message': 'Token desactivado exitosamente'
        }, status=status.HTTP_200_OK)
    
    except DeviceToken.DoesNotExist:
        return Response({
            'message': 'Token no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_device_tokens(request):
    """
    Listar todos los tokens del usuario actual
    """
    tokens = DeviceToken.objects.filter(user=request.user)
    serializer = DeviceTokenSerializer(tokens, many=True)
    
    return Response({
        'count': tokens.count(),
        'data': serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_device_token(request, token_id):
    """
    Eliminar permanentemente un token
    """
    try:
        device_token = DeviceToken.objects.get(
            id=token_id,
            user=request.user
        )
        device_token.delete()
        
        return Response({
            'message': 'Token eliminado exitosamente'
        }, status=status.HTTP_200_OK)
    
    except DeviceToken.DoesNotExist:
        return Response({
            'message': 'Token no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
