from django.urls import path, include
from rest_framework.routers import DefaultRouter
from inventario.views import CategoriaViewSet, ProductoViewSet, CarritoViewSet, DetalleCarritoViewSet

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'carritos', CarritoViewSet, basename='carrito')
router.register(r'detalles-carrito', DetalleCarritoViewSet, basename='detalle-carrito')

urlpatterns = [
    path('', include(router.urls)),
]
