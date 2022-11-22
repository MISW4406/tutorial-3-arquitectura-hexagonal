from abc import ABC
from aeroalpes.seedwork.dominio.repositorios import Repositorio

class RepositorioReservas(Repositorio, ABC):
    ...

class RepositorioProveedores(Repositorio, ABC):
    ...