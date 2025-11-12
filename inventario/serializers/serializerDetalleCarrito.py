from rest_framework import serializers
from inventario.modelsDetalleCarrito import DetalleCarrito


class DetalleCarritoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    producto_codigo = serializers.CharField(source='producto.codigo', read_only=True)
    producto_imagen = serializers.URLField(source='producto.imagen', read_only=True)
    carrito_codigo = serializers.CharField(source='carrito.codigo', read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = DetalleCarrito
        fields = [
            'id', 
            'carrito', 
            'carrito_codigo',
            'producto', 
            'producto_nombre',
            'producto_codigo',
            'producto_imagen',
            'cantidad', 
            'precio_unitario',
            'subtotal'
        ]
        read_only_fields = ['subtotal', 'precio_unitario']

    def validate(self, data):
        """Validación adicional en el serializer"""
        producto = data.get('producto')
        cantidad = data.get('cantidad', 1)

        # Validar stock disponible
        if producto and cantidad > producto.stock:
            raise serializers.ValidationError(
                f"Stock insuficiente para {producto.nombre}. Solo hay {producto.stock} unidades disponibles."
            )

        # Validar cantidad mínima
        if cantidad <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor a 0.")

        return data
