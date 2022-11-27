"""Pruebas para archivo de Servicios de Seedwork

En este archivo usted encontrará las diferentes pruebas de validacióm para los Servicios base y reusables definidas en el seedwork

"""

import pytest
from aeroalpes.seedwork.dominio.servicios import Servicio


"""
    Clases de Soporte para validar el seedwork
"""

class ServicioImpl(Servicio):
    ...

"""
    Pruebas
"""

def test_crear_servicio_desde_base():
    # Dada un nuevo Servicio
    servicio = ServicioImpl()

    # El Servicio es correcto y no tiene fallos en la creación
    assert servicio is not None



