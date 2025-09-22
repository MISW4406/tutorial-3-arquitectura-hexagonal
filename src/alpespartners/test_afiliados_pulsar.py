#!/usr/bin/env python3
"""
Script de prueba para verificar la integración de Afiliados con Pulsar
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000/v1"
AFILIADOS_URL = f"{BASE_URL}/afiliados"

def test_afiliados_with_pulsar():
    """Prueba la integración de afiliados con Pulsar"""
    print("🚀 Probando integración de Afiliados con Pulsar")
    print("=" * 60)
    
    # 1. Crear afiliado (debería emitir evento AfiliadoRegistrado)
    print("1. Creando afiliado...")
    afiliado_data = {
        "codigo_afiliado": "AFF_PULSAR_001",
        "nombre": "Test Pulsar Integration",
        "tipo_afiliado": "INDIVIDUAL",
        "email": "test.pulsar@email.com",
        "telefono": "+57 300 123 4567",
        "direccion": "Calle Test #123",
        "ciudad": "Bogotá",
        "pais": "Colombia",
        "codigo_postal": "110111",
        "tipo_documento": "CC",
        "numero_documento": "12345678",
        "nombre_fiscal": "Test Pulsar Integration",
        "direccion_fiscal": "Calle Test #123",
        "comision_porcentaje": 5.0,
        "limite_mensual": 10000.0,
        "metodo_pago_preferido": "TRANSFERENCIA_BANCARIA",
        "notificaciones_email": True,
        "notificaciones_sms": False,
        "notas": "Afiliado para prueba de Pulsar"
    }
    
    response = requests.post(f"{AFILIADOS_URL}", json=afiliado_data)
    if response.status_code == 201:
        afiliado = response.json()
        id_afiliado = afiliado['id_afiliado']
        print(f"✅ Afiliado creado: {id_afiliado}")
        print(f"   Evento esperado: AfiliadoRegistrado")
    else:
        print(f"❌ Error creando afiliado: {response.status_code}")
        return
    
    time.sleep(2)  # Esperar para que se procese el evento
    
    # 2. Activar afiliado (debería emitir evento AfiliadoActivado)
    print("\n2. Activando afiliado...")
    response = requests.post(f"{AFILIADOS_URL}/{id_afiliado}/activar", json={"notas": "Activado para prueba de Pulsar"})
    if response.status_code == 200:
        print("✅ Afiliado activado")
        print("   Evento esperado: AfiliadoActivado")
    else:
        print(f"❌ Error activando afiliado: {response.status_code}")
    
    time.sleep(2)
    
    # 3. Actualizar configuración (debería emitir evento ConfiguracionAfiliadoActualizada)
    print("\n3. Actualizando configuración...")
    update_data = {
        "comision_porcentaje": 7.5,
        "limite_mensual": 15000.0
    }
    response = requests.put(f"{AFILIADOS_URL}/{id_afiliado}", json=update_data)
    if response.status_code == 200:
        print("✅ Configuración actualizada")
        print("   Evento esperado: ConfiguracionAfiliadoActualizada")
    else:
        print(f"❌ Error actualizando configuración: {response.status_code}")
    
    time.sleep(2)
    
    # 4. Suspender afiliado (debería emitir evento AfiliadoSuspendido)
    print("\n4. Suspendiendo afiliado...")
    response = requests.post(f"{AFILIADOS_URL}/{id_afiliado}/suspender", json={"motivo": "Suspensión de prueba"})
    if response.status_code == 200:
        print("✅ Afiliado suspendido")
        print("   Evento esperado: AfiliadoSuspendido")
    else:
        print(f"❌ Error suspendiendo afiliado: {response.status_code}")
    
    time.sleep(2)
    
    # 5. Desactivar afiliado (debería emitir evento AfiliadoDesactivado)
    print("\n5. Desactivando afiliado...")
    response = requests.post(f"{AFILIADOS_URL}/{id_afiliado}/desactivar", json={"motivo": "Desactivación de prueba"})
    if response.status_code == 200:
        print("✅ Afiliado desactivado")
        print("   Evento esperado: AfiliadoDesactivado")
    else:
        print(f"❌ Error desactivando afiliado: {response.status_code}")
    
    time.sleep(2)
    
    # 6. Eliminar afiliado (debería emitir evento AfiliadoEliminado)
    print("\n6. Eliminando afiliado...")
    response = requests.delete(f"{AFILIADOS_URL}/{id_afiliado}")
    if response.status_code == 200:
        print("✅ Afiliado eliminado")
        print("   Evento esperado: AfiliadoEliminado")
    else:
        print(f"❌ Error eliminando afiliado: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("🎉 Prueba de integración con Pulsar completada")
    print("\n📋 Eventos esperados en Pulsar:")
    print("   1. AfiliadoRegistrado")
    print("   2. AfiliadoActivado")
    print("   3. ConfiguracionAfiliadoActualizada")
    print("   4. AfiliadoSuspendido")
    print("   5. AfiliadoDesactivado")
    print("   6. AfiliadoEliminado")
    print("\n💡 Para verificar los eventos en Pulsar:")
    print("   - Accede a http://localhost:8081 (Pulsar Web Console)")
    print("   - Navega al topic: persistent://public/default/afiliados-eventos")
    print("   - Verifica que se hayan publicado los eventos")

if __name__ == "__main__":
    test_afiliados_with_pulsar()
