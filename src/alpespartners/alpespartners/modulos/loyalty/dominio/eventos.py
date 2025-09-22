from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

from ....seedwork.dominio.eventos import EventoDominio

@dataclass
class EmbajadorCreado(EventoDominio):
    id_embajador: str
    nombre: str
    email: str
    id_partner: Optional[str]
    fecha_registro: datetime
    
    def __init__(self, id_embajador: str, nombre: str, email: str,
                 id_partner: Optional[str], fecha_registro: datetime):
        super().__init__()
        self.id_embajador = id_embajador
        self.nombre = nombre
        self.email = email
        self.id_partner = id_partner
        self.fecha_registro = fecha_registro

@dataclass
class ReferidoRegistrado(EventoDominio):
    """
    Evento que se dispara cuando un embajador registra un referido exitoso.
    Este evento será escuchado por el Tracking Service para contabilizar métricas.
    """
    id_referido: str
    id_embajador: str
    id_partner: Optional[str]
    email_referido: str
    nombre_referido: Optional[str]
    valor_conversion: float
    comision_embajador: float
    metadata_referido: Optional[Dict] = None
    timestamp: datetime = None
    
    def __init__(self, id_referido: str, id_embajador: str, id_partner: Optional[str],
                 email_referido: str, nombre_referido: Optional[str],
                 valor_conversion: float, comision_embajador: float, metadata_referido: Optional[Dict] = None,
                 timestamp: datetime = None):
        super().__init__()
        self.id_referido = id_referido
        self.id_embajador = id_embajador
        self.id_partner = id_partner
        self.email_referido = email_referido
        self.nombre_referido = nombre_referido
        self.valor_conversion = valor_conversion
        self.comision_embajador = comision_embajador
        self.metadata_referido = metadata_referido or {}
        self.timestamp = timestamp or datetime.now()

@dataclass
class EmbajadorActivado(EventoDominio):
    id_embajador: str
    id_partner: Optional[str]
    fecha_activacion: datetime
    
    def __init__(self, id_embajador: str, id_partner: Optional[str], fecha_activacion: datetime):
        super().__init__()
        self.id_embajador = id_embajador
        self.id_partner = id_partner
        self.fecha_activacion = fecha_activacion