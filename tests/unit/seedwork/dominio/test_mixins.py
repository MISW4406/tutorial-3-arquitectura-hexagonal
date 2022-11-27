"""Pruebas para archivo de mixins de Seedwork

En este archivo usted encontrará las diferentes pruebas de validacióm para los mixins base y reusables definidas en el seedwork

"""

import pytest
from aeroalpes.seedwork.dominio.mixins import ValidarReglasMixin
from aeroalpes.seedwork.dominio.excepciones import (
    ReglaNegocioExcepcion)

"""
    Clases de Soporte para validar el seedwork
"""

class MiClase(ValidarReglasMixin):
    ...

class ReglaNegocioValida:
    def es_valido(self):
        return True

class ReglaNegocioInvalida:
    def es_valido(self):
        return False

"""
    Pruebas
"""

def test_valida_regla_erronea():
    with pytest.raises(ReglaNegocioExcepcion):
        # Dado un objeto con regla de negocio invalida
        obj = MiClase()
        regla_negocio = ReglaNegocioInvalida()

        # Cuando es validado
        obj.validar_regla(regla_negocio)

        # Lanza exceoción

def test_valida_regla_valida():
    # Dado un objeto con regla de negocio invalida
    obj = MiClase()
    regla_negocio = ReglaNegocioValida()

    # Cuando es validado
    obj.validar_regla(regla_negocio)

    # Llega hasta el final de la operación
    assert True



