# src/alpespartners/alpespartners/modulos/loyalty/infraestructura/repositorios.py

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from ..dominio.entidades import Embajador
from ..dominio.repositorios import RepositorioEmbajadores
from ..dominio.objetos_valor import EstadoEmbajador
from .modelos import EmbajadorModel

class RepositorioEmbajadoresSQL(RepositorioEmbajadores):    
    def __init__(self, db: Session):
        self.db = db

    def agregar(self, embajador: Embajador) -> None:
        """Persiste un nuevo embajador en la base de datos"""
        db_embajador = EmbajadorModel(
            id=embajador.id_embajador,
            nombre=embajador.nombre,
            email=embajador.email,
            estado=embajador.estado.value if embajador.estado else "PENDIENTE",
            id_partner=embajador.id_partner,
            fecha_registro=embajador.fecha_registro,
            total_referidos=embajador.total_referidos,
            comisiones_ganadas=embajador.comisiones_ganadas
        )
        
        self.db.add(db_embajador)
        self.db.commit()
        self.db.refresh(db_embajador)

    def obtener_por_id(self, id_embajador: str) -> Optional[Embajador]:
        """Obtiene un embajador por su ID"""
        db_embajador = self.db.query(EmbajadorModel).filter(EmbajadorModel.id == id_embajador).first()
        if not db_embajador:
            return None
        
        return self._map_to_domain(db_embajador)

    def obtener_por_email(self, email: str) -> Optional[Embajador]:
        """Obtiene un embajador por su email"""
        db_embajador = self.db.query(EmbajadorModel).filter(EmbajadorModel.email == email).first()
        if not db_embajador:
            return None
            
        return self._map_to_domain(db_embajador)

    def obtener_por_partner(self, id_partner: str, activos_solo: bool = False) -> List[Embajador]:
        """Obtiene todos los embajadores de un partner específico"""
        query = self.db.query(EmbajadorModel).filter(EmbajadorModel.id_partner == id_partner)
        
        if activos_solo:
            query = query.filter(EmbajadorModel.estado == "ACTIVO")
        
        db_embajadores = query.all()
        return [self._map_to_domain(db_emb) for db_emb in db_embajadores]

    def actualizar(self, embajador: Embajador) -> None:
        """Actualiza un embajador existente"""
        db_embajador = self.db.query(EmbajadorModel).filter(
            EmbajadorModel.id == embajador.id_embajador
        ).first()
        
        if db_embajador:
            db_embajador.nombre = embajador.nombre
            db_embajador.email = embajador.email
            db_embajador.estado = embajador.estado.value if embajador.estado else db_embajador.estado
            db_embajador.id_partner = embajador.id_partner
            db_embajador.total_referidos = embajador.total_referidos
            db_embajador.comisiones_ganadas = embajador.comisiones_ganadas
            
            self.db.commit()
            self.db.refresh(db_embajador)

    def _map_to_domain(self, db_embajador: EmbajadorModel) -> Embajador:
        """Convierte el modelo de DB a entidad de dominio"""
        embajador = Embajador(
            id=db_embajador.id,
            nombre=db_embajador.nombre,
            email=db_embajador.email,
            estado=EstadoEmbajador(db_embajador.estado) if db_embajador.estado else None,
            id_partner=db_embajador.id_partner,
            fecha_registro=db_embajador.fecha_registro,
            total_referidos=db_embajador.total_referidos,
            comisiones_ganadas=db_embajador.comisiones_ganadas
        )
        
        return embajador