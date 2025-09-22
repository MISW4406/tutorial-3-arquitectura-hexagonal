from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class EstadoAfiliado(Enum):
    ACTIVO = "ACTIVO"
    INACTIVO = "INACTIVO"
    SUSPENDIDO = "SUSPENDIDO"
    PENDIENTE_APROBACION = "PENDIENTE_APROBACION"

class TipoAfiliado(Enum):
    INDIVIDUAL = "INDIVIDUAL"
    EMPRESA = "EMPRESA"
    INFLUENCER = "INFLUENCER"

@dataclass
class InformacionContactoDTO:
    """DTO para información de contacto"""
    email: str
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    codigo_postal: Optional[str] = None

@dataclass
class InformacionFiscalDTO:
    """DTO para información fiscal"""
    tipo_documento: str
    numero_documento: str
    nombre_fiscal: str
    direccion_fiscal: Optional[str] = None

@dataclass
class ConfiguracionAfiliadoDTO:
    """DTO para configuración del afiliado"""
    comision_porcentaje: float
    metodo_pago_preferido: str
    notificaciones_email: bool
    notificaciones_sms: bool
    limite_mensual: Optional[float] = None

@dataclass
class AfiliadoDTO:
    """DTO para representar un afiliado"""
    id_afiliado: str
    codigo_afiliado: str
    nombre: str
    tipo_afiliado: str
    estado: str
    informacion_contacto: InformacionContactoDTO
    informacion_fiscal: InformacionFiscalDTO
    configuracion: ConfiguracionAfiliadoDTO
    fecha_registro: datetime
    fecha_ultima_actividad: Optional[datetime] = None
    notas: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ResultadoAfiliadoDTO:
    """DTO para resultado de operaciones"""
    exitoso: bool
    mensaje: str
    id_afiliado: Optional[str] = None
    codigo_error: Optional[str] = None

@dataclass
class EstadisticasAfiliadosDTO:
    """DTO para estadísticas de afiliados"""
    total_afiliados: int
    afiliados_activos: int
    afiliados_inactivos: int
    afiliados_suspendidos: int
    afiliados_pendientes: int
    por_tipo: Dict[str, int]
    por_ciudad: Dict[str, int]
    por_pais: Dict[str, int]
    tasa_activacion: float
