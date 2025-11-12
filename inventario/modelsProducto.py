from django.db import models
from inventario.modelsCategoria import Categoria


class Producto(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    precio_compra_anterior = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    costo_promedio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    stock = models.IntegerField(default=0)
    imagen = models.URLField(blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, related_name='productos', null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-fecha_creacion']
