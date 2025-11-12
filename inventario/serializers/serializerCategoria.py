from rest_framework import serializers
from inventario.modelsCategoria import Categoria


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'
