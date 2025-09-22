from enum import Enum
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

class EstadoAfiliado(Enum):
    """Estados posibles de un afiliado"""
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"
    SUSPENDIDO = "SUSPENDIDO"
    PENDIENTE_APROBACION = "PENDIENTE_APROBACION"

class TipoAfiliado(Enum):
    """Tipos de afiliado"""
    INDIVIDUAL = "INDIVIDUAL"
    EMPRESA = "EMPRESA"
    INFLUENCER = "INFLUENCER"

@dataclass
class InformacionContacto:
    """Objeto valor para información de contacto"""
    email: str
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    codigo_postal: Optional[str] = None

@dataclass
class InformacionFiscal:
    """Objeto valor para información fiscal"""
    tipo_documento: str  # DNI, NIT, etc.
    numero_documento: str
    nombre_fiscal: str
    direccion_fiscal: Optional[str] = None

@dataclass
class ConfiguracionAfiliado:
    """Objeto valor para configuración del afiliado"""
    comision_porcentaje: float = 5.0
    limite_mensual: Optional[float] = None
    metodo_pago_preferido: str = "TRANSFERENCIA_BANCARIA"
    notificaciones_email: bool = True
    notificaciones_sms: bool = False
