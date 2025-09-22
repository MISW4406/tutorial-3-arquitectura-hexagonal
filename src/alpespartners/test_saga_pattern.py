#!/usr/bin/env python3
"""
Script de prueba para demostrar el patrón Saga implementado.
Este script demuestra:
1. Saga exitosa (todos los pasos se completan)
2. Saga con fallo y compensación (un paso falla y se ejecutan compensaciones)
3. Monitoreo del Saga Log
"""

import requests
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
    """Realiza una petición HTTP"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method.upper() == "GET":
            response = requests.get(url)
        elif method.upper() == "POST":
            response = requests.post(url, json=data)
        else:
            raise ValueError(f"Método no soportado: {method}")
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en petición: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   Respuesta: {e.response.text}")
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

def demo_crear_saga_manual():
    """Demuestra la creación manual de una saga"""
    print_separator("DEMO: CREACIÓN MANUAL DE SAGA")
    print("Esta demo muestra cómo crear una saga manualmente")
    print("con datos personalizados.")
    
    print_step(1, "Creando saga manual")
    datos_saga = {
        "tipo_saga": "PROCESAMIENTO_CONVERSION",
        "id_partner": "partner_manual_001",
        "id_campana": "campana_manual_001",
        "id_conversion": "conversion_manual_001",
        "tipo_conversion": "VENTA",
        "informacion_monetaria": {"valor": 150.0, "moneda": "USD"},
        "metadata_cliente": {"ip": "192.168.1.100", "user_agent": "Manual Test"},
        "id_embajador": "embajador_manual_001",
        "email_referido": "referido@manual.com",
        "valor_conversion": 150.0,
        "porcentaje_comision": 7.5,
        "id_afiliado": "afiliado_manual_001",
        "comision": 11.25,
        "metodo_pago": "TRANSFERENCIA_BANCARIA"
    }
    
    response = make_request("POST", "/saga/crear", datos_saga)
    
    if response:
        print(f"✅ Saga creada manualmente")
        print(f"   ID Saga: {response['id_saga']}")
        print(f"   Tipo: {response['tipo']}")
        print(f"   Estado: {response['estado']}")
        
        saga_id = response['id_saga']
        
        print_step(2, "Ejecutando saga creada")
        ejecutar_data = {"id_saga": saga_id}
        ejecutar_response = make_request("POST", "/saga/ejecutar", ejecutar_data)
        
        if ejecutar_response:
            print(f"🎯 Saga ejecutada")
            print(f"   Exitoso: {ejecutar_response['exitoso']}")
            print(f"   Estado: {ejecutar_response['estado']}")
            print(f"   Mensaje: {ejecutar_response['mensaje']}")
    else:
        print("❌ Error creando saga manual")

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
    time.sleep(2)
    
    demo_crear_saga_manual()
    
    print_separator("DEMOSTRACIÓN COMPLETADA")
    print("✅ Todas las demos del patrón Saga han sido ejecutadas")
    print("📊 Revisa los logs y estadísticas para ver el funcionamiento")
    print("🔄 El patrón Saga maneja transacciones distribuidas con compensación")

if __name__ == "__main__":
    main()

