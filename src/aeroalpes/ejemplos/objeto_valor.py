"""
Ejemplo 2.a: Este fragmento de código nos presenta una clase ObjetoValor
La clase Color es considerada ObjetoValor puesto que es inmutable y sus atributos constituyen un objeto único en el sistema
"""

from dataclasses import dataclass

@dataclass(frozen=True)
class Color():
    """
    Clase que representa el ObjetoValor Color

    ---------------------
    Atributos
    ---------------------

    _rojo: int
        Número entre 0 y 255 que representa la cantidad de color rojo
    _verde: int
        Número entre 0 y 255 que representa la cantidad de color verde
    _azul: int
        Número entre 0 y 255 que representa la cantidad de color azul
    """

    _rojo:int
    _verde:int
    _azul:int

    # Código comentado pues no es necesario (y genera errores) tener el método __init__ cuando se usa la anotación @dataclass
    # def __init__(self, rojo:int, verde:int, azul:int):
    #     self._rojo = rojo
    #     self._verde = verde
    #     self._azul = azul

# Ejecute los siguientes fragmentos de código para ver el comportamiento inmutable de dataclass y frozen
mi_color = Color(252, 123, 34)
print(mi_color._rojo)
mi_color._rojo = 220
print(mi_color._rojo)
