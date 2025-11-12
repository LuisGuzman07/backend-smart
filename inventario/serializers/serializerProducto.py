from rest_framework import serializers
from inventario.modelsProducto import Producto


class ProductoSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Producto
        fields = [
            'id', 'codigo', 'nombre', 'descripcion', 'precio_compra',
            'precio_compra_anterior', 'precio_venta', 'costo_promedio',
            'fecha_creacion', 'stock', 'imagen', 'categoria', 'categoria_nombre'
        ]

    def get_categoria_nombre(self, obj):
        return obj.categoria.nombre if obj.categoria else None
