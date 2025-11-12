from rest_framework import viewsets, status
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from inventario.modelsDetalleCarrito import DetalleCarrito
from inventario.serializers.serializerDetalleCarrito import DetalleCarritoSerializer


class DetalleCarritoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los detalles de carrito.
    Permite agregar, actualizar cantidad y eliminar productos del carrito.
    Valida stock automáticamente.
    """
    queryset = DetalleCarrito.objects.all()
    serializer_class = DetalleCarritoSerializer

    def create(self, request, *args, **kwargs):
        """
        Agregar un producto al carrito.
        Si el producto ya existe en el carrito, suma la cantidad.
        """
        carrito_id = request.data.get('carrito')
        producto_id = request.data.get('producto')
        cantidad = int(request.data.get('cantidad', 1))

        try:
            # Verificar si el producto ya existe en el carrito
            detalle_existente = DetalleCarrito.objects.filter(
                carrito_id=carrito_id,
                producto_id=producto_id
            ).first()

            if detalle_existente:
                # Si existe, actualizar la cantidad
                nueva_cantidad = detalle_existente.cantidad + cantidad
                detalle_existente.cantidad = nueva_cantidad
                detalle_existente.save()
                
                serializer = self.get_serializer(detalle_existente)
                return Response(
                    {
                        "message": "Cantidad actualizada",
                        "data": serializer.data
                    },
                    status=status.HTTP_200_OK
                )
            else:
                # Si no existe, crear nuevo detalle
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
        Actualizar cantidad de un producto en el carrito.
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
        Eliminar un producto del carrito.
        """
        instance = self.get_object()
        instance.delete()
        return Response(
            {"message": "Producto eliminado del carrito"},
            status=status.HTTP_204_NO_CONTENT
        )
