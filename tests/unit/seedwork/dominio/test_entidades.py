"""Pruebas para archivo de entidades de Seedwork

En este archivo usted encontrará las diferentes pruebas de validación para los modelos abstractos y reusables del seedwork

"""

from dataclasses import dataclass, field
import pytest
from datetime import datetime
from uuid import UUID
from aeroalpes.seedwork.dominio.entidades import Entidad
from aeroalpes.seedwork.dominio.excepciones import IdDebeSerInmutableExcepcion


"""
    Clases de Soporte para validar el seedwork
"""

@dataclass
class EntidadPrueba(Entidad):
    campo1: str = field(default=None)
    campo2: int = field(default=0)

"""
    Pruebas
"""

def test_entidad_es_implementable():
    # Dada una entidad que hereda de Entidad
    entidadPrueba = EntidadPrueba()

    # Cuando los atributos son validos
    entidadPrueba.campo1 = "Campo1"
    entidadPrueba.campo2 = 2

    # Entonces el objeto no debe ser nulo y los atributos son establecidos
    assert entidadPrueba is not None
    assert entidadPrueba.campo1 == "Campo1"
    assert entidadPrueba.campo2 == 2


def test_inicializa_los_atributos_de_entidad():
    # Dada una entidad
    # Sin ningun tipo de parametros
    entidadPrueba = EntidadPrueba()

    # Entonces debe inicializar los atributos en la clase padre Entidad
    assert entidadPrueba is not None
    assert entidadPrueba.id is not None and type(entidadPrueba.id) == UUID
    assert entidadPrueba.fecha_actualizacion is not None and type(entidadPrueba.fecha_actualizacion) == datetime
    assert entidadPrueba.fecha_creacion is not None  and type(entidadPrueba.fecha_creacion) == datetime

def test_entidad_tiene_constructor_con_parametros():
    # Dada una entidad
    # Con parametros de entrada en el constructor
    entidadPrueba = EntidadPrueba(campo1="Campo1", campo2=2)

    # Entonces debe inicializarlos sin problema
    assert entidadPrueba is not None
    assert entidadPrueba.campo1 == "Campo1"
    assert entidadPrueba.campo2 == 2

def test_entidad_id_es_inmutable():
    with pytest.raises(IdDebeSerInmutableExcepcion):
        # Dada una entidad
        entidadPrueba = EntidadPrueba()

        # Cuando se intenta cambiar el ID ya establecido
        entidadPrueba.id = "Nuevo ID"

        # Entonces debe lanzar una excepción
        

        

