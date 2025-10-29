"""
Capa de repositorio - Acceso a datos.

Este paquete implementa el patrón Repository para abstraer
el acceso a datos y proporcionar una API consistente para
operaciones CRUD sobre las entidades.
"""

from src.repositories.base import IRepository, BaseRepository

__all__ = [
    "IRepository",
    "BaseRepository",
]
