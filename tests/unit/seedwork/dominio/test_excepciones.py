"""Pruebas para archivo de excepciones de Seedwork

En este archivo usted encontrará las diferentes pruebas de validacióm para las excepciones base y reusables definidas en el seedwork

"""

from aeroalpes.seedwork.dominio.excepciones import (
    ExcepcionDominio, 
    IdDebeSerInmutableExcepcion, 
    ReglaNegocioExcepcion,
    ExcepcionFabrica)
import pytest

"""
    Clases de Soporte para validar el seedwork
"""

class ExcepcionPrueba(ExcepcionDominio):
    ...

def regla_de_negocio(valor="ReglaNegocio"):
    class ReglaNegocio:
        def __str__(self):
            return valor
    return ReglaNegocio()

"""
    Pruebas
"""

def test_excepcion_heredada_es_creable_y_ejecutable():
    with pytest.raises(ExcepcionPrueba):
        # Dada una nuevo excepcióm
        excepcion = ExcepcionPrueba()

        # Entonces es lanzada exitosamente
        raise excepcion

def test_IdDebeSerInmutableExcepcion_es_creable_y_ejecutable():
    with pytest.raises(ExcepcionDominio):
        # Dada una nuevo excepcióm
        mensaje='El identificador debe ser inmutable'
        excepcion = IdDebeSerInmutableExcepcion(mensaje=mensaje)

        # Es covnertible a Str
        assert str(excepcion) == mensaje
        
        # Entonces es lanzada exitosamente
        raise excepcion

def test_ReglaNegocioExcepcion_es_creable_y_ejecutable():
    with pytest.raises(ExcepcionDominio):
        # Dada una nuevo excepcióm
        regla_negocio = regla_de_negocio(valor="ReglaNegocio")
        excepcion = ReglaNegocioExcepcion(regla_negocio)

        # Es covnertible a Str
        assert str(excepcion) == "ReglaNegocio"
        
        # Entonces es lanzada exitosamente
        raise excepcion

def test_ExcepcionFabrica_es_creable_y_ejecutable():
    with pytest.raises(ExcepcionDominio):
        # Dada una nuevo excepcióm
        mensaje='Excepción Fábrica'
        regla_negocio = regla_de_negocio(valor="ReglaNegocio")
        excepcion = ReglaNegocioExcepcion(regla_negocio)

        # Es covnertible a Str
        assert str(excepcion) == "ReglaNegocio"
        
        # Entonces es lanzada exitosamente
        raise excepcion






