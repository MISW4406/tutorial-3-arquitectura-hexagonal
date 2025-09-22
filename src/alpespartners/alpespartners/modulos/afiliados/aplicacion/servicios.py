from typing import List, Optional
from datetime import datetime
from uuid import uuid4

from ..dominio.entidades import Afiliado
from ..dominio.repositorios import RepositorioAfiliados
from ..dominio.objetos_valor import (
    TipoAfiliado, 
    EstadoAfiliado, 
    InformacionContacto, 
    InformacionFiscal, 
    ConfiguracionAfiliado
)

from .comandos import (
    ComandoCrearAfiliado,
    ComandoActualizarAfiliado,
    ComandoActivarAfiliado,
    ComandoDesactivarAfiliado,
    ComandoSuspenderAfiliado,
    ComandoEliminarAfiliado
)

from .queries import (
    QueryObtenerAfiliado,
    QueryObtenerAfiliadoPorCodigo,
    QueryObtenerAfiliadoPorEmail,
    QueryBuscarAfiliados,
    QueryListarAfiliados,
    QueryObtenerAfiliadosPorEstado,
    QueryObtenerAfiliadosPorTipo,
    QueryContarAfiliados
)

from .dto import (
    AfiliadoDTO,
    ResultadoAfiliadoDTO,
    EstadisticasAfiliadosDTO,
    InformacionContactoDTO,
    InformacionFiscalDTO,
    ConfiguracionAfiliadoDTO
)

class ServicioAfiliados:
    """Servicio de aplicación para gestión de afiliados"""
    
    def __init__(self, repositorio_afiliados: RepositorioAfiliados, despachador_eventos=None):
        self.repositorio_afiliados = repositorio_afiliados
        self.despachador_eventos = despachador_eventos

    def crear_afiliado(self, comando: ComandoCrearAfiliado) -> str:
        """Crea un nuevo afiliado"""
        
        # Validar que el código no exista
        if self.repositorio_afiliados.obtener_por_codigo(comando.codigo_afiliado):
            raise ValueError(f"Ya existe un afiliado con el código {comando.codigo_afiliado}")
        
        # Validar que el email no exista
        if self.repositorio_afiliados.obtener_por_email(comando.email):
            raise ValueError(f"Ya existe un afiliado con el email {comando.email}")
        
        # Crear objetos valor
        informacion_contacto = InformacionContacto(
            email=comando.email,
            telefono=comando.telefono,
            direccion=comando.direccion,
            ciudad=comando.ciudad,
            pais=comando.pais,
            codigo_postal=comando.codigo_postal
        )
        
        informacion_fiscal = InformacionFiscal(
            tipo_documento=comando.tipo_documento,
            numero_documento=comando.numero_documento,
            nombre_fiscal=comando.nombre_fiscal or comando.nombre,
            direccion_fiscal=comando.direccion_fiscal
        )
        
        configuracion = ConfiguracionAfiliado(
            comision_porcentaje=comando.comision_porcentaje,
            limite_mensual=comando.limite_mensual,
            metodo_pago_preferido=comando.metodo_pago_preferido,
            notificaciones_email=comando.notificaciones_email,
            notificaciones_sms=comando.notificaciones_sms
        )
        
        # Crear entidad
        afiliado = Afiliado(
            id=str(uuid4()),
            codigo_afiliado=comando.codigo_afiliado,
            nombre=comando.nombre,
            tipo_afiliado=TipoAfiliado(comando.tipo_afiliado),
            informacion_contacto=informacion_contacto,
            informacion_fiscal=informacion_fiscal,
            configuracion=configuracion,
            notas=comando.notas,
            metadata=comando.metadata or {}
        )
        
        # Guardar
        self.repositorio_afiliados.agregar(afiliado)
        
        # Emitir evento de registro
        afiliado.emitir_evento_registro()
        
        # Publicar eventos si hay despachador
        if self.despachador_eventos and afiliado.eventos:
            self.despachador_eventos.publicar_eventos(afiliado.eventos)
        
        return afiliado.id_afiliado

    def actualizar_afiliado(self, comando: ComandoActualizarAfiliado) -> ResultadoAfiliadoDTO:
        """Actualiza un afiliado existente"""
        
        afiliado = self.repositorio_afiliados.obtener_por_id(comando.id_afiliado)
        if not afiliado:
            return ResultadoAfiliadoDTO(
                exitoso=False,
                mensaje=f"No se encontró afiliado con ID {comando.id_afiliado}",
                codigo_error="AFILIADO_NO_ENCONTRADO"
            )
        
        # Actualizar campos si se proporcionan
        if comando.nombre:
            afiliado.nombre = comando.nombre
        
        if comando.email:
            # Verificar que el email no esté en uso por otro afiliado
            afiliado_existente = self.repositorio_afiliados.obtener_por_email(comando.email)
            if afiliado_existente and afiliado_existente.id_afiliado != comando.id_afiliado:
                return ResultadoAfiliadoDTO(
                    exitoso=False,
                    mensaje=f"El email {comando.email} ya está en uso por otro afiliado",
                    codigo_error="EMAIL_EN_USO"
                )
            
            # Actualizar información de contacto
            nueva_info_contacto = InformacionContacto(
                email=comando.email,
                telefono=comando.telefono or afiliado.informacion_contacto.telefono,
                direccion=comando.direccion or afiliado.informacion_contacto.direccion,
                ciudad=comando.ciudad or afiliado.informacion_contacto.ciudad,
                pais=comando.pais or afiliado.informacion_contacto.pais,
                codigo_postal=comando.codigo_postal or afiliado.informacion_contacto.codigo_postal
            )
            afiliado.actualizar_informacion_contacto(nueva_info_contacto)
        
        if comando.comision_porcentaje is not None:
            nueva_configuracion = ConfiguracionAfiliado(
                comision_porcentaje=comando.comision_porcentaje,
                limite_mensual=comando.limite_mensual or afiliado.configuracion.limite_mensual,
                metodo_pago_preferido=comando.metodo_pago_preferido or afiliado.configuracion.metodo_pago_preferido,
                notificaciones_email=comando.notificaciones_email if comando.notificaciones_email is not None else afiliado.configuracion.notificaciones_email,
                notificaciones_sms=comando.notificaciones_sms if comando.notificaciones_sms is not None else afiliado.configuracion.notificaciones_sms
            )
            afiliado.actualizar_configuracion(nueva_configuracion)
        
        if comando.notas:
            afiliado.notas = comando.notas
        
        if comando.metadata:
            afiliado.metadata.update(comando.metadata)
        
        # Guardar cambios
        self.repositorio_afiliados.actualizar(afiliado)
        
        # Publicar eventos si hay despachador
        if self.despachador_eventos and afiliado.eventos:
            self.despachador_eventos.publicar_eventos(afiliado.eventos)
        
        return ResultadoAfiliadoDTO(
            exitoso=True,
            mensaje="Afiliado actualizado exitosamente",
            id_afiliado=afiliado.id_afiliado
        )

    def activar_afiliado(self, comando: ComandoActivarAfiliado) -> ResultadoAfiliadoDTO:
        """Activa un afiliado"""
        
        afiliado = self.repositorio_afiliados.obtener_por_id(comando.id_afiliado)
        if not afiliado:
            return ResultadoAfiliadoDTO(
                exitoso=False,
                mensaje=f"No se encontró afiliado con ID {comando.id_afiliado}",
                codigo_error="AFILIADO_NO_ENCONTRADO"
            )
        
        try:
            afiliado.activar(comando.notas)
            self.repositorio_afiliados.actualizar(afiliado)
            
            # Publicar eventos si hay despachador
            if self.despachador_eventos and afiliado.eventos:
                self.despachador_eventos.publicar_eventos(afiliado.eventos)
            
            return ResultadoAfiliadoDTO(
                exitoso=True,
                mensaje="Afiliado activado exitosamente",
                id_afiliado=afiliado.id_afiliado
            )
        except ValueError as e:
            return ResultadoAfiliadoDTO(
                exitoso=False,
                mensaje=str(e),
                codigo_error="ESTADO_INVALIDO"
            )

    def desactivar_afiliado(self, comando: ComandoDesactivarAfiliado) -> ResultadoAfiliadoDTO:
        """Desactiva un afiliado"""
        
        afiliado = self.repositorio_afiliados.obtener_por_id(comando.id_afiliado)
        if not afiliado:
            return ResultadoAfiliadoDTO(
                exitoso=False,
                mensaje=f"No se encontró afiliado con ID {comando.id_afiliado}",
                codigo_error="AFILIADO_NO_ENCONTRADO"
            )
        
        try:
            afiliado.desactivar(comando.motivo)
            self.repositorio_afiliados.actualizar(afiliado)
            
            # Publicar eventos si hay despachador
            if self.despachador_eventos and afiliado.eventos:
                self.despachador_eventos.publicar_eventos(afiliado.eventos)
            
            return ResultadoAfiliadoDTO(
                exitoso=True,
                mensaje="Afiliado desactivado exitosamente",
                id_afiliado=afiliado.id_afiliado
            )
        except ValueError as e:
            return ResultadoAfiliadoDTO(
                exitoso=False,
                mensaje=str(e),
                codigo_error="ESTADO_INVALIDO"
            )

    def suspender_afiliado(self, comando: ComandoSuspenderAfiliado) -> ResultadoAfiliadoDTO:
        """Suspende un afiliado"""
        
        afiliado = self.repositorio_afiliados.obtener_por_id(comando.id_afiliado)
        if not afiliado:
            return ResultadoAfiliadoDTO(
                exitoso=False,
                mensaje=f"No se encontró afiliado con ID {comando.id_afiliado}",
                codigo_error="AFILIADO_NO_ENCONTRADO"
            )
        
        try:
            afiliado.suspender(comando.motivo)
            self.repositorio_afiliados.actualizar(afiliado)
            
            # Publicar eventos si hay despachador
            if self.despachador_eventos and afiliado.eventos:
                self.despachador_eventos.publicar_eventos(afiliado.eventos)
            
            return ResultadoAfiliadoDTO(
                exitoso=True,
                mensaje="Afiliado suspendido exitosamente",
                id_afiliado=afiliado.id_afiliado
            )
        except ValueError as e:
            return ResultadoAfiliadoDTO(
                exitoso=False,
                mensaje=str(e),
                codigo_error="ESTADO_INVALIDO"
            )

    def eliminar_afiliado(self, comando: ComandoEliminarAfiliado) -> ResultadoAfiliadoDTO:
        """Elimina un afiliado"""
        
        afiliado = self.repositorio_afiliados.obtener_por_id(comando.id_afiliado)
        if not afiliado:
            return ResultadoAfiliadoDTO(
                exitoso=False,
                mensaje=f"No se encontró afiliado con ID {comando.id_afiliado}",
                codigo_error="AFILIADO_NO_ENCONTRADO"
            )
        
        # En un sistema real, aquí se haría soft delete o se verificarían dependencias
        # Por simplicidad, eliminamos directamente
        self.repositorio_afiliados.eliminar(comando.id_afiliado)
        
        return ResultadoAfiliadoDTO(
            exitoso=True,
            mensaje="Afiliado eliminado exitosamente",
            id_afiliado=comando.id_afiliado
        )

    # Métodos de consulta
    def obtener_afiliado(self, query: QueryObtenerAfiliado) -> Optional[AfiliadoDTO]:
        """Obtiene un afiliado por ID"""
        afiliado = self.repositorio_afiliados.obtener_por_id(query.id_afiliado)
        return self._mapear_afiliado_a_dto(afiliado) if afiliado else None

    def obtener_afiliado_por_codigo(self, query: QueryObtenerAfiliadoPorCodigo) -> Optional[AfiliadoDTO]:
        """Obtiene un afiliado por código"""
        afiliado = self.repositorio_afiliados.obtener_por_codigo(query.codigo_afiliado)
        return self._mapear_afiliado_a_dto(afiliado) if afiliado else None

    def obtener_afiliado_por_email(self, query: QueryObtenerAfiliadoPorEmail) -> Optional[AfiliadoDTO]:
        """Obtiene un afiliado por email"""
        afiliado = self.repositorio_afiliados.obtener_por_email(query.email)
        return self._mapear_afiliado_a_dto(afiliado) if afiliado else None

    def buscar_afiliados(self, query: QueryBuscarAfiliados) -> List[AfiliadoDTO]:
        """Busca afiliados con filtros"""
        # Si hay nombre, buscar por nombre, sino obtener todos
        if query.nombre:
            afiliados = self.repositorio_afiliados.buscar_por_nombre(query.nombre)
        else:
            afiliados = self.repositorio_afiliados.listar_todos(limite=10000)  # Obtener todos para filtrar
        
        # Aplicar filtros adicionales
        if query.estado:
            afiliados = [a for a in afiliados if a.estado.value == query.estado]
        if query.tipo:
            afiliados = [a for a in afiliados if a.tipo_afiliado.value == query.tipo]
        if query.ciudad:
            afiliados = [a for a in afiliados if a.informacion_contacto.ciudad == query.ciudad]
        if query.pais:
            afiliados = [a for a in afiliados if a.informacion_contacto.pais == query.pais]
        
        # Aplicar paginación
        afiliados = afiliados[query.offset:query.offset + query.limite]
        
        return [self._mapear_afiliado_a_dto(afiliado) for afiliado in afiliados]

    def listar_afiliados(self, query: QueryListarAfiliados) -> List[AfiliadoDTO]:
        """Lista todos los afiliados"""
        afiliados = self.repositorio_afiliados.listar_todos(query.limite, query.offset)
        return [self._mapear_afiliado_a_dto(afiliado) for afiliado in afiliados]

    def obtener_estadisticas(self) -> EstadisticasAfiliadosDTO:
        """Obtiene estadísticas de afiliados"""
        # Obtener todos los afiliados para estadísticas (sin límite)
        todos_afiliados = []
        offset = 0
        limite = 1000
        
        while True:
            batch = self.repositorio_afiliados.listar_todos(limite=limite, offset=offset)
            if not batch:
                break
            todos_afiliados.extend(batch)
            offset += limite
        
        total = len(todos_afiliados)
        activos = len([a for a in todos_afiliados if a.estado == EstadoAfiliado.ACTIVO])
        inactivos = len([a for a in todos_afiliados if a.estado == EstadoAfiliado.INACTIVO])
        suspendidos = len([a for a in todos_afiliados if a.estado == EstadoAfiliado.SUSPENDIDO])
        pendientes = len([a for a in todos_afiliados if a.estado == EstadoAfiliado.PENDIENTE_APROBACION])
        
        # Contar por tipo
        por_tipo = {}
        for afiliado in todos_afiliados:
            tipo = afiliado.tipo_afiliado.value
            por_tipo[tipo] = por_tipo.get(tipo, 0) + 1
        
        # Contar por ciudad
        por_ciudad = {}
        for afiliado in todos_afiliados:
            if afiliado.informacion_contacto.ciudad:
                ciudad = afiliado.informacion_contacto.ciudad
                por_ciudad[ciudad] = por_ciudad.get(ciudad, 0) + 1
        
        # Contar por país
        por_pais = {}
        for afiliado in todos_afiliados:
            if afiliado.informacion_contacto.pais:
                pais = afiliado.informacion_contacto.pais
                por_pais[pais] = por_pais.get(pais, 0) + 1
        
        # Calcular tasa de activación
        tasa_activacion = (activos / total * 100) if total > 0 else 0.0
        
        return EstadisticasAfiliadosDTO(
            total_afiliados=total,
            afiliados_activos=activos,
            afiliados_inactivos=inactivos,
            afiliados_suspendidos=suspendidos,
            afiliados_pendientes=pendientes,
            por_tipo=por_tipo,
            por_ciudad=por_ciudad,
            por_pais=por_pais,
            tasa_activacion=tasa_activacion
        )

    def _mapear_afiliado_a_dto(self, afiliado: Afiliado) -> AfiliadoDTO:
        """Mapea un afiliado a DTO"""
        return AfiliadoDTO(
            id_afiliado=afiliado.id_afiliado,
            codigo_afiliado=afiliado.codigo_afiliado,
            nombre=afiliado.nombre,
            tipo_afiliado=afiliado.tipo_afiliado.value,
            estado=afiliado.estado.value,
            informacion_contacto=InformacionContactoDTO(
                email=afiliado.informacion_contacto.email,
                telefono=afiliado.informacion_contacto.telefono,
                direccion=afiliado.informacion_contacto.direccion,
                ciudad=afiliado.informacion_contacto.ciudad,
                pais=afiliado.informacion_contacto.pais,
                codigo_postal=afiliado.informacion_contacto.codigo_postal
            ),
            informacion_fiscal=InformacionFiscalDTO(
                tipo_documento=afiliado.informacion_fiscal.tipo_documento,
                numero_documento=afiliado.informacion_fiscal.numero_documento,
                nombre_fiscal=afiliado.informacion_fiscal.nombre_fiscal,
                direccion_fiscal=afiliado.informacion_fiscal.direccion_fiscal
            ),
            configuracion=ConfiguracionAfiliadoDTO(
                comision_porcentaje=afiliado.configuracion.comision_porcentaje,
                limite_mensual=afiliado.configuracion.limite_mensual,
                metodo_pago_preferido=afiliado.configuracion.metodo_pago_preferido,
                notificaciones_email=afiliado.configuracion.notificaciones_email,
                notificaciones_sms=afiliado.configuracion.notificaciones_sms
            ),
            fecha_registro=afiliado.fecha_registro,
            fecha_ultima_actividad=afiliado.fecha_ultima_actividad,
            notas=afiliado.notas,
            metadata=afiliado.metadata
        )
