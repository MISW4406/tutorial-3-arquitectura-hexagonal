"""
Ejemplo 2.b: Este fragmento de código nos presenta dos clases: Una Objecto valor y otra Entidad.
La clase Nombre es considerada ObjetoValor puesto que es inmutable y sus atributos constituyen un objeto único en el sistema
Por otra parte la clase Cliente es una entidad que necesita de un identificador único y con ciclo de vida cambiante
"""

from dataclasses import dataclass, field

@dataclass(frozen=True)
class Nombre():
    """
    Clase que representa el ObjetoValor Nombre

    ---------------------
    Atributos
    ---------------------

    nombres: str
        Nombre completo de un usuario, cliente, o en general persona
    apellidos: str
        Apellidos de un usuario, cliente, o en general persona
    """

    nombres: str
    apellidos: str

@dataclass
class Cliente():
    """
    Clase que representa la Entidad Cliente

    ---------------------
    Atributos
    ---------------------

    nombre: Nombre
        Referencia al ObjetoValor nombre, que incluye los nombres y apellidos del cliente
    id: int
        Número único que indentifica al cliente en el sistema
    """

    nombre: Nombre
    id: int
    _id: int = field(init=False, repr=False)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id: int) -> None:
        """
        Método setter para el atributo ID. Hace override de la funcionalidad por default para lanzar
        una excepción en caso que se quiera sobreescribir el atributo ID

        ---------------------
        Parámetros
        ---------------------

        id: int
            ID único por el cual se identificará al Cliente

        ---------------------
        Lanza
        ---------------------

        Exception:
            Si ya existe un ID y se trata de modificar el valor

        """
        try:
            if self._id:
                raise Exception('ID es inmutable!')
        except AttributeError as error:
            self._id = id

# Ejecute los siguientes fragmentos de código para ver el comportamiento de las entidades con IDs inmutables
nombre = Nombre('Juan', 'Urrego')
cliente = Cliente(nombre, 1)
print(cliente)
cliente.id = 3
print(cliente)