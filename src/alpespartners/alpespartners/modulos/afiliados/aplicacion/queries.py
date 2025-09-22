from dataclasses import dataclass
from typing import Optional, List
from ..dominio.objetos_valor import EstadoAfiliado, TipoAfiliado

@dataclass
class QueryObtenerAfiliado:
    """Query para obtener un afiliado por ID"""
    id_afiliado: str

@dataclass
class QueryObtenerAfiliadoPorCodigo:
    """Query para obtener un afiliado por código"""
    codigo_afiliado: str

@dataclass
class QueryObtenerAfiliadoPorEmail:
    """Query para obtener un afiliado por email"""
    email: str

@dataclass
class QueryBuscarAfiliados:
    """Query para buscar afiliados con filtros"""
    nombre: Optional[str] = None
    estado: Optional[str] = None
    tipo: Optional[str] = None
    ciudad: Optional[str] = None
    pais: Optional[str] = None
    limite: int = 100
    offset: int = 0

@dataclass
class QueryListarAfiliados:
    """Query para listar todos los afiliados"""
    limite: int = 100
    offset: int = 0

@dataclass
class QueryObtenerAfiliadosPorEstado:
    """Query para obtener afiliados por estado"""
    estado: str
    limite: int = 100
    offset: int = 0

@dataclass
class QueryObtenerAfiliadosPorTipo:
    """Query para obtener afiliados por tipo"""
    tipo: str
    limite: int = 100
    offset: int = 0

@dataclass
class QueryContarAfiliados:
    """Query para contar afiliados"""
    estado: Optional[str] = None
    tipo: Optional[str] = None
