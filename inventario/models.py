# Importar modelos desde archivos separados
from inventario.modelsCategoria import Categoria
from inventario.modelsProducto import Producto
from inventario.modelsCarrito import Carrito
from inventario.modelsDetalleCarrito import DetalleCarrito

# Exportar para que otros módulos puedan importar desde inventario.models
__all__ = ['Categoria', 'Producto', 'Carrito', 'DetalleCarrito']
