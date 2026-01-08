"""Script para probar que la API está funcionando."""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Probar el endpoint de health check."""
    print("1. Probando health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code == 200
    print("   ✓ Health check OK\n")

def test_root_endpoint():
    """Probar el endpoint raíz."""
    print("2. Probando endpoint raíz...")
    response = requests.get(f"{BASE_URL}/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("   ✓ Root endpoint OK\n")

def test_docs():
    """Probar que la documentación está disponible."""
    print("3. Probando documentación...")
    response = requests.get(f"{BASE_URL}/docs")
    print(f"   Status: {response.status_code}")
    assert response.status_code == 200
    print("   ✓ Documentación disponible en http://localhost:8000/docs\n")

def test_openapi_schema():
    """Probar que el schema OpenAPI está disponible."""
    print("4. Probando schema OpenAPI...")
    response = requests.get(f"{BASE_URL}/openapi.json")
    print(f"   Status: {response.status_code}")
    assert response.status_code == 200
    schema = response.json()
    print(f"   Título: {schema.get('info', {}).get('title')}")
    print(f"   Versión: {schema.get('info', {}).get('version')}")
    print(f"   Endpoints disponibles: {len(schema.get('paths', {}))}")
    print("   ✓ OpenAPI schema OK\n")

def main():
    """Ejecutar todas las pruebas."""
    print("=" * 60)
    print("PRUEBAS DE LA API - SIA SOFKA U")
    print("=" * 60)
    print()
    
    try:
        test_health_check()
        test_root_endpoint()
        test_docs()
        test_openapi_schema()
        
        print("=" * 60)
        print("✓ TODAS LAS PRUEBAS PASARON")
        print("=" * 60)
        print()
        print("La API está funcionando correctamente!")
        print()
        print("Endpoints disponibles:")
        print("  - Documentación interactiva: http://localhost:8000/docs")
        print("  - Documentación alternativa: http://localhost:8000/redoc")
        print("  - Health check: http://localhost:8000/health")
        print("  - API Base: http://localhost:8000/api/v1")
        print()
        
    except requests.exceptions.ConnectionError:
        print("✗ ERROR: No se puede conectar a la API")
        print("  Asegúrate de que el servicio esté corriendo:")
        print("  docker-compose up -d")
        print()
    except AssertionError as e:
        print(f"✗ ERROR: {e}")
        print()
    except Exception as e:
        print(f"✗ ERROR: {e}")
        print()

if __name__ == "__main__":
    main()

