from dataclasses import dataclass
from typing import Optional
from ..dominio.objetos_valor import (
    TipoAfiliado, 
    InformacionContacto, 
    InformacionFiscal, 
    ConfiguracionAfiliado
)

@dataclass
class ComandoCrearAfiliado:
    """Comando para crear un nuevo afiliado"""
    codigo_afiliado: str
    nombre: str
    tipo_afiliado: str
    email: str
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    codigo_postal: Optional[str] = None
    tipo_documento: str = "DNI"
    numero_documento: str = ""
    nombre_fiscal: str = ""
    direccion_fiscal: Optional[str] = None
    comision_porcentaje: float = 5.0
    limite_mensual: Optional[float] = None
    metodo_pago_preferido: str = "TRANSFERENCIA_BANCARIA"
    notificaciones_email: bool = True
    notificaciones_sms: bool = False
    notas: Optional[str] = None
    metadata: Optional[dict] = None

@dataclass
class ComandoActualizarAfiliado:
    """Comando para actualizar un afiliado existente"""
    id_afiliado: str
    nombre: Optional[str] = None
    email: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    codigo_postal: Optional[str] = None
    comision_porcentaje: Optional[float] = None
    limite_mensual: Optional[float] = None
    metodo_pago_preferido: Optional[str] = None
    notificaciones_email: Optional[bool] = None
    notificaciones_sms: Optional[bool] = None
    notas: Optional[str] = None
    metadata: Optional[dict] = None

@dataclass
class ComandoActivarAfiliado:
    """Comando para activar un afiliado"""
    id_afiliado: str
    notas: Optional[str] = None

@dataclass
class ComandoDesactivarAfiliado:
    """Comando para desactivar un afiliado"""
    id_afiliado: str
    motivo: str

@dataclass
class ComandoSuspenderAfiliado:
    """Comando para suspender un afiliado"""
    id_afiliado: str
    motivo: str

@dataclass
class ComandoEliminarAfiliado:
    """Comando para eliminar un afiliado"""
    id_afiliado: str
