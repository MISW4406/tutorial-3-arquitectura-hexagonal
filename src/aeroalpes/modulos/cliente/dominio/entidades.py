"""Entidades del dominio de cliente

En este archivo usted encontrará las entidades del dominio de cliente

"""

from datetime import datetime
from aeroalpes.seedwork.dominio.entidades import Entidad
from dataclasses import dataclass, field

from .objetos_valor import Nombre, Email, Cedula, Rut

@dataclass
class Usuario(Entidad):
    nombre: Nombre = field(default_factory=Nombre)
    email: Email = field(default_factory=Email)

@dataclass
class ClienteNatural(Usuario):
    cedula: Cedula = field(default_factory=Cedula)
    fecha_nacimiento: datetime = field(default_factory=datetime)

@dataclass
class ClienteEmpresa(Usuario):
    rut: Rut = field(default_factory=Rut)
    fecha_constitucion: datetime = field(default_factory=datetime)
