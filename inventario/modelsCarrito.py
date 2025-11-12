from django.db import models
from perfiles.models import Cliente


class Carrito(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('completado', 'Completado'),
        ('abandonado', 'Abandonado'),
    ]
    
    codigo = models.CharField(max_length=50, unique=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='carritos')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Carrito {self.codigo} - {self.cliente.nombre} ({self.estado})"

    class Meta:
        verbose_name = 'Carrito'
        verbose_name_plural = 'Carritos'
        ordering = ['-fecha_actualizacion']

    @property
    def total_items(self):
        """Calcula el total de productos en el carrito"""
        return sum(detalle.cantidad for detalle in self.detalles.all())

    @property
    def total_carrito(self):
        """Calcula el total del carrito"""
        return sum(detalle.subtotal for detalle in self.detalles.all())

    def esta_vacio(self):
        """Verifica si el carrito está vacío"""
        return self.detalles.count() == 0
