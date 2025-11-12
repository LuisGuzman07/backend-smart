from rest_framework import viewsets
from inventario.modelsCategoria import Categoria
from inventario.serializers.serializerCategoria import CategoriaSerializer


class CategoriaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar las categorías de productos.
    Proporciona operaciones CRUD completas.
    """
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
