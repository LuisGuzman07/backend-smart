from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from inventario.modelsCarrito import Carrito
from inventario.serializers.serializerCarrito import CarritoSerializer, CarritoSimpleSerializer


class CarritoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los carritos de compra.
    Proporciona operaciones CRUD completas con soporte para múltiples carritos por cliente.
    """
    queryset = Carrito.objects.all()
    serializer_class = CarritoSerializer

    def get_serializer_class(self):
        """Usa CarritoSimpleSerializer para listados, CarritoSerializer para detalle"""
        if self.action == 'list':
            return CarritoSimpleSerializer
        return CarritoSerializer

    def create(self, request, *args, **kwargs):
        """
        Crear un nuevo carrito.
        El cliente puede tener múltiples carritos (uno activo y otros completados/abandonados).
        """
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"error": "Datos inválidos", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        """Actualizar un carrito existente."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Datos inválidos", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def completar(self, request, pk=None):
        """Marca el carrito como completado"""
        carrito = self.get_object()
        
        if carrito.esta_vacio():
            return Response(
                {"error": "No se puede completar un carrito vacío"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        carrito.estado = 'completado'
        carrito.save()
        
        serializer = self.get_serializer(carrito)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def abandonar(self, request, pk=None):
        """Marca el carrito como abandonado"""
        carrito = self.get_object()
        carrito.estado = 'abandonado'
        carrito.save()
        
        serializer = self.get_serializer(carrito)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def limpiar_carritos_activos(self, request):
        """
        Limpia (elimina) todos los carritos activos sin nota de venta asociada.
        Útil para limpiar carritos huérfanos de compras fallidas.
        """
        from transacciones.modelsNotaDeVenta import NotaDeVenta
        
        # Obtener IDs de carritos que tienen notas de venta asociadas
        carritos_con_notas = NotaDeVenta.objects.values_list('id', flat=True)
        
        # Eliminar carritos activos que no tienen nota de venta
        carritos_a_eliminar = Carrito.objects.filter(estado='activo').exclude(id__in=carritos_con_notas)
        count = carritos_a_eliminar.count()
        carritos_a_eliminar.delete()
        
        return Response({
            "mensaje": f"Se eliminaron {count} carritos activos sin nota de venta asociada",
            "eliminados": count
        }, status=status.HTTP_200_OK)
