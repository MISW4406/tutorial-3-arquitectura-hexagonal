from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import uuid4

@dataclass
class EventoDominio:
    """Clase base para eventos de dominio"""
    id: str
    fecha: datetime
    tipo_evento: str
    
    def __init__(self, tipo_evento: str):
        self.id = str(uuid4())
        self.fecha = datetime.now()
        self.tipo_evento = tipo_evento

@dataclass
class AfiliadoRegistrado(EventoDominio):
    """Evento cuando se registra un nuevo afiliado"""
    id_afiliado: str
    codigo_afiliado: str
    nombre: str
    tipo_afiliado: str
    email: str
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    comision_porcentaje: float = 5.0
    metadata: Optional[Dict[str, Any]] = None
    
    def __init__(self, **kwargs):
        super().__init__("AfiliadoRegistrado")
        for key, value in kwargs.items():
            setattr(self, key, value)

@dataclass
class AfiliadoActivado(EventoDominio):
    """Evento cuando se activa un afiliado"""
    id_afiliado: str
    codigo_afiliado: str
    fecha_activacion: datetime
    notas: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __init__(self, **kwargs):
        super().__init__("AfiliadoActivado")
        for key, value in kwargs.items():
            setattr(self, key, value)

@dataclass
class AfiliadoSuspendido(EventoDominio):
    """Evento cuando se suspende un afiliado"""
    id_afiliado: str
    codigo_afiliado: str
    motivo: str
    fecha_suspension: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    def __init__(self, **kwargs):
        super().__init__("AfiliadoSuspendido")
        for key, value in kwargs.items():
            setattr(self, key, value)

@dataclass
class AfiliadoDesactivado(EventoDominio):
    """Evento cuando se desactiva un afiliado"""
    id_afiliado: str
    codigo_afiliado: str
    motivo: str
    fecha_desactivacion: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    def __init__(self, **kwargs):
        super().__init__("AfiliadoDesactivado")
        for key, value in kwargs.items():
            setattr(self, key, value)

@dataclass
class AfiliadoActualizado(EventoDominio):
    """Evento cuando se actualiza información de un afiliado"""
    id_afiliado: str
    codigo_afiliado: str
    campos_actualizados: Dict[str, Any]
    fecha_actualizacion: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    def __init__(self, **kwargs):
        super().__init__("AfiliadoActualizado")
        for key, value in kwargs.items():
            setattr(self, key, value)

@dataclass
class ConfiguracionAfiliadoActualizada(EventoDominio):
    """Evento cuando se actualiza la configuración de un afiliado"""
    id_afiliado: str
    codigo_afiliado: str
    comision_anterior: float
    comision_nueva: float
    limite_anterior: Optional[float]
    limite_nuevo: Optional[float]
    fecha_actualizacion: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    def __init__(self, **kwargs):
        super().__init__("ConfiguracionAfiliadoActualizada")
        for key, value in kwargs.items():
            setattr(self, key, value)

@dataclass
class AfiliadoEliminado(EventoDominio):
    """Evento cuando se elimina un afiliado"""
    id_afiliado: str
    codigo_afiliado: str
    fecha_eliminacion: datetime
    motivo: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __init__(self, **kwargs):
        super().__init__("AfiliadoEliminado")
        for key, value in kwargs.items():
            setattr(self, key, value)
