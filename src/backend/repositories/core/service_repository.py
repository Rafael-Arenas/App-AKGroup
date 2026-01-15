"""
Repositorio para Service (departamentos/servicios).

Maneja el acceso a datos para servicios/departamentos.
"""

from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from src.backend.models.core.contacts import Service
from src.backend.repositories.base import BaseRepository
from src.backend.utils.logger import logger


class ServiceRepository(BaseRepository[Service]):
    """
    Repositorio para Service con métodos específicos.

    Además de los métodos CRUD base, proporciona métodos
    para búsquedas específicas de servicios/departamentos.

    Example:
        repo = ServiceRepository(session)
        service = repo.get_by_name("Ventas")
        services = repo.get_active_services()
    """

    def __init__(self, session: Session):
        """
        Inicializa el repositorio de Service.

        Args:
            session: Sesión de SQLAlchemy
        """
        super().__init__(session, Service)

    def get_by_name(self, name: str) -> Optional[Service]:
        """
        Busca un servicio por nombre.

        Args:
            name: Nombre del servicio

        Returns:
            Service si existe, None en caso contrario

        Example:
            service = repo.get_by_name("Ventas")
            if service:
                print(f"Servicio encontrado: {service.name}")
        """
        logger.debug(f"Buscando servicio por nombre: {name}")

        stmt = select(Service).filter(Service.name == name.strip())
        service = self.session.execute(stmt).scalar_one_or_none()

        if service:
            logger.debug(f"Servicio encontrado: {service.name} (id={service.id})")
        else:
            logger.debug(f"No se encontró servicio con nombre='{name}'")

        return service

    def search_by_name(self, name: str) -> List[Service]:
        """
        Busca servicios por nombre (búsqueda parcial).

        Args:
            name: Texto a buscar en el nombre
        """
        logger.debug(f"Buscando servicios por nombre: {name}")

        search_pattern = f"%{name}%"
        stmt = select(Service).filter(Service.name.ilike(search_pattern)).order_by(Service.name)
        services = list(self.session.execute(stmt).scalars().all())

        logger.debug(f"Encontrados {len(services)} servicio(s) con nombre '{name}'")
        return services

    def get_active_services(self, skip: int = 0, limit: int = 100) -> List[Service]:
        """
        Obtiene solo los servicios activos.
        """
        logger.debug(f"Obteniendo servicios activos - skip={skip}, limit={limit}")

        stmt = (
            select(Service)
            .filter(Service.is_active == True)
            .order_by(Service.name)
            .offset(skip)
            .limit(limit)
        )
        services = list(self.session.execute(stmt).scalars().all())

        logger.debug(f"Encontrados {len(services)} servicio(s) activo(s)")
        return services

    def get_all_ordered(self, skip: int = 0, limit: int = 100) -> List[Service]:
        """
        Obtiene todos los servicios ordenados alfabéticamente.
        """
        logger.debug(f"Obteniendo servicios ordenados - skip={skip}, limit={limit}")

        stmt = (
            select(Service)
            .order_by(Service.name)
            .offset(skip)
            .limit(limit)
        )
        services = list(self.session.execute(stmt).scalars().all())

        logger.debug(f"Encontrados {len(services)} servicio(s)")
        return services

    def count_contacts(self, service_id: int) -> int:
        """
        Cuenta cuántos contactos están asociados a un servicio.
        """
        from src.backend.models.core.contacts import Contact

        logger.debug(f"Contando contactos del servicio id={service_id}")

        stmt = select(func.count(Contact.id)).filter(Contact.service_id == service_id)
        count = self.session.execute(stmt).scalar() or 0

        logger.debug(f"Servicio id={service_id} tiene {count} contacto(s)")
        return count
