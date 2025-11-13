"""
Script de prueba para consultas de detalles de ventas
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_exa2.settings')
django.setup()

from analitica.utils.nl_parser import interpretar_consulta

# Casos de prueba
consultas_prueba = [
    "Quiero un reporte de ventas del mes de septiembre, agrupado por producto",
    "Productos vendidos en septiembre",
    "Detalles de ventas pagadas este mes",
    "Items vendidos con sus clientes en octubre",
    "Ventas agrupadas por producto este año",
]

print("=" * 80)
print("PRUEBA DE CONSULTAS DE DETALLES DE VENTAS")
print("=" * 80)

for consulta in consultas_prueba:
    print(f"\n🔍 Consulta: '{consulta}'")
    print("-" * 80)
    
    resultado = interpretar_consulta(consulta)
    
    if resultado.get('error'):
        print(f"❌ Error: {resultado['error']}")
    else:
        print(f"✅ Entidad detectada: {resultado['entidad']}")
        print(f"📋 Filtros aplicados:")
        for filtro, valor in resultado['filtros'].items():
            print(f"   - {filtro}: {valor}")
        
        if not resultado['filtros']:
            print("   (Sin filtros)")
        
        print(f"📊 Campos sugeridos:")
        for campo in resultado['campos_sugeridos']:
            print(f"   - {campo}")

print("\n" + "=" * 80)
print("FIN DE LAS PRUEBAS")
print("=" * 80)
