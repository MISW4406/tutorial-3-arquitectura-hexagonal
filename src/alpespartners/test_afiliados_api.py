#!/usr/bin/env python3
"""
Script de prueba para la API de Afiliados
Prueba todos los endpoints del servicio de afiliados
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any

# Configuración
BASE_URL = "http://localhost:8000"
AFILIADOS_URL = f"{BASE_URL}/v1/afiliados"

class AfiliadosAPITester:
    """Clase para probar la API de afiliados"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.afiliados_creados = []
    
    def log(self, message: str, level: str = "INFO"):
        """Log con timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def test_health_check(self) -> bool:
        """Probar health check"""
        self.log("🔍 Probando health check...")
        try:
            response = self.session.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                self.log("✅ Health check exitoso", "SUCCESS")
                return True
            else:
                self.log(f"❌ Health check falló: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Error en health check: {str(e)}", "ERROR")
            return False
    
    def test_obtener_estados(self) -> bool:
        """Probar obtener estados de afiliado"""
        self.log("🔍 Probando obtener estados de afiliado...")
        try:
            response = self.session.get(f"{AFILIADOS_URL}/estados")
            if response.status_code == 200:
                estados = response.json()
                self.log(f"✅ Estados obtenidos: {estados}", "SUCCESS")
                return True
            else:
                self.log(f"❌ Error obteniendo estados: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Error en obtener estados: {str(e)}", "ERROR")
            return False
    
    def test_obtener_tipos(self) -> bool:
        """Probar obtener tipos de afiliado"""
        self.log("🔍 Probando obtener tipos de afiliado...")
        try:
            response = self.session.get(f"{AFILIADOS_URL}/tipos")
            if response.status_code == 200:
                tipos = response.json()
                self.log(f"✅ Tipos obtenidos: {tipos}", "SUCCESS")
                return True
            else:
                self.log(f"❌ Error obteniendo tipos: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Error en obtener tipos: {str(e)}", "ERROR")
            return False
    
    def test_crear_afiliado(self, datos_afiliado: Dict[str, Any]) -> str:
        """Probar crear afiliado"""
        self.log(f"🔍 Probando crear afiliado: {datos_afiliado['codigo_afiliado']}...")
        try:
            response = self.session.post(f"{AFILIADOS_URL}", json=datos_afiliado)
            if response.status_code == 201:
                afiliado = response.json()
                print("test", afiliado)
                id_afiliado = afiliado['id_afiliado']
                self.afiliados_creados.append(id_afiliado)
                self.log(f"✅ Afiliado creado exitosamente: {id_afiliado}", "SUCCESS")
                return id_afiliado
            else:
                self.log(f"❌ Error creando afiliado: {response.status_code} - {response.text}", "ERROR")
                return None
        except Exception as e:
            self.log(f"❌ Error en crear afiliado: {str(e)}", "ERROR")
            return None
    
    def test_obtener_afiliado(self, id_afiliado: str) -> bool:
        """Probar obtener afiliado por ID"""
        self.log(f"🔍 Probando obtener afiliado: {id_afiliado}...")
        try:
            response = self.session.get(f"{AFILIADOS_URL}/{id_afiliado}")
            if response.status_code == 200:
                afiliado = response.json()
                self.log(f"✅ Afiliado obtenido: {afiliado['nombre']}", "SUCCESS")
                return True
            else:
                self.log(f"❌ Error obteniendo afiliado: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Error en obtener afiliado: {str(e)}", "ERROR")
            return False
    
    def test_obtener_afiliado_por_codigo(self, codigo_afiliado: str) -> bool:
        """Probar obtener afiliado por código"""
        self.log(f"🔍 Probando obtener afiliado por código: {codigo_afiliado}...")
        try:
            response = self.session.get(f"{AFILIADOS_URL}/codigo/{codigo_afiliado}")
            if response.status_code == 200:
                afiliado = response.json()
                self.log(f"✅ Afiliado obtenido por código: {afiliado['nombre']}", "SUCCESS")
                return True
            else:
                self.log(f"❌ Error obteniendo afiliado por código: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Error en obtener afiliado por código: {str(e)}", "ERROR")
            return False
    
    def test_actualizar_afiliado(self, id_afiliado: str, datos_actualizacion: Dict[str, Any]) -> bool:
        """Probar actualizar afiliado"""
        self.log(f"🔍 Probando actualizar afiliado: {id_afiliado}...")
        try:
            response = self.session.put(f"{AFILIADOS_URL}/{id_afiliado}", json=datos_actualizacion)
            if response.status_code == 200:
                resultado = response.json()
                if resultado['exitoso']:
                    self.log(f"✅ Afiliado actualizado exitosamente", "SUCCESS")
                    return True
                else:
                    self.log(f"❌ Error actualizando afiliado: {resultado['mensaje']}", "ERROR")
                    return False
            else:
                self.log(f"❌ Error actualizando afiliado: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Error en actualizar afiliado: {str(e)}", "ERROR")
            return False
    
    def test_activar_afiliado(self, id_afiliado: str) -> bool:
        """Probar activar afiliado"""
        self.log(f"🔍 Probando activar afiliado: {id_afiliado}...")
        try:
            response = self.session.post(f"{AFILIADOS_URL}/{id_afiliado}/activar", json={"notas": "Activado por prueba"})
            if response.status_code == 200:
                resultado = response.json()
                if resultado['exitoso']:
                    self.log(f"✅ Afiliado activado exitosamente", "SUCCESS")
                    return True
                else:
                    self.log(f"❌ Error activando afiliado: {resultado['mensaje']}", "ERROR")
                    return False
            else:
                self.log(f"❌ Error activando afiliado: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Error en activar afiliado: {str(e)}", "ERROR")
            return False
    
    def test_suspender_afiliado(self, id_afiliado: str) -> bool:
        """Probar suspender afiliado"""
        self.log(f"🔍 Probando suspender afiliado: {id_afiliado}...")
        try:
            response = self.session.post(f"{AFILIADOS_URL}/{id_afiliado}/suspender", json={"motivo": "Suspensión de prueba"})
            if response.status_code == 200:
                resultado = response.json()
                if resultado['exitoso']:
                    self.log(f"✅ Afiliado suspendido exitosamente", "SUCCESS")
                    return True
                else:
                    self.log(f"❌ Error suspendiendo afiliado: {resultado['mensaje']}", "ERROR")
                    return False
            else:
                self.log(f"❌ Error suspendiendo afiliado: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Error en suspender afiliado: {str(e)}", "ERROR")
            return False
    
    def test_desactivar_afiliado(self, id_afiliado: str) -> bool:
        """Probar desactivar afiliado"""
        self.log(f"🔍 Probando desactivar afiliado: {id_afiliado}...")
        try:
            response = self.session.post(f"{AFILIADOS_URL}/{id_afiliado}/desactivar", json={"motivo": "Desactivación de prueba"})
            if response.status_code == 200:
                resultado = response.json()
                if resultado['exitoso']:
                    self.log(f"✅ Afiliado desactivado exitosamente", "SUCCESS")
                    return True
                else:
                    self.log(f"❌ Error desactivando afiliado: {resultado['mensaje']}", "ERROR")
                    return False
            else:
                self.log(f"❌ Error desactivando afiliado: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Error en desactivar afiliado: {str(e)}", "ERROR")
            return False
    
    def test_listar_afiliados(self, filtros: Dict[str, Any] = None) -> bool:
        """Probar listar afiliados"""
        self.log("🔍 Probando listar afiliados...")
        try:
            params = filtros or {}
            response = self.session.get(f"{AFILIADOS_URL}", params=params)
            if response.status_code == 200:
                afiliados = response.json()
                self.log(f"✅ Afiliados listados: {len(afiliados)} encontrados", "SUCCESS")
                return True
            else:
                self.log(f"❌ Error listando afiliados: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Error en listar afiliados: {str(e)}", "ERROR")
            return False
    
    def test_buscar_afiliados(self, filtros: Dict[str, Any]) -> bool:
        """Probar buscar afiliados con filtros"""
        self.log(f"🔍 Probando buscar afiliados con filtros: {filtros}...")
        try:
            response = self.session.get(f"{AFILIADOS_URL}", params=filtros)
            if response.status_code == 200:
                afiliados = response.json()
                self.log(f"✅ Búsqueda exitosa: {len(afiliados)} afiliados encontrados", "SUCCESS")
                return True
            else:
                self.log(f"❌ Error en búsqueda: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Error en buscar afiliados: {str(e)}", "ERROR")
            return False
    
    def test_obtener_estadisticas(self) -> bool:
        """Probar obtener estadísticas"""
        self.log("🔍 Probando obtener estadísticas...")
        try:
            response = self.session.get(f"{AFILIADOS_URL}/estadisticas")
            if response.status_code == 200:
                estadisticas = response.json()
                self.log(f"✅ Estadísticas obtenidas: {estadisticas['total_afiliados']} afiliados totales", "SUCCESS")
                return True
            else:
                self.log(f"❌ Error obteniendo estadísticas: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Error en obtener estadísticas: {str(e)}", "ERROR")
            return False
    
    def test_eliminar_afiliado(self, id_afiliado: str) -> bool:
        """Probar eliminar afiliado"""
        self.log(f"🔍 Probando eliminar afiliado: {id_afiliado}...")
        try:
            response = self.session.delete(f"{AFILIADOS_URL}/{id_afiliado}")
            if response.status_code == 200:
                resultado = response.json()
                if resultado['exitoso']:
                    self.log(f"✅ Afiliado eliminado exitosamente", "SUCCESS")
                    return True
                else:
                    self.log(f"❌ Error eliminando afiliado: {resultado['mensaje']}", "ERROR")
                    return False
            else:
                self.log(f"❌ Error eliminando afiliado: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"❌ Error en eliminar afiliado: {str(e)}", "ERROR")
            return False
    
    def limpiar_afiliados_creados(self):
        """Limpiar afiliados creados durante las pruebas"""
        self.log("🧹 Limpiando afiliados creados...")
        for id_afiliado in self.afiliados_creados:
            try:
                self.test_eliminar_afiliado(id_afiliado)
            except:
                pass  # Ignorar errores en limpieza
        self.afiliados_creados.clear()
    
    def ejecutar_pruebas_completas(self):
        """Ejecutar todas las pruebas"""
        self.log("🚀 Iniciando pruebas completas de la API de Afiliados")
        self.log("=" * 60)
        
        resultados = []
        
        # 1. Health check
        resultados.append(("Health Check", self.test_health_check()))
        
        # 2. Obtener información básica
        resultados.append(("Obtener Estados", self.test_obtener_estados()))
        resultados.append(("Obtener Tipos", self.test_obtener_tipos()))
        
        # 3. Crear afiliados de prueba
        afiliados_prueba = [
            {
                "codigo_afiliado": "AFF001",
                "nombre": "Juan Pérez",
                "tipo_afiliado": "INDIVIDUAL",
                "email": "juan.perez@email.com",
                "telefono": "+57 300 123 4567",
                "direccion": "Calle 123 #45-67",
                "ciudad": "Bogotá",
                "pais": "Colombia",
                "codigo_postal": "110111",
                "tipo_documento": "CC",
                "numero_documento": "12345678",
                "nombre_fiscal": "Juan Pérez",
                "direccion_fiscal": "Calle 123 #45-67",
                "comision_porcentaje": 5.0,
                "limite_mensual": 10000.0,
                "metodo_pago_preferido": "TRANSFERENCIA_BANCARIA",
                "notificaciones_email": True,
                "notificaciones_sms": False,
                "notas": "Afiliado de prueba 1"
            },
            {
                "codigo_afiliado": "AFF002",
                "nombre": "María García",
                "tipo_afiliado": "EMPRESA",
                "email": "maria.garcia@empresa.com",
                "telefono": "+57 300 987 6543",
                "direccion": "Carrera 7 #32-10",
                "ciudad": "Medellín",
                "pais": "Colombia",
                "codigo_postal": "050001",
                "tipo_documento": "NIT",
                "numero_documento": "900123456-1",
                "nombre_fiscal": "Empresa García S.A.S.",
                "direccion_fiscal": "Carrera 7 #32-10",
                "comision_porcentaje": 7.5,
                "limite_mensual": 50000.0,
                "metodo_pago_preferido": "TRANSFERENCIA_BANCARIA",
                "notificaciones_email": True,
                "notificaciones_sms": True,
                "notas": "Afiliado de prueba 2"
            },
            {
                "codigo_afiliado": "AFF003",
                "nombre": "Carlos López",
                "tipo_afiliado": "INFLUENCER",
                "email": "carlos.lopez@influencer.com",
                "telefono": "+57 300 555 1234",
                "direccion": "Calle 80 #11-42",
                "ciudad": "Cali",
                "pais": "Colombia",
                "codigo_postal": "760001",
                "tipo_documento": "CC",
                "numero_documento": "87654321",
                "nombre_fiscal": "Carlos López",
                "direccion_fiscal": "Calle 80 #11-42",
                "comision_porcentaje": 10.0,
                "limite_mensual": 25000.0,
                "metodo_pago_preferido": "TRANSFERENCIA_BANCARIA",
                "notificaciones_email": True,
                "notificaciones_sms": False,
                "notas": "Afiliado de prueba 3"
            }
        ]
        
        ids_afiliados = []
        for afiliado in afiliados_prueba:
            id_afiliado = self.test_crear_afiliado(afiliado)
            if id_afiliado:
                ids_afiliados.append(id_afiliado)
                resultados.append((f"Crear Afiliado {afiliado['codigo_afiliado']}", True))
            else:
                resultados.append((f"Crear Afiliado {afiliado['codigo_afiliado']}", False))
        
        if ids_afiliados:
            # 4. Probar operaciones con el primer afiliado
            id_afiliado = ids_afiliados[0]
            
            resultados.append(("Obtener Afiliado por ID", self.test_obtener_afiliado(id_afiliado)))
            resultados.append(("Obtener Afiliado por Código", self.test_obtener_afiliado_por_codigo("AFF001")))
            
            # Actualizar afiliado
            datos_actualizacion = {
                "nombre": "Juan Pérez Actualizado",
                "telefono": "+57 300 999 8888",
                "comision_porcentaje": 6.0,
                "notas": "Afiliado actualizado en prueba"
            }
            resultados.append(("Actualizar Afiliado", self.test_actualizar_afiliado(id_afiliado, datos_actualizacion)))
            
            # Cambiar estados
            resultados.append(("Activar Afiliado", self.test_activar_afiliado(id_afiliado)))
            resultados.append(("Suspender Afiliado", self.test_suspender_afiliado(id_afiliado)))
            resultados.append(("Desactivar Afiliado", self.test_desactivar_afiliado(id_afiliado)))
            
            # 5. Probar listados y búsquedas
            resultados.append(("Listar Afiliados", self.test_listar_afiliados()))
            resultados.append(("Buscar por Nombre", self.test_buscar_afiliados({"nombre": "Juan"})))
            resultados.append(("Buscar por Ciudad", self.test_buscar_afiliados({"ciudad": "Bogotá"})))
            resultados.append(("Buscar por Tipo", self.test_buscar_afiliados({"tipo": "INDIVIDUAL"})))
            resultados.append(("Buscar por Estado", self.test_buscar_afiliados({"estado": "INACTIVO"})))
            
            # 6. Estadísticas
            resultados.append(("Obtener Estadísticas", self.test_obtener_estadisticas()))
            
            # 7. Limpiar (eliminar afiliados de prueba)
            self.log("🧹 Limpiando afiliados de prueba...")
            for id_afiliado in ids_afiliados:
                self.test_eliminar_afiliado(id_afiliado)
        
        # Resumen de resultados
        self.log("=" * 60)
        self.log("📊 RESUMEN DE PRUEBAS")
        self.log("=" * 60)
        
        exitosas = 0
        fallidas = 0
        
        for prueba, resultado in resultados:
            estado = "✅ EXITOSA" if resultado else "❌ FALLIDA"
            self.log(f"{prueba}: {estado}")
            if resultado:
                exitosas += 1
            else:
                fallidas += 1
        
        self.log("=" * 60)
        self.log(f"Total de pruebas: {len(resultados)}")
        self.log(f"Exitosas: {exitosas}")
        self.log(f"Fallidas: {fallidas}")
        self.log(f"Tasa de éxito: {(exitosas/len(resultados)*100):.1f}%")
        
        if fallidas == 0:
            self.log("🎉 ¡Todas las pruebas pasaron exitosamente!", "SUCCESS")
        else:
            self.log(f"⚠️  {fallidas} pruebas fallaron", "WARNING")
        
        return fallidas == 0

def main():
    """Función principal"""
    print("🧪 Test de API de Afiliados - Alpes Partners")
    print("=" * 60)
    
    tester = AfiliadosAPITester()
    
    try:
        # Esperar un momento para que el servicio esté listo
        print("⏳ Esperando que el servicio esté listo...")
        time.sleep(2)
        
        # Ejecutar pruebas
        exito = tester.ejecutar_pruebas_completas()
        
        if exito:
            print("\n🎉 ¡Todas las pruebas completadas exitosamente!")
            return 0
        else:
            print("\n❌ Algunas pruebas fallaron. Revisa los logs arriba.")
            return 1
            
    except KeyboardInterrupt:
        print("\n⏹️  Pruebas interrumpidas por el usuario")
        return 1
    except Exception as e:
        print(f"\n💥 Error inesperado: {str(e)}")
        return 1
    finally:
        # Limpiar recursos
        tester.limpiar_afiliados_creados()

if __name__ == "__main__":
    exit(main())
