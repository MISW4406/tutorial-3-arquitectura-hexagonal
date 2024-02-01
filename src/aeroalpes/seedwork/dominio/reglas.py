"""Reglas de negocio reusables parte del seedwork del proyecto

En este archivo usted encontrará reglas de negocio reusables parte del seedwork del proyecto

"""

from abc import ABC, abstractmethod

class ReglaNegocio(ABC):

    __mensaje: str ='La regla de negocio es invalida'

    def __init__(self, mensaje):
        self.__mensaje = mensaje

    def mensaje_error(self) -> str:
        return self.__mensaje

    @abstractmethod
    def es_valido(self) -> bool:
        ...

    def __str__(self):
        return f"{self.__class__.__name__} - {self.__mensaje}"


class ReglaNegocioCompuesta(ReglaNegocio):
    __causa: str
    __reglas: list[ReglaNegocio]
    
    def __init__(self, mensaje, reglas):
        super(ReglaNegocioCompuesta, self).__init__(mensaje)
        self.__reglas = reglas
    
    @property
    def causa(self):
        return self.__causa

    @causa.setter
    def causa(self, causa):
        self.__causa = causa
    
    def es_valido(self) -> bool:
        for regla in self.__reglas:
            if not regla.es_valido():
                self.causa = str(regla)
                return False
        return True

    def __str__(self):
        return f"{self.__class__.__name__} > {self.__causa}"


class IdEntidadEsInmutable(ReglaNegocio):

    entidad: object

    def __init__(self, entidad, mensaje='El identificador de la entidad debe ser Inmutable'):
        super().__init__(mensaje)
        self.entidad = entidad

    def es_valido(self) -> bool:
        try:
            if self.entidad._id:
                return False
        except AttributeError as error:
            return True
