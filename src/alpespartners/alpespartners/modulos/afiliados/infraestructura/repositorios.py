from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
import uuid

from ..dominio.entidades import Afiliado
from ..dominio.repositorios import RepositorioAfiliados
from ..dominio.objetos_valor import (
    EstadoAfiliado, 
    TipoAfiliado, 
    InformacionContacto, 
    InformacionFiscal, 
    ConfiguracionAfiliado
)
from .modelos import AfiliadoModel

class RepositorioAfiliadosSQL(RepositorioAfiliados):
    """Implementación SQL del repositorio de afiliados"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def agregar(self, afiliado: Afiliado) -> None:
        """Agrega un nuevo afiliado"""
        modelo = self._mapear_entidad_a_modelo(afiliado)
        self.session.add(modelo)
        self.session.commit()
        
        # Actualizar el ID de la entidad después del commit
        afiliado.id = str(modelo.id)
    
    def actualizar(self, afiliado: Afiliado) -> None:
        """Actualiza un afiliado existente"""
        try:
            # Convertir string ID a UUID para la comparación
            uuid_id = uuid.UUID(afiliado.id)
            modelo = self.session.query(AfiliadoModel).filter(AfiliadoModel.id == uuid_id).first()
            if modelo:
                self._actualizar_modelo_desde_entidad(modelo, afiliado)
                self.session.commit()
        except (ValueError, TypeError):
            # Si el ID no es un UUID válido, no hacer nada
            pass
    
    def eliminar(self, id_afiliado: str) -> None:
        """Elimina un afiliado"""
        try:
            # Convertir string ID a UUID para la comparación
            uuid_id = uuid.UUID(id_afiliado)
            modelo = self.session.query(AfiliadoModel).filter(AfiliadoModel.id == uuid_id).first()
            if modelo:
                self.session.delete(modelo)
                self.session.commit()
        except (ValueError, TypeError):
            # Si el ID no es un UUID válido, no hacer nada
            pass
    
    def obtener_por_id(self, id_afiliado: str) -> Optional[Afiliado]:
        """Obtiene un afiliado por su ID"""
        try:
            # Convertir string ID a UUID para la comparación
            uuid_id = uuid.UUID(id_afiliado)
            modelo = self.session.query(AfiliadoModel).filter(AfiliadoModel.id == uuid_id).first()
            if modelo:
                return self._mapear_modelo_a_entidad(modelo)
        except (ValueError, TypeError):
            # Si el ID no es un UUID válido, retornar None
            pass
        return None
    
    def obtener_por_codigo(self, codigo_afiliado: str) -> Optional[Afiliado]:
        """Obtiene un afiliado por su código"""
        modelo = self.session.query(AfiliadoModel).filter(AfiliadoModel.codigo_afiliado == codigo_afiliado).first()
        if modelo:
            return self._mapear_modelo_a_entidad(modelo)
        return None
    
    def obtener_por_email(self, email: str) -> Optional[Afiliado]:
        """Obtiene un afiliado por su email"""
        modelo = self.session.query(AfiliadoModel).filter(AfiliadoModel.email == email).first()
        if modelo:
            return self._mapear_modelo_a_entidad(modelo)
        return None
    
    def obtener_por_estado(self, estado: EstadoAfiliado) -> List[Afiliado]:
        """Obtiene afiliados por estado"""
        modelos = self.session.query(AfiliadoModel).filter(
            AfiliadoModel.estado == estado.value
        ).order_by(desc(AfiliadoModel.fecha_registro)).all()
        return [self._mapear_modelo_a_entidad(modelo) for modelo in modelos]
    
    def obtener_por_tipo(self, tipo: TipoAfiliado) -> List[Afiliado]:
        """Obtiene afiliados por tipo"""
        modelos = self.session.query(AfiliadoModel).filter(
            AfiliadoModel.tipo_afiliado == tipo.value
        ).order_by(desc(AfiliadoModel.fecha_registro)).all()
        return [self._mapear_modelo_a_entidad(modelo) for modelo in modelos]
    
    def buscar_por_nombre(self, nombre: str) -> List[Afiliado]:
        """Busca afiliados por nombre (búsqueda parcial)"""
        modelos = self.session.query(AfiliadoModel).filter(
            AfiliadoModel.nombre.ilike(f"%{nombre}%")
        ).order_by(desc(AfiliadoModel.fecha_registro)).all()
        return [self._mapear_modelo_a_entidad(modelo) for modelo in modelos]
    
    def listar_todos(self, limite: int = 100, offset: int = 0) -> List[Afiliado]:
        """Lista todos los afiliados con paginación"""
        modelos = self.session.query(AfiliadoModel).order_by(
            desc(AfiliadoModel.fecha_registro)
        ).offset(offset).limit(limite).all()
        return [self._mapear_modelo_a_entidad(modelo) for modelo in modelos]
    
    def contar_total(self) -> int:
        """Cuenta el total de afiliados"""
        return self.session.query(AfiliadoModel).count()
    
    def _mapear_entidad_a_modelo(self, afiliado: Afiliado) -> AfiliadoModel:
        """Mapea una entidad de afiliado a modelo SQLAlchemy"""
        return AfiliadoModel(
            id=afiliado.id,
            codigo_afiliado=afiliado.codigo_afiliado,
            nombre=afiliado.nombre,
            tipo_afiliado=afiliado.tipo_afiliado.value,
            estado=afiliado.estado.value,
            email=afiliado.informacion_contacto.email,
            telefono=afiliado.informacion_contacto.telefono,
            direccion=afiliado.informacion_contacto.direccion,
            ciudad=afiliado.informacion_contacto.ciudad,
            pais=afiliado.informacion_contacto.pais,
            codigo_postal=afiliado.informacion_contacto.codigo_postal,
            tipo_documento=afiliado.informacion_fiscal.tipo_documento,
            numero_documento=afiliado.informacion_fiscal.numero_documento,
            nombre_fiscal=afiliado.informacion_fiscal.nombre_fiscal,
            direccion_fiscal=afiliado.informacion_fiscal.direccion_fiscal,
            comision_porcentaje=afiliado.configuracion.comision_porcentaje,
            limite_mensual=afiliado.configuracion.limite_mensual,
            metodo_pago_preferido=afiliado.configuracion.metodo_pago_preferido,
            notificaciones_email=afiliado.configuracion.notificaciones_email,
            notificaciones_sms=afiliado.configuracion.notificaciones_sms,
            fecha_registro=afiliado.fecha_registro,
            fecha_ultima_actividad=afiliado.fecha_ultima_actividad,
            notas=afiliado.notas,
            metadatos=afiliado.metadata,
            version=afiliado.version
        )
    
    def _actualizar_modelo_desde_entidad(self, modelo: AfiliadoModel, afiliado: Afiliado) -> None:
        """Actualiza un modelo SQLAlchemy desde una entidad"""
        modelo.nombre = afiliado.nombre
        modelo.estado = afiliado.estado.value
        modelo.email = afiliado.informacion_contacto.email
        modelo.telefono = afiliado.informacion_contacto.telefono
        modelo.direccion = afiliado.informacion_contacto.direccion
        modelo.ciudad = afiliado.informacion_contacto.ciudad
        modelo.pais = afiliado.informacion_contacto.pais
        modelo.codigo_postal = afiliado.informacion_contacto.codigo_postal
        modelo.comision_porcentaje = afiliado.configuracion.comision_porcentaje
        modelo.limite_mensual = afiliado.configuracion.limite_mensual
        modelo.metodo_pago_preferido = afiliado.configuracion.metodo_pago_preferido
        modelo.notificaciones_email = afiliado.configuracion.notificaciones_email
        modelo.notificaciones_sms = afiliado.configuracion.notificaciones_sms
        modelo.fecha_ultima_actividad = afiliado.fecha_ultima_actividad
        modelo.notas = afiliado.notas
        modelo.metadatos = afiliado.metadata
        modelo.version = afiliado.version
    
    def _mapear_modelo_a_entidad(self, modelo: AfiliadoModel) -> Afiliado:
        """Mapea un modelo SQLAlchemy a entidad de afiliado"""
        # Reconstruir objetos valor
        informacion_contacto = InformacionContacto(
            email=modelo.email,
            telefono=modelo.telefono,
            direccion=modelo.direccion,
            ciudad=modelo.ciudad,
            pais=modelo.pais,
            codigo_postal=modelo.codigo_postal
        )
        
        informacion_fiscal = InformacionFiscal(
            tipo_documento=modelo.tipo_documento,
            numero_documento=modelo.numero_documento,
            nombre_fiscal=modelo.nombre_fiscal,
            direccion_fiscal=modelo.direccion_fiscal
        )
        
        configuracion = ConfiguracionAfiliado(
            comision_porcentaje=modelo.comision_porcentaje,
            limite_mensual=modelo.limite_mensual,
            metodo_pago_preferido=modelo.metodo_pago_preferido,
            notificaciones_email=modelo.notificaciones_email,
            notificaciones_sms=modelo.notificaciones_sms
        )
        
        afiliado = Afiliado(
            id=str(modelo.id),
            codigo_afiliado=modelo.codigo_afiliado,
            nombre=modelo.nombre,
            tipo_afiliado=TipoAfiliado(modelo.tipo_afiliado),
            informacion_contacto=informacion_contacto,
            informacion_fiscal=informacion_fiscal,
            configuracion=configuracion,
            estado=EstadoAfiliado(modelo.estado),
            fecha_registro=modelo.fecha_registro,
            fecha_ultima_actividad=modelo.fecha_ultima_actividad,
            notas=modelo.notas,
            metadata=modelo.metadatos or {}
        )
        
        # Establecer la versión después de crear el objeto
        afiliado.version = modelo.version
        
        return afiliado
