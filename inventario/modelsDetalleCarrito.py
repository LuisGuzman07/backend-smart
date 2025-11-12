from django.db import models
from django.core.exceptions import ValidationError
from inventario.modelsCarrito import Carrito
from inventario.modelsProducto import Producto


class DetalleCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='detalles_carrito')
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Precio del producto al momento de agregarlo al carrito"
    )

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad} - Carrito {self.carrito.codigo}"

    class Meta:
        verbose_name = 'Detalle de Carrito'
        verbose_name_plural = 'Detalles de Carrito'
        unique_together = ['carrito', 'producto']
        ordering = ['-id']

    @property
    def subtotal(self):
        """Calcula el subtotal de esta línea del carrito"""
        if self.precio_unitario is None:
            return 0
        return self.cantidad * self.precio_unitario

    def clean(self):
        """Validaciones antes de guardar"""
        super().clean()
        
        # Validar que haya stock suficiente
        if self.cantidad > self.producto.stock:
            raise ValidationError(
                f'Stock insuficiente. Solo hay {self.producto.stock} unidades disponibles.'
            )
        
        # Validar cantidad mínima
        if self.cantidad <= 0:
            raise ValidationError('La cantidad debe ser mayor a 0.')

    def save(self, *args, **kwargs):
        # Si no se especifica precio, tomar el precio actual del producto
        if not self.precio_unitario:
            self.precio_unitario = self.producto.precio_venta
        
        # Ejecutar validaciones
        self.full_clean()
        
        super().save(*args, **kwargs)
