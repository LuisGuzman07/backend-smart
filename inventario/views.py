# Importar views desde archivos separados
from inventario.viewsCategoria import CategoriaViewSet
from inventario.viewsProducto import ProductoViewSet
from inventario.viewsCarrito import CarritoViewSet
from inventario.viewsDetalleCarrito import DetalleCarritoViewSet

# Exportar para que otros módulos puedan importar desde inventario.views
__all__ = ['CategoriaViewSet', 'ProductoViewSet', 'CarritoViewSet', 'DetalleCarritoViewSet']
