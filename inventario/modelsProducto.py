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
    # Campo para rastrear si ya se notificó sobre stock bajo (evita spam)
    notificado_stock_bajo = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-fecha_creacion']
    
    def save(self, *args, **kwargs):
        """
        Override del save para verificar stock bajo y enviar notificaciones
        """
        # Guardar el stock anterior si existe
        stock_anterior = None
        if self.pk:
            try:
                producto_anterior = Producto.objects.get(pk=self.pk)
                stock_anterior = producto_anterior.stock
            except Producto.DoesNotExist:
                pass
        
        # Guardar el producto
        super().save(*args, **kwargs)
        
        # Verificar si el stock bajó a 3 o menos
        if stock_anterior is not None and stock_anterior > 3 and self.stock <= 3:
            # El stock acaba de bajar a 3 o menos
            self.notificar_stock_bajo()
            self.notificado_stock_bajo = True
            super().save(update_fields=['notificado_stock_bajo'])
        elif self.stock > 3 and self.notificado_stock_bajo:
            # El stock se reabastació, resetear la bandera
            self.notificado_stock_bajo = False
            super().save(update_fields=['notificado_stock_bajo'])
    
    def notificar_stock_bajo(self):
        """
        Envía notificación a administradores cuando el stock es bajo (≤ 3)
        """
        try:
            from django.contrib.auth.models import User
            from perfiles.fcm_service import send_push_to_user
            
            # Construir mensaje según el stock
            if self.stock == 0:
                titulo = "🚨 Producto SIN STOCK"
                cuerpo = f"¡{self.nombre} se ha agotado! Stock actual: 0 unidades"
                emoji = "🚨"
            elif self.stock == 1:
                titulo = "⚠️ Stock CRÍTICO"
                cuerpo = f"{self.nombre} tiene solo 1 unidad disponible"
                emoji = "⚠️"
            else:
                titulo = "📦 Stock BAJO"
                cuerpo = f"{self.nombre} tiene solo {self.stock} unidades disponibles"
                emoji = "📦"
            
            # Enviar a todos los administradores
            admins = User.objects.filter(is_staff=True, is_active=True)
            for admin in admins:
                send_push_to_user(
                    user=admin,
                    title=titulo,
                    body=cuerpo,
                    data={
                        'type': 'stock_bajo',
                        'producto_id': str(self.id),
                        'producto_nombre': self.nombre,
                        'stock_actual': str(self.stock),
                        'screen': '/catalogo',
                    }
                )
                print(f"📱 Notificación de stock bajo enviada al admin: {admin.username}")
                
        except Exception as e:
            print(f"⚠️ Error enviando notificación de stock bajo: {str(e)}")
