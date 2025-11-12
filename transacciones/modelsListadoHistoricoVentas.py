from django.db import models
from django.db.models import Q, Sum, Count
from .modelsNotaDeVenta import NotaDeVenta
from .modelsPago import Pago
from perfiles.models import Cliente


class ListadoHistoricoVentas(models.Model):
    """
    Modelo para gestionar el listado histórico de ventas.
    Este modelo actúa como una vista materializada o registro histórico
    de todas las transacciones de ventas realizadas en el sistema.
    
    Relaciona: Cliente -> NotaDeVenta -> Pago
    """
    
    # Relación con la nota de venta (cada registro del histórico está asociado a una nota de venta)
    nota_venta = models.OneToOneField(
        NotaDeVenta,
        on_delete=models.CASCADE,
        related_name='historial_venta',
        primary_key=True,
        help_text="Nota de venta asociada a esta venta"
    )
    
    # Información del cliente (denormalizada para consultas rápidas)
    cliente_nombre = models.CharField(
        max_length=200,
        help_text="Nombre completo del cliente"
    )
    cliente_ci = models.CharField(
        max_length=20,
        help_text="CI del cliente"
    )
    cliente_email = models.EmailField(
        blank=True,
        null=True,
        help_text="Email del cliente"
    )
    
    # Información de la venta
    numero_venta = models.CharField(
        max_length=50,
        unique=True,
        help_text="Número de comprobante de la venta"
    )
    fecha_venta = models.DateTimeField(
        help_text="Fecha y hora de la venta"
    )
    
    # Montos
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Subtotal de la venta"
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total de la venta"
    )
    
    # Información del pago
    metodo_pago = models.CharField(
        max_length=50,
        default='Stripe',
        help_text="Método de pago utilizado"
    )
    estado_pago = models.CharField(
        max_length=20,
        choices=[
            ('pendiente', 'Pendiente'),
            ('completado', 'Completado'),
            ('fallido', 'Fallido'),
            ('anulado', 'Anulado'),
        ],
        default='pendiente',
        help_text="Estado del pago"
    )
    fecha_pago = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Fecha en que se completó el pago"
    )
    referencia_pago = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="ID de referencia del pago (Stripe payment_intent_id)"
    )
    
    # Información adicional
    notas = models.TextField(
        blank=True,
        null=True,
        help_text="Notas u observaciones de la venta"
    )
    
    # Auditoría
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        help_text="Fecha de registro en el histórico"
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        help_text="Última actualización del registro"
    )
    
    class Meta:
        verbose_name = 'Historial de Venta'
        verbose_name_plural = 'Listado Histórico de Ventas'
        ordering = ['-fecha_venta']
        indexes = [
            models.Index(fields=['-fecha_venta']),
            models.Index(fields=['estado_pago']),
            models.Index(fields=['cliente_ci']),
            models.Index(fields=['numero_venta']),
        ]
    
    def __str__(self):
        return f"Venta {self.numero_venta} - {self.cliente_nombre} - Bs. {self.total} ({self.estado_pago})"
    
    @classmethod
    def crear_desde_nota_venta(cls, nota_venta):
        """
        Crea un registro en el histórico a partir de una nota de venta.
        Se llama automáticamente cuando se crea/actualiza una nota de venta con pago.
        SOLO registra notas de venta que tengan pago asociado y estén pagadas.
        """
        # VALIDACIÓN: Solo registrar si la nota de venta tiene pago y está pagada
        if nota_venta.estado != 'pagada':
            raise ValueError(
                f"No se puede crear registro histórico: "
                f"La nota de venta debe estar en estado 'pagada', actualmente está '{nota_venta.estado}'"
            )
        
        if not hasattr(nota_venta, 'pago'):
            raise ValueError(
                "No se puede crear registro histórico: "
                "La nota de venta no tiene un pago asociado"
            )
        
        cliente = nota_venta.cliente
        pago = nota_venta.pago
        
        # Verificar si ya existe el registro
        historial, created = cls.objects.get_or_create(
            nota_venta=nota_venta,
            defaults={
                'cliente_nombre': f"{cliente.nombre} {cliente.apellido}",
                'cliente_ci': cliente.ci,
                'cliente_email': cliente.email if hasattr(cliente, 'email') else None,
                'numero_venta': nota_venta.numero_comprobante,
                'fecha_venta': nota_venta.fecha,
                'subtotal': nota_venta.subtotal,
                'total': nota_venta.total,
                'fecha_pago': pago.fecha,
                'referencia_pago': pago.total_stripe,
                'metodo_pago': 'Stripe',
                'estado_pago': 'completado',
            }
        )
        
        # Si el registro ya existía, actualizarlo con la información del pago
        if not created:
            historial.fecha_pago = pago.fecha
            historial.referencia_pago = pago.total_stripe
            historial.metodo_pago = 'Stripe'
            historial.estado_pago = 'completado'
            historial.save()
        
        return historial
    
    @classmethod
    def actualizar_estado_pago(cls, nota_venta_id, nuevo_estado):
        """
        Actualiza el estado de pago de una venta en el histórico
        """
        try:
            historial = cls.objects.get(nota_venta_id=nota_venta_id)
            historial.estado_pago = nuevo_estado
            historial.save()
            return historial
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def obtener_estadisticas(cls, fecha_inicio=None, fecha_fin=None):
        """
        Obtiene estadísticas del histórico de ventas
        """
        queryset = cls.objects.all()
        
        if fecha_inicio:
            queryset = queryset.filter(fecha_venta__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha_venta__lte=fecha_fin)
        
        stats = queryset.aggregate(
            total_ventas=Count('nota_venta'),
            total_ingresos=Sum('total'),
            ventas_completadas=Count('nota_venta', filter=Q(estado_pago='completado')),
            ventas_pendientes=Count('nota_venta', filter=Q(estado_pago='pendiente')),
        )
        
        return stats
    
    @classmethod
    def obtener_ventas_por_cliente(cls, cliente_ci):
        """
        Obtiene todas las ventas de un cliente específico
        """
        return cls.objects.filter(cliente_ci=cliente_ci)
    
    @classmethod
    def obtener_ventas_por_fecha(cls, fecha_inicio, fecha_fin):
        """
        Obtiene ventas en un rango de fechas
        """
        return cls.objects.filter(
            fecha_venta__gte=fecha_inicio,
            fecha_venta__lte=fecha_fin
        )
    
    def marcar_como_anulada(self):
        """
        Marca la venta como anulada
        """
        self.estado_pago = 'anulado'
        self.save()
        
        # También anular la nota de venta asociada
        if self.nota_venta:
            self.nota_venta.anular()
    
    def get_detalles_productos(self):
        """
        Obtiene los detalles de productos de esta venta
        """
        if self.nota_venta and hasattr(self.nota_venta, 'detalles'):
            return self.nota_venta.detalles.all()
        return []
    
    def get_cantidad_items(self):
        """
        Obtiene la cantidad de items (productos diferentes) de esta venta
        """
        if self.nota_venta and hasattr(self.nota_venta, 'detalles'):
            return self.nota_venta.detalles.count()
        return 0
    
    def calcular_ganancia_neta(self):
        """
        Calcula la ganancia neta (total sin costos)
        """
        return self.total

