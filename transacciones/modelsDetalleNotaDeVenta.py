from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal
from transacciones.modelsNotaDeVenta import NotaDeVenta
from inventario.modelsProducto import Producto


class DetalleNotaDeVenta(models.Model):
    cantidad = models.PositiveIntegerField(default=1)
    codigo = models.CharField(max_length=50, blank=True, null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    nota_venta = models.ForeignKey(NotaDeVenta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='detalles_nota_venta')

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad} - Nota de Venta {self.nota_venta.numero_comprobante}"

    class Meta:
        verbose_name = 'Detalle de Nota de Venta'
        verbose_name_plural = 'Detalles de Nota de Venta'
        ordering = ['-id']

    def calcular_totales(self):
        """Calcula subtotal y total del detalle"""
        # Obtener precio del producto
        precio_unitario = self.producto.precio_venta
        
        # Calcular subtotal
        self.subtotal = (precio_unitario * self.cantidad).quantize(Decimal('0.01'))
        
        # El total es igual al subtotal (sin descuentos ni impuestos)
        self.total = self.subtotal
        
        # Asignar código del producto si no existe
        if not self.codigo:
            self.codigo = self.producto.codigo

    def clean(self):
        """Validaciones antes de guardar"""
        super().clean()
        
        # Validar que haya stock suficiente
        if self.cantidad > self.producto.stock:
            raise ValidationError(
                f'Stock insuficiente. Solo hay {self.producto.stock} unidades disponibles de {self.producto.nombre}.'
            )
        
        # Validar cantidad mínima
        if self.cantidad <= 0:
            raise ValidationError('La cantidad debe ser mayor a 0.')

    def save(self, *args, **kwargs):
        # Calcular totales antes de guardar
        self.calcular_totales()
        
        # Ejecutar validaciones
        self.full_clean()
        
        super().save(*args, **kwargs)
        
        # Actualizar totales de la nota de venta
        self.nota_venta.calcular_totales()

    def delete(self, *args, **kwargs):
        nota_venta = self.nota_venta
        super().delete(*args, **kwargs)
        # Recalcular totales de la nota de venta después de eliminar
        nota_venta.calcular_totales()
