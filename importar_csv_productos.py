import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_exa2.settings')
django.setup()

import csv
from decimal import Decimal
from inventario.modelsCategoria import Categoria
from inventario.modelsProducto import Producto

with open('Productos_inventario.csv', newline='', encoding='utf-8') as csvfile:
    filtered_lines = (line for line in csvfile if not line.strip().startswith('#'))
    reader = csv.DictReader(filtered_lines)
    for row in reader:
        categoria, _ = Categoria.objects.get_or_create(nombre=row['categoria'])
        producto, created = Producto.objects.get_or_create(
            codigo=row['codigo'],
            defaults={
                'nombre': row['nombre'],
                'descripcion': row['descripcion'],
                'precio_compra': Decimal(row['precio_compra']),
                'precio_compra_anterior': Decimal(row['precio_compra_anterior']) if row['precio_compra_anterior'] else None,
                'precio_venta': Decimal(row['precio_venta']),
                'costo_promedio': Decimal(row['costo_promedio']),
                'stock': int(row['stock']),
                'imagen': row['imagen'] or None,
                'categoria': categoria
            }
        )
        if created:
            print(f"✅ Producto importado: {producto.nombre}")
        else:
            print(f"⚠️ Producto existente: {producto.nombre}")
