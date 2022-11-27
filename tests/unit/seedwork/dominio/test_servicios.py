"""Pruebas para archivo de fábrica de Seedwork

En este archivo usted encontrará las diferentes pruebas de validacióm para las fábricas base y reusables definidas en el seedwork

"""

import pytest
from aeroalpes.seedwork.dominio.fabricas import Fabrica


"""
    Clases de Soporte para validar el seedwork
"""

class FabricaImplementada(Fabrica):
    def crear_objeto(self, obj: any, mapeador: any) -> any:
        return "Mi Objeto"

class FabricaSinImplementar(Fabrica):
    ...

"""
    Pruebas
"""

def test_crear_fabrica_sin_implementacion():
    with pytest.raises(TypeError):
        fabrica = FabricaSinImplementar()

def test_crear_fabrica_con_implementacion():
    # Dada un nueva fabrica
    fabrica = FabricaImplementada()

    # Con metodo creacional
    assert fabrica.crear_objeto({}, {}) is not None



