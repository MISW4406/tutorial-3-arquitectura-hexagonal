"""Pruebas para archivo de objetos_valor de Seedwork

En este archivo usted encontrará las diferentes pruebas de validación para los modelos abstractos y reusables del seedwork

"""

from dataclasses import dataclass, field
import pytest
from datetime import datetime
from aeroalpes.seedwork.dominio.objetos_valor import (
    ObjetoValor,
    Codigo,
    Ruta,
    Pais,
    Ciudad)
from aeroalpes.seedwork.dominio.excepciones import IdDebeSerInmutableExcepcion


"""
    Clases de Soporte para validar el seedwork
"""

@dataclass(frozen=True)
class RutaImplementada(Ruta):
    def origen(self) -> any:
        return "BOG"
    
    def destino(self) -> any:
        return "JFK"
    
    def fecha_salida(self) -> datetime:
        return datetime.strptime('01/01/23 00:00:00', '%d/%m/%y %H:%M:%S')

    def fecha_llegada(self) -> datetime:
        return datetime.strptime('02/01/23 00:00:00', '%d/%m/%y %H:%M:%S')

class RutaSinImplementar(Ruta):
    ...

@dataclass(frozen=True)
class MyObjetoValor(ObjetoValor):
    campo1: str = field(default=None)
    campo2: int = field(default=0)
    ciudad: int = field(default=Ciudad)
    ruta: Ruta = field(default=Ruta)

"""
    Pruebas
"""

def test_objeto_valor_es_implementable():
    # Dada un objeto valor que hereda de un Objeto Valor
    objeto_valor = MyObjetoValor(campo1="Campo1", campo2=2)

    # Entonces el objeto no debe ser nulo y los atributos son establecidos
    assert objeto_valor is not None
    assert objeto_valor.campo1 == "Campo1"
    assert objeto_valor.campo2 == 2

def test_ruta_es_implementable():
    # Dada una implementación de ruta
    ruta = RutaImplementada()

    # Entonces debe inicializarlos sin problema
    assert ruta.origen() == "BOG"
    assert ruta.destino() == "JFK"
    assert ruta.fecha_salida() == datetime.strptime('01/01/23 00:00:00', '%d/%m/%y %H:%M:%S')
    assert ruta.fecha_llegada() == datetime.strptime('02/01/23 00:00:00', '%d/%m/%y %H:%M:%S')

def test_ruta_no_es_implementable_lanza_excepcion():
    with pytest.raises(TypeError):
        # Dada una implementación de ruta erronea
        ruta = RutaSinImplementar()


def test_objeto_valores_gis_son_implementables():
    # Dado objetos valores GIS
    codigo_pais = Codigo(codigo="COL")
    pais = Pais(codigo=codigo_pais, nombre="Colombia")

    codigo_ciudad = Codigo(codigo="BOG")
    ciudad = Ciudad(codigo=codigo_ciudad, nombre="Bogotá", pais=pais)
    
    # Dada un objeto valor que hereda de Objeto Valor
    objeto_valor = MyObjetoValor(campo1="Campo1", campo2=2, ciudad=ciudad, ruta=RutaImplementada())

    # Entonces el objeto no debe ser nulo y los atributos son establecidos
    assert objeto_valor is not None
    assert objeto_valor.campo1 == "Campo1"
    assert objeto_valor.campo2 == 2
    assert objeto_valor.ciudad is not None
    assert objeto_valor.ciudad.codigo.codigo == "BOG"
    assert objeto_valor.ciudad.nombre == "Bogotá"
    assert objeto_valor.ciudad.pais is not None
    assert objeto_valor.ciudad.pais.codigo.codigo == "COL"
    assert objeto_valor.ciudad.pais.nombre == "Colombia"
        

        

