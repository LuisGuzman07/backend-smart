from rest_framework.routers import DefaultRouter
from .views import ClienteViewSet, EmpleadoViewSet, UserRegisterView, CustomTokenObtainPairView, RoleViewSet, UserViewSet, PermissionListView
from django.urls import path, include


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
    # Endpoints JWT
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]