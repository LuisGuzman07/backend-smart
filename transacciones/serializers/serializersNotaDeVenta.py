from rest_framework import serializers
from transacciones.modelsNotaDeVenta import NotaDeVenta
from transacciones.serializers.serializersDetalleNotaDeVenta import DetalleNotaDeVentaSerializer


class NotaDeVentaSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    cliente_apellido = serializers.CharField(source='cliente.apellido', read_only=True)
    cliente_ci = serializers.CharField(source='cliente.ci', read_only=True)
    detalles = DetalleNotaDeVentaSerializer(many=True, read_only=True)

    class Meta:
        model = NotaDeVenta
        fields = [
            'id',
            'numero_comprobante',
            'fecha',
            'estado',
            'cliente',
            'cliente_nombre',
            'cliente_apellido',
            'cliente_ci',
            'subtotal',
            'total',
            'detalles'
        ]
        read_only_fields = ['fecha', 'subtotal', 'total']

    def validate_numero_comprobante(self, value):
        """Validar que el número de comprobante sea único"""
        if self.instance:  # Si es actualización
            if NotaDeVenta.objects.exclude(pk=self.instance.pk).filter(numero_comprobante=value).exists():
                raise serializers.ValidationError("Ya existe una nota de venta con este número de comprobante.")
        else:  # Si es creación
            if NotaDeVenta.objects.filter(numero_comprobante=value).exists():
                raise serializers.ValidationError("Ya existe una nota de venta con este número de comprobante.")
        return value


class NotaDeVentaSimpleSerializer(serializers.ModelSerializer):
    """Serializer sin detalles anidados, útil para listados"""
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    cliente_apellido = serializers.CharField(source='cliente.apellido', read_only=True)

    class Meta:
        model = NotaDeVenta
        fields = [
            'id',
            'numero_comprobante',
            'fecha',
            'estado',
            'cliente',
            'cliente_nombre',
            'cliente_apellido',
            'subtotal',
            'total'
        ]
        read_only_fields = ['fecha', 'subtotal', 'total']
