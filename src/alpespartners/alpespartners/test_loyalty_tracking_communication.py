"""
Script de testing para validar la comunicación completa entre Loyalty y Tracking Services.
Este script simula el flujo completo:
1. Crear embajador
2. Activar embajador  
3. Registrar referido (evento ReferidoRegistrado)
4. Verificar que Tracking procesó el evento
"""

import requests
import time
import json

# Configuración
BASE_URL = "http://localhost:8000/v1"
HEADERS = {"Content-Type": "application/json"}

def test_comunicacion_loyalty_tracking():
    """
    Test de comunicación completa entre servicios.
    """
    print("INICIANDO TEST DE COMUNICACIÓN LOYALTY ↔ TRACKING")
    print("=" * 60)
    
    try:
        # Paso 1: Crear embajador
        print("1. Creando embajador...")
        embajador_data = {
            "nombre": "María García",
            "email": "maria.f@example.com",
            "id_partner": "partner-123"
        }
        
        response = requests.post(
            f"{BASE_URL}/loyalty/embajadores",
            json=embajador_data,
            headers=HEADERS
        )
        
        if response.status_code != 200:
            print(f"Error creando embajador: {response.text}")
            return False
            
        result = response.json()
        id_embajador = result["id_embajador"]
        print(f"Embajador creado: {id_embajador}")
        
        # Paso 2: Activar embajador
        print("\n 2. Activando embajador...")
        activar_data = {"id_embajador": id_embajador}
        
        response = requests.post(
            f"{BASE_URL}/loyalty/embajadores/activar",
            json=activar_data,
            headers=HEADERS
        )
        
        if response.status_code != 200:
            print(f"Error activando embajador: {response.text}")
            return False
            
        print("Embajador activado exitosamente")
        
        # Paso 3: Registrar referido (esto dispara el evento)
        print("\n 3. Registrando referido (disparando evento)...")
        referido_data = {
            "id_embajador": id_embajador,
            "email_referido": "cliente.referido@example.com",
            "nombre_referido": "Cliente Referido",
            "valor_conversion": 150.00,
            "porcentaje_comision": 10.0
        }
        
        response = requests.post(
            f"{BASE_URL}/loyalty/referidos",
            json=referido_data,
            headers=HEADERS
        )
        
        if response.status_code != 200:
            print(f"Error registrando referido: {response.text}")
            return False
            
        result = response.json()
        id_referido = result["id_referido"]
        print(f"Referido registrado: {id_referido}")
        print(f"Evento publicado: {result['evento_publicado']}")
        
        # Paso 4: Verificar métricas del embajador
        print("\n 4. Verificando métricas del embajador...")
        
        response = requests.get(
            f"{BASE_URL}/loyalty/embajadores/{id_embajador}/metricas",
            headers=HEADERS
        )
        
        if response.status_code != 200:
            print(f"Error obteniendo embajador: {response.text}")
            return False
            
        embajador_info = response.json()
        print(f"Métricas del embajador:")
        print(f"   - Total referidos: {embajador_info['total_referidos']}")
        print(f"   - Comisiones ganadas: ${embajador_info['comisiones_ganadas']}")
        
        # Paso 5: Verificar en Tracking Service (conversiones del partner)
        print("\n 5. Verificando procesamiento en Tracking Service...")
        
        print("Esperando que el consumer procese el evento (5 segundos)...")
        time.sleep(5)
        
        response = requests.get(
            f"{BASE_URL}/tracking/conversiones/partner-123",
            headers=HEADERS
        )
        
        if response.status_code == 200:
            conversiones = response.json()
            print(f"Conversiones en Tracking Service: {len(conversiones)}")
            
            # Buscar la conversión relacionada con nuestro referido
            conversion_encontrada = False
            for conversion in conversiones:
                if conversion.get('id_click') == id_referido:
                    conversion_encontrada = True
                    print(f"Conversión procesada exitosamente:")
                    print(f"   - ID Conversión: {conversion.get('id_conversion')}")
                    print(f"   - Valor: ${conversion.get('valor')}")
                    print(f"   - Comisión: ${conversion.get('comision')}")
                    break
            
            if not conversion_encontrada:
                print("No se encontró la conversión relacionada con el referido")
                print("Esto puede significar que el consumer no está corriendo")
                return False
                
        else:
            print(f"No se pudieron obtener conversiones: {response.text}")
            return False
        
        print("\n TEST COMPLETADO EXITOSAMENTE")
        print("Comunicación Loyalty → Tracking funcionando correctamente")
        return True
        
    except requests.exceptions.ConnectionError:
        print("Error de conexión. ¿Está corriendo el servidor?")
        return False
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return False

def test_health_check():
    """Verifica que ambos servicios estén disponibles"""
    print("Verificando disponibilidad de servicios...")
    
    try:
        response = requests.get(f"{BASE_URL.replace('/v1', '')}/health")
        if response.status_code == 200:
            health_info = response.json()
            print(f"Servicios disponibles: {health_info.get('services', [])}")
            return True
        else:
            print(f"Health check falló: {response.text}")
            return False
    except:
        print("No se puede conectar al servidor")
        return False

if __name__ == "__main__":
    print("TESTING COMUNICACIÓN LOYALTY ↔ TRACKING SERVICES")
    print("=" * 60)
    
    # Verificar que el servidor esté corriendo
    if not test_health_check():
        print("\n Asegúrate de que el servidor esté corriendo:")
        print("   docker-compose up")
        exit(1)
    
    print("\n" + "=" * 60)
    
    # Ejecutar test principal
    success = test_comunicacion_loyalty_tracking()
    
    if success:
        print("\n RESULTADO: COMUNICACIÓN EXITOSA")
        print("Los microservicios se comunican correctamente via eventos")
    else:
        print("\nRESULTADO: COMUNICACIÓN FALLÓ")
        print("Revisa los logs para identificar el problema")
        
    print("\n NOTA: Para ver los eventos en tiempo real, ejecuta en otra terminal:")
    print("   docker exec alpespartners-app-1 python run_loyalty_consumer.py")