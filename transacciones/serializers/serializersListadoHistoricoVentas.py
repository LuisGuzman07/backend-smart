from rest_framework import serializers
from transacciones.modelsListadoHistoricoVentas import ListadoHistoricoVentas
from transacciones.modelsNotaDeVenta import NotaDeVenta
from transacciones.modelsPago import Pago


class ListadoHistoricoVentasSerializer(serializers.ModelSerializer):
    """
    Serializer completo para el Listado Histórico de Ventas.
    Incluye toda la información necesaria para visualizar el historial.
    """
    
    # Campos calculados o derivados
    cantidad_items = serializers.SerializerMethodField()
    ganancia_neta = serializers.SerializerMethodField()
    dias_desde_venta = serializers.SerializerMethodField()
    estado_nota_venta = serializers.CharField(source='nota_venta.estado', read_only=True)
    
    class Meta:
        model = ListadoHistoricoVentas
        fields = [
            'nota_venta',
            'cliente_nombre',
            'cliente_ci',
            'cliente_email',
            'numero_venta',
            'fecha_venta',
            'subtotal',
            'total',
            'metodo_pago',
            'estado_pago',
            'fecha_pago',
            'referencia_pago',
            'cantidad_items',
            'notas',
            'fecha_registro',
            'fecha_actualizacion',
            'ganancia_neta',
            'dias_desde_venta',
            'estado_nota_venta',
        ]
        read_only_fields = [
            'fecha_registro',
            'fecha_actualizacion',
            'cantidad_items',
            'ganancia_neta',
            'dias_desde_venta',
        ]
    
    def get_cantidad_items(self, obj):
        """Obtiene la cantidad de items de la venta"""
        return obj.get_cantidad_items()
    
    def get_ganancia_neta(self, obj):
        """Calcula la ganancia neta de la venta"""
        return obj.calcular_ganancia_neta()
    
    def get_dias_desde_venta(self, obj):
        """Calcula cuántos días han pasado desde la venta"""
        from django.utils import timezone
        if obj.fecha_venta:
            delta = timezone.now() - obj.fecha_venta
            return delta.days
        return None


class ListadoHistoricoVentasSimpleSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listados rápidos.
    Solo incluye los campos esenciales.
    """
    
    cantidad_items = serializers.SerializerMethodField()
    
    class Meta:
        model = ListadoHistoricoVentas
        fields = [
            'nota_venta',
            'numero_venta',
            'cliente_nombre',
            'fecha_venta',
            'total',
            'estado_pago',
            'metodo_pago',
            'cantidad_items',
        ]
    
    def get_cantidad_items(self, obj):
        """Obtiene la cantidad de items de la venta"""
        return obj.get_cantidad_items()


class ListadoHistoricoVentasDetalleSerializer(serializers.ModelSerializer):
    """
    Serializer detallado que incluye información de productos vendidos.
    """
    
    # Información de la nota de venta
    nota_venta_info = serializers.SerializerMethodField()
    
    # Información del pago
    pago_info = serializers.SerializerMethodField()
    
    # Detalles de productos
    productos_vendidos = serializers.SerializerMethodField()
    
    # Campos calculados
    ganancia_neta = serializers.SerializerMethodField()
    
    class Meta:
        model = ListadoHistoricoVentas
        fields = [
            'nota_venta',
            'cliente_nombre',
            'cliente_ci',
            'cliente_email',
            'numero_venta',
            'fecha_venta',
            'subtotal',
            'total',
            'metodo_pago',
            'estado_pago',
            'fecha_pago',
            'referencia_pago',
            'notas',
            'nota_venta_info',
            'pago_info',
            'productos_vendidos',
            'ganancia_neta',
        ]
    
    def get_nota_venta_info(self, obj):
        """Obtiene información detallada de la nota de venta"""
        if obj.nota_venta:
            return {
                'id': obj.nota_venta.id,
                'numero_comprobante': obj.nota_venta.numero_comprobante,
                'estado': obj.nota_venta.estado,
                'fecha': obj.nota_venta.fecha,
                'cliente': {
                    'id': obj.nota_venta.cliente.id,
                    'nombre': f"{obj.nota_venta.cliente.nombre} {obj.nota_venta.cliente.apellido}",
                    'ci': obj.nota_venta.cliente.ci,
                }
            }
        return None
    
    def get_pago_info(self, obj):
        """Obtiene información del pago si existe"""
        if obj.nota_venta and hasattr(obj.nota_venta, 'pago'):
            pago = obj.nota_venta.pago
            return {
                'fecha': pago.fecha,
                'monto': str(pago.monto),
                'moneda': pago.moneda,
                'stripe_id': pago.total_stripe,
            }
        return None
    
    def get_productos_vendidos(self, obj):
        """Obtiene la lista de productos vendidos en esta venta"""
        detalles = obj.get_detalles_productos()
        productos = []
        
        for detalle in detalles:
            # Calcular precio unitario desde el subtotal
            precio_unitario = 0
            if detalle.cantidad > 0:
                precio_unitario = float(detalle.subtotal) / detalle.cantidad
            
            productos.append({
                'producto_id': detalle.producto.id,
                'producto_nombre': detalle.producto.nombre,
                'producto_codigo': detalle.codigo or detalle.producto.codigo,
                'cantidad': detalle.cantidad,
                'precio_unitario': str(round(precio_unitario, 2)),
                'subtotal': str(detalle.subtotal),
                'total': str(detalle.total),
            })
        
        return productos
    
    def get_ganancia_neta(self, obj):
        """Calcula la ganancia neta"""
        return str(obj.calcular_ganancia_neta())


class EstadisticasVentasSerializer(serializers.Serializer):
    """
    Serializer para las estadísticas de ventas.
    No está vinculado a un modelo, solo para serializar datos calculados.
    """
    
    total_ventas = serializers.IntegerField()
    total_ingresos = serializers.DecimalField(max_digits=12, decimal_places=2)
    ventas_completadas = serializers.IntegerField()
    ventas_pendientes = serializers.IntegerField()
    
    # Campos opcionales calculados
    ingreso_promedio = serializers.SerializerMethodField()
    tasa_completacion = serializers.SerializerMethodField()
    
    def get_ingreso_promedio(self, obj):
        """Calcula el ingreso promedio por venta"""
        total_ventas = obj.get('total_ventas', 0)
        total_ingresos = obj.get('total_ingresos', 0)
        
        if total_ventas and total_ventas > 0:
            return round(float(total_ingresos) / total_ventas, 2)
        return 0.00
    
    def get_tasa_completacion(self, obj):
        """Calcula el porcentaje de ventas completadas"""
        total_ventas = obj.get('total_ventas', 0)
        ventas_completadas = obj.get('ventas_completadas', 0)
        
        if total_ventas and total_ventas > 0:
            return round((ventas_completadas / total_ventas) * 100, 2)
        return 0.00


class CrearHistorialVentaSerializer(serializers.Serializer):
    """
    Serializer para crear un registro en el historial desde una nota de venta.
    """
    
    nota_venta_id = serializers.IntegerField(
        help_text="ID de la nota de venta para crear el registro histórico"
    )
    
    def validate_nota_venta_id(self, value):
        """Validar que la nota de venta exista"""
        try:
            NotaDeVenta.objects.get(id=value)
        except NotaDeVenta.DoesNotExist:
            raise serializers.ValidationError(
                f"No existe una nota de venta con ID {value}"
            )
        return value
    
    def create(self, validated_data):
        """
        Crea el registro histórico desde la nota de venta
        """
        nota_venta_id = validated_data['nota_venta_id']
        nota_venta = NotaDeVenta.objects.get(id=nota_venta_id)
        historial = ListadoHistoricoVentas.crear_desde_nota_venta(nota_venta)
        return historial


class ActualizarEstadoPagoSerializer(serializers.Serializer):
    """
    Serializer para actualizar el estado de pago de una venta
    """
    
    estado_pago = serializers.ChoiceField(
        choices=[
            ('pendiente', 'Pendiente'),
            ('completado', 'Completado'),
            ('fallido', 'Fallido'),
            ('anulado', 'Anulado'),
        ],
        help_text="Nuevo estado del pago"
    )
    
    def update(self, instance, validated_data):
        """
        Actualiza el estado de pago
        """
        instance.estado_pago = validated_data['estado_pago']
        instance.save()
        return instance
