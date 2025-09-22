from abc import ABC, abstractmethod
from typing import List, Optional
from .entidades import Afiliado
from .objetos_valor import EstadoAfiliado, TipoAfiliado

class RepositorioAfiliados(ABC):
    """Interfaz del repositorio de afiliados"""
    
    @abstractmethod
    def agregar(self, afiliado: Afiliado) -> None:
        """Agrega un nuevo afiliado"""
        pass
    
    @abstractmethod
    def actualizar(self, afiliado: Afiliado) -> None:
        """Actualiza un afiliado existente"""
        pass
    
    @abstractmethod
    def obtener_por_id(self, id_afiliado: str) -> Optional[Afiliado]:
        """Obtiene un afiliado por su ID"""
        pass
    
    @abstractmethod
    def obtener_por_codigo(self, codigo_afiliado: str) -> Optional[Afiliado]:
        """Obtiene un afiliado por su código"""
        pass
    
    @abstractmethod
    def obtener_por_email(self, email: str) -> Optional[Afiliado]:
        """Obtiene un afiliado por su email"""
        pass
    
    @abstractmethod
    def obtener_por_estado(self, estado: EstadoAfiliado) -> List[Afiliado]:
        """Obtiene afiliados por estado"""
        pass
    
    @abstractmethod
    def obtener_por_tipo(self, tipo: TipoAfiliado) -> List[Afiliado]:
        """Obtiene afiliados por tipo"""
        pass
    
    @abstractmethod
    def buscar_por_nombre(self, nombre: str) -> List[Afiliado]:
        """Busca afiliados por nombre (búsqueda parcial)"""
        pass
    
    @abstractmethod
    def listar_todos(self, limite: int = 100, offset: int = 0) -> List[Afiliado]:
        """Lista todos los afiliados con paginación"""
        pass
    
    @abstractmethod
    def contar_total(self) -> int:
        """Cuenta el total de afiliados"""
        pass
