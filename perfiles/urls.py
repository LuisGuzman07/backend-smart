from rest_framework.routers import DefaultRouter
from .views import ClienteViewSet, EmpleadoViewSet, UserRegisterView, CustomTokenObtainPairView, RoleViewSet, UserViewSet, PermissionListView, MeView
from .views_device_token import register_device_token, unregister_device_token, list_device_tokens, delete_device_token
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt


# Importa las vistas JWT
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

router = DefaultRouter()
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'empleados', EmpleadoViewSet, basename='empleado')
router.register(r'roles', RoleViewSet, basename='rol')
router.register(r'usuarios', UserViewSet, basename='usuario')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('permissions/', PermissionListView.as_view(), name='permissions'),
    path('me/', MeView.as_view(), name='me'),
    # Endpoints JWT
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    # Endpoints para tokens de dispositivos FCM
    path('device-tokens/', csrf_exempt(register_device_token), name='register_device_token'),
    path('device-tokens/unregister/', csrf_exempt(unregister_device_token), name='unregister_device_token'),
    path('device-tokens/list/', list_device_tokens, name='list_device_tokens'),
    path('device-tokens/<int:token_id>/', delete_device_token, name='delete_device_token'),
]