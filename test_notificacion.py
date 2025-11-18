"""
Script de prueba para notificaciones push
Ejecutar: python test_notificacion.py
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_exa2.settings')
django.setup()

from django.contrib.auth.models import User
from perfiles.fcm_service import send_push_to_user
from perfiles.models_device_token import DeviceToken


print("=" * 70)
print("🧪 PRUEBA DE NOTIFICACIONES PUSH - SmartSales")
print("=" * 70)

# Verificar configuración de Firebase
from django.conf import settings
if not settings.FIREBASE_PROJECT_ID or not settings.FIREBASE_SERVICE_ACCOUNT_JSON:
    print("\n❌ ERROR: Firebase no está configurado")
    print("   Verifica que las variables estén en .env:")
    print("   - FIREBASE_PROJECT_ID")
    print("   - FIREBASE_SERVICE_ACCOUNT_JSON")
    sys.exit(1)

print(f"\n✅ Firebase configurado: {settings.FIREBASE_PROJECT_ID}")

# Verificar usuarios con tokens
print("\n📱 Buscando dispositivos registrados...")
tokens = DeviceToken.objects.filter(is_active=True)

if not tokens.exists():
    print("❌ No hay dispositivos registrados")
    print("\n📝 Para registrar un dispositivo:")
    print("   1. Abre la app Flutter en tu celular")
    print("   2. Inicia sesión")
    print("   3. Espera a que se registre el token")
    print("   4. Ejecuta este script nuevamente")
    sys.exit(1)

print(f"✅ Encontrados {tokens.count()} dispositivo(s) activo(s)")

# Mostrar usuarios disponibles
users_with_tokens = User.objects.filter(device_tokens__is_active=True).distinct()
print("\n👥 Usuarios con dispositivos registrados:")
for idx, user in enumerate(users_with_tokens, 1):
    token_count = user.device_tokens.filter(is_active=True).count()
    print(f"   {idx}. {user.username} - {token_count} dispositivo(s)")

# Seleccionar usuario (puedes cambiarlo por el username que quieras)
print("\n" + "=" * 70)
username = input("Ingresa el username (o Enter para usar el primero): ").strip()

if username:
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"❌ Usuario '{username}' no encontrado")
        sys.exit(1)
else:
    user = users_with_tokens.first()

print(f"👤 Usuario seleccionado: {user.username}")

# Mostrar tokens del usuario
user_tokens = DeviceToken.objects.filter(user=user, is_active=True)
print(f"\n📱 {user_tokens.count()} dispositivo(s):")
for token in user_tokens:
    print(f"   - {token.platform}: {token.token[:40]}...")

# Enviar notificación
print("\n" + "=" * 70)
print("📤 Enviando notificación de prueba...")
print("=" * 70)

resultado = send_push_to_user(
    user=user,
    title="🎉 ¡Prueba exitosa!",
    body="Las notificaciones push están funcionando correctamente en SmartSales",
    data={
        'type': 'test',
        'timestamp': str(os.times()),
        'screen': '/perfil'
    }
)

# Mostrar resultados
print(f"\n📊 RESULTADOS:")
print(f"   Total: {resultado['total']}")
print(f"   ✅ Exitosos: {resultado['successful']}")
print(f"   ❌ Fallidos: {resultado['failed']}")

if resultado['errors']:
    print(f"\n⚠️ Errores:")
    for error in resultado['errors']:
        print(f"   - {error}")

if resultado['successful'] > 0:
    print("\n✅ ¡NOTIFICACIÓN ENVIADA!")
    print("   Revisa tu dispositivo móvil")
else:
    print("\n❌ No se pudo enviar la notificación")
    print("   Verifica:")
    print("   - Token FCM válido")
    print("   - Configuración de Firebase")
    print("   - Conectividad a internet")

print("\n" + "=" * 70)
