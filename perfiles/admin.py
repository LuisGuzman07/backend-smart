from django.contrib import admin
from .models import Empleado, Cliente
from .models_device_token import DeviceToken

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

@admin.register(DeviceToken)
class DeviceTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'platform', 'is_active', 'created_at', 'token_preview')
    search_fields = ('user__username', 'user__email', 'token')
    list_filter = ('platform', 'is_active', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    
    def token_preview(self, obj):
        """Mostrar solo los primeros 30 caracteres del token"""
        return f"{obj.token[:30]}..." if obj.token else ""
    token_preview.short_description = 'Token (preview)'
