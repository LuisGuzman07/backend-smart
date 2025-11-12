from django.db import models
from django.conf import settings

class Empleado(models.Model):

    ci = models.CharField(max_length=20, unique=True, blank=True, null=True) 
    nombre = models.CharField(max_length=150)
    apellido = models.CharField(max_length=150, blank=True, null=True)
    SEXO_CHOICES = [
    ('M', 'Masculino'),
    ('F', 'Femenino'),
    ]
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    direccion = models.TextField(blank=True, null=True)   
    ESTADO_CHOICES = [
    ('Activo', 'Activo'),
    ('Inactivo', 'Inactivo'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='Activo')
    fecha_nacimiento = models.DateField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    CARGOS = (
        ('GESTOR_PEDIDOS', 'Gestor de Pedidos'),
        ('ANALISTA_NEGOCIO', 'Analista de Negocio'),
    )
    cargo = models.CharField(max_length=50, choices=CARGOS, default='GESTOR_PEDIDOS') 
    # nombre y email ya están en User
    sueldo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)

      # Relación 1-a-1: Un empleado es un usuario de Django
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.get_cargo_display()})"




# Modelo para los clientes (usuarios finales de la tienda online)
class Cliente(models.Model):
    
    nombre = models.CharField(max_length=150)
    apellido = models.CharField(max_length=150, blank=True, null=True)
    ci = models.CharField(max_length=20, unique=True, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    estado = models.CharField(max_length=50, default='activo')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    SEXO_CHOICES = [
    ('M', 'Masculino'),
    ('F', 'Femenino'),
    ]
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    # nombre ya está en User
    telefono = models.CharField(max_length=20, blank=True, null=True)
    # Relación 1-a-1: Un cliente es un usuario de Django
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return f"{self.nombre} {self.apellido}"