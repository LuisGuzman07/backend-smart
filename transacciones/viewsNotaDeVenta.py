from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from transacciones.modelsNotaDeVenta import NotaDeVenta
from transacciones.serializers.serializersNotaDeVenta import NotaDeVentaSerializer, NotaDeVentaSimpleSerializer


@method_decorator(csrf_exempt, name='dispatch')
class NotaDeVentaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar las notas de venta.
    Proporciona operaciones CRUD completas para notas de venta con sus detalles.
    """
    queryset = NotaDeVenta.objects.all()
    serializer_class = NotaDeVentaSerializer
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        """Usa NotaDeVentaSimpleSerializer para listados, NotaDeVentaSerializer para detalle"""
        if self.action == 'list':
            return NotaDeVentaSimpleSerializer
        return NotaDeVentaSerializer

    def create(self, request, *args, **kwargs):
        """
        Crear una nueva nota de venta.
        El número de comprobante debe ser único.
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
        """Actualizar una nota de venta existente."""
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
    def pagar(self, request, pk=None):
        """Marca la nota de venta como pagada"""
        nota_venta = self.get_object()
        
        if nota_venta.estado == 'anulada':
            return Response(
                {"error": "No se puede pagar una nota de venta anulada"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if nota_venta.estado == 'pagada':
            return Response(
                {"message": "La nota de venta ya está pagada"},
                status=status.HTTP_200_OK
            )
        
        nota_venta.marcar_pagada()
        
        serializer = self.get_serializer(nota_venta)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def anular(self, request, pk=None):
        """Marca la nota de venta como anulada"""
        nota_venta = self.get_object()
        
        if nota_venta.estado == 'anulada':
            return Response(
                {"message": "La nota de venta ya está anulada"},
                status=status.HTTP_200_OK
            )
        
        nota_venta.anular()
        
        serializer = self.get_serializer(nota_venta)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def recalcular(self, request, pk=None):
        """Recalcula los totales de la nota de venta"""
        nota_venta = self.get_object()
        nota_venta.calcular_totales()
        
        serializer = self.get_serializer(nota_venta)
        return Response(serializer.data)

    @action(detail=False, methods=['delete'], url_path='limpiar_datos')
    def limpiar_datos_prueba(self, request):
        """
        Elimina todas las notas de venta del sistema (para pruebas/demostración).
        Debido al CASCADE, esto también eliminará:
        - Todos los detalles de nota de venta
        - Todos los pagos relacionados
        - Todo el historial de ventas relacionado
        """
        try:
            cantidad_eliminada = NotaDeVenta.objects.all().count()
            NotaDeVenta.objects.all().delete()
            
            return Response({
                "message": f"Se eliminaron {cantidad_eliminada} notas de venta y todos sus registros relacionados correctamente",
                "notas_venta_eliminadas": cantidad_eliminada
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Error al limpiar notas de venta: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['delete'], url_path='limpiar_pendientes')
    def limpiar_pendientes_sin_pago(self, request):
        """
        Elimina las notas de venta pendientes que NO tienen pago asociado.
        Estas son notas de venta que quedaron de intentos de pago fallidos.
        """
        try:
            # Obtener notas de venta pendientes sin pago
            notas_pendientes_sin_pago = NotaDeVenta.objects.filter(
                estado='pendiente',
                pago__isnull=True
            )
            
            cantidad_eliminada = notas_pendientes_sin_pago.count()
            notas_pendientes_sin_pago.delete()
            
            return Response({
                "message": f"Se eliminaron {cantidad_eliminada} notas de venta pendientes sin pago",
                "notas_eliminadas": cantidad_eliminada,
                "descripcion": "Estas eran notas de venta de intentos de pago fallidos"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Error al limpiar notas pendientes: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='desde-carrito')
    def crear_desde_carrito(self, request):
        """
        Crea una nota de venta desde un carrito.
        Recibe: carrito_id
        Crea la nota de venta con todos sus detalles y elimina el carrito.
        """
        from inventario.modelsCarrito import Carrito
        from transacciones.modelsDetalleNotaDeVenta import DetalleNotaDeVenta
        from datetime import datetime
        
        carrito_id = request.data.get('carrito_id')
        
        if not carrito_id:
            return Response(
                {"error": "Se requiere carrito_id"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Obtener el carrito con sus detalles
            carrito = Carrito.objects.prefetch_related('detalles__producto').get(id=carrito_id)
            
            if not carrito.cliente:
                return Response(
                    {"error": "El carrito no tiene un cliente asignado"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verificar que el carrito tenga items
            if carrito.detalles.count() == 0:
                return Response(
                    {"error": "El carrito está vacío"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Generar número de comprobante único
            numero_comprobante = f"NV-{int(datetime.now().timestamp())}-{carrito_id}"
            
            # Crear la nota de venta
            nota_venta = NotaDeVenta.objects.create(
                numero_comprobante=numero_comprobante,
                cliente=carrito.cliente,
                estado='pendiente'
            )
            
            # Crear los detalles de la nota de venta desde los detalles del carrito
            for detalle_carrito in carrito.detalles.all():
                DetalleNotaDeVenta.objects.create(
                    nota_venta=nota_venta,
                    producto=detalle_carrito.producto,
                    cantidad=detalle_carrito.cantidad
                )
            
            # Recalcular totales
            nota_venta.calcular_totales()
            
            # Eliminar el carrito
            carrito.delete()
            
            # Serializar la nota de venta completa
            serializer = self.get_serializer(nota_venta)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Carrito.DoesNotExist:
            return Response(
                {"error": f"No existe el carrito con ID {carrito_id}"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": f"Error al crear nota de venta: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'], url_path='marcar-pagada')
    def marcar_pagada(self, request, pk=None):
        """Alias para el método pagar() - marca la nota de venta como pagada"""
        return self.pagar(request, pk)
