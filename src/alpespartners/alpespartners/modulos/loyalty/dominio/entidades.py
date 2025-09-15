from dataclasses import dataclass, field
from datetime import datetime
from typing import List
from uuid import uuid4

from .eventos import EmbajadorCreado
from .objetos_valor import EstadoEmbajador

@dataclass
class Entidad:
    id: str = field(default_factory=lambda: str(uuid4()))

@dataclass
class AgregacionRaiz(Entidad):
    eventos: List = field(default_factory=list)

    def agregar_evento(self, evento):
        self.eventos.append(evento)

@dataclass
class Embajador(AgregacionRaiz):
    nombre: str = field(default=None)
    email: str = field(default=None)
    estado: EstadoEmbajador = field(default=None)
    id_partner: str = field(default=None)  # Relacionado con el partner que representa
    fecha_registro: datetime = field(default_factory=datetime.now)
    
    # Métricas básicas
    total_referidos: int = field(default=0)
    comisiones_ganadas: float = field(default=0.0)

    @property
    def id_embajador(self) -> str:
        return self.id

    def crear_embajador(self):
        """Crea un nuevo embajador y dispara el evento correspondiente"""
        if self.estado != EstadoEmbajador.ACTIVO:
            self.estado = EstadoEmbajador.PENDIENTE
        
        evento = EmbajadorCreado(
            id_embajador=self.id_embajador,
            nombre=self.nombre,
            email=self.email,
            id_partner=self.id_partner,
            fecha_registro=self.fecha_registro
        )
        self.agregar_evento(evento)

    def activar_embajador(self):
        """Activa un embajador que esta en estado pendiente"""
        if self.estado == EstadoEmbajador.PENDIENTE:
            self.estado = EstadoEmbajador.ACTIVO

    def registrar_referido_exitoso(self, valor_conversion: float = 0.0, comision: float = 0.0):
        """Actualiza las métricas cuando se registra un referido exitoso"""
        self.total_referidos += 1
        self.comisiones_ganadas += comision