from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from .objetos_valor import EstadoSaga, TipoSaga, EstadoPaso, DatosPaso, PasoCompensacion
from ...seedwork.dominio.entidades import Entidad

@dataclass
class Paso(Entidad):
    """Representa un paso individual en la saga"""
    orden: int
    servicio: str
    accion: str
    estado: EstadoPaso
    datos_entrada: Dict[str, Any]
    datos_salida: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp_inicio: Optional[datetime] = None
    timestamp_fin: Optional[datetime] = None
    compensacion: Optional[PasoCompensacion] = None

    def iniciar(self):
        """Marca el paso como en progreso"""
        self.estado = EstadoPaso.EN_PROGRESO
        self.timestamp_inicio = datetime.now()

    def completar(self, datos_salida: Dict[str, Any]):
        """Marca el paso como completado"""
        self.estado = EstadoPaso.COMPLETADO
        self.datos_salida = datos_salida
        self.timestamp_fin = datetime.now()

    def fallar(self, error: str):
        """Marca el paso como fallido"""
        self.estado = EstadoPaso.FALLIDO
        self.error = error
        self.timestamp_fin = datetime.now()

    def compensar(self, datos_compensacion: Dict[str, Any]):
        """Ejecuta la compensación del paso"""
        self.compensacion = PasoCompensacion(
            servicio=self.servicio,
            accion=f"compensar_{self.accion}",
            datos_compensacion=datos_compensacion,
            timestamp=datetime.now()
        )

@dataclass
class Saga(Entidad):
    """Entidad principal que representa una saga"""
    tipo: TipoSaga
    estado: EstadoSaga
    pasos: List[Paso] = field(default_factory=list)
    datos_contexto: Dict[str, Any] = field(default_factory=dict)
    timestamp_inicio: datetime = field(default_factory=datetime.now)
    timestamp_fin: Optional[datetime] = None
    error_global: Optional[str] = None
    compensaciones_ejecutadas: List[PasoCompensacion] = field(default_factory=list)

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())

    def agregar_paso(self, orden: int, servicio: str, accion: str, datos_entrada: Dict[str, Any]):
        """Agrega un nuevo paso a la saga"""
        paso = Paso(
            id=str(uuid.uuid4()),
            orden=orden,
            servicio=servicio,
            accion=accion,
            estado=EstadoPaso.PENDIENTE,
            datos_entrada=datos_entrada
        )
        self.pasos.append(paso)
        return paso

    def iniciar(self):
        """Inicia la saga"""
        self.estado = EstadoSaga.INICIADA
        self.timestamp_inicio = datetime.now()

    def marcar_en_progreso(self):
        """Marca la saga como en progreso"""
        self.estado = EstadoSaga.EN_PROGRESO

    def completar(self):
        """Marca la saga como completada"""
        self.estado = EstadoSaga.COMPLETADA
        self.timestamp_fin = datetime.now()

    def fallar(self, error: str):
        """Marca la saga como fallida"""
        self.estado = EstadoSaga.FALLIDA
        self.error_global = error
        self.timestamp_fin = datetime.now()

    def iniciar_compensacion(self):
        """Inicia el proceso de compensación"""
        self.estado = EstadoSaga.COMPENSANDO

    def completar_compensacion(self):
        """Marca la compensación como completada"""
        self.estado = EstadoSaga.COMPENSADA
        self.timestamp_fin = datetime.now()

    def obtener_paso_actual(self) -> Optional[Paso]:
        """Obtiene el paso actual que debe ejecutarse"""
        for paso in sorted(self.pasos, key=lambda p: p.orden):
            if paso.estado == EstadoPaso.PENDIENTE:
                return paso
        return None

    def obtener_pasos_completados(self) -> List[Paso]:
        """Obtiene todos los pasos completados"""
        return [paso for paso in self.pasos if paso.estado == EstadoPaso.COMPLETADO]

    def obtener_pasos_fallidos(self) -> List[Paso]:
        """Obtiene todos los pasos fallidos"""
        return [paso for paso in self.pasos if paso.estado == EstadoPaso.FALLIDO]

    def necesita_compensacion(self) -> bool:
        """Determina si la saga necesita compensación"""
        return len(self.obtener_pasos_completados()) > 0 and self.estado in [EstadoSaga.FALLIDA, EstadoSaga.COMPENSANDO]

