from enum import Enum

class EstadoEmbajador(Enum):
    PENDIENTE = "PENDIENTE"       # Esperando aprobación
    ACTIVO = "ACTIVO"            # Puede referir y ganar comisiones
    INACTIVO = "INACTIVO"        # Desactivado