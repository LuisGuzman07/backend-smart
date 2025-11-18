"""
Script de prueba para simular una compra y verificar notificación al admin
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_exa2.settings')
django.setup()

from django.contrib.auth.models import User
from perfiles.models import Cliente
from inventario.modelsProducto import Producto
from transacciones.modelsNotaDeVenta import NotaDeVenta
from transacciones.modelsDetalleNotaDeVenta import DetalleNotaDeVenta
from transacciones.modelsPago import Pago
from transacciones.modelsListadoHistoricoVentas import ListadoHistoricoVentas
from datetime import datetime
from decimal import Decimal

print("🛒 SIMULANDO COMPRA DE CLIENTE")
print("=" * 50)

# 1. Obtener o crear cliente
try:
    usuario_cliente = User.objects.get(username='esteban')
    cliente = Cliente.objects.get(usuario=usuario_cliente)
    print(f"✅ Cliente encontrado: {cliente.nombre} {cliente.apellido}")
except:
    print("❌ No se encontró el cliente 'esteban'")
    exit(1)

# 2. Obtener productos del inventario
productos = Producto.objects.filter(stock__gt=0)[:2]  # Tomar 2 productos con stock
if productos.count() < 1:
    print("❌ No hay productos con stock disponible")
    exit(1)

print(f"\n📦 Productos seleccionados:")
for p in productos:
    print(f"   - {p.nombre} | Stock: {p.stock} | Precio: Bs. {p.precio_venta}")

# 3. Crear nota de venta
numero_comprobante = f"TEST-NV-{int(datetime.now().timestamp())}"
nota_venta = NotaDeVenta.objects.create(
    numero_comprobante=numero_comprobante,
    cliente=cliente,
    estado='pendiente'
)
print(f"\n📄 Nota de venta creada: {numero_comprobante}")

# 4. Crear detalles de la nota de venta
for producto in productos:
    cantidad = min(2, producto.stock)  # Comprar máximo 2 unidades
    detalle = DetalleNotaDeVenta.objects.create(
        nota_venta=nota_venta,
        producto=producto,
        cantidad=cantidad
    )
    print(f"   ✅ Detalle: {cantidad}x {producto.nombre}")

# 5. Recalcular totales
nota_venta.calcular_totales()
print(f"\n💰 Total de la compra: Bs. {nota_venta.total}")

# 6. Crear el pago (esto debería disparar la notificación)
print("\n💳 Procesando pago...")
pago = Pago.objects.create(
    nota_venta=nota_venta,
    monto=nota_venta.total,
    moneda='USD',
    total_stripe=f'test_payment_intent_{int(datetime.now().timestamp())}'
)

# 7. Crear registro en historial de ventas (esto debe hacerse DESPUÉS del pago)
historial = ListadoHistoricoVentas.crear_desde_nota_venta(nota_venta)

print(f"✅ Pago procesado exitosamente")
print(f"📊 Historial de venta creado: {historial.numero_venta}")

# 9. Verificar administradores
admins = User.objects.filter(is_staff=True, is_active=True)
print(f"\n👥 Administradores activos: {admins.count()}")
for admin in admins:
    print(f"   - {admin.username} ({'staff' if admin.is_staff else 'user'})")
    # Verificar si tiene dispositivos registrados
    from perfiles.models_device_token import DeviceToken
    tokens = DeviceToken.objects.filter(user=admin, is_active=True)
    print(f"     📱 Dispositivos: {tokens.count()}")
    for token in tokens:
        print(f"        - {token.platform}: {token.token[:50]}...")

print("\n" + "=" * 50)
print("✅ COMPRA SIMULADA EXITOSAMENTE")
print("🔔 Verifica tu dispositivo para la notificación")
print("=" * 50)
