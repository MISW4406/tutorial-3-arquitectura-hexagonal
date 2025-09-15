from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from ..dominio.entidades import Embajador
from ..dominio.repositorios import RepositorioEmbajadores
from ..dominio.objetos_valor import EstadoEmbajador
from ..dominio.eventos import EmbajadorCreado, EmbajadorActivado, ReferidoRegistrado
from ....seedwork.dominio.eventos import Despachador

@dataclass
class ServicioLoyalty:
    
    repositorio_embajadores: RepositorioEmbajadores
    despachador: Despachador

    def crear_embajador(self,
                       nombre: str,
                       email: str,
                       id_partner: Optional[str] = None) -> str:

        embajador_existente = self.repositorio_embajadores.obtener_por_email(email)
        if embajador_existente:
            raise ValueError(f"Ya existe un embajador con el email {email}")
        
        info_contacto = None
        
        embajador = Embajador(
            nombre=nombre,
            email=email,
            estado=EstadoEmbajador.PENDIENTE,
            id_partner=id_partner,
            fecha_registro=datetime.now()
        )
        
        embajador.crear_embajador()
        
        self.repositorio_embajadores.agregar(embajador)
        
        for evento in embajador.eventos:
            self.despachador.publicar_evento(evento)
        
        return embajador.id_embajador

    def activar_embajador(self, id_embajador: str) -> None:
        embajador = self.repositorio_embajadores.obtener_por_id(id_embajador)
        if not embajador:
            raise ValueError(f"No se encontró embajador con ID {id_embajador}")
        
        if embajador.estado != EstadoEmbajador.PENDIENTE:
            raise ValueError(f"El embajador debe estar en estado PENDIENTE para ser activado")
        
        embajador.activar_embajador()
        
        self.repositorio_embajadores.actualizar(embajador)
        
        evento = EmbajadorActivado(
            id_embajador=embajador.id_embajador,
            id_partner=embajador.id_partner,
            fecha_activacion=datetime.now()
        )
        self.despachador.publicar_evento(evento)

    def registrar_referido(self,
                          id_embajador: str,
                          email_referido: str,
                          nombre_referido: Optional[str] = None,
                          valor_conversion: float = 0.0,
                          porcentaje_comision: float = 5.0,
                          metadata_referido: Optional[dict] = None) -> str:
        """
        Registra un nuevo referido para un embajador.
        Este método dispara un evento que será escuchado por el Tracking Service.
        """
        
        embajador = self.repositorio_embajadores.obtener_por_id(id_embajador)
        if not embajador:
            raise ValueError(f"No se encontró embajador con ID {id_embajador}")
        
        if embajador.estado != EstadoEmbajador.ACTIVO:
            raise ValueError(f"El embajador debe estar ACTIVO para generar referidos")
        
        comision_embajador = valor_conversion * (porcentaje_comision / 100)
        
        embajador.registrar_referido_exitoso(valor_conversion, comision_embajador)
        
        self.repositorio_embajadores.actualizar(embajador)
        
        id_referido = str(uuid4())
        
        # Crear y publicar evento - ESTE ES EL EVENTO QUE ESCUCHARÁ TRACKING SERVICE
        evento = ReferidoRegistrado(
            id_referido=id_referido,
            id_embajador=embajador.id_embajador,
            id_partner=embajador.id_partner,
            email_referido=email_referido,
            nombre_referido=nombre_referido,
            valor_conversion=valor_conversion,
            comision_embajador=comision_embajador,
            metadata_referido=metadata_referido or {},
            timestamp=datetime.now()
        )
        
        self.despachador.publicar_evento(evento)
        
        return id_referido

    def obtener_embajadores_partner(self, id_partner: str, activos_solo: bool = True) -> List[Embajador]:
        """Obtiene todos los embajadores de un partner"""
        return self.repositorio_embajadores.obtener_por_partner(id_partner, activos_solo)

    def obtener_embajador_por_id(self, id_embajador: str) -> Optional[Embajador]:
        """Obtiene un embajador por su ID"""
        return self.repositorio_embajadores.obtener_por_id(id_embajador)

    def obtener_embajador_por_email(self, email: str) -> Optional[Embajador]:
        """Obtiene un embajador por su email"""
        return self.repositorio_embajadores.obtener_por_email(email)