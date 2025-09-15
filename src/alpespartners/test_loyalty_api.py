#!/usr/bin/env python3
"""
Script de prueba para la API de Loyalty
Prueba todos los endpoints del servicio de loyalty
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any

# Configuración
BASE_URL = "http://localhost:8000"
LOYALTY_URL = f"{BASE_URL}/v1/loyalty"

class LoyaltyAPITester:
    """Clase para probar la API de loyalty"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.embajadores_creados = []
        self.referidos_creados = []
    
    def log(self, message: str, level: str = "INFO"):
        """Log con timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        level_emoji = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "ERROR": "❌",
            "WARNING": "⚠️"
        }
        print(f"{timestamp} {level_emoji.get(level, 'ℹ️')} {message}")
    
    def test_health_check(self) -> bool:
        """Probar health check"""
        self.log("🔍 Probando health check...")
        try:
            response = self.session.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Health check exitoso: {data['status']}", "SUCCESS")
                self.log(f"📊 Pulsar status: {data.get('pulsar_status', 'unknown')}")
                return True
            else:
                self.log(f"❌ Health check falló: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Error en health check: {str(e)}", "ERROR")
            return False
    
    def test_crear_embajador(self, nombre: str, email: str, id_partner: str = None) -> str:
        """Probar crear embajador"""
        self.log(f"🔍 Probando crear embajador: {nombre} ({email})...")
        try:
            data = {
                "nombre": nombre,
                "email": email
            }
            if id_partner:
                data["id_partner"] = id_partner
            
            response = self.session.post(f"{LOYALTY_URL}/embajadores", json=data)
            if response.status_code == 200:
                resultado = response.json()
                id_embajador = resultado.get("id_embajador")
                if id_embajador:
                    self.embajadores_creados.append(id_embajador)
                    self.log(f"✅ Embajador creado exitosamente: {id_embajador}", "SUCCESS")
                    return id_embajador
                else:
                    self.log(f"❌ No se obtuvo ID del embajador: {resultado}", "ERROR")
                    return None
            else:
                self.log(f"❌ Error creando embajador: {response.status_code} - {response.text}", "ERROR")
                return None
        except Exception as e:
            self.log(f"❌ Error en crear embajador: {str(e)}", "ERROR")
            return None
    
    def test_activar_embajador(self, id_embajador: str) -> bool:
        """Probar activar embajador"""
        self.log(f"🔍 Probando activar embajador: {id_embajador}...")
        try:
            data = {"id_embajador": id_embajador}
            response = self.session.post(f"{LOYALTY_URL}/embajadores/activar", json=data)
            if response.status_code == 200:
                resultado = response.json()
                self.log(f"✅ Embajador activado exitosamente: {resultado.get('mensaje')}", "SUCCESS")
                return True
            else:
                self.log(f"❌ Error activando embajador: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Error en activar embajador: {str(e)}", "ERROR")
            return False
    
    def test_registrar_referido(self, id_embajador: str, email_referido: str, 
                               nombre_referido: str, valor_conversion: float = 100.0, 
                               porcentaje_comision: float = 5.0) -> str:
        """Probar registrar referido"""
        self.log(f"🔍 Probando registrar referido: {nombre_referido} ({email_referido})...")
        try:
            data = {
                "id_embajador": id_embajador,
                "email_referido": email_referido,
                "nombre_referido": nombre_referido,
                "valor_conversion": valor_conversion,
                "porcentaje_comision": porcentaje_comision
            }
            
            response = self.session.post(f"{LOYALTY_URL}/referidos", json=data)
            if response.status_code == 200:
                resultado = response.json()
                id_referido = resultado.get("id_referido")
                if id_referido:
                    self.referidos_creados.append(id_referido)
                    self.log(f"✅ Referido registrado exitosamente: {id_referido}", "SUCCESS")
                    self.log(f"💰 Valor conversión: ${valor_conversion}")
                    self.log(f"📊 Comisión: {porcentaje_comision}%")
                    return id_referido
                else:
                    self.log(f"❌ No se obtuvo ID del referido: {resultado}", "ERROR")
                    return None
            else:
                self.log(f"❌ Error registrando referido: {response.status_code} - {response.text}", "ERROR")
                return None
        except Exception as e:
            self.log(f"❌ Error en registrar referido: {str(e)}", "ERROR")
            return None
    
    def test_obtener_metricas_embajador(self, id_embajador: str) -> bool:
        """Probar obtener métricas del embajador"""
        self.log(f"🔍 Probando obtener métricas del embajador: {id_embajador}...")
        try:
            response = self.session.get(f"{LOYALTY_URL}/embajadores/{id_embajador}/metricas")
            if response.status_code == 200:
                metricas = response.json()
                self.log(f"✅ Métricas obtenidas exitosamente", "SUCCESS")
                self.log(f"📊 Total referidos: {metricas.get('total_referidos', 0)}")
                self.log(f"💰 Comisiones ganadas: ${metricas.get('comisiones_ganadas', 0.0)}")
                self.log(f"📈 Estado: {metricas.get('estado', 'unknown')}")
                return True
            else:
                self.log(f"❌ Error obteniendo métricas: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Error en obtener métricas: {str(e)}", "ERROR")
            return False
    
    def test_crear_embajador_duplicado(self, nombre: str, email: str) -> bool:
        """Probar crear embajador con email duplicado (debe fallar)"""
        self.log(f"🔍 Probando crear embajador duplicado: {email}...")
        try:
            data = {
                "nombre": nombre,
                "email": email
            }
            
            response = self.session.post(f"{LOYALTY_URL}/embajadores", json=data)
            if response.status_code == 400:
                self.log(f"✅ Correctamente rechazado embajador duplicado", "SUCCESS")
                return True
            else:
                self.log(f"❌ Debería haber fallado con email duplicado: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Error en prueba de duplicado: {str(e)}", "ERROR")
            return False
    
    def test_activar_embajador_inexistente(self, id_embajador: str) -> bool:
        """Probar activar embajador inexistente (debe fallar)"""
        self.log(f"🔍 Probando activar embajador inexistente: {id_embajador}...")
        try:
            data = {"id_embajador": id_embajador}
            response = self.session.post(f"{LOYALTY_URL}/embajadores/activar", json=data)
            if response.status_code == 400:
                self.log(f"✅ Correctamente rechazado embajador inexistente", "SUCCESS")
                return True
            else:
                self.log(f"❌ Debería haber fallado con embajador inexistente: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Error en prueba de embajador inexistente: {str(e)}", "ERROR")
            return False
    
    def limpiar_datos_prueba(self):
        """Limpiar datos creados durante las pruebas"""
        self.log("🧹 Limpiando datos de prueba...")
        # Nota: En un sistema real, aquí se eliminarían los datos de prueba
        # Por ahora solo limpiamos las listas locales
        self.embajadores_creados.clear()
        self.referidos_creados.clear()
        self.log("✅ Datos de prueba limpiados", "SUCCESS")
    
    def ejecutar_pruebas_completas(self):
        """Ejecutar todas las pruebas de loyalty"""
        self.log("🚀 Iniciando pruebas completas de Loyalty API", "INFO")
        self.log("=" * 60)
        
        resultados = {
            "health_check": False,
            "crear_embajador": False,
            "activar_embajador": False,
            "registrar_referido": False,
            "obtener_metricas": False,
            "embajador_duplicado": False,
            "embajador_inexistente": False
        }
        
        # 1. Health Check
        resultados["health_check"] = self.test_health_check()
        self.log("-" * 40)
        
        # 2. Crear embajador
        id_embajador = self.test_crear_embajador(
            nombre="Juan Pérez",
            email="juan.perez@example.com",
            id_partner="partner-123"
        )
        resultados["crear_embajador"] = id_embajador is not None
        self.log("-" * 40)
        
        if id_embajador:
            # 3. Activar embajador
            resultados["activar_embajador"] = self.test_activar_embajador(id_embajador)
            self.log("-" * 40)
            
            # 4. Registrar referido
            id_referido = self.test_registrar_referido(
                id_embajador=id_embajador,
                email_referido="maria.garcia@example.com",
                nombre_referido="María García",
                valor_conversion=250.0,
                porcentaje_comision=7.5
            )
            resultados["registrar_referido"] = id_referido is not None
            self.log("-" * 40)
            
            # 5. Obtener métricas
            resultados["obtener_metricas"] = self.test_obtener_metricas_embajador(id_embajador)
            self.log("-" * 40)
        
        # 6. Pruebas de error
        resultados["embajador_duplicado"] = self.test_crear_embajador_duplicado(
            "Otro Juan", "juan.perez@example.com"
        )
        self.log("-" * 40)
        
        resultados["embajador_inexistente"] = self.test_activar_embajador_inexistente(
            "00000000-0000-0000-0000-000000000000"
        )
        self.log("-" * 40)
        
        # Resumen de resultados
        self.log("📊 RESUMEN DE PRUEBAS", "INFO")
        self.log("=" * 60)
        
        total_pruebas = len(resultados)
        pruebas_exitosas = sum(resultados.values())
        
        for prueba, resultado in resultados.items():
            estado = "✅ PASS" if resultado else "❌ FAIL"
            self.log(f"{prueba}: {estado}")
        
        self.log("-" * 40)
        self.log(f"Total: {pruebas_exitosas}/{total_pruebas} pruebas exitosas")
        
        if pruebas_exitosas == total_pruebas:
            self.log("🎉 ¡Todas las pruebas pasaron!", "SUCCESS")
        else:
            self.log(f"⚠️ {total_pruebas - pruebas_exitosas} pruebas fallaron", "WARNING")
        
        # Limpiar datos
        self.limpiar_datos_prueba()
        
        return pruebas_exitosas == total_pruebas

def main():
    """Función principal"""
    print("🔧 Loyalty API Tester")
    print("=" * 60)
    
    tester = LoyaltyAPITester()
    
    try:
        exito = tester.ejecutar_pruebas_completas()
        exit_code = 0 if exito else 1
        print(f"\n🏁 Pruebas completadas. Exit code: {exit_code}")
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️ Pruebas interrumpidas por el usuario")
        exit(1)
    except Exception as e:
        print(f"\n💥 Error inesperado: {str(e)}")
        exit(1)

if __name__ == "__main__":
    main()
