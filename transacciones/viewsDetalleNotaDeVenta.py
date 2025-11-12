from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.exceptions import ValidationError
from transacciones.modelsDetalleNotaDeVenta import DetalleNotaDeVenta
from transacciones.serializers.serializersDetalleNotaDeVenta import DetalleNotaDeVentaSerializer


class DetalleNotaDeVentaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los detalles de nota de venta.
    Permite agregar, actualizar y eliminar productos de una nota de venta.
    Valida stock automáticamente y recalcula totales.
    """
    queryset = DetalleNotaDeVenta.objects.all()
    serializer_class = DetalleNotaDeVentaSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """
        Filtrar detalles por nota de venta si se proporciona el parámetro
        """
        queryset = super().get_queryset()
        nota_venta_id = self.request.query_params.get('nota_venta', None)
        
        if nota_venta_id:
            queryset = queryset.filter(nota_venta_id=nota_venta_id)
        
        return queryset

    def create(self, request, *args, **kwargs):
        """
        Agregar un producto a la nota de venta.
        Valida stock y calcula totales automáticamente.
        """
        try:
            serializer = self.get_serializer(data=request.data)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"error": "Datos inválidos", "details": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Error al agregar producto: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def update(self, request, *args, **kwargs):
        """
        Actualizar cantidad de un producto en la nota de venta.
        """
        try:
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
        
        except ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        """
        Eliminar un producto de la nota de venta.
        Recalcula automáticamente los totales de la nota de venta.
        """
        instance = self.get_object()
        instance.delete()
        return Response(
            {"message": "Producto eliminado de la nota de venta"},
            status=status.HTTP_204_NO_CONTENT
        )

    def list(self, request, *args, **kwargs):
        """
        Listar detalles con filtrado por nota_venta
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        # Log para debug
        nota_venta_id = request.query_params.get('nota_venta', None)
        if nota_venta_id:
            print(f"📋 Filtrando detalles para nota_venta_id: {nota_venta_id}")
            print(f"📦 Detalles encontrados: {queryset.count()}")
        
        return Response(serializer.data)
