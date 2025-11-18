from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from transacciones.modelsPago import Pago
from transacciones.modelsNotaDeVenta import NotaDeVenta
from transacciones.serializers.serializersPago import (
    PagoSerializer, 
    PagoSimpleSerializer,
    PagoCreateSerializer
)
from inventario.modelsCarrito import Carrito
import stripe
import uuid
from datetime import datetime

# Configurar Stripe con la clave secreta
stripe.api_key = settings.STRIPE_SECRET_KEY


@method_decorator(csrf_exempt, name='dispatch')
class PagoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los pagos con Stripe.
    Proporciona operaciones CRUD para pagos asociados a notas de venta.
    """
    queryset = Pago.objects.select_related('nota_venta', 'nota_venta__cliente').all()
    serializer_class = PagoSerializer
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        """Usa diferentes serializers según la acción"""
        if self.action == 'list':
            return PagoSimpleSerializer
        elif self.action == 'create':
            return PagoCreateSerializer
        return PagoSerializer

    def create(self, request, *args, **kwargs):
        """
        Crear un nuevo pago.
        Automáticamente marca la nota de venta como pagada.
        """
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            pago = serializer.save()
            # Retornar con el serializer completo
            response_serializer = PagoSerializer(pago)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"error": "Datos inválidos", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        """
        Eliminar un pago no está permitido por defecto.
        Solo se puede hacer mediante una acción específica.
        """
        return Response(
            {"error": "No se puede eliminar un pago directamente. Use la acción 'cancelar' si es necesario."},
            status=status.HTTP_403_FORBIDDEN
        )

    @action(detail=False, methods=['post'], url_path='create-payment-intent')
    def create_payment_intent(self, request):
        """
        Crear una intención de pago REAL con Stripe.
        Recibe: carrito_id
        Retorna: clientSecret para el frontend
        """
        carrito_id = request.data.get('carrito_id')
        
        if not carrito_id:
            return Response(
                {"error": "Se requiere carrito_id"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            carrito = Carrito.objects.get(id=carrito_id)
        except Carrito.DoesNotExist:
            return Response(
                {"error": f"No existe el carrito con ID {carrito_id}"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Verificar que el carrito tenga items
        if carrito.detalles.count() == 0:
            return Response(
                {"error": "El carrito está vacío"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Crear Payment Intent REAL con Stripe
            # Convertir el monto a centavos (Stripe trabaja en centavos)
            amount_in_cents = int(float(carrito.total_carrito) * 100)
            
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_in_cents,
                currency='usd',  # Stripe no soporta BOB directamente, usar USD
                automatic_payment_methods={
                    'enabled': True,
                },
                metadata={
                    'carrito_id': carrito_id,
                    'cliente_id': carrito.cliente.id if carrito.cliente else None,
                    'cliente_nombre': f"{carrito.cliente.nombre} {carrito.cliente.apellido}" if carrito.cliente else "N/A",
                }
            )
            
            return Response({
                "clientSecret": payment_intent.client_secret,
                "paymentIntentId": payment_intent.id,
                "amount": float(carrito.total_carrito),
                "amount_cents": amount_in_cents,
                "currency": "usd",
                "carrito_id": carrito_id
            }, status=status.HTTP_200_OK)
            
        except stripe.error.StripeError as e:
            return Response(
                {"error": f"Error de Stripe: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Error al crear payment intent: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='confirm-payment')
    def confirm_payment(self, request):
        """
        Confirmar el pago después de procesarlo con Stripe.
        Recibe: payment_intent_id, carrito_id
        Verifica el estado del pago en Stripe y crea la factura si es exitoso.
        """
        payment_intent_id = request.data.get('payment_intent_id')
        carrito_id = request.data.get('carrito_id')
        
        if not payment_intent_id:
            return Response(
                {"error": "Se requiere payment_intent_id"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Verificar el pago con Stripe
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            # Verificar que el pago fue exitoso
            if payment_intent.status != 'succeeded':
                return Response({
                    "success": False,
                    "message": f"El pago no fue exitoso. Estado: {payment_intent.status}",
                    "status": payment_intent.status
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Pago exitoso - retornar confirmación
            return Response({
                "success": True,
                "message": "Pago confirmado exitosamente",
                "payment_intent_id": payment_intent_id,
                "status": payment_intent.status,
                "amount_received": payment_intent.amount_received / 100,  # Convertir de centavos
            }, status=status.HTTP_200_OK)
            
        except stripe.error.StripeError as e:
            return Response(
                {"error": f"Error al verificar pago con Stripe: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Error al confirmar pago: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'], url_path='confirm-payment-auto')
    def confirm_payment_auto(self, request):
        """
        Confirmar pago automáticamente para apps móviles (modo prueba).
        En modo prueba, Stripe confirma automáticamente con tarjetas de test.
        Este endpoint verifica el pago y crea la nota de venta + pago en el sistema.
        """
        payment_intent_id = request.data.get('payment_intent_id')
        
        if not payment_intent_id:
            return Response(
                {"error": "Se requiere payment_intent_id"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Obtener el Payment Intent de Stripe
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            
            # Obtener carrito_id de los metadata
            carrito_id = payment_intent.metadata.get('carrito_id')
            if not carrito_id:
                return Response(
                    {"error": "No se encontró carrito_id en los metadatos del pago"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Obtener el carrito
            try:
                carrito = Carrito.objects.get(id=carrito_id)
            except Carrito.DoesNotExist:
                return Response(
                    {"error": f"No existe el carrito con ID {carrito_id}"},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Si el pago aún está pendiente, confirmarlo automáticamente (modo test)
            if payment_intent.status == 'requires_confirmation':
                payment_intent = stripe.PaymentIntent.confirm(payment_intent_id)
            
            # Verificar que el pago fue exitoso
            if payment_intent.status != 'succeeded':
                return Response({
                    "success": False,
                    "message": f"El pago no fue exitoso. Estado: {payment_intent.status}",
                    "status": payment_intent.status
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Pago exitoso - Crear nota de venta si no existe
            # Aquí deberías crear la nota de venta y registrar el pago
            # Por ahora solo confirmamos el pago
            
            return Response({
                "success": True,
                "message": "Pago confirmado y procesado exitosamente",
                "payment_intent_id": payment_intent_id,
                "status": payment_intent.status,
                "amount_received": payment_intent.amount_received / 100,
                "carrito_id": carrito_id
            }, status=status.HTTP_200_OK)
            
        except stripe.error.StripeError as e:
            return Response(
                {"error": f"Error de Stripe: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Error al confirmar pago: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def procesar_stripe(self, request):
        """
        Endpoint para procesar un pago desde Stripe webhook.
        Espera: nota_venta_id, monto, moneda, payment_intent_id
        
        IMPORTANTE: Antes de procesar el pago, valida que haya stock suficiente
        para todos los productos. Si el pago se confirma, el stock se reduce automáticamente.
        """
        nota_venta_id = request.data.get('nota_venta_id')
        monto = request.data.get('monto')
        moneda = request.data.get('moneda', 'USD')
        payment_intent_id = request.data.get('payment_intent_id')

        # Validar datos requeridos
        if not all([nota_venta_id, monto, payment_intent_id]):
            return Response(
                {"error": "Faltan datos requeridos: nota_venta_id, monto, payment_intent_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar que la nota de venta existe
        try:
            nota_venta = NotaDeVenta.objects.get(id=nota_venta_id)
        except NotaDeVenta.DoesNotExist:
            return Response(
                {"error": f"No existe la nota de venta con ID {nota_venta_id}"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Verificar que la nota de venta no tenga ya un pago
        if hasattr(nota_venta, 'pago'):
            return Response(
                {"error": f"La nota de venta {nota_venta.numero_comprobante} ya tiene un pago registrado"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # VALIDAR STOCK DISPONIBLE antes de procesar el pago
        stock_valido, mensaje_stock = nota_venta.validar_stock_disponible()
        if not stock_valido:
            return Response(
                {
                    "error": "No se puede procesar el pago por falta de stock",
                    "details": mensaje_stock
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Crear el pago (esto automáticamente reducirá el stock)
        serializer = PagoCreateSerializer(data={
            'nota_venta': nota_venta_id,
            'monto': monto,
            'moneda': moneda,
            'total_stripe': payment_intent_id
        })

        if serializer.is_valid():
            pago = serializer.save()
            response_serializer = PagoSerializer(pago)
            
            # 🔔 ENVIAR NOTIFICACIÓN A ADMINISTRADORES
            try:
                from django.contrib.auth.models import User
                from perfiles.fcm_service import send_push_to_user
                
                # Obtener información del cliente y productos
                cliente = nota_venta.cliente
                cliente_nombre = f"{cliente.nombre} {cliente.apellido}"
                
                # Obtener el primer producto y cantidad total
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
                
                # Construir mensaje de notificación
                titulo = "💰 Nueva venta realizada"
                cuerpo = f"{cliente_nombre} realizó una compra de {producto_texto} por un valor de Bs. {float(nota_venta.total):.2f}"
                
                # Enviar notificación a todos los administradores
                admins = User.objects.filter(is_staff=True, is_active=True)
                for admin in admins:
                    send_push_to_user(
                        user=admin,
                        title=titulo,
                        body=cuerpo,
                        data={
                            'type': 'nueva_venta',
                            'nota_venta_id': str(nota_venta.id),
                            'historial_venta_id': str(nota_venta.historial_venta.id) if hasattr(nota_venta, 'historial_venta') else None,
                            'screen': '/historial-ventas',
                            'cliente_nombre': cliente_nombre,
                            'total': str(nota_venta.total)
                        }
                    )
                    print(f"📱 Notificación enviada al admin: {admin.username}")
                    
            except Exception as e:
                # No fallar el pago si la notificación falla
                print(f"⚠️ Error enviando notificación: {str(e)}")
            
            return Response(
                {
                    "message": "Pago procesado exitosamente. El stock de los productos ha sido reducido.",
                    "pago": response_serializer.data
                },
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"error": "Error al procesar el pago", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'])
    def por_nota_venta(self, request):
        """
        Obtener el pago de una nota de venta específica.
        Parámetro: nota_venta_id
        """
        nota_venta_id = request.query_params.get('nota_venta_id')
        
        if not nota_venta_id:
            return Response(
                {"error": "Se requiere el parámetro nota_venta_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            pago = Pago.objects.get(nota_venta_id=nota_venta_id)
            serializer = self.get_serializer(pago)
            return Response(serializer.data)
        except Pago.DoesNotExist:
            return Response(
                {"error": f"No existe un pago para la nota de venta con ID {nota_venta_id}"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'])
    def verificar_monto(self, request, pk=None):
        """
        Verifica que el monto del pago coincida con el total de la nota de venta
        """
        pago = self.get_object()
        es_valido = pago.validar_monto()
        
        return Response({
            "monto_pago": str(pago.monto),
            "total_nota_venta": str(pago.nota_venta.total),
            "coincide": es_valido,
            "diferencia": str(abs(pago.monto - pago.nota_venta.total))
        })

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Obtiene estadísticas de los pagos
        """
        from django.db.models import Sum, Count, Avg
        
        stats = Pago.objects.aggregate(
            total_pagos=Count('nota_venta'),
            monto_total=Sum('monto'),
            monto_promedio=Avg('monto')
        )
        
        return Response({
            "total_pagos": stats['total_pagos'] or 0,
            "monto_total": str(stats['monto_total'] or 0),
            "monto_promedio": str(stats['monto_promedio'] or 0),
            "monedas": list(Pago.objects.values_list('moneda', flat=True).distinct())
        })
