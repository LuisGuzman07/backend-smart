"""
Configuración de reportes estáticos disponibles
Define qué reportes se pueden generar y qué datos necesitan
"""

REPORTES_ESTATICOS = {
    'ventas_estado': {
        'nombre': 'Ventas por Estado',
        'descripcion': 'Lista de todas las ventas agrupadas por estado',
        'modelo': 'transacciones.NotaDeVenta',
        'campos': [
            'id', 
            'numero_comprobante',
            'fecha', 
            'estado',
            'cliente__nombre', 
            'cliente__apellido',
            'cliente__ci',
            'subtotal',
            'total'
        ],
        'filtros_default': {}
    },
    
    'ventas_mes': {
        'nombre': 'Ventas del Mes Actual',
        'descripcion': 'Todas las ventas realizadas en el mes actual',
        'modelo': 'transacciones.NotaDeVenta',
        'campos': [
            'id',
            'numero_comprobante',
            'fecha',
            'estado',
            'cliente__nombre',
            'cliente__apellido',
            'subtotal',
            'total',
        ],
        'filtros_default': {
            'fecha__month': 'mes_actual',
            'fecha__year': 'anio_actual'
        }
    },
    
    'productos_stock_bajo': {
        'nombre': 'Productos con Stock Bajo',
        'descripcion': 'Productos que requieren reabastecimiento (stock < 10)',
        'modelo': 'inventario.Producto',
        'campos': [
            'id',
            'codigo',
            'nombre',
            'stock',
            'precio_compra',
            'precio_venta',
            'categoria__nombre',
        ],
        'filtros_default': {
            'stock__lt': 10
        }
    },
    
    'ventas_por_cliente': {
        'nombre': 'Resumen de Ventas por Cliente',
        'descripcion': 'Análisis de ventas agrupadas por cliente',
        'modelo': 'transacciones.NotaDeVenta',
        'campos': [
            'cliente__nombre',
            'cliente__apellido',
            'cliente__ci',
            'numero_comprobante',
            'fecha',
            'total',
        ],
        'filtros_default': {
            'estado': 'pagada'
        }
    },
    
    'productos_mas_vendidos': {
        'nombre': 'Productos Más Vendidos',
        'descripcion': 'Top de productos con mayores ventas',
        'modelo': 'inventario.Producto',
        'campos': [
            'id',
            'codigo',
            'nombre',
            'precio_venta',
            'stock',
            'categoria__nombre',
        ],
        'filtros_default': {}
    },
}


def obtener_config_reporte(tipo_reporte):
    """
    Obtiene la configuración de un reporte estático
    
    Args:
        tipo_reporte: Clave del reporte (ej: 'ventas_estado')
    
    Returns:
        Dict con la configuración o None si no existe
    """
    return REPORTES_ESTATICOS.get(tipo_reporte)


def listar_reportes_disponibles():
    """
    Retorna lista de reportes disponibles con su info básica
    
    Returns:
        Lista de diccionarios con: id, nombre, descripcion
    """
    return [
        {
            'id': key,
            'nombre': config['nombre'],
            'descripcion': config['descripcion']
        }
        for key, config in REPORTES_ESTATICOS.items()
    ]
