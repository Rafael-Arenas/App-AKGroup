"""
Capa de repositorio - Acceso a datos.

Este paquete implementa el patrón Repository para abstraer
el acceso a datos y proporcionar una API consistente para
operaciones CRUD sobre las entidades.

Uso recomendado:
    from src.backend.repositories import RepositoryFactory

    # En un endpoint
    repos = RepositoryFactory(session)
    company = repos.companies.get_by_id(1)
    orders = repos.orders.get_by_company(1)
"""

from src.backend.repositories.base import IRepository, BaseRepository, GenericLookupRepository
from src.backend.repositories.factory import RepositoryFactory, Repos

__all__ = [
    # Base classes
    "IRepository",
    "BaseRepository",
    "GenericLookupRepository",
    # Factory
    "RepositoryFactory",
    "Repos",  # Alias
]
