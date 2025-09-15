#!/usr/bin/env python3
"""
Script de prueba para los endpoints de la API de pagos
"""

import requests
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuración
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/v1"

class PagosAPITester:
    """Clase para probar los endpoints de la API de pagos"""
    
    def __init__(self, base_url: str = API_BASE):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def test_health_check(self) -> bool:
        """Probar el health check"""
        logger.info("🔍 Probando health check...")
        try:
            response = self.session.get(f"{BASE_URL}/health")
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ Health check exitoso: {data['status']}")
            logger.info(f"   Servicios: {data['services']}")
            logger.info(f"   Pulsar: {data.get('pulsar_status', 'N/A')}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error en health check: {str(e)}")
            return False
    
    def test_crear_pago(self) -> str:
        """Probar creación de pago"""
        logger.info("\n💰 Probando creación de pago...")
        
        pago_data = {
            "id_embajador": "emb_001",
            "id_partner": "partner_001",
            "id_conversion": "conv_001",
            "monto": 50.0,
            "moneda": "USD",
            "metodo_pago": "TRANSFERENCIA_BANCARIA",
            "datos_beneficiario": {
                "banco": "Banco Simulado",
                "numero_cuenta": "****1234",
                "tipo_cuenta": "AHORROS"
            },
            "referencia": "COM-001",
            "descripcion": "Comisión por referido exitoso",
            "metadata": {
                "test": True,
                "fuente": "api_test"
            }
        }
        
        try:
            response = self.session.post(f"{self.base_url}/pagos", json=pago_data)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ Pago creado exitosamente: {data['id_pago']}")
            logger.info(f"   Estado: {data['estado']}")
            logger.info(f"   Monto: ${data['monto']} {data['moneda']}")
            
            return data['id_pago']
            
        except Exception as e:
            logger.error(f"❌ Error creando pago: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"   Response: {e.response.text}")
            return None
    
    def test_obtener_pago(self, id_pago: str) -> bool:
        """Probar obtención de pago por ID"""
        logger.info(f"\n🔍 Probando obtención de pago {id_pago[:8]}...")
        
        try:
            response = self.session.get(f"{self.base_url}/pagos/{id_pago}")
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ Pago obtenido exitosamente")
            logger.info(f"   Estado: {data['estado']}")
            logger.info(f"   Embajador: {data['id_embajador']}")
            logger.info(f"   Fecha creación: {data['fecha_creacion']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo pago: {str(e)}")
            return False
    
    def test_procesar_pago(self, id_pago: str) -> bool:
        """Probar procesamiento de pago"""
        logger.info(f"\n⚡ Probando procesamiento de pago {id_pago[:8]}...")
        
        try:
            response = self.session.post(f"{self.base_url}/pagos/{id_pago}/procesar")
            response.raise_for_status()
            
            data = response.json()
            if data['exitoso']:
                logger.info(f"✅ Pago procesado exitosamente")
                logger.info(f"   Transacción: {data['id_transaccion_externa']}")
                logger.info(f"   Mensaje: {data['mensaje']}")
            else:
                logger.info(f"❌ Pago falló: {data['mensaje']}")
                if data.get('codigo_error'):
                    logger.info(f"   Código error: {data['codigo_error']}")
            
            return data['exitoso']
            
        except Exception as e:
            logger.error(f"❌ Error procesando pago: {str(e)}")
            return False
    
    def test_obtener_pagos_embajador(self, id_embajador: str) -> bool:
        """Probar obtención de pagos por embajador"""
        logger.info(f"\n👤 Probando pagos del embajador {id_embajador}...")
        
        try:
            response = self.session.get(f"{self.base_url}/pagos/embajador/{id_embajador}")
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ Pagos obtenidos: {len(data)} pagos encontrados")
            
            for i, pago in enumerate(data, 1):
                logger.info(f"   {i}. Pago {pago['id_pago'][:8]}... - {pago['estado']} - ${pago['monto']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo pagos de embajador: {str(e)}")
            return False
    
    def test_obtener_pagos_pendientes(self) -> bool:
        """Probar obtención de pagos pendientes"""
        logger.info("\n⏳ Probando pagos pendientes...")
        
        try:
            response = self.session.get(f"{self.base_url}/pagos/pendientes")
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ Pagos pendientes: {len(data)} pagos encontrados")
            
            for i, pago in enumerate(data, 1):
                logger.info(f"   {i}. Pago {pago['id_pago'][:8]}... - {pago['estado']} - ${pago['monto']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo pagos pendientes: {str(e)}")
            return False
    
    def test_obtener_estadisticas(self) -> bool:
        """Probar obtención de estadísticas"""
        logger.info("\n📊 Probando estadísticas...")
        
        try:
            response = self.session.get(f"{self.base_url}/pagos/estadisticas")
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"✅ Estadísticas obtenidas:")
            logger.info(f"   Total pagos: {data['total_pagos']}")
            logger.info(f"   Total monto: ${data['total_monto']}")
            logger.info(f"   Pagos exitosos: {data['pagos_exitosos']}")
            logger.info(f"   Pagos fallidos: {data['pagos_fallidos']}")
            logger.info(f"   Pagos pendientes: {data['pagos_pendientes']}")
            logger.info(f"   Monto promedio: ${data['monto_promedio']:.2f}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {str(e)}")
            return False
    
    def test_obtener_metadatos(self) -> bool:
        """Probar obtención de metadatos (estados, métodos, tipos)"""
        logger.info("\n📋 Probando metadatos...")
        
        try:
            # Estados de pago
            response = self.session.get(f"{self.base_url}/pagos/estados")
            response.raise_for_status()
            estados = response.json()
            logger.info(f"✅ Estados de pago: {estados}")
            
            # Métodos de pago
            response = self.session.get(f"{self.base_url}/pagos/metodos")
            response.raise_for_status()
            metodos = response.json()
            logger.info(f"✅ Métodos de pago: {metodos}")
            
            # Tipos de pago
            response = self.session.get(f"{self.base_url}/pagos/tipos")
            response.raise_for_status()
            tipos = response.json()
            logger.info(f"✅ Tipos de pago: {tipos}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo metadatos: {str(e)}")
            return False
    
    def test_crear_multiples_pagos(self) -> list:
        """Probar creación de múltiples pagos"""
        logger.info("\n🔄 Probando creación de múltiples pagos...")
        
        pagos_data = [
            {
                "id_embajador": "emb_002",
                "id_partner": "partner_001",
                "id_conversion": "conv_002",
                "monto": 75.0,
                "moneda": "USD",
                "metodo_pago": "PAYPAL",
                "datos_beneficiario": {
                    "email": "embajador2@example.com"
                },
                "referencia": "COM-002",
                "descripcion": "Comisión PayPal",
                "metadata": {"test": True, "batch": 1}
            },
            {
                "id_embajador": "emb_003",
                "id_partner": "partner_002",
                "id_conversion": "conv_003",
                "monto": 100.0,
                "moneda": "USD",
                "metodo_pago": "STRIPE",
                "datos_beneficiario": {
                    "stripe_account_id": "acct_1234567890"
                },
                "referencia": "COM-003",
                "descripcion": "Comisión Stripe",
                "metadata": {"test": True, "batch": 2}
            }
        ]
        
        ids_pagos = []
        
        for i, pago_data in enumerate(pagos_data, 1):
            try:
                response = self.session.post(f"{self.base_url}/pagos", json=pago_data)
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"✅ Pago {i} creado: {data['id_pago'][:8]}...")
                ids_pagos.append(data['id_pago'])
                
            except Exception as e:
                logger.error(f"❌ Error creando pago {i}: {str(e)}")
        
        return ids_pagos
    
    def test_procesar_pagos_pendientes(self) -> bool:
        """Probar procesamiento de pagos pendientes"""
        logger.info("\n⚡ Probando procesamiento de pagos pendientes...")
        
        try:
            # Obtener pagos pendientes
            response = self.session.get(f"{self.base_url}/pagos/pendientes")
            response.raise_for_status()
            pagos_pendientes = response.json()
            
            if not pagos_pendientes:
                logger.info("ℹ️ No hay pagos pendientes para procesar")
                return True
            
            logger.info(f"🔄 Procesando {len(pagos_pendientes)} pagos pendientes...")
            
            for i, pago in enumerate(pagos_pendientes[:3], 1):  # Procesar solo los primeros 3
                logger.info(f"   Procesando pago {i}/{min(3, len(pagos_pendientes))}: {pago['id_pago'][:8]}...")
                
                response = self.session.post(f"{self.base_url}/pagos/{pago['id_pago']}/procesar")
                response.raise_for_status()
                
                resultado = response.json()
                if resultado['exitoso']:
                    logger.info(f"   ✅ Pago procesado: {resultado['id_transaccion_externa']}")
                else:
                    logger.info(f"   ❌ Pago falló: {resultado['mensaje']}")
                
                # Pequeña pausa entre procesamientos
                time.sleep(0.5)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error procesando pagos pendientes: {str(e)}")
            return False
    
    def run_full_test(self) -> bool:
        """Ejecutar todas las pruebas"""
        logger.info("🚀 === INICIANDO PRUEBAS COMPLETAS DE API DE PAGOS ===")
        logger.info("   Arquitectura Hexagonal + Event-Driven + FastAPI")
        logger.info("")
        
        tests_passed = 0
        total_tests = 0
        
        # Test 1: Health check
        total_tests += 1
        if self.test_health_check():
            tests_passed += 1
        
        # Test 2: Crear pago
        total_tests += 1
        id_pago = self.test_crear_pago()
        if id_pago:
            tests_passed += 1
            
            # Test 3: Obtener pago
            total_tests += 1
            if self.test_obtener_pago(id_pago):
                tests_passed += 1
            
            # Test 4: Procesar pago
            total_tests += 1
            if self.test_procesar_pago(id_pago):
                tests_passed += 1
        
        # Test 5: Crear múltiples pagos
        total_tests += 1
        ids_pagos_adicionales = self.test_crear_multiples_pagos()
        if ids_pagos_adicionales:
            tests_passed += 1
        
        # Test 6: Obtener pagos de embajador
        total_tests += 1
        if self.test_obtener_pagos_embajador("emb_001"):
            tests_passed += 1
        
        # Test 7: Obtener pagos pendientes
        total_tests += 1
        if self.test_obtener_pagos_pendientes():
            tests_passed += 1
        
        # Test 8: Procesar pagos pendientes
        total_tests += 1
        if self.test_procesar_pagos_pendientes():
            tests_passed += 1
        
        # Test 9: Obtener estadísticas
        total_tests += 1
        if self.test_obtener_estadisticas():
            tests_passed += 1
        
        # Test 10: Obtener metadatos
        total_tests += 1
        if self.test_obtener_metadatos():
            tests_passed += 1
        
        # Resumen final
        logger.info(f"\n📊 === RESUMEN DE PRUEBAS ===")
        logger.info(f"   Pruebas pasadas: {tests_passed}/{total_tests}")
        logger.info(f"   Porcentaje de éxito: {(tests_passed/total_tests)*100:.1f}%")
        
        if tests_passed == total_tests:
            logger.info("🎉 ¡Todas las pruebas pasaron exitosamente!")
            return True
        else:
            logger.warning(f"⚠️ {total_tests - tests_passed} pruebas fallaron")
            return False

def main():
    """Función principal"""
    logger.info("Iniciando pruebas de API de pagos...")
    
    # Verificar que el servidor esté corriendo
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            logger.error("❌ El servidor no está respondiendo correctamente")
            logger.error("   Asegúrate de que el servidor esté corriendo en http://localhost:8000")
            return False
    except requests.exceptions.RequestException:
        logger.error("❌ No se puede conectar al servidor")
        logger.error("   Asegúrate de que el servidor esté corriendo en http://localhost:8000")
        logger.error("   Ejecuta: docker-compose up -d")
        return False
    
    # Ejecutar pruebas
    tester = PagosAPITester()
    success = tester.run_full_test()
    
    if success:
        logger.info("\n✅ Todas las pruebas de API completadas exitosamente")
        logger.info("   El servicio de pagos está funcionando correctamente")
        logger.info("   Puedes acceder a la documentación en: http://localhost:8000/docs")
    else:
        logger.error("\n❌ Algunas pruebas fallaron")
        logger.error("   Revisa los logs para más detalles")
    
    return success

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
