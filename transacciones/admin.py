from django.contrib import admin
from .modelsNotaDeVenta import NotaDeVenta
from .modelsDetalleNotaDeVenta import DetalleNotaDeVenta
from .modelsPago import Pago
from .modelsListadoHistoricoVentas import ListadoHistoricoVentas


@admin.register(NotaDeVenta)
class NotaDeVentaAdmin(admin.ModelAdmin):
    list_display = ['numero_comprobante', 'cliente', 'fecha', 'total', 'estado']
    list_filter = ['estado', 'fecha']
    search_fields = ['numero_comprobante', 'cliente__nombre']


@admin.register(DetalleNotaDeVenta)
class DetalleNotaDeVentaAdmin(admin.ModelAdmin):
    list_display = ['nota_venta', 'producto', 'cantidad', 'subtotal', 'total']
    list_filter = ['nota_venta']


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ['nota_venta', 'fecha', 'monto', 'moneda', 'total_stripe']
    list_filter = ['fecha', 'moneda']
    search_fields = ['total_stripe', 'nota_venta__numero_comprobante']
    readonly_fields = ['fecha']


@admin.register(ListadoHistoricoVentas)
class ListadoHistoricoVentasAdmin(admin.ModelAdmin):
    list_display = ['numero_venta', 'cliente_nombre', 'cliente_ci', 'fecha_venta', 'total', 'estado_pago', 'metodo_pago']
    list_filter = ['estado_pago', 'metodo_pago', 'fecha_venta']
    search_fields = ['numero_venta', 'cliente_nombre', 'cliente_ci', 'referencia_pago']
    readonly_fields = ['fecha_registro', 'fecha_actualizacion']
    date_hierarchy = 'fecha_venta'
    
    fieldsets = (
        ('Información de la Venta', {
            'fields': ('nota_venta', 'numero_venta', 'fecha_venta')
        }),
        ('Información del Cliente', {
            'fields': ('cliente_nombre', 'cliente_ci', 'cliente_email')
        }),
        ('Montos', {
            'fields': ('subtotal', 'total')
        }),
        ('Información del Pago', {
            'fields': ('metodo_pago', 'estado_pago', 'fecha_pago', 'referencia_pago')
        }),
        ('Adicional', {
            'fields': ('notas',)
        }),
        ('Auditoría', {
            'fields': ('fecha_registro', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )

