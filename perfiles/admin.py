from django.contrib import admin
from .models import Empleado, Cliente

@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'apellido', 'ci', 'cargo', 'estado', 'usuario')
    search_fields = ('nombre', 'apellido', 'ci')
    list_filter = ('cargo', 'estado')

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'apellido', 'ci', 'estado', 'sexo', 'telefono', 'usuario')
    search_fields = ('nombre', 'apellido', 'ci', 'telefono')
    list_filter = ('estado', 'sexo')
