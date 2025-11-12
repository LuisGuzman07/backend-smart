from rest_framework import serializers
from transacciones.modelsPago import Pago
from transacciones.modelsNotaDeVenta import NotaDeVenta


class PagoSerializer(serializers.ModelSerializer):
    # Campos de solo lectura de la nota de venta relacionada
    numero_comprobante = serializers.CharField(source='nota_venta.numero_comprobante', read_only=True)
    nota_venta_total = serializers.DecimalField(
        source='nota_venta.total', 
        read_only=True,
        max_digits=10,
        decimal_places=2
    )
    nota_venta_estado = serializers.CharField(source='nota_venta.estado', read_only=True)
    cliente_nombre = serializers.CharField(source='nota_venta.cliente.nombre', read_only=True)
    
    class Meta:
        model = Pago
        fields = [
            'nota_venta',
            'numero_comprobante',
            'fecha',
            'monto',
            'moneda',
            'total_stripe',
            'nota_venta_total',
            'nota_venta_estado',
            'cliente_nombre'
        ]
        read_only_fields = ['fecha']
    
    def validate_nota_venta(self, value):
        """Validar que la nota de venta no tenga ya un pago asociado"""
        if hasattr(value, 'pago'):
            raise serializers.ValidationError(
                f"La nota de venta {value.numero_comprobante} ya tiene un pago asociado."
            )
        
        # Validar que la nota de venta no esté anulada
        if value.estado == 'anulada':
            raise serializers.ValidationError(
                "No se puede realizar un pago para una nota de venta anulada."
            )
        
        return value
    
    def validate_monto(self, value):
        """Validar que el monto sea mayor a 0"""
        if value <= 0:
            raise serializers.ValidationError("El monto del pago debe ser mayor a 0.")
        return value
    
    def validate(self, data):
        """Validar que el monto coincida con el total de la nota de venta"""
        nota_venta = data.get('nota_venta')
        monto = data.get('monto')
        
        if nota_venta and monto:
            if monto != nota_venta.total:
                raise serializers.ValidationError({
                    'monto': f"El monto del pago ({monto}) debe coincidir con el total de la nota de venta ({nota_venta.total})."
                })
        
        return data
    
    def validate_total_stripe(self, value):
        """Validar que el ID de Stripe sea único"""
        if self.instance:  # Si es actualización
            if Pago.objects.exclude(pk=self.instance.pk).filter(total_stripe=value).exists():
                raise serializers.ValidationError("Ya existe un pago con este ID de Stripe.")
        else:  # Si es creación
            if Pago.objects.filter(total_stripe=value).exists():
                raise serializers.ValidationError("Ya existe un pago con este ID de Stripe.")
        return value


class PagoSimpleSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados o referencias anidadas"""
    numero_comprobante = serializers.CharField(source='nota_venta.numero_comprobante', read_only=True)
    
    class Meta:
        model = Pago
        fields = [
            'nota_venta',
            'numero_comprobante',
            'fecha',
            'monto',
            'moneda',
            'total_stripe'
        ]
        read_only_fields = ['fecha']


class PagoCreateSerializer(serializers.ModelSerializer):
    """Serializer específico para crear pagos desde Stripe webhook"""
    
    class Meta:
        model = Pago
        fields = [
            'nota_venta',
            'monto',
            'moneda',
            'total_stripe'
        ]
    
    def validate_nota_venta(self, value):
        """Validar que la nota de venta exista y no tenga pago"""
        if hasattr(value, 'pago'):
            raise serializers.ValidationError(
                "Esta nota de venta ya tiene un pago registrado."
            )
        return value
    
    def create(self, validated_data):
        """
        Crear el pago y automáticamente marcar la nota de venta como pagada
        (esto se hace automáticamente en el método save del modelo)
        """
        pago = Pago.objects.create(**validated_data)
        return pago
