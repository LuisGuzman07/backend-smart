import os
import csv
import random
import time
from decimal import Decimal
from collections import defaultdict
from datetime import datetime, timezone as dt_timezone
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_exa2.settings')
django.setup()

from django.utils import timezone
from transacciones.modelsNotaDeVenta import NotaDeVenta
from transacciones.modelsDetalleNotaDeVenta import DetalleNotaDeVenta
from transacciones.modelsPago import Pago
from transacciones.modelsListadoHistoricoVentas import ListadoHistoricoVentas
from perfiles.models import Cliente
from inventario.modelsProducto import Producto
from django.contrib.auth.models import User

def crear_ventas():
    with open('historial_ventas.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        ventas_dict = defaultdict(list)
        for row in reader:
            venta_id = row['venta_id']
            ventas_dict[venta_id].append(row)

    # Fechas entre septiembre y octubre 2025
    fecha_inicio = datetime(2025, 9, 1, tzinfo=dt_timezone.utc)
    fecha_fin = datetime(2025, 10, 31, 23, 59, 59, tzinfo=dt_timezone.utc)

    for venta_id, detalles in ventas_dict.items():
        # Tomar datos comunes de la primera fila
        primera_fila = detalles[0]
        cliente_ci = primera_fila['cliente_ci']
        metodo_pago = primera_fila.get('metodo_pago', 'Stripe')
        moneda = primera_fila.get('moneda', 'BOB')
        referencia_pago = primera_fila['referencia_pago']

        # Verificar si la venta ya existe por referencia de pago
        if Pago.objects.filter(total_stripe=referencia_pago).exists():
            print(f"Venta {venta_id} ya existe (referencia {referencia_pago}), omitiendo.")
            continue

        # Obtener cliente
        try:
            cliente = Cliente.objects.get(ci=cliente_ci)
        except Cliente.DoesNotExist:
            print(f"Cliente con CI {cliente_ci} no encontrado, omitiendo venta {venta_id}.")
            continue

        # Asignar usuario manualmente si no tiene
        if not cliente.usuario:
            # Asignar un usuario existente o crear uno, pero aquí asumimos que tienen
            print(f"Cliente {cliente.nombre} no tiene usuario asignado, omitiendo.")
            continue

        # Generar fecha aleatoria
        timestamp_aleatorio = random.randint(int(fecha_inicio.timestamp()), int(fecha_fin.timestamp()))
        fecha_venta = datetime.fromtimestamp(timestamp_aleatorio, tz=dt_timezone.utc)

        # Generar número de comprobante único
        timestamp = int(time.time() * 1000000)  # Microsegundos para unicidad
        numero_comprobante = f"NV-{timestamp}"

        # Crear Nota de Venta con estado pagada
        nota_venta = NotaDeVenta.objects.create(
            numero_comprobante=numero_comprobante,
            cliente=cliente,
            estado='pagada'
        )

        # Crear detalles
        for detalle in detalles:
            codigo = detalle['producto_codigo']
            cantidad = int(detalle['cantidad'])

            try:
                producto = Producto.objects.get(codigo=codigo)
            except Producto.DoesNotExist:
                print(f"Producto con código {codigo} no encontrado, omitiendo detalle en venta {venta_id}.")
                continue

            DetalleNotaDeVenta.objects.create(
                nota_venta=nota_venta,
                producto=producto,
                cantidad=cantidad
            )

        # Calcular totales (se hace automáticamente en save de Detalle)
        nota_venta.calcular_totales()

        # Crear Pago
        pago = Pago.objects.create(
            nota_venta=nota_venta,
            monto=nota_venta.total,
            moneda=moneda,
            total_stripe=referencia_pago
        )

        # Setear fechas manualmente
        NotaDeVenta.objects.filter(pk=nota_venta.pk).update(fecha=fecha_venta)
        Pago.objects.filter(nota_venta=nota_venta).update(fecha=fecha_venta)

        # Crear registro en histórico
        try:
            historial = ListadoHistoricoVentas.crear_desde_nota_venta(nota_venta)
            # Setear fecha_venta en histórico
            ListadoHistoricoVentas.objects.filter(pk=nota_venta.pk).update(fecha_venta=fecha_venta, fecha_pago=fecha_venta)
            print(f"Venta {numero_comprobante} (ID: {venta_id}) creada exitosamente para {cliente.nombre} {cliente.apellido}, total: Bs. {nota_venta.total}, fecha: {fecha_venta.date()}")
        except ValueError as e:
            print(f"Error al crear histórico para venta {numero_comprobante}: {e}")

if __name__ == '__main__':
    crear_ventas()