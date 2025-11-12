from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q
from datetime import datetime, timedelta
from transacciones.modelsListadoHistoricoVentas import ListadoHistoricoVentas
from transacciones.modelsNotaDeVenta import NotaDeVenta
from transacciones.serializers.serializersListadoHistoricoVentas import (
    ListadoHistoricoVentasSerializer,
    ListadoHistoricoVentasSimpleSerializer,
    ListadoHistoricoVentasDetalleSerializer,
    EstadisticasVentasSerializer,
    CrearHistorialVentaSerializer,
    ActualizarEstadoPagoSerializer
)


@method_decorator(csrf_exempt, name='dispatch')
class ListadoHistoricoVentasViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar el Listado Histórico de Ventas.
    
    Endpoints disponibles:
    - GET /api/transacciones/historial-ventas/ - Listar todas las ventas
    - GET /api/transacciones/historial-ventas/{id}/ - Detalle de una venta
    - POST /api/transacciones/historial-ventas/ - Crear registro histórico
    - PUT /api/transacciones/historial-ventas/{id}/ - Actualizar venta
    - DELETE /api/transacciones/historial-ventas/{id}/ - Eliminar venta
    
    Acciones personalizadas:
    - GET /api/transacciones/historial-ventas/estadisticas/ - Estadísticas generales
    - GET /api/transacciones/historial-ventas/por_cliente/?ci=XXX - Ventas de un cliente
    - GET /api/transacciones/historial-ventas/por_fecha/?inicio=XXX&fin=XXX - Ventas por rango
    - GET /api/transacciones/historial-ventas/recientes/ - Últimas ventas
    - POST /api/transacciones/historial-ventas/{id}/actualizar_estado/ - Actualizar estado
    - POST /api/transacciones/historial-ventas/{id}/anular/ - Anular venta
    - POST /api/transacciones/historial-ventas/crear_desde_factura/ - Crear desde factura
    """
    
    queryset = ListadoHistoricoVentas.objects.select_related('nota_venta', 'nota_venta__cliente').all()
    serializer_class = ListadoHistoricoVentasSerializer
    permission_classes = [AllowAny]
    
    # Filtros y búsqueda
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['numero_venta', 'cliente_nombre', 'cliente_ci', 'referencia_pago']
    ordering_fields = ['fecha_venta', 'total', 'estado_pago']
    ordering = ['-fecha_venta']  # Por defecto ordenar por fecha descendente
    
    def get_serializer_class(self):
        """Usa diferentes serializers según la acción"""
        if self.action == 'list':
            return ListadoHistoricoVentasSimpleSerializer
        elif self.action == 'retrieve':
            return ListadoHistoricoVentasDetalleSerializer
        elif self.action == 'crear_desde_factura':
            return CrearHistorialVentaSerializer
        elif self.action == 'actualizar_estado':
            return ActualizarEstadoPagoSerializer
        return ListadoHistoricoVentasSerializer
    
    def get_queryset(self):
        """
        Filtra el queryset basado en parámetros de búsqueda opcionales
        """
        queryset = super().get_queryset()
        
        # Filtrar por estado de pago
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado_pago=estado)
        
        # Filtrar por método de pago
        metodo = self.request.query_params.get('metodo', None)
        if metodo:
            queryset = queryset.filter(metodo_pago__icontains=metodo)
        
        # Filtrar por rango de fechas
        fecha_inicio = self.request.query_params.get('fecha_inicio', None)
        fecha_fin = self.request.query_params.get('fecha_fin', None)
        
        if fecha_inicio:
            queryset = queryset.filter(fecha_venta__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha_venta__lte=fecha_fin)
        
        # Filtrar por cliente
        cliente_ci = self.request.query_params.get('cliente_ci', None)
        if cliente_ci:
            queryset = queryset.filter(cliente_ci=cliente_ci)
        
        # Filtrar por monto mínimo y máximo
        monto_min = self.request.query_params.get('monto_min', None)
        monto_max = self.request.query_params.get('monto_max', None)
        
        if monto_min:
            queryset = queryset.filter(total__gte=monto_min)
        if monto_max:
            queryset = queryset.filter(total__lte=monto_max)
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        Lista todas las ventas históricas con filtros opcionales
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Paginación
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Obtiene el detalle completo de una venta incluyendo productos
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """
        Crea un nuevo registro en el historial.
        Normalmente esto se hace automáticamente desde la factura.
        """
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            historial = serializer.save()
            response_serializer = ListadoHistoricoVentasDetalleSerializer(historial)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"error": "Datos inválidos", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        """
        Actualiza un registro del historial
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(
                {"error": "Datos inválidos", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        """
        Elimina un registro del historial (solo permitido para registros específicos)
        """
        instance = self.get_object()
        
        # Verificar que el registro pueda ser eliminado
        if instance.estado_pago == 'completado':
            return Response(
                {"error": "No se puede eliminar una venta completada. Use la acción 'anular' en su lugar."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        instance.delete()
        return Response(
            {"message": "Registro eliminado correctamente"},
            status=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=False, methods=['get'], url_path='estadisticas')
    def estadisticas(self, request):
        """
        Obtiene estadísticas generales de ventas.
        
        Parámetros opcionales:
        - fecha_inicio: Filtrar desde esta fecha
        - fecha_fin: Filtrar hasta esta fecha
        
        Ejemplo: /api/transacciones/historial-ventas/estadisticas/?fecha_inicio=2025-01-01&fecha_fin=2025-12-31
        """
        fecha_inicio = request.query_params.get('fecha_inicio', None)
        fecha_fin = request.query_params.get('fecha_fin', None)
        
        # Convertir strings a datetime si existen
        if fecha_inicio:
            fecha_inicio = datetime.fromisoformat(fecha_inicio)
        if fecha_fin:
            fecha_fin = datetime.fromisoformat(fecha_fin)
        
        # Obtener estadísticas
        stats = ListadoHistoricoVentas.obtener_estadisticas(fecha_inicio, fecha_fin)
        
        # Serializar
        serializer = EstadisticasVentasSerializer(stats)
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='por_cliente')
    def por_cliente(self, request):
        """
        Obtiene todas las ventas de un cliente específico.
        
        Parámetro requerido:
        - ci: Cédula de identidad del cliente
        
        Ejemplo: /api/transacciones/historial-ventas/por_cliente/?ci=12345678
        """
        cliente_ci = request.query_params.get('ci', None)
        
        if not cliente_ci:
            return Response(
                {"error": "Se requiere el parámetro 'ci'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ventas = ListadoHistoricoVentas.obtener_ventas_por_cliente(cliente_ci)
        serializer = ListadoHistoricoVentasSimpleSerializer(ventas, many=True)
        
        return Response({
            "cliente_ci": cliente_ci,
            "total_ventas": ventas.count(),
            "ventas": serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='por_fecha')
    def por_fecha(self, request):
        """
        Obtiene ventas en un rango de fechas.
        
        Parámetros requeridos:
        - inicio: Fecha de inicio (formato: YYYY-MM-DD)
        - fin: Fecha de fin (formato: YYYY-MM-DD)
        
        Ejemplo: /api/transacciones/historial-ventas/por_fecha/?inicio=2025-01-01&fin=2025-01-31
        """
        fecha_inicio = request.query_params.get('inicio', None)
        fecha_fin = request.query_params.get('fin', None)
        
        if not all([fecha_inicio, fecha_fin]):
            return Response(
                {"error": "Se requieren los parámetros 'inicio' y 'fin'"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            fecha_inicio = datetime.fromisoformat(fecha_inicio)
            fecha_fin = datetime.fromisoformat(fecha_fin)
        except ValueError:
            return Response(
                {"error": "Formato de fecha inválido. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        ventas = ListadoHistoricoVentas.obtener_ventas_por_fecha(fecha_inicio, fecha_fin)
        serializer = ListadoHistoricoVentasSimpleSerializer(ventas, many=True)
        
        return Response({
            "fecha_inicio": fecha_inicio.date(),
            "fecha_fin": fecha_fin.date(),
            "total_ventas": ventas.count(),
            "ventas": serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='recientes')
    def recientes(self, request):
        """
        Obtiene las ventas más recientes.
        
        Parámetro opcional:
        - limit: Cantidad de ventas a retornar (por defecto 10)
        
        Ejemplo: /api/transacciones/historial-ventas/recientes/?limit=20
        """
        limit = int(request.query_params.get('limit', 10))
        
        ventas = self.get_queryset()[:limit]
        serializer = ListadoHistoricoVentasSimpleSerializer(ventas, many=True)
        
        return Response({
            "total": len(ventas),
            "ventas": serializer.data
        })
    
    @action(detail=True, methods=['post'], url_path='actualizar_estado')
    def actualizar_estado(self, request, pk=None):
        """
        Actualiza el estado de pago de una venta.
        
        Body:
        {
            "estado_pago": "completado" | "pendiente" | "fallido" | "anulado"
        }
        """
        historial = self.get_object()
        serializer = ActualizarEstadoPagoSerializer(historial, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            response_serializer = ListadoHistoricoVentasSerializer(historial)
            return Response({
                "message": "Estado actualizado correctamente",
                "venta": response_serializer.data
            })
        else:
            return Response(
                {"error": "Datos inválidos", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], url_path='anular')
    def anular(self, request, pk=None):
        """
        Anula una venta y su factura asociada.
        
        POST /api/transacciones/historial-ventas/{id}/anular/
        """
        historial = self.get_object()
        
        # Verificar que no esté ya anulada
        if historial.estado_pago == 'anulado':
            return Response(
                {"error": "Esta venta ya está anulada"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Anular la venta
        historial.marcar_como_anulada()
        
        serializer = ListadoHistoricoVentasSerializer(historial)
        return Response({
            "message": "Venta anulada correctamente",
            "venta": serializer.data
        })
    
    @action(detail=False, methods=['post'], url_path='crear_desde_nota_venta')
    def crear_desde_nota_venta(self, request):
        """
        Crea un registro en el historial a partir de una nota de venta existente.
        
        Body:
        {
            "nota_venta_id": 123
        }
        """
        serializer = CrearHistorialVentaSerializer(data=request.data)
        
        if serializer.is_valid():
            historial = serializer.save()
            response_serializer = ListadoHistoricoVentasDetalleSerializer(historial)
            return Response({
                "message": "Registro histórico creado correctamente",
                "venta": response_serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"error": "Datos inválidos", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], url_path='por_estado')
    def por_estado(self, request):
        """
        Obtiene ventas agrupadas por estado de pago.
        
        Ejemplo: /api/transacciones/historial-ventas/por_estado/
        """
        from django.db.models import Count, Sum
        
        resumen = ListadoHistoricoVentas.objects.values('estado_pago').annotate(
            cantidad=Count('nota_venta'),
            total_monto=Sum('total')
        ).order_by('estado_pago')
        
        return Response({
            "resumen_por_estado": list(resumen)
        })
    
    @action(detail=False, methods=['get'], url_path='top_clientes')
    def top_clientes(self, request):
        """
        Obtiene los clientes con más compras.
        
        Parámetro opcional:
        - limit: Cantidad de clientes a retornar (por defecto 10)
        
        Ejemplo: /api/transacciones/historial-ventas/top_clientes/?limit=5
        """
        from django.db.models import Count, Sum
        
        limit = int(request.query_params.get('limit', 10))
        
        top_clientes = ListadoHistoricoVentas.objects.values(
            'cliente_ci', 'cliente_nombre'
        ).annotate(
            total_compras=Count('nota_venta'),
            total_gastado=Sum('total')
        ).order_by('-total_gastado')[:limit]
        
        return Response({
            "top_clientes": list(top_clientes)
        })
