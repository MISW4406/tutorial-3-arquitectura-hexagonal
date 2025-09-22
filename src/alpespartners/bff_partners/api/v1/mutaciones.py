import strawberry
import typing
import uuid
import requests
import os
from datetime import datetime
from strawberry.types import Info

import utils
from despachadores import Despachador

from .esquemas import *

@strawberry.type
class Mutation:
    """Mutaciones GraphQL para Alpes Partners"""

    @strawberry.mutation
    async def registrar_click(
        self, 
        id_partner: str, 
        id_campana: str, 
        url_origen: str, 
        url_destino: str,
        info: Info
    ) -> RespuestaOperacion:
        """Registra un nuevo click"""
        try:
            payload = {
                "id_partner": id_partner,
                "id_campana": id_campana,
                "url_origen": url_origen,
                "url_destino": url_destino,
                "metadata_cliente": {
                    "timestamp": utils.time_millis(),
                    "source": "BFF"
                }
            }
            
            comando = {
                "id": str(uuid.uuid4()),
                "time": utils.time_millis(),
                "specversion": "v1",
                "type": "ComandoRegistrarClick",
                "ingestion": utils.time_millis(),
                "datacontenttype": "AVRO",
                "service_name": "BFF Partners",
                "data": payload
            }
            
            despachador = Despachador()
            info.context["background_tasks"].add_task(
                despachador.publicar_mensaje, 
                comando, 
                "comando-registrar-click", 
                "public/default/comando-registrar-click"
            )
            
            return RespuestaOperacion(
                mensaje="Click registrado exitosamente", 
                codigo=202, 
                exito=True
            )
        except Exception as e:
            return RespuestaOperacion(
                mensaje=f"Error registrando click: {str(e)}", 
                codigo=500, 
                exito=False
            )

    @strawberry.mutation
    async def registrar_conversion(
        self, 
        id_partner: str, 
        id_campana: str, 
        tipo_conversion: str,
        valor: float,
        moneda: str,
        info: Info
    ) -> RespuestaOperacion:
        """Registra una nueva conversión"""
        try:
            payload = {
                "id_partner": id_partner,
                "id_campana": id_campana,
                "tipo_conversion": tipo_conversion,
                "informacion_monetaria": {
                    "valor": valor,
                    "moneda": moneda,
                    "comision": valor * 0.1,  # 10% de comisión por defecto
                    "porcentaje_comision": 10.0
                },
                "metadata_cliente": {
                    "timestamp": utils.time_millis(),
                    "source": "BFF"
                }
            }
            
            comando = {
                "id": str(uuid.uuid4()),
                "time": utils.time_millis(),
                "specversion": "v1",
                "type": "ComandoRegistrarConversion",
                "ingestion": utils.time_millis(),
                "datacontenttype": "AVRO",
                "service_name": "BFF Partners",
                "data": payload
            }
            
            despachador = Despachador()
            info.context["background_tasks"].add_task(
                despachador.publicar_mensaje, 
                comando, 
                "comando-registrar-conversion", 
                "public/default/comando-registrar-conversion"
            )
            
            return RespuestaOperacion(
                mensaje="Conversión registrada exitosamente", 
                codigo=202, 
                exito=True
            )
        except Exception as e:
            return RespuestaOperacion(
                mensaje=f"Error registrando conversión: {str(e)}", 
                codigo=500, 
                exito=False
            )

    @strawberry.mutation
    async def crear_afiliado(
        self, 
        codigo_afiliado: str, 
        nombre: str, 
        email: str, 
        tipo_afiliado: str,
        info: Info
    ) -> RespuestaOperacion:
        """Crea un nuevo afiliado"""
        try:
            payload = {
                "codigo_afiliado": codigo_afiliado,
                "nombre": nombre,
                "email": email,
                "tipo_afiliado": tipo_afiliado,
                "informacion_contacto": {
                    "email": email,
                    "telefono": "",
                    "direccion": ""
                }
            }
            
            comando = {
                "id": str(uuid.uuid4()),
                "time": utils.time_millis(),
                "specversion": "v1",
                "type": "ComandoCrearAfiliado",
                "ingestion": utils.time_millis(),
                "datacontenttype": "AVRO",
                "service_name": "BFF Partners",
                "data": payload
            }
            
            despachador = Despachador()
            info.context["background_tasks"].add_task(
                despachador.publicar_mensaje, 
                comando, 
                "comando-crear-afiliado", 
                "public/default/comando-crear-afiliado"
            )
            
            return RespuestaOperacion(
                mensaje="Afiliado creado exitosamente", 
                codigo=202, 
                exito=True
            )
        except Exception as e:
            return RespuestaOperacion(
                mensaje=f"Error creando afiliado: {str(e)}", 
                codigo=500, 
                exito=False
            )

    @strawberry.mutation
    async def procesar_pago_comision(
        self, 
        id_partner: str, 
        monto: float, 
        moneda: str,
        info: Info
    ) -> RespuestaOperacion:
        """Procesa un pago de comisión"""
        try:
            payload = {
                "id_partner": id_partner,
                "monto": monto,
                "moneda": moneda,
                "tipo_pago": "COMISION",
                "metadata": {
                    "initiated_by": "BFF",
                    "timestamp": utils.time_millis()
                }
            }
            
            comando = {
                "id": str(uuid.uuid4()),
                "time": utils.time_millis(),
                "specversion": "v1",
                "type": "ComandoCrearPago",
                "ingestion": utils.time_millis(),
                "datacontenttype": "AVRO",
                "service_name": "BFF Partners",
                "data": payload
            }
            
            despachador = Despachador()
            info.context["background_tasks"].add_task(
                despachador.publicar_mensaje, 
                comando, 
                "comando-crear-pago", 
                "public/default/comando-crear-pago"
            )
            
            return RespuestaOperacion(
                mensaje="Pago de comisión iniciado exitosamente", 
                codigo=202, 
                exito=True
            )
        except Exception as e:
            return RespuestaOperacion(
                mensaje=f"Error procesando pago: {str(e)}", 
                codigo=500, 
                exito=False
            )