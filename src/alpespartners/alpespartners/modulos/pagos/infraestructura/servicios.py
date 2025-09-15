import random
import time
from datetime import datetime
from typing import Optional

from ..dominio.servicios import ServicioProcesamientoPagos, ServicioValidacionPagos, ServicioNotificaciones
from ..dominio.objetos_valor import ResultadoPago, InformacionPago, DetalleComision, MetodoPago

class ServicioProcesamientoPagosSimulado(ServicioProcesamientoPagos):
    """Servicio simulado de procesamiento de pagos (sin integración real)"""
    
    def __init__(self, tasa_exito: float = 0.95, delay_min: float = 1.0, delay_max: float = 3.0):
        self.tasa_exito = tasa_exito
        self.delay_min = delay_min
        self.delay_max = delay_max
    
    def procesar_pago(self, informacion_pago: InformacionPago, 
                     detalle_comision: DetalleComision) -> ResultadoPago:
        """Simula el procesamiento de un pago"""
        
        # Simular delay de procesamiento
        delay = random.uniform(self.delay_min, self.delay_max)
        time.sleep(delay)
        
        # Simular éxito/fallo basado en tasa de éxito
        if random.random() < self.tasa_exito:
            id_transaccion = f"TXN_{int(time.time())}_{random.randint(1000, 9999)}"
            return ResultadoPago(
                exitoso=True,
                id_transaccion_externa=id_transaccion,
                mensaje="Pago procesado exitosamente"
            )
        else:
            return ResultadoPago(
                exitoso=False,
                id_transaccion_externa=None,
                mensaje="Error en el procesamiento del pago",
                codigo_error="PAYMENT_FAILED"
            )
    
    def verificar_estado_pago(self, id_transaccion_externa: str) -> ResultadoPago:
        """Simula la verificación del estado de un pago"""
        
        # Simular delay de verificación
        delay = random.uniform(0.5, 1.5)
        time.sleep(delay)
        
        # Simular que la verificación siempre es exitosa para transacciones existentes
        return ResultadoPago(
            exitoso=True,
            id_transaccion_externa=id_transaccion_externa,
            mensaje="Pago verificado exitosamente"
        )
    
    def revertir_pago(self, id_transaccion_externa: str, motivo: str) -> ResultadoPago:
        """Simula la reversión de un pago"""
        
        # Simular delay de reversión
        delay = random.uniform(1.0, 2.0)
        time.sleep(delay)
        
        # Simular que la reversión siempre es exitosa
        return ResultadoPago(
            exitoso=True,
            id_transaccion_externa=id_transaccion_externa,
            mensaje=f"Pago revertido exitosamente: {motivo}"
        )

class ServicioValidacionPagosImpl(ServicioValidacionPagos):
    """Implementación del servicio de validación de pagos"""
    
    def __init__(self, monto_minimo: float = 1.0, monto_maximo: float = 10000.0):
        self.monto_minimo = monto_minimo
        self.monto_maximo = monto_maximo
    
    def validar_informacion_pago(self, informacion_pago: InformacionPago) -> bool:
        """Valida que la información de pago sea correcta"""
        
        # Validar método de pago
        if not informacion_pago.metodo_pago:
            return False
        
        # Validar datos del beneficiario según el método de pago
        if informacion_pago.metodo_pago == MetodoPago.TRANSFERENCIA_BANCARIA:
            required_fields = ['banco', 'numero_cuenta', 'tipo_cuenta']
            if not all(field in informacion_pago.datos_beneficiario for field in required_fields):
                return False
        
        elif informacion_pago.metodo_pago == MetodoPago.PAYPAL:
            if 'email' not in informacion_pago.datos_beneficiario:
                return False
        
        elif informacion_pago.metodo_pago == MetodoPago.STRIPE:
            if 'stripe_account_id' not in informacion_pago.datos_beneficiario:
                return False
        
        elif informacion_pago.metodo_pago == MetodoPago.WISE:
            if 'wise_account_id' not in informacion_pago.datos_beneficiario:
                return False
        
        # Validar referencia y descripción
        if not informacion_pago.referencia or not informacion_pago.descripcion:
            return False
        
        return True
    
    def validar_monto_pago(self, monto: float, moneda: str) -> bool:
        """Valida que el monto del pago sea válido"""
        
        # Validar monto positivo
        if monto <= 0:
            return False
        
        # Validar límites de monto
        if monto < self.monto_minimo or monto > self.monto_maximo:
            return False
        
        # Validar moneda soportada
        monedas_soportadas = ['USD', 'EUR', 'COP', 'MXN']
        if moneda not in monedas_soportadas:
            return False
        
        return True
    
    def validar_limites_embajador(self, id_embajador: str, monto: float) -> bool:
        """Valida que el embajador no exceda sus límites de pago"""
        
        # En una implementación real, aquí se consultaría la base de datos
        # para verificar límites diarios, mensuales, etc.
        
        # Por ahora, solo validamos que el monto no sea excesivo
        limite_diario = 1000.0
        limite_mensual = 10000.0
        
        # Simulación simple - en realidad se consultaría la BD
        return monto <= limite_diario

class ServicioNotificacionesSimulado(ServicioNotificaciones):
    """Servicio simulado de notificaciones"""
    
    def notificar_pago_exitoso(self, id_embajador: str, monto: float, 
                              moneda: str) -> None:
        """Simula notificación de pago exitoso"""
        print(f"📧 NOTIFICACIÓN: Pago exitoso de {monto} {moneda} para embajador {id_embajador}")
        # En una implementación real, aquí se enviaría email/SMS/push notification
    
    def notificar_pago_fallido(self, id_embajador: str, monto: float, 
                              moneda: str, motivo: str) -> None:
        """Simula notificación de pago fallido"""
        print(f"📧 NOTIFICACIÓN: Pago fallido de {monto} {moneda} para embajador {id_embajador}. Motivo: {motivo}")
        # En una implementación real, aquí se enviaría email/SMS/push notification
    
    def notificar_comision_revertida(self, id_embajador: str, monto: float, 
                                   moneda: str, motivo: str) -> None:
        """Simula notificación de comisión revertida"""
        print(f"📧 NOTIFICACIÓN: Comisión revertida de {monto} {moneda} para embajador {id_embajador}. Motivo: {motivo}")
        # En una implementación real, aquí se enviaría email/SMS/push notification
