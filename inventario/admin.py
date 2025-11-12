from django.contrib import admin
from inventario.models import Categoria, Producto, Carrito, DetalleCarrito


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion')
    search_fields = ('nombre',)
    ordering = ('nombre',)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'categoria', 'precio_compra', 'precio_venta', 'stock', 'fecha_creacion')
    list_filter = ('categoria', 'fecha_creacion')
    search_fields = ('codigo', 'nombre', 'descripcion')
    readonly_fields = ('fecha_creacion',)
    ordering = ('-fecha_creacion',)
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('codigo', 'nombre', 'descripcion', 'categoria', 'imagen')
        }),
        ('Precios', {
            'fields': ('precio_compra', 'precio_compra_anterior', 'precio_venta', 'costo_promedio')
        }),
        ('Inventario', {
            'fields': ('stock', 'fecha_creacion')
        }),
    )


@admin.register(Carrito)
class CarritoAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo', 'estado', 'cliente', 'fecha_creacion', 'fecha_actualizacion')
    list_filter = ('estado', 'fecha_creacion')
    search_fields = ('codigo', 'cliente__nombre', 'cliente__apellido')
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')
    ordering = ('-fecha_actualizacion',)


@admin.register(DetalleCarrito)
class DetalleCarritoAdmin(admin.ModelAdmin):
    list_display = ('id', 'carrito', 'producto', 'cantidad', 'precio_unitario', 'get_subtotal')
    list_filter = ('carrito__estado',)
    search_fields = ('producto__nombre', 'carrito__codigo')
    readonly_fields = ('get_subtotal',)
    ordering = ('-id',)
    
    def get_subtotal(self, obj):
        """Calcula el subtotal, maneja el caso cuando precio_unitario es None"""
        if obj.precio_unitario is None:
            return "N/A"
        return obj.subtotal
    get_subtotal.short_description = 'Subtotal'
    
    def save_model(self, request, obj, form, change):
        """Asegura que el precio_unitario se asigne antes de guardar"""
        if not obj.precio_unitario and obj.producto:
            obj.precio_unitario = obj.producto.precio_venta
        super().save_model(request, obj, form, change)
