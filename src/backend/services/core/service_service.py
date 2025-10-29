"""
Servicio de lógica de negocio para Service (departamentos/servicios).

Implementa validaciones y reglas de negocio para servicios/departamentos.
"""

from sqlalchemy.orm import Session

from src.backend.models.core.contacts import Service
from src.backend.repositories.core.service_repository import ServiceRepository
from src.shared.schemas.core.service import ServiceCreate, ServiceUpdate, ServiceResponse
from src.backend.services.base import BaseService
from src.backend.exceptions.service import ValidationException, BusinessRuleException
from src.backend.exceptions.repository import NotFoundException
from src.backend.utils.logger import logger


class ServiceService(BaseService[Service, ServiceCreate, ServiceUpdate, ServiceResponse]):
    """
    Servicio para Service con validaciones de negocio.

    Maneja la lógica de negocio para servicios/departamentos, incluyendo:
    - Validación de unicidad de nombre
    - Validación antes de eliminación
    - Reglas de negocio específicas

    Example:
        service = ServiceService(repository, session)
        dept = service.create(ServiceCreate(...), user_id=1)
    """

    def __init__(
        self,
        repository: ServiceRepository,
        session: Session,
    ):
        """
        Inicializa el servicio de Service.

        Args:
            repository: Repositorio de Service
            session: Sesión de SQLAlchemy
        """
        super().__init__(
            repository=repository,
            session=session,
            model=Service,
            response_schema=ServiceResponse,
        )
        # Cast para tener acceso a métodos específicos de ServiceRepository
        self.service_repo: ServiceRepository = repository

    def validate_create(self, entity: Service) -> None:
        """
        Valida reglas de negocio antes de crear un servicio.

        Args:
            entity: Servicio a validar

        Raises:
            ValidationException: Si el nombre ya existe
        """
        logger.debug(f"Validando creación de servicio: name={entity.name}")

        # Validar que el nombre sea único
        existing = self.service_repo.get_by_name(entity.name)
        if existing:
            raise ValidationException(
                f"Ya existe un servicio con el nombre '{entity.name}'",
                details={
                    "name": entity.name,
                    "existing_service_id": existing.id,
                }
            )

        logger.debug("Validación de creación exitosa")

    def validate_update(self, entity: Service) -> None:
        """
        Valida reglas de negocio antes de actualizar un servicio.

        Args:
            entity: Servicio a validar

        Raises:
            ValidationException: Si el nombre ya existe en otro servicio
        """
        logger.debug(f"Validando actualización de servicio id={entity.id}")

        # Validar que el nombre sea único (excluyendo el mismo servicio)
        existing = self.service_repo.get_by_name(entity.name)
        if existing and existing.id != entity.id:
            raise ValidationException(
                f"Ya existe otro servicio con el nombre '{entity.name}'",
                details={
                    "name": entity.name,
                    "current_service_id": entity.id,
                    "existing_service_id": existing.id,
                }
            )

        logger.debug("Validación de actualización exitosa")

    def delete(self, id: int, user_id: int, soft: bool = True) -> None:
        """
        Elimina un servicio.

        Valida que no tenga contactos asociados antes de eliminar.

        Args:
            id: ID del servicio a eliminar
            user_id: ID del usuario que elimina
            soft: Si True, hace soft delete; si False, hard delete

        Raises:
            NotFoundException: Si el servicio no existe
            BusinessRuleException: Si el servicio tiene contactos asociados

        Example:
            service.delete(id=1, user_id=1, soft=True)
        """
        logger.info(f"Servicio: eliminando service id={id} (soft={soft})")

        # Verificar que existe
        service = self.service_repo.get_by_id(id)
        if not service:
            raise NotFoundException(
                f"Servicio no encontrado",
                details={"service_id": id}
            )

        # Verificar que no tiene contactos asociados
        contact_count = self.service_repo.count_contacts(id)
        if contact_count > 0:
            raise BusinessRuleException(
                f"No se puede eliminar el servicio porque tiene {contact_count} contacto(s) asociado(s)",
                details={
                    "service_id": id,
                    "service_name": service.name,
                    "contact_count": contact_count
                }
            )

        # Proceder con la eliminación
        super().delete(id, user_id, soft)

    def get_by_name(self, name: str) -> ServiceResponse:
        """
        Busca un servicio por nombre.

        Args:
            name: Nombre del servicio

        Returns:
            Servicio encontrado

        Raises:
            NotFoundException: Si no se encuentra el servicio

        Example:
            service = service.get_by_name("Ventas")
        """
        logger.info(f"Servicio: buscando servicio por nombre='{name}'")

        service = self.service_repo.get_by_name(name)
        if not service:
            raise NotFoundException(
                f"No se encontró servicio con nombre '{name}'",
                details={"name": name}
            )

        return self.response_schema.model_validate(service)

    def search_by_name(self, name: str) -> list[ServiceResponse]:
        """
        Busca servicios por nombre (búsqueda parcial).

        Args:
            name: Texto a buscar

        Returns:
            Lista de servicios que coinciden

        Example:
            services = service.search_by_name("vent")
        """
        logger.info(f"Servicio: buscando servicios por nombre='{name}'")

        services = self.service_repo.search_by_name(name)
        return [self.response_schema.model_validate(s) for s in services]

    def get_active_services(self, skip: int = 0, limit: int = 100) -> list[ServiceResponse]:
        """
        Obtiene solo los servicios activos.

        Args:
            skip: Registros a saltar
            limit: Número máximo de registros

        Returns:
            Lista de servicios activos

        Example:
            active_services = service.get_active_services()
        """
        logger.info("Servicio: obteniendo servicios activos")

        services = self.service_repo.get_active_services(skip, limit)
        return [self.response_schema.model_validate(s) for s in services]

    def get_all_ordered(self, skip: int = 0, limit: int = 100) -> list[ServiceResponse]:
        """
        Obtiene todos los servicios ordenados alfabéticamente.

        Args:
            skip: Registros a saltar
            limit: Número máximo de registros

        Returns:
            Lista de servicios ordenados

        Example:
            services = service.get_all_ordered()
        """
        logger.info("Servicio: obteniendo servicios ordenados")

        services = self.service_repo.get_all_ordered(skip, limit)
        return [self.response_schema.model_validate(s) for s in services]

    def count_contacts(self, service_id: int) -> int:
        """
        Cuenta cuántos contactos están asociados a un servicio.

        Args:
            service_id: ID del servicio

        Returns:
            Número de contactos

        Example:
            count = service.count_contacts(service_id=1)
        """
        logger.info(f"Servicio: contando contactos del servicio id={service_id}")
        return self.service_repo.count_contacts(service_id)
