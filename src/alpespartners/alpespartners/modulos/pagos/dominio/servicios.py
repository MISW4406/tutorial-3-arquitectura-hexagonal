from abc import ABC, abstractmethod
from typing import Optional
from .objetos_valor import ResultadoPago, InformacionPago, DetalleComision

class ServicioProcesamientoPagos(ABC):
    """Interfaz para el servicio de procesamiento de pagos"""
    
    @abstractmethod
    def procesar_pago(self, informacion_pago: InformacionPago, 
                     detalle_comision: DetalleComision) -> ResultadoPago:
        """Procesa un pago y retorna el resultado"""
        pass
    
    @abstractmethod
    def verificar_estado_pago(self, id_transaccion_externa: str) -> ResultadoPago:
        """Verifica el estado de un pago en el sistema externo"""
        pass
    
    @abstractmethod
    def revertir_pago(self, id_transaccion_externa: str, 
                     motivo: str) -> ResultadoPago:
        """Revierte un pago en el sistema externo"""
        pass

class ServicioValidacionPagos(ABC):
    """Interfaz para el servicio de validación de pagos"""
    
    @abstractmethod
    def validar_informacion_pago(self, informacion_pago: InformacionPago) -> bool:
        """Valida que la información de pago sea correcta"""
        pass
    
    @abstractmethod
    def validar_monto_pago(self, monto: float, moneda: str) -> bool:
        """Valida que el monto del pago sea válido"""
        pass
    
    @abstractmethod
    def validar_limites_embajador(self, id_embajador: str, monto: float) -> bool:
        """Valida que el embajador no exceda sus límites de pago"""
        pass

class ServicioNotificaciones(ABC):
    """Interfaz para el servicio de notificaciones"""
    
    @abstractmethod
    def notificar_pago_exitoso(self, id_embajador: str, monto: float, 
                              moneda: str) -> None:
        """Notifica al embajador que su pago fue exitoso"""
        pass
    
    @abstractmethod
    def notificar_pago_fallido(self, id_embajador: str, monto: float, 
                              moneda: str, motivo: str) -> None:
        """Notifica al embajador que su pago falló"""
        pass
    
    @abstractmethod
    def notificar_comision_revertida(self, id_embajador: str, monto: float, 
                                   moneda: str, motivo: str) -> None:
        """Notifica al embajador que su comisión fue revertida"""
        pass
