from django.contrib import admin
from .models import Reporte


@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'tipo', 'formato', 'usuario', 'fecha_generacion', 'registros_procesados', 'tiempo_generacion']
    list_filter = ['tipo', 'formato', 'fecha_generacion']
    search_fields = ['nombre', 'descripcion', 'consulta_original']
    readonly_fields = ['fecha_generacion', 'tiempo_generacion']
    ordering = ['-fecha_generacion']
    
    fieldsets = (
        ('Información General', {
            'fields': ('usuario', 'tipo', 'nombre', 'descripcion')
        }),
        ('Configuración', {
            'fields': ('consulta_original', 'formato', 'archivo')
        }),
        ('Estadísticas', {
            'fields': ('registros_procesados', 'tiempo_generacion', 'fecha_generacion')
        }),
    )
