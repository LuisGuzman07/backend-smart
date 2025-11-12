from django.db import models
from .modelsNotaDeVenta import NotaDeVenta


class Pago(models.Model):
    # Relación 1 a 1 con NotaDeVenta - La FK va en Pago
    nota_venta = models.OneToOneField(
        NotaDeVenta, 
        on_delete=models.CASCADE, 
        related_name='pago',
        primary_key=True,
        help_text="Nota de venta asociada al pago"
    )
    
    fecha = models.DateTimeField(auto_now_add=True, help_text="Fecha del pago")
    monto = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Monto pagado"
    )
    moneda = models.CharField(
        max_length=10, 
        default='USD',
        help_text="Moneda del pago (USD, BOB, etc.)"
    )
    total_stripe = models.CharField(
        max_length=100,
        unique=True,
        help_text="ID de pago en Stripe (payment_intent_id)"
    )
    
    def __str__(self):
        return f"Pago Stripe {self.total_stripe} - Nota de Venta {self.nota_venta.numero_comprobante} - ${self.monto}"

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-fecha']
    
    def save(self, *args, **kwargs):
        """
        Al guardar el pago, marca automáticamente la nota de venta como pagada
        """
        super().save(*args, **kwargs)
        if self.nota_venta.estado != 'pagada':
            self.nota_venta.marcar_pagada()
    
    def validar_monto(self):
        """
        Valida que el monto del pago coincida con el total de la nota de venta
        """
        return self.monto == self.nota_venta.total
