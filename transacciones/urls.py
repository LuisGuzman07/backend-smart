from django.urls import path, include
from rest_framework.routers import DefaultRouter
from transacciones.viewsNotaDeVenta import NotaDeVentaViewSet
from transacciones.viewsDetalleNotaDeVenta import DetalleNotaDeVentaViewSet
from transacciones.viewsPago import PagoViewSet
from transacciones.viewsListadohistoricoVentas import ListadoHistoricoVentasViewSet

router = DefaultRouter()
router.register(r'nota-venta', NotaDeVentaViewSet, basename='nota-venta')
router.register(r'detalle-nota-venta', DetalleNotaDeVentaViewSet, basename='detalle-nota-venta')
router.register(r'pagos', PagoViewSet, basename='pago')
router.register(r'historial-ventas', ListadoHistoricoVentasViewSet, basename='historial-ventas')

urlpatterns = [
    path('', include(router.urls)),
]
