"""
Script de prueba para verificar el endpoint de reportes naturales
"""
import requests
import json

BASE_URL = "http://192.168.100.6:8000/api"

# Token de prueba - reemplaza con un token válido
TOKEN = "TU_TOKEN_AQUI"

def test_generar_reporte_natural():
    """Prueba el endpoint de generación de reportes naturales"""
    
    url = f"{BASE_URL}/analitica/reportes/generar-natural/"
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "consulta": "productos con stock bajo",
        "formato": "PDF"
    }
    
    print("=" * 60)
    print("TEST: Generar Reporte Natural")
    print("=" * 60)
    print(f"URL: {url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Body: {json.dumps(data, indent=2)}")
    print("-" * 60)
    
    try:
        response = requests.post(url, json=data, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print("-" * 60)
        print("Response Body:")
        
        try:
            response_json = response.json()
            print(json.dumps(response_json, indent=2, ensure_ascii=False))
        except:
            print(response.text)
            
    except Exception as e:
        print(f"ERROR: {e}")

def test_obtener_ejemplos():
    """Prueba el endpoint de ejemplos"""
    
    url = f"{BASE_URL}/analitica/reportes/ejemplos_nl/"
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    print("\n" + "=" * 60)
    print("TEST: Obtener Ejemplos NL")
    print("=" * 60)
    print(f"URL: {url}")
    print("-" * 60)
    
    try:
        response = requests.get(url, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print("-" * 60)
        print("Response Body:")
        
        try:
            response_json = response.json()
            print(json.dumps(response_json, indent=2, ensure_ascii=False))
        except:
            print(response.text)
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    print("\n🔍 TESTS DE API DE REPORTES")
    print("=" * 60)
    print("⚠️  IMPORTANTE: Actualiza la variable TOKEN con un token válido")
    print("=" * 60)
    
    if TOKEN == "TU_TOKEN_AQUI":
        print("\n❌ Por favor, actualiza el TOKEN en el script antes de ejecutar")
        print("\nPara obtener un token:")
        print("1. Inicia sesión en la app")
        print("2. Copia el token desde flutter_secure_storage")
        print("3. O usa el endpoint /api/perfiles/login/\n")
    else:
        test_obtener_ejemplos()
        test_generar_reporte_natural()
