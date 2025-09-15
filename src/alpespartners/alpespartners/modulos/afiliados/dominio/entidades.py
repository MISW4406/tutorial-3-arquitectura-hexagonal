from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List
from uuid import uuid4
from .objetos_valor import (
    EstadoAfiliado, 
    TipoAfiliado, 
    InformacionContacto, 
    InformacionFiscal, 
    ConfiguracionAfiliado
)
from .eventos import (
    AfiliadoRegistrado,
    AfiliadoActivado,
    AfiliadoSuspendido,
    AfiliadoDesactivado,
    AfiliadoActualizado,
    ConfiguracionAfiliadoActualizada,
    AfiliadoEliminado
)

@dataclass
class Entidad:
    id: str = field(default_factory=lambda: str(uuid4()))

class Afiliado(Entidad):
    """Entidad principal para afiliados"""
    
    def __init__(self,
                 codigo_afiliado: str,
                 nombre: str,
                 tipo_afiliado: TipoAfiliado,
                 informacion_contacto: InformacionContacto,
                 informacion_fiscal: InformacionFiscal,
                 configuracion: ConfiguracionAfiliado,
                 estado: EstadoAfiliado = EstadoAfiliado.PENDIENTE_APROBACION,
                 fecha_registro: Optional[datetime] = None,
                 fecha_ultima_actividad: Optional[datetime] = None,
                 notas: Optional[str] = None,
                 metadata: Optional[dict] = None,
                 id: Optional[str] = None):
        
        # Llamar al constructor de la clase padre
        super().__init__(id=id)
        
        # Campos requeridos
        self.codigo_afiliado = codigo_afiliado
        self.nombre = nombre
        self.tipo_afiliado = tipo_afiliado
        self.informacion_contacto = informacion_contacto
        self.informacion_fiscal = informacion_fiscal
        self.configuracion = configuracion
        
        # Campos opcionales
        self.estado = estado
        self.fecha_registro = fecha_registro or datetime.now()
        self.fecha_ultima_actividad = fecha_ultima_actividad
        self.notas = notas
        self.metadata = metadata or {}
        
        # Campos para Event Sourcing
        self.eventos: List = []
        self.version: int = 0

    def activar(self, notas: Optional[str] = None):
        """Activa el afiliado"""
        if self.estado not in [EstadoAfiliado.PENDIENTE_APROBACION, EstadoAfiliado.INACTIVO]:
            raise ValueError(f"No se puede activar un afiliado en estado {self.estado}")
        
        self.estado = EstadoAfiliado.ACTIVO
        self.fecha_ultima_actividad = datetime.now()
        if notas:
            self.notas = notas
        
        # Emitir evento
        evento = AfiliadoActivado(
            id_afiliado=self.id_afiliado,
            codigo_afiliado=self.codigo_afiliado,
            fecha_activacion=self.fecha_ultima_actividad,
            notas=notas,
            metadata={"version": self.version + 1}
        )
        self.agregar_evento(evento)

    def desactivar(self, motivo: str):
        """Desactiva el afiliado"""
        if self.estado == EstadoAfiliado.ACTIVO:
            self.estado = EstadoAfiliado.INACTIVO
            self.fecha_ultima_actividad = datetime.now()
            if self.notas:
                self.notas += f"\nDesactivado: {motivo}"
            else:
                self.notas = f"Desactivado: {motivo}"
            
            # Emitir evento
            evento = AfiliadoDesactivado(
                id_afiliado=self.id_afiliado,
                codigo_afiliado=self.codigo_afiliado,
                motivo=motivo,
                fecha_desactivacion=self.fecha_ultima_actividad,
                metadata={"version": self.version + 1}
            )
            self.agregar_evento(evento)

    def suspender(self, motivo: str):
        """Suspende el afiliado"""
        if self.estado == EstadoAfiliado.ACTIVO:
            self.estado = EstadoAfiliado.SUSPENDIDO
            self.fecha_ultima_actividad = datetime.now()
            if self.notas:
                self.notas += f"\nSuspendido: {motivo}"
            else:
                self.notas = f"Suspendido: {motivo}"
            
            # Emitir evento
            evento = AfiliadoSuspendido(
                id_afiliado=self.id_afiliado,
                codigo_afiliado=self.codigo_afiliado,
                motivo=motivo,
                fecha_suspension=self.fecha_ultima_actividad,
                metadata={"version": self.version + 1}
            )
            self.agregar_evento(evento)

    def actualizar_informacion_contacto(self, nueva_informacion: InformacionContacto):
        """Actualiza la información de contacto"""
        self.informacion_contacto = nueva_informacion
        self.fecha_ultima_actividad = datetime.now()

    def actualizar_configuracion(self, nueva_configuracion: ConfiguracionAfiliado):
        """Actualiza la configuración del afiliado"""
        configuracion_anterior = self.configuracion
        self.configuracion = nueva_configuracion
        self.fecha_ultima_actividad = datetime.now()
        
        # Emitir evento si cambió la comisión o límite
        if (configuracion_anterior.comision_porcentaje != nueva_configuracion.comision_porcentaje or
            configuracion_anterior.limite_mensual != nueva_configuracion.limite_mensual):
            
            evento = ConfiguracionAfiliadoActualizada(
                id_afiliado=self.id_afiliado,
                codigo_afiliado=self.codigo_afiliado,
                comision_anterior=configuracion_anterior.comision_porcentaje,
                comision_nueva=nueva_configuracion.comision_porcentaje,
                limite_anterior=configuracion_anterior.limite_mensual,
                limite_nuevo=nueva_configuracion.limite_mensual,
                fecha_actualizacion=self.fecha_ultima_actividad,
                metadata={"version": self.version + 1}
            )
            self.agregar_evento(evento)

    def registrar_actividad(self):
        """Registra actividad del afiliado"""
        self.fecha_ultima_actividad = datetime.now()
    
    def emitir_evento_registro(self):
        """Emite evento de registro del afiliado"""
        evento = AfiliadoRegistrado(
            id_afiliado=self.id_afiliado,
            codigo_afiliado=self.codigo_afiliado,
            nombre=self.nombre,
            tipo_afiliado=self.tipo_afiliado.value,
            email=self.informacion_contacto.email,
            ciudad=self.informacion_contacto.ciudad,
            pais=self.informacion_contacto.pais,
            comision_porcentaje=self.configuracion.comision_porcentaje,
            metadata={"version": self.version}
        )
        self.agregar_evento(evento)

    @property
    def id_afiliado(self) -> str:
        return self.id

    @property
    def es_activo(self) -> bool:
        return self.estado == EstadoAfiliado.ACTIVO

    @property
    def puede_recibir_comisiones(self) -> bool:
        return self.estado == EstadoAfiliado.ACTIVO
    
    def agregar_evento(self, evento):
        """Agrega un evento a la lista de eventos del afiliado"""
        self.eventos.append(evento)
        self.version += 1