"""
Whitelist de entidades, campos y filtros permitidos para reportes personalizados
Define qué campos y filtros pueden usarse de forma segura
"""

# Configuración de entidades disponibles
ENTIDADES_DISPONIBLES = {
    'productos': {
        'nombre': 'Productos',
        'modelo': 'inventario.Producto',
        'campos_disponibles': {
            'id': {'label': 'ID', 'tipo': 'number'},
            'codigo': {'label': 'Código', 'tipo': 'text'},
            'nombre': {'label': 'Nombre', 'tipo': 'text'},
            'descripcion': {'label': 'Descripción', 'tipo': 'text'},
            'precio_compra': {'label': 'Precio Compra', 'tipo': 'number'},
            'precio_venta': {'label': 'Precio Venta', 'tipo': 'number'},
            'costo_promedio': {'label': 'Costo Promedio', 'tipo': 'number'},
            'stock': {'label': 'Stock', 'tipo': 'number'},
            'fecha_creacion': {'label': 'Fecha Creación', 'tipo': 'date'},
            'categoria__nombre': {'label': 'Categoría', 'tipo': 'text'},
        },
        'filtros_disponibles': {
            'stock__lt': {'label': 'Stock menor a', 'tipo': 'number'},
            'stock__lte': {'label': 'Stock menor o igual a', 'tipo': 'number'},
            'stock__gt': {'label': 'Stock mayor a', 'tipo': 'number'},
            'stock__gte': {'label': 'Stock mayor o igual a', 'tipo': 'number'},
            'precio_venta__lt': {'label': 'Precio menor a', 'tipo': 'number'},
            'precio_venta__gt': {'label': 'Precio mayor a', 'tipo': 'number'},
            'categoria__nombre__icontains': {'label': 'Categoría contiene', 'tipo': 'text'},
            'nombre__icontains': {'label': 'Nombre contiene', 'tipo': 'text'},
            'codigo__icontains': {'label': 'Código contiene', 'tipo': 'text'},
        }
    },
    
    'clientes': {
        'nombre': 'Clientes',
        'modelo': 'perfiles.Cliente',
        'campos_disponibles': {
            'id': {'label': 'ID', 'tipo': 'number'},
            'nombre': {'label': 'Nombre', 'tipo': 'text'},
            'apellido': {'label': 'Apellido', 'tipo': 'text'},
            'ci': {'label': 'CI', 'tipo': 'text'},
            'telefono': {'label': 'Teléfono', 'tipo': 'text'},
            'direccion': {'label': 'Dirección', 'tipo': 'text'},
            'sexo': {'label': 'Sexo', 'tipo': 'text'},
            'estado': {'label': 'Estado', 'tipo': 'text'},
            'fecha_registro': {'label': 'Fecha Registro', 'tipo': 'date'},
        },
        'filtros_disponibles': {
            'estado': {'label': 'Estado', 'tipo': 'choice', 'choices': ['activo', 'inactivo']},
            'sexo': {'label': 'Sexo', 'tipo': 'choice', 'choices': ['M', 'F']},
            'nombre__icontains': {'label': 'Nombre contiene', 'tipo': 'text'},
            'apellido__icontains': {'label': 'Apellido contiene', 'tipo': 'text'},
            'ci__icontains': {'label': 'CI contiene', 'tipo': 'text'},
            'fecha_registro__gte': {'label': 'Registrado desde', 'tipo': 'date'},
            'fecha_registro__lte': {'label': 'Registrado hasta', 'tipo': 'date'},
            'notas_venta__fecha__gte': {'label': 'Con compras desde', 'tipo': 'date'},
            'notas_venta__fecha__lte': {'label': 'Con compras hasta', 'tipo': 'date'},
        }
    },
    
    'ventas': {
        'nombre': 'Ventas (Notas de Venta)',
        'modelo': 'transacciones.NotaDeVenta',
        'campos_disponibles': {
            'id': {'label': 'ID', 'tipo': 'number'},
            'numero_comprobante': {'label': 'N° Comprobante', 'tipo': 'text'},
            'fecha': {'label': 'Fecha', 'tipo': 'date'},
            'estado': {'label': 'Estado', 'tipo': 'text'},
            'subtotal': {'label': 'Subtotal', 'tipo': 'number'},
            'total': {'label': 'Total', 'tipo': 'number'},
            'cliente__nombre': {'label': 'Cliente Nombre', 'tipo': 'text'},
            'cliente__apellido': {'label': 'Cliente Apellido', 'tipo': 'text'},
            'cliente__ci': {'label': 'Cliente CI', 'tipo': 'text'},
        },
        'filtros_disponibles': {
            'estado': {'label': 'Estado', 'tipo': 'choice', 'choices': ['pendiente', 'pagada', 'anulada']},
            'fecha__gte': {'label': 'Fecha desde', 'tipo': 'date'},
            'fecha__lte': {'label': 'Fecha hasta', 'tipo': 'date'},
            'total__gt': {'label': 'Total mayor a', 'tipo': 'number'},
            'total__lt': {'label': 'Total menor a', 'tipo': 'number'},
            'cliente__nombre__icontains': {'label': 'Cliente nombre contiene', 'tipo': 'text'},
            'cliente__ci__icontains': {'label': 'Cliente CI contiene', 'tipo': 'text'},
        }
    },
    
    'categorias': {
        'nombre': 'Categorías',
        'modelo': 'inventario.Categoria',
        'campos_disponibles': {
            'id': {'label': 'ID', 'tipo': 'number'},
            'nombre': {'label': 'Nombre', 'tipo': 'text'},
            'descripcion': {'label': 'Descripción', 'tipo': 'text'},
        },
        'filtros_disponibles': {
            'nombre__icontains': {'label': 'Nombre contiene', 'tipo': 'text'},
        }
    },
    
    'detalles_ventas': {
        'nombre': 'Detalles de Ventas (por Producto)',
        'modelo': 'transacciones.DetalleNotaDeVenta',
        'campos_disponibles': {
            'id': {'label': 'ID', 'tipo': 'number'},
            'cantidad': {'label': 'Cantidad', 'tipo': 'number'},
            'codigo': {'label': 'Código Producto', 'tipo': 'text'},
            'subtotal': {'label': 'Subtotal', 'tipo': 'number'},
            'total': {'label': 'Total', 'tipo': 'number'},
            'producto__nombre': {'label': 'Producto', 'tipo': 'text'},
            'producto__codigo': {'label': 'Código Producto', 'tipo': 'text'},
            'producto__categoria__nombre': {'label': 'Categoría', 'tipo': 'text'},
            'nota_venta__numero_comprobante': {'label': 'N° Comprobante', 'tipo': 'text'},
            'nota_venta__fecha': {'label': 'Fecha Venta', 'tipo': 'date'},
            'nota_venta__estado': {'label': 'Estado Venta', 'tipo': 'text'},
            'nota_venta__cliente__nombre': {'label': 'Cliente Nombre', 'tipo': 'text'},
            'nota_venta__cliente__apellido': {'label': 'Cliente Apellido', 'tipo': 'text'},
            'nota_venta__cliente__ci': {'label': 'Cliente CI', 'tipo': 'text'},
        },
        'filtros_disponibles': {
            'nota_venta__fecha__gte': {'label': 'Fecha venta desde', 'tipo': 'date'},
            'nota_venta__fecha__lte': {'label': 'Fecha venta hasta', 'tipo': 'date'},
            'nota_venta__estado': {'label': 'Estado venta', 'tipo': 'choice', 'choices': ['pendiente', 'pagada', 'anulada']},
            'producto__nombre__icontains': {'label': 'Producto contiene', 'tipo': 'text'},
            'producto__categoria__nombre__icontains': {'label': 'Categoría contiene', 'tipo': 'text'},
            'nota_venta__cliente__nombre__icontains': {'label': 'Cliente nombre contiene', 'tipo': 'text'},
            'cantidad__gt': {'label': 'Cantidad mayor a', 'tipo': 'number'},
            'cantidad__lt': {'label': 'Cantidad menor a', 'tipo': 'number'},
            'total__gt': {'label': 'Total mayor a', 'tipo': 'number'},
            'total__lt': {'label': 'Total menor a', 'tipo': 'number'},
        }
    },
    
    'ventas_por_cliente': {
        'nombre': 'Ventas Agrupadas por Cliente',
        'modelo': 'transacciones.NotaDeVenta',
        'campos_disponibles': {
            'cliente__id': {'label': 'ID Cliente', 'tipo': 'number'},
            'cliente__nombre': {'label': 'Nombre Cliente', 'tipo': 'text'},
            'cliente__apellido': {'label': 'Apellido Cliente', 'tipo': 'text'},
            'cliente__ci': {'label': 'CI Cliente', 'tipo': 'text'},
            'cliente__telefono': {'label': 'Teléfono Cliente', 'tipo': 'text'},
            'cantidad_compras': {'label': 'Cantidad de Compras', 'tipo': 'aggregation'},
            'total_pagado': {'label': 'Total Pagado', 'tipo': 'aggregation'},
            'fecha_primera_compra': {'label': 'Primera Compra', 'tipo': 'aggregation'},
            'fecha_ultima_compra': {'label': 'Última Compra', 'tipo': 'aggregation'},
        },
        'filtros_disponibles': {
            'fecha__gte': {'label': 'Fecha desde', 'tipo': 'date'},
            'fecha__lte': {'label': 'Fecha hasta', 'tipo': 'date'},
            'estado': {'label': 'Estado', 'tipo': 'choice', 'choices': ['pendiente', 'pagada', 'anulada']},
            'cliente__nombre__icontains': {'label': 'Cliente nombre contiene', 'tipo': 'text'},
            'total__gt': {'label': 'Total mayor a', 'tipo': 'number'},
            'total__lt': {'label': 'Total menor a', 'tipo': 'number'},
        }
    },
}


def obtener_config_entidad(entidad_id):
    """
    Obtiene la configuración de una entidad
    
    Args:
        entidad_id: ID de la entidad (productos, clientes, ventas, categorias)
    
    Returns:
        Dict con la configuración o None si no existe
    """
    return ENTIDADES_DISPONIBLES.get(entidad_id)


def obtener_entidades():
    """
    Retorna todas las entidades disponibles
    
    Returns:
        Dict con todas las entidades
    """
    return ENTIDADES_DISPONIBLES


def validar_campos(entidad_id, campos):
    """
    Valida que los campos solicitados estén en la whitelist
    
    Args:
        entidad_id: ID de la entidad
        campos: Lista de campos a validar
    
    Returns:
        Tupla (bool, list): (son_validos, campos_invalidos)
    """
    config = obtener_config_entidad(entidad_id)
    if not config:
        return False, ['Entidad no válida']
    
    campos_permitidos = set(config['campos_disponibles'].keys())
    campos_invalidos = [campo for campo in campos if campo not in campos_permitidos]
    
    return len(campos_invalidos) == 0, campos_invalidos


def validar_filtros(entidad_id, filtros):
    """
    Valida que los filtros solicitados estén en la whitelist
    
    Args:
        entidad_id: ID de la entidad
        filtros: Dict de filtros a validar
    
    Returns:
        Tupla (bool, list): (son_validos, filtros_invalidos)
    """
    config = obtener_config_entidad(entidad_id)
    if not config:
        return False, ['Entidad no válida']
    
    filtros_permitidos = set(config['filtros_disponibles'].keys())
    filtros_invalidos = [filtro for filtro in filtros.keys() if filtro not in filtros_permitidos]
    
    return len(filtros_invalidos) == 0, filtros_invalidos
