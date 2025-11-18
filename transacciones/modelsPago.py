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
        Al guardar el pago:
        1. Marca automáticamente la nota de venta como pagada
        2. Reduce el stock de los productos vendidos
        3. Envía notificación a administradores
        """
        # Verificar si es un nuevo pago (no una actualización)
        es_nuevo_pago = self.nota_venta_id and not Pago.objects.filter(nota_venta_id=self.nota_venta_id).exists()
        
        super().save(*args, **kwargs)
        
        # Solo marcar como pagada y reducir stock si el estado no es 'pagada'
        if self.nota_venta.estado != 'pagada':
            self.nota_venta.marcar_pagada()
            
            # Reducir el stock de cada producto vendido
            if es_nuevo_pago:
                self.reducir_stock_productos()
                
                # 🔔 ENVIAR NOTIFICACIÓN A ADMINISTRADORES
                self.enviar_notificacion_admin()
    
    def reducir_stock_productos(self):
        """
        Reduce el stock de todos los productos en la nota de venta.
        Se ejecuta automáticamente al confirmar el pago.
        """
        for detalle in self.nota_venta.detalles.all():
            producto = detalle.producto
            cantidad_vendida = detalle.cantidad
            
            # Validar que hay stock suficiente antes de reducir
            if producto.stock >= cantidad_vendida:
                producto.stock -= cantidad_vendida
                producto.save()
            else:
                # Si no hay stock suficiente, registrar el error
                # pero no detener el proceso (el pago ya se procesó)
                print(f"ADVERTENCIA: Stock insuficiente para {producto.nombre}. "
                      f"Stock actual: {producto.stock}, Cantidad vendida: {cantidad_vendida}")
    
    def validar_monto(self):
        """
        Valida que el monto del pago coincida con el total de la nota de venta
        """
        return self.monto == self.nota_venta.total
    
    def enviar_notificacion_admin(self):
        """
        Envía notificación push a todos los administradores cuando se realiza una nueva venta
        """
        try:
            from django.contrib.auth.models import User
            from perfiles.fcm_service import send_push_to_user
            
            nota_venta = self.nota_venta
            cliente = nota_venta.cliente
            cliente_nombre = f"{cliente.nombre} {cliente.apellido}"
            
            # Obtener información de productos
            detalles = nota_venta.detalles.all()
            if detalles.exists():
                primer_detalle = detalles.first()
                cantidad_productos = sum(d.cantidad for d in detalles)
                
                if cantidad_productos == 1:
                    producto_texto = f"{primer_detalle.cantidad} {primer_detalle.producto.nombre}"
                elif detalles.count() == 1:
                    producto_texto = f"{primer_detalle.cantidad} {primer_detalle.producto.nombre}"
                else:
                    producto_texto = f"{primer_detalle.cantidad} {primer_detalle.producto.nombre} + {detalles.count() - 1} más"
            else:
                producto_texto = "productos"
            
            # Construir mensaje
            titulo = "💰 Nueva venta realizada"
            cuerpo = f"{cliente_nombre} realizó una compra de {producto_texto} por un valor de Bs. {float(nota_venta.total):.2f}"
            
            # Enviar a todos los administradores
            admins = User.objects.filter(is_staff=True, is_active=True)
            for admin in admins:
                send_push_to_user(
                    user=admin,
                    title=titulo,
                    body=cuerpo,
                    data={
                        'type': 'nueva_venta',
                        'nota_venta_id': str(nota_venta.id),
                        'screen': '/historial-ventas',
                        'cliente_nombre': cliente_nombre,
                        'total': str(nota_venta.total)
                    }
                )
                print(f"📱 Notificación enviada al admin: {admin.username}")
                
        except Exception as e:
            print(f"⚠️ Error enviando notificación admin: {str(e)}")
