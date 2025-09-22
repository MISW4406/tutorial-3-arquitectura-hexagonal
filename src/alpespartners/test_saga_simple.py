#!/usr/bin/env python3
"""
Script de prueba simple para demostrar el patrón Saga implementado.
Este script usa solo la biblioteca estándar de Python (urllib) para hacer las peticiones HTTP.
"""

import urllib.request
import urllib.parse
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000/v1"

def print_separator(title):
    """Imprime un separador visual"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_step(step, description):
    """Imprime un paso del proceso"""
    print(f"\n🔹 Paso {step}: {description}")
    print("-" * 40)

def make_request(method, endpoint, data=None):
    """Realiza una petición HTTP usando urllib"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            req = urllib.request.Request(url)
        elif method.upper() == "POST":
            json_data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=json_data, headers={'Content-Type': 'application/json'})
        else:
            raise ValueError(f"Método no soportado: {method}")
        
        with urllib.request.urlopen(req) as response:
            response_data = response.read().decode('utf-8')
            return json.loads(response_data)
            
    except urllib.error.HTTPError as e:
        print(f"❌ Error HTTP {e.code}: {e.reason}")
        try:
            error_body = e.read().decode('utf-8')
            print(f"   Respuesta: {error_body}")
        except:
            pass
        return None
    except Exception as e:
        print(f"❌ Error en petición: {e}")
        return None

def demo_saga_exitosa():
    """Demuestra una saga exitosa"""
    print_separator("DEMO: SAGA EXITOSA")
    print("Esta demo muestra una saga que se ejecuta exitosamente")
    print("todos los pasos se completan sin errores.")
    
    print_step(1, "Ejecutando saga exitosa")
    response = make_request("GET", "/saga/demo/exitoso")
    
    if response:
        print(f"✅ Saga creada y ejecutada exitosamente")
        print(f"   ID Saga: {response['id_saga']}")
        print(f"   Estado: {response['exitoso']}")
        print(f"   Mensaje: {response['mensaje']}")
        
        saga_id = response['id_saga']
        
        print_step(2, "Consultando estado de la saga")
        estado = make_request("GET", f"/saga/{saga_id}/estado")
        
        if estado:
            print(f"📊 Estado de la saga:")
            print(f"   Tipo: {estado['tipo']}")
            print(f"   Estado: {estado['estado']}")
            print(f"   Pasos: {len(estado['pasos'])}")
            
            for i, paso in enumerate(estado['pasos'], 1):
                print(f"   Paso {i}: {paso['servicio']}.{paso['accion']} - {paso['estado']}")
        
        print_step(3, "Consultando log de la saga")
        logs = make_request("GET", f"/saga/{saga_id}/log")
        
        if logs:
            print(f"📝 Log de eventos ({len(logs)} eventos):")
            for log in logs:
                timestamp = log['timestamp'][:19]  # Solo fecha y hora
                print(f"   [{timestamp}] {log['evento']}")
    else:
        print("❌ Error ejecutando saga exitosa")

def demo_saga_con_fallo():
    """Demuestra una saga con fallo y compensación"""
    print_separator("DEMO: SAGA CON FALLO Y COMPENSACIÓN")
    print("Esta demo muestra una saga donde un paso falla")
    print("y se ejecutan las compensaciones correspondientes.")
    
    print_step(1, "Ejecutando saga con fallo simulado")
    response = make_request("GET", "/saga/demo/fallo")
    
    if response:
        print(f"⚠️ Saga ejecutada con fallo y compensación")
        print(f"   ID Saga: {response['id_saga']}")
        print(f"   Estado: {response['exitoso']}")
        print(f"   Mensaje: {response['mensaje']}")
        
        saga_id = response['id_saga']
        
        print_step(2, "Consultando estado de la saga")
        estado = make_request("GET", f"/saga/{saga_id}/estado")
        
        if estado:
            print(f"📊 Estado de la saga:")
            print(f"   Tipo: {estado['tipo']}")
            print(f"   Estado: {estado['estado']}")
            print(f"   Error: {estado.get('error_global', 'N/A')}")
            print(f"   Pasos: {len(estado['pasos'])}")
            
            for i, paso in enumerate(estado['pasos'], 1):
                status_icon = "✅" if paso['estado'] == "COMPLETADO" else "❌" if paso['estado'] == "FALLIDO" else "⏳"
                print(f"   {status_icon} Paso {i}: {paso['servicio']}.{paso['accion']} - {paso['estado']}")
                
                if paso.get('compensacion'):
                    comp = paso['compensacion']
                    print(f"      🔄 Compensación: {comp['servicio']}.{comp['accion']} - {'✅' if comp['exitoso'] else '❌'}")
        
        print_step(3, "Consultando log detallado de la saga")
        logs = make_request("GET", f"/saga/{saga_id}/log")
        
        if logs:
            print(f"📝 Log detallado ({len(logs)} eventos):")
            for log in logs:
                timestamp = log['timestamp'][:19]
                icon = "🟢" if log['nivel'] == "INFO" else "🟡" if log['nivel'] == "WARNING" else "🔴"
                print(f"   {icon} [{timestamp}] {log['evento']}")
                
                # Mostrar datos relevantes del evento
                if log['evento'] in ['PASO_COMPLETADO', 'PASO_FALLIDO', 'PASO_COMPENSADO']:
                    datos = log.get('datos', {})
                    if 'servicio' in datos:
                        print(f"      Servicio: {datos['servicio']}.{datos.get('accion', 'N/A')}")
    else:
        print("❌ Error ejecutando saga con fallo")

def demo_estadisticas():
    """Demuestra las estadísticas de sagas"""
    print_separator("DEMO: ESTADÍSTICAS DE SAGAS")
    print("Esta demo muestra las estadísticas generales")
    print("de todas las sagas ejecutadas.")
    
    print_step(1, "Consultando estadísticas")
    stats = make_request("GET", "/saga/estadisticas")
    
    if stats:
        print(f"📈 Estadísticas de Sagas:")
        print(f"   Total de sagas: {stats['total_sagas']}")
        print(f"   ✅ Completadas: {stats['sagas_completadas']}")
        print(f"   ❌ Fallidas: {stats['sagas_fallidas']}")
        print(f"   🔄 Compensadas: {stats['sagas_compensadas']}")
        print(f"   ⏳ En progreso: {stats['sagas_en_progreso']}")
        print(f"   📊 Tasa de éxito: {stats['tasa_exito']}%")
    else:
        print("❌ Error obteniendo estadísticas")

def main():
    """Función principal que ejecuta todas las demos"""
    print("🚀 DEMOSTRACIÓN DEL PATRÓN SAGA")
    print("Sistema de microservicios con Apache Pulsar")
    print("Patrón Saga para transacciones distribuidas")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Verificar que el servidor esté corriendo
    print("\n🔍 Verificando conexión con el servidor...")
    health = make_request("GET", "/health")
    
    if not health:
        print("❌ No se puede conectar al servidor. Asegúrate de que esté corriendo en http://localhost:8000")
        print("💡 Para iniciar el servidor:")
        print("   cd src/alpespartners")
        print("   python -m alpespartners.main")
        return
    
    print(f"✅ Servidor conectado: {health['status']}")
    print(f"   Servicios disponibles: {', '.join(health['services'])}")
    print(f"   Event broker: {health['event_broker']}")
    
    # Ejecutar demos
    demo_saga_exitosa()
    time.sleep(2)
    
    demo_saga_con_fallo()
    time.sleep(2)
    
    demo_estadisticas()
    
    print_separator("DEMOSTRACIÓN COMPLETADA")
    print("✅ Todas las demos del patrón Saga han sido ejecutadas")
    print("📊 Revisa los logs y estadísticas para ver el funcionamiento")
    print("🔄 El patrón Saga maneja transacciones distribuidas con compensación")
    print("\n💡 Para más información, consulta SAGA_README.md")

if __name__ == "__main__":
    main()

