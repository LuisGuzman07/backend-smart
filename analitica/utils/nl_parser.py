"""
Parser de Lenguaje Natural para Reportes
Interpreta consultas en español y las convierte en filtros de base de datos
"""
import re
from datetime import datetime, timedelta
from django.utils import timezone
from .whitelist import ENTIDADES_DISPONIBLES


# Mapeo de palabras clave a entidades
KEYWORDS_ENTIDADES = {
    'productos': ['producto', 'productos', 'articulo', 'articulos', 'item', 'items', 'inventario', 'stock'],
    'clientes': ['cliente', 'clientes', 'comprador', 'compradores'],
    'ventas': ['venta', 'ventas', 'nota', 'notas', 'compra', 'compras', 'transaccion', 'transacciones'],
    'categorias': ['categoria', 'categorias', 'categoría', 'categorías'],
    'detalles_ventas': ['detalle', 'detalles', 'detalle de venta', 'detalles de venta', 'detalles de ventas', 'productos vendidos', 'items vendidos'],
    'ventas_por_cliente': ['ventas por cliente', 'ventas agrupadas por cliente', 'compras por cliente', 'ventas de cada cliente'],
}

# Mapeo de estados de ventas
ESTADOS_VENTAS = {
    'pendiente': ['pendiente', 'pendientes', 'sin pagar'],
    'pagada': ['pagada', 'pagadas', 'completada', 'completadas', 'finalizada', 'finalizadas'],
    'anulada': ['anulada', 'anuladas', 'cancelada', 'canceladas'],
}

# Mapeo de estados de clientes
ESTADOS_CLIENTES = {
    'activo': ['activo', 'activos', 'activa', 'activas'],
    'inactivo': ['inactivo', 'inactivos', 'inactiva', 'inactivas'],
}


def detectar_entidad(consulta):
    """
    Detecta qué entidad está solicitando el usuario
    
    Args:
        consulta: String con la consulta en lenguaje natural
    
    Returns:
        String con el ID de la entidad o None
    """
    consulta_lower = consulta.lower()
    
    # Prioridad 1: Detectar ventas agrupadas por cliente
    keywords_ventas_por_cliente = [
        'ventas por cliente', 'ventas agrupadas por cliente', 'compras por cliente',
        'ventas de cada cliente', 'compras de cada cliente', 'cantidad de compras',
        'monto total que pagó', 'total pagado por cliente'
    ]
    
    # Buscar indicadores de agrupación por cliente
    tiene_agrupacion_cliente = any(kw in consulta_lower for kw in keywords_ventas_por_cliente)
    tiene_agregaciones = any(kw in consulta_lower for kw in ['cantidad de compras', 'monto total', 'total pagado', 'cuántas compras', 'cuantas compras'])
    tiene_nombre_cliente = 'nombre del cliente' in consulta_lower or 'nombre de cliente' in consulta_lower
    
    if tiene_agrupacion_cliente or (tiene_agregaciones and tiene_nombre_cliente):
        return 'ventas_por_cliente'
    
    # Prioridad 2: Detectar detalles de ventas (agrupado por producto, productos vendidos, etc.)
    keywords_detalles_fuertes = ['agrupado por producto', 'agrupadas por producto', 'agrupado por productos', 'agrupadas por productos', 'agrupados por producto', 'agrupados por productos', 'detalles de venta', 'detalle de venta']
    keywords_vendidos = ['productos vendidos', 'items vendidos', 'artículos vendidos', 'articulos vendidos']
    keywords_detalle_simple = ['detalle', 'detalles']
    keywords_ventas_contexto = ['venta', 'ventas', 'compra', 'compras', 'vendido', 'vendidos']
    
    # Primero verificar patrones fuertes
    if any(kw in consulta_lower for kw in keywords_detalles_fuertes):
        return 'detalles_ventas'
    
    # Verificar "productos/items vendidos"
    if any(kw in consulta_lower for kw in keywords_vendidos):
        return 'detalles_ventas'
    
    # Verificar "detalle/detalles" + contexto de ventas
    tiene_detalle = any(kw in consulta_lower for kw in keywords_detalle_simple)
    tiene_venta = any(kw in consulta_lower for kw in keywords_ventas_contexto)
    
    if tiene_detalle and tiene_venta:
        return 'detalles_ventas'
    
    # Prioridad 2: Buscar patrones que indiquen claramente la entidad principal
    patron_lista = r'(?:dame|muestra|lista|reporte|reportes?)\s+(?:de\s+)?(?:los?\s+|las?\s+)?(producto[s]?|cliente[s]?|venta[s]?|categoria[s]?|categoría[s]?)'
    match = re.search(patron_lista, consulta_lower)
    if match:
        entidad_texto = match.group(1)
        # Mapear el texto a la entidad
        if any(kw in entidad_texto for kw in ['producto']):
            return 'productos'
        elif 'cliente' in entidad_texto:
            return 'clientes'
        elif 'venta' in entidad_texto:
            return 'ventas'
        elif any(kw in entidad_texto for kw in ['categoria', 'categoría']):
            return 'categorias'
    
    # Prioridad 3: Si no hay patrón específico, buscar la primera coincidencia
    for entidad_id, keywords in KEYWORDS_ENTIDADES.items():
        for keyword in keywords:
            if keyword in consulta_lower:
                return entidad_id
    
    return None


def extraer_fechas(consulta):
    """
    Extrae rangos de fechas de la consulta
    
    Args:
        consulta: String con la consulta
    
    Returns:
        Dict con fecha_desde y fecha_hasta si se encuentran
    """
    fechas = {}
    consulta_lower = consulta.lower()
    now = timezone.now()
    
    # Este mes
    if 'este mes' in consulta_lower:
        fecha_desde = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        fecha_hasta = now
        fechas['fecha_desde'] = fecha_desde
        fechas['fecha_hasta'] = fecha_hasta
        return fechas
    
    # Este año
    if 'este año' in consulta_lower or 'este ano' in consulta_lower:
        fecha_desde = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        fecha_hasta = now
        fechas['fecha_desde'] = fecha_desde
        fechas['fecha_hasta'] = fecha_hasta
        return fechas
    
    # Hoy
    if 'hoy' in consulta_lower:
        fecha_desde = now.replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_hasta = now
        fechas['fecha_desde'] = fecha_desde
        fechas['fecha_hasta'] = fecha_hasta
        return fechas
    
    # Ayer
    if 'ayer' in consulta_lower:
        ayer = now - timedelta(days=1)
        fecha_desde = ayer.replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_hasta = ayer.replace(hour=23, minute=59, second=59)
        fechas['fecha_desde'] = fecha_desde
        fechas['fecha_hasta'] = fecha_hasta
        return fechas
    
    # Esta semana
    if 'esta semana' in consulta_lower:
        fecha_desde = now - timedelta(days=now.weekday())
        fecha_hasta = now
        fechas['fecha_desde'] = fecha_desde
        fechas['fecha_hasta'] = fecha_hasta
        return fechas
    
    # Último mes / mes pasado
    if 'último mes' in consulta_lower or 'ultimo mes' in consulta_lower or 'mes pasado' in consulta_lower:
        primer_dia_mes_actual = now.replace(day=1)
        ultimo_dia_mes_pasado = primer_dia_mes_actual - timedelta(days=1)
        primer_dia_mes_pasado = ultimo_dia_mes_pasado.replace(day=1)
        fechas['fecha_desde'] = primer_dia_mes_pasado
        fechas['fecha_hasta'] = ultimo_dia_mes_pasado
        return fechas
    
    # Últimos X días
    match_dias = re.search(r'últimos? (\d+) días?|ultimos? (\d+) dias?', consulta_lower)
    if match_dias:
        dias = int(match_dias.group(1) or match_dias.group(2))
        fecha_desde = now - timedelta(days=dias)
        fecha_hasta = now
        fechas['fecha_desde'] = fecha_desde
        fechas['fecha_hasta'] = fecha_hasta
        return fechas
    
    # Últimas X semanas
    match_semanas = re.search(r'últimas? (\d+) semanas?|ultimas? (\d+) semanas?', consulta_lower)
    if match_semanas:
        semanas = int(match_semanas.group(1) or match_semanas.group(2))
        fecha_desde = now - timedelta(weeks=semanas)
        fecha_hasta = now
        fechas['fecha_desde'] = fecha_desde
        fechas['fecha_hasta'] = fecha_hasta
        return fechas
    
    # Buscar rangos de fechas específicas en formato DD/MM/YYYY
    patron_rango = r'(?:del|desde)\s+(\d{1,2})[/-](\d{1,2})[/-](\d{4})\s+(?:al|hasta)\s+(\d{1,2})[/-](\d{1,2})[/-](\d{4})'
    match_rango = re.search(patron_rango, consulta)
    if match_rango:
        dia1, mes1, año1 = int(match_rango.group(1)), int(match_rango.group(2)), int(match_rango.group(3))
        dia2, mes2, año2 = int(match_rango.group(4)), int(match_rango.group(5)), int(match_rango.group(6))
        
        try:
            fecha_inicio = timezone.datetime(año1, mes1, dia1)
            fecha_fin = timezone.datetime(año2, mes2, dia2, 23, 59, 59)
            fechas['fecha_desde'] = timezone.make_aware(fecha_inicio)
            fechas['fecha_hasta'] = timezone.make_aware(fecha_fin)
            return fechas
        except ValueError:
            pass  # Fecha inválida, continuar con otros patrones
    
    # Buscar meses específicos (enero, febrero, etc.)
    meses = {
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
        'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
        'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
    }
    
    for mes_nombre, mes_num in meses.items():
        if mes_nombre in consulta_lower:
            # Extraer año si está presente
            year_match = re.search(r'\b(20\d{2})\b', consulta)
            year = int(year_match.group(1)) if year_match else timezone.now().year
            
            fecha_inicio = timezone.datetime(year, mes_num, 1)
            if mes_num == 12:
                fecha_fin = timezone.datetime(year + 1, 1, 1) - timedelta(seconds=1)
            else:
                fecha_fin = timezone.datetime(year, mes_num + 1, 1) - timedelta(seconds=1)
            
            fechas['fecha_desde'] = timezone.make_aware(fecha_inicio)
            fechas['fecha_hasta'] = timezone.make_aware(fecha_fin)
            return fechas
    
    return fechas


def extraer_estado_venta(consulta):
    """
    Extrae el estado de venta de la consulta
    
    Args:
        consulta: String con la consulta
    
    Returns:
        String con el estado o None
    """
    consulta_lower = consulta.lower()
    
    for estado_key, keywords in ESTADOS_VENTAS.items():
        for keyword in keywords:
            if keyword in consulta_lower:
                return estado_key
    
    return None


def extraer_estado_cliente(consulta):
    """
    Extrae el estado de cliente de la consulta
    
    Args:
        consulta: String con la consulta
    
    Returns:
        String con el estado o None
    """
    consulta_lower = consulta.lower()
    
    for estado_key, keywords in ESTADOS_CLIENTES.items():
        for keyword in keywords:
            if keyword in consulta_lower:
                return estado_key
    
    return None


def extraer_comparacion_numerica(consulta, campo_base):
    """
    Extrae comparaciones numéricas (mayor que, menor que, etc.)
    Puede extraer múltiples comparaciones en una misma consulta
    
    Args:
        consulta: String con la consulta
        campo_base: String con el nombre del campo (total, stock, precio, etc.)
    
    Returns:
        Dict con los filtros numéricos
    """
    filtros = {}
    consulta_lower = consulta.lower()
    
    # Patrones para extraer números - ordenados por especificidad
    patrones = [
        # Patrones que incluyen el nombre del campo (más específicos)
        (rf'{campo_base}\s+mayor\s+(?:a|que|de)\s+(\d+(?:\.\d+)?)', f'{campo_base}__gt'),
        (rf'{campo_base}\s+menor\s+(?:a|que|de)\s+(\d+(?:\.\d+)?)', f'{campo_base}__lt'),
        (rf'{campo_base}\s+mayor\s+o\s+igual\s+(?:a|que)\s+(\d+(?:\.\d+)?)', f'{campo_base}__gte'),
        (rf'{campo_base}\s+menor\s+o\s+igual\s+(?:a|que)\s+(\d+(?:\.\d+)?)', f'{campo_base}__lte'),
        (rf'{campo_base}\s+igual\s+(?:a|que)\s+(\d+(?:\.\d+)?)', campo_base),
        # Patrones genéricos (menos específicos)
        (rf'mayor\s+(?:a|que|de)\s+(\d+(?:\.\d+)?)', f'{campo_base}__gt'),
        (rf'menor\s+(?:a|que|de)\s+(\d+(?:\.\d+)?)', f'{campo_base}__lt'),
        (rf'mayor\s+o\s+igual\s+(?:a|que)\s+(\d+(?:\.\d+)?)', f'{campo_base}__gte'),
        (rf'menor\s+o\s+igual\s+(?:a|que)\s+(\d+(?:\.\d+)?)', f'{campo_base}__lte'),
        (rf'más\s+de\s+(\d+(?:\.\d+)?)', f'{campo_base}__gt'),
        (rf'menos\s+de\s+(\d+(?:\.\d+)?)', f'{campo_base}__lt'),
    ]
    
    # Buscar TODAS las coincidencias, no solo la primera
    for patron, filtro_key in patrones:
        matches = re.finditer(patron, consulta_lower)
        for match in matches:
            valor = float(match.group(1))
            # Solo agregar si no existe ya ese tipo de filtro
            if filtro_key not in filtros:
                filtros[filtro_key] = valor
    
    return filtros


def extraer_stock_bajo(consulta):
    """
    Detecta si se solicitan productos con stock bajo/crítico
    
    Args:
        consulta: String con la consulta
    
    Returns:
        Bool indicando si se debe filtrar por stock bajo
    """
    consulta_lower = consulta.lower()
    keywords_stock_bajo = ['stock bajo', 'stock crítico', 'stock critico', 'poco stock', 'sin stock', 'inventario bajo']
    
    return any(keyword in consulta_lower for keyword in keywords_stock_bajo)


def extraer_busqueda_texto(consulta, entidad):
    """
    Extrae búsquedas de texto (nombre contiene, etc.)
    
    Args:
        consulta: String con la consulta
        entidad: String con el ID de la entidad
    
    Returns:
        Dict con filtros de texto
    """
    filtros = {}
    consulta_lower = consulta.lower()
    
    # Patrones mejorados con más flexibilidad
    patrones = {
        'productos': [
            # Patrones para categoría - más flexibles
            (r'(?:de\s+(?:la\s+)?categor[ií]a|categor[ií]a)\s+["\']?([a-záéíóúñ\s]+?)(?:["\']|$)', 'categoria__nombre__icontains'),
            # Patrones para nombre de producto
            (r'nombre\s+["\']?([^"\']+)["\']?', 'nombre__icontains'),
            (r'llamad[oa]s?\s+["\']?([^"\']+)["\']?', 'nombre__icontains'),
            (r'con\s+nombre\s+["\']?([^"\']+)["\']?', 'nombre__icontains'),
            # Patrón para código
            (r'c[óo]digo\s+["\']?([^"\']+)["\']?', 'codigo__icontains'),
        ],
        'clientes': [
            # Patrones para nombre
            (r'nombre\s+["\']?([^"\']+)["\']?', 'nombre__icontains'),
            (r'llamad[oa]s?\s+["\']?([^"\']+)["\']?', 'nombre__icontains'),
            # Patrón para apellido
            (r'apellido\s+["\']?([^"\']+)["\']?', 'apellido__icontains'),
            # Patrón para CI
            (r'ci\s+["\']?([^"\']+)["\']?', 'ci__icontains'),
            (r'c\.?i\.?\s+["\']?([^"\']+)["\']?', 'ci__icontains'),
        ],
        'ventas': [
            # Patrones para cliente
            (r'cliente\s+(?:llamado|con\s+nombre|de\s+nombre)\s+["\']?([^"\']+)["\']?', 'cliente__nombre__icontains'),
            (r'de\s+(?:la?|el)\s+cliente\s+["\']?([^"\']+)["\']?', 'cliente__nombre__icontains'),
            # Patrón para CI del cliente
            (r'ci\s+["\']?([^"\']+)["\']?', 'cliente__ci__icontains'),
        ],
        'categorias': [
            # Patrones para nombre de categoría
            (r'nombre\s+["\']?([^"\']+)["\']?', 'nombre__icontains'),
            (r'llamad[oa]s?\s+["\']?([^"\']+)["\']?', 'nombre__icontains'),
        ],
    }
    
    if entidad in patrones:
        for patron, filtro_key in patrones[entidad]:
            match = re.search(patron, consulta_lower)
            if match:
                valor = match.group(1).strip()
                # Limpiar el valor capturado
                valor = re.sub(r'\s+', ' ', valor)  # Normalizar espacios
                filtros[filtro_key] = valor
                break  # Usar el primer match encontrado para evitar conflictos
    
    return filtros


def interpretar_consulta(consulta):
    """
    Función principal que interpreta una consulta en lenguaje natural
    
    Args:
        consulta: String con la consulta del usuario
    
    Returns:
        Dict con:
        - entidad: ID de la entidad
        - filtros: Dict de filtros a aplicar
        - campos_sugeridos: Lista de campos relevantes
        - error: String con mensaje de error si no se puede interpretar
    """
    resultado = {
        'entidad': None,
        'filtros': {},
        'campos_sugeridos': [],
        'consulta_original': consulta,
        'error': None
    }
    
    # 1. Detectar entidad
    entidad = detectar_entidad(consulta)
    if not entidad:
        resultado['error'] = 'No se pudo identificar la entidad (productos, clientes, ventas o categorías)'
        return resultado
    
    resultado['entidad'] = entidad
    config_entidad = ENTIDADES_DISPONIBLES[entidad]
    
    # 2. Extraer fechas si aplica
    if entidad in ['ventas']:
        fechas = extraer_fechas(consulta)
        
        if fechas.get('fecha_desde'):
            resultado['filtros']['fecha__gte'] = fechas['fecha_desde'].strftime('%Y-%m-%d')
        if fechas.get('fecha_hasta'):
            resultado['filtros']['fecha__lte'] = fechas['fecha_hasta'].strftime('%Y-%m-%d')
    
    # 3. Filtros específicos por entidad
    if entidad == 'productos':
        # Stock bajo (solo si no hay comparación numérica explícita)
        if extraer_stock_bajo(consulta):
            resultado['filtros']['stock__lt'] = 10
        
        # Stock comparación (solo si se menciona "stock")
        if 'stock' in consulta.lower():
            filtros_stock = extraer_comparacion_numerica(consulta, 'stock')
            resultado['filtros'].update(filtros_stock)
        
        # Precio comparación (solo si se menciona "precio")
        if 'precio' in consulta.lower():
            filtros_precio = extraer_comparacion_numerica(consulta, 'precio_venta')
            resultado['filtros'].update(filtros_precio)
        
        # Campos sugeridos
        resultado['campos_sugeridos'] = [
            'id', 'codigo', 'nombre', 'precio_compra', 'precio_venta', 
            'stock', 'categoria__nombre', 'fecha_creacion'
        ]
    
    elif entidad == 'ventas':
        # Estado
        estado = extraer_estado_venta(consulta)
        if estado:
            resultado['filtros']['estado'] = estado
        
        # Total
        filtros_total = extraer_comparacion_numerica(consulta, 'total')
        resultado['filtros'].update(filtros_total)
        
        # Campos sugeridos
        resultado['campos_sugeridos'] = [
            'id', 'numero_comprobante', 'fecha', 'estado', 'subtotal', 'total',
            'cliente__nombre', 'cliente__apellido', 'cliente__ci'
        ]
    
    elif entidad == 'clientes':
        # Detectar si se busca clientes relacionados con compras/ventas
        consulta_lower = consulta.lower()
        keywords_compras = ['compra', 'compras', 'compraron', 'hicieron una compra', 'realizaron una compra', 'venta', 'ventas']
        keywords_registro = ['registrado', 'registrados', 'registrada', 'registradas', 'se registro', 'se registraron']
        
        busca_por_compras = any(kw in consulta_lower for kw in keywords_compras)
        busca_por_registro = any(kw in consulta_lower for kw in keywords_registro)
        
        # Extraer fechas
        fechas = extraer_fechas(consulta)
        
        if busca_por_compras and fechas:
            # Si se buscan clientes por compras, filtrar por fecha de ventas
            if fechas.get('fecha_desde'):
                resultado['filtros']['notas_venta__fecha__gte'] = fechas['fecha_desde'].strftime('%Y-%m-%d')
            if fechas.get('fecha_hasta'):
                resultado['filtros']['notas_venta__fecha__lte'] = fechas['fecha_hasta'].strftime('%Y-%m-%d')
        elif busca_por_registro and fechas:
            # Si se buscan clientes por registro, filtrar por fecha de registro
            if fechas.get('fecha_desde'):
                resultado['filtros']['fecha_registro__gte'] = fechas['fecha_desde'].strftime('%Y-%m-%d')
            if fechas.get('fecha_hasta'):
                resultado['filtros']['fecha_registro__lte'] = fechas['fecha_hasta'].strftime('%Y-%m-%d')
        elif fechas and not busca_por_compras:
            # Por defecto, si hay fechas pero no menciona compras, asumir registro
            if fechas.get('fecha_desde'):
                resultado['filtros']['fecha_registro__gte'] = fechas['fecha_desde'].strftime('%Y-%m-%d')
            if fechas.get('fecha_hasta'):
                resultado['filtros']['fecha_registro__lte'] = fechas['fecha_hasta'].strftime('%Y-%m-%d')
        
        # Estado
        estado = extraer_estado_cliente(consulta)
        if estado:
            resultado['filtros']['estado'] = estado
        
        # Sexo
        if 'masculino' in consulta_lower or 'hombre' in consulta_lower:
            resultado['filtros']['sexo'] = 'M'
        elif 'femenino' in consulta_lower or 'mujer' in consulta_lower:
            resultado['filtros']['sexo'] = 'F'
        
        # Campos sugeridos
        resultado['campos_sugeridos'] = [
            'id', 'nombre', 'apellido', 'ci', 'telefono', 'direccion', 
            'sexo', 'estado', 'fecha_registro'
        ]
    
    elif entidad == 'categorias':
        # Campos sugeridos
        resultado['campos_sugeridos'] = [
            'id', 'nombre', 'descripcion'
        ]
    
    elif entidad == 'detalles_ventas':
        # Extraer fechas para ventas
        fechas = extraer_fechas(consulta)
        if fechas.get('fecha_desde'):
            resultado['filtros']['nota_venta__fecha__gte'] = fechas['fecha_desde'].strftime('%Y-%m-%d')
        if fechas.get('fecha_hasta'):
            resultado['filtros']['nota_venta__fecha__lte'] = fechas['fecha_hasta'].strftime('%Y-%m-%d')
        
        # Estado de venta
        estado = extraer_estado_venta(consulta)
        if estado:
            resultado['filtros']['nota_venta__estado'] = estado
        
        # Detectar si se solicita agrupación por producto
        consulta_lower = consulta.lower()
        keywords_agrupacion = ['agrupado por producto', 'agrupadas por producto', 'agrupados por producto', 'agrupado por productos', 'agrupadas por productos', 'agrupados por productos', 'por producto']
        requiere_agrupacion_producto = any(kw in consulta_lower for kw in keywords_agrupacion)
        
        if requiere_agrupacion_producto:
            # Campos para agrupación por producto
            resultado['campos_sugeridos'] = [
                'producto__nombre', 'producto__codigo', 'producto__categoria__nombre',
                'total_cantidad', 'total_vendido'
            ]
            resultado['requiere_agrupacion'] = True
            resultado['agrupar_por'] = 'producto'
        else:
            # Campos sugeridos para detalles sin agrupar
            resultado['campos_sugeridos'] = [
                'producto__nombre', 'cantidad', 'total', 
                'nota_venta__fecha', 'nota_venta__cliente__nombre', 
                'nota_venta__cliente__apellido', 'nota_venta__numero_comprobante'
            ]
    
    elif entidad == 'ventas_por_cliente':
        # Extraer fechas para ventas
        fechas = extraer_fechas(consulta)
        if fechas.get('fecha_desde'):
            resultado['filtros']['fecha__gte'] = fechas['fecha_desde'].strftime('%Y-%m-%d')
        if fechas.get('fecha_hasta'):
            resultado['filtros']['fecha__lte'] = fechas['fecha_hasta'].strftime('%Y-%m-%d')
        
        # Estado de venta
        estado = extraer_estado_venta(consulta)
        if estado:
            resultado['filtros']['estado'] = estado
        
        # Campos sugeridos para ventas por cliente (incluye agregaciones)
        resultado['campos_sugeridos'] = [
            'cliente__nombre', 'cliente__apellido', 'cliente__ci',
            'cantidad_compras', 'total_pagado',
            'fecha_primera_compra', 'fecha_ultima_compra'
        ]
        
        # Marcar que requiere agrupación
        resultado['requiere_agrupacion'] = True
        resultado['agrupar_por'] = 'cliente'
    
    # 4. Extraer búsquedas de texto
    filtros_texto = extraer_busqueda_texto(consulta, entidad)
    resultado['filtros'].update(filtros_texto)
    
    # 5. Validar que los filtros estén en la whitelist
    filtros_validos = {}
    filtros_disponibles = set(config_entidad['filtros_disponibles'].keys())
    
    for filtro_key, filtro_valor in resultado['filtros'].items():
        if filtro_key in filtros_disponibles:
            filtros_validos[filtro_key] = filtro_valor
    
    resultado['filtros'] = filtros_validos
    
    return resultado


def generar_ejemplos_consultas():
    """
    Genera ejemplos de consultas que el sistema puede interpretar
    
    Returns:
        Dict con ejemplos por entidad
    """
    return {
        'productos': [
            "Productos con stock bajo",
            "Productos con stock menor a 10",
            "Productos con precio mayor a 100",
            "Productos de la categoría línea blanca",
            "Productos de la categoría electrodomésticos",
            "Productos creados este mes",
        ],
        'clientes': [
            "Clientes registrados este mes",
            "Clientes activos",
            "Clientes masculinos",
            "Clientes con estado activo",
            "Clientes registrados este año",
        ],
        'ventas': [
            "Ventas pagadas este mes",
            "Ventas pendientes",
            "Ventas con total mayor a 500",
            "Ventas del cliente Juan",
            "Ventas completadas hoy",
        ],
        'categorias': [
            "Todas las categorías",
            "Categorías con nombre herramientas",
        ],
        'detalles_ventas': [
            "Ventas del mes de septiembre agrupado por producto",
            "Productos vendidos este mes",
            "Detalles de ventas pagadas en octubre",
            "Items vendidos con sus clientes este año",
        ],
        'ventas_por_cliente': [
            "Ventas por cliente del mes de octubre",
            "Mostrar cantidad de compras y monto total por cliente",
            "Clientes con sus compras del periodo 01/10/2024 al 01/01/2025",
            "Ventas agrupadas por cliente este año",
        ]
    }
