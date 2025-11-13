from django.db import models
from decimal import Decimal
from perfiles.models import Cliente


class NotaDeVenta(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('pagada', 'Pagada'),
        ('anulada', 'Anulada'),
    ]
    
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha = models.DateTimeField(auto_now_add=True)
    numero_comprobante = models.CharField(max_length=50, unique=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='notas_venta')

    def __str__(self):
        return f"Nota de Venta {self.numero_comprobante} - {self.cliente.nombre} ({self.estado})"

    class Meta:
        verbose_name = 'Nota de Venta'
        verbose_name_plural = 'Notas de Venta'
        ordering = ['-fecha']

    def calcular_totales(self):
        """Calcula el subtotal y total de la nota de venta"""
        # Calcular subtotal desde los detalles
        subtotal = sum(detalle.subtotal for detalle in self.detalles.all())
        self.subtotal = Decimal(str(subtotal)).quantize(Decimal('0.01'))
        
        # El total es igual al subtotal (sin impuestos ni descuentos)
        self.total = self.subtotal
        self.save()

    def anular(self):
        """Anula la nota de venta"""
        self.estado = 'anulada'
        self.save()

    def marcar_pagada(self):
        """Marca la nota de venta como pagada"""
        self.estado = 'pagada'
        self.save()
    
    def validar_stock_disponible(self):
        """
        Valida que haya stock suficiente para todos los productos en la nota de venta.
        Retorna una tupla (es_valido, mensaje_error)
        """
        productos_sin_stock = []
        
        for detalle in self.detalles.all():
            if detalle.producto.stock < detalle.cantidad:
                productos_sin_stock.append({
                    'producto': detalle.producto.nombre,
                    'stock_actual': detalle.producto.stock,
                    'cantidad_requerida': detalle.cantidad
                })
        
        if productos_sin_stock:
            mensaje = "Stock insuficiente para los siguientes productos: "
            mensaje += ", ".join([
                f"{p['producto']} (disponible: {p['stock_actual']}, requerido: {p['cantidad_requerida']})"
                for p in productos_sin_stock
            ])
            return False, mensaje
        
        return True, "Stock suficiente para todos los productos"
