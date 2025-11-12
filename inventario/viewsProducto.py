from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import requests
from inventario.modelsProducto import Producto
from inventario.serializers.serializerProducto import ProductoSerializer


class ProductoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los productos.
    Proporciona operaciones CRUD completas con soporte para categorías e imágenes.
    """
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

    def create(self, request, *args, **kwargs):
        """
        Crear un nuevo producto con soporte para subida de imágenes.
        """
        return self.handle_image_upload(request, is_update=False)

    def update(self, request, *args, **kwargs):
        """
        Actualizar un producto existente con soporte para subida de imágenes.
        """
        return self.handle_image_upload(request, is_update=True, *args, **kwargs)

    def handle_image_upload(self, request, is_update=False, *args, **kwargs):
        """
        Maneja la lógica de subida de imágenes a ImgBB y procesamiento de datos.
        """
        # Crear una copia mutable de los datos
        data = request.data.copy()
        imagen_file = request.FILES.get("imagen")

        if imagen_file:
            # Subir imagen a ImgBB
            url = "https://api.imgbb.com/1/upload"
            payload = {"key": settings.API_KEY_IMGBB}
            files = {"image": imagen_file.read()}
            
            try:
                response = requests.post(url, data=payload, files=files)
                response.raise_for_status()  # Lanza excepción si hay error HTTP
                
                if response.status_code == 200:
                    image_url = response.json()["data"]["url"]
                    data["imagen"] = image_url
                else:
                    return Response(
                        {"error": "Error al subir imagen a ImgBB"}, 
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
            except requests.exceptions.RequestException as e:
                return Response(
                    {"error": f"Error de conexión con ImgBB: {str(e)}"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        elif is_update:
            # Si es una actualización y no hay nueva imagen, mantener la existente
            instance = self.get_object()
            if not data.get("imagen") and instance.imagen:
                data["imagen"] = instance.imagen

        # Si no se proporciona costo_promedio, usar precio_compra
        if not data.get('costo_promedio') and not is_update:
            data['costo_promedio'] = data.get('precio_compra')
        
        # Si es actualización y el precio de compra cambió, guardar el anterior
        if is_update:
            instance = self.get_object()
            if 'precio_compra' in data and data['precio_compra'] != str(instance.precio_compra):
                data['precio_compra_anterior'] = instance.precio_compra
            
            # Si no se proporciona costo_promedio, mantener el actual o usar el nuevo precio_compra
            if not data.get('costo_promedio'):
                data['costo_promedio'] = data.get('precio_compra', instance.costo_promedio)

        # Crear el serializer con los datos procesados
        if is_update:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=data, partial=kwargs.get('partial', False))
        else:
            serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED if not is_update else status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Datos inválidos", "details": serializer.errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        """
        Eliminar un producto.
        """
        instance = self.get_object()
        return super().destroy(request, *args, **kwargs)
