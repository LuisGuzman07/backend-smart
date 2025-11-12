# Imports principales
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

# Imports de Django REST Framework
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

# Imports de modelos locales
from .models import Cliente, Empleado

# Imports de serializers locales
from .serializers import ClienteSerializer, EmpleadoSerializer
from .serializers_register import UserRegistrationSerializer
from .serializers_user import serializer_user
from .serializers_rol import PermissionSerializer, RoleSerializer, GroupSerializer

# Create your views here.

# Endpoint para listar todos los permisos
class PermissionListView(APIView):
    def get(self, request):
        permissions = Permission.objects.all()
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data)

# ViewSet para el CRUD de usuario
class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all().order_by('username')
    serializer_class = serializer_user

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

# Vista personalizada para login JWT sin requerir CSRF
@method_decorator(csrf_exempt, name='dispatch')
class CustomTokenObtainPairView(TokenObtainPairView):
    pass

class ClienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Clientes.
    - Listar con filtros y búsqueda
    - Borrado lógico
    """
    queryset = Cliente.objects.filter(estado='activo').order_by('nombre', 'apellido')
    serializer_class = ClienteSerializer

    def perform_destroy(self, instance):
        instance.estado = 'inactivo'
        instance.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class EmpleadoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Empleados.
    - Listar con filtros y búsqueda
    - Borrado lógico
    """
    queryset = Empleado.objects.filter(estado='Activo').order_by('nombre', 'apellido')
    serializer_class = EmpleadoSerializer

    def create(self, request, *args, **kwargs):
        print("DEBUG - Datos recibidos:", request.data)
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("DEBUG - Errores de validación:", serializer.errors)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_destroy(self, instance):
        instance.estado = 'Inactivo'
        instance.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

# Vista para registrar usuarios
class UserRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'detail': 'Usuario creado correctamente.'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RoleViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        group = serializer.save()
        return Response(GroupSerializer(group).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        group = serializer.save()
        return Response(GroupSerializer(group).data)
