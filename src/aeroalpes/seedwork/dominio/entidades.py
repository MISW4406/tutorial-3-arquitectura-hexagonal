from dataclasses import dataclass, field
from .mixins import ValidarReglasMixin
from .reglas import IdEntidadEsInmutable
from .excepciones import IdDebeSerInmutableExcepcion
from datetime import datetime
from uuid import UUID

@dataclass
class Entidad:
    id: UUID = field(hash=True)
    _id: UUID = field(init=False, repr=False, hash=True)
    fecha_creacion: datetime =  field(default=datetime.now())
    fecha_actualizacion: datetime = field(default=datetime.now())

    @classmethod
    def siguiente_id(self) -> UUID:
        return UUID.v4()

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id: UUID) -> None:
        if not IdEntidadEsInmutable(self).es_valido():
            raise IdDebeSerInmutableExcepcion(IdEntidadEsInmutable.__mensaje)
        self._id =id
        

@dataclass
class AgregacionRaiz(Entidad, ValidarReglasMixin):
    ...


@dataclass
class Locacion(Entidad):
    def __str__(self) -> str:
        ...