"""
Servicio de lógica de negocio para Staff (usuarios del sistema).

Implementa validaciones y reglas de negocio para usuarios/staff.
"""

from sqlalchemy.orm import Session

from src.backend.models.core.staff import Staff
from src.backend.repositories.core.staff_repository import StaffRepository
from src.shared.schemas.core.staff import StaffCreate, StaffUpdate, StaffResponse
from src.backend.services.base import BaseService
from src.backend.exceptions.service import ValidationException
from src.backend.exceptions.repository import NotFoundException
from src.backend.utils.logger import logger


class StaffService(BaseService[Staff, StaffCreate, StaffUpdate, StaffResponse]):
    """
    Servicio para Staff con validaciones de negocio.

    Maneja la lógica de negocio para usuarios del sistema, incluyendo:
    - Validación de unicidad de username, email y trigram
    - Validación de formato de datos
    - Reglas de negocio específicas

    Example:
        service = StaffService(repository, session)
        staff = service.create(StaffCreate(...), user_id=1)
    """

    def __init__(
        self,
        repository: StaffRepository,
        session: Session,
    ):
        """
        Inicializa el servicio de Staff.

        Args:
            repository: Repositorio de Staff
            session: Sesión de SQLAlchemy
        """
        super().__init__(
            repository=repository,
            session=session,
            model=Staff,
            response_schema=StaffResponse,
        )
        # Cast para tener acceso a métodos específicos de StaffRepository
        self.staff_repo: StaffRepository = repository

    def validate_create(self, entity: Staff) -> None:
        """
        Valida reglas de negocio antes de crear un usuario.

        Args:
            entity: Usuario a validar

        Raises:
            ValidationException: Si la validación falla
        """
        logger.debug(f"Validando creación de staff: username={entity.username}")

        # Validar que el username sea único
        existing = self.staff_repo.get_by_username(entity.username)
        if existing:
            raise ValidationException(
                f"Ya existe un usuario con el username '{entity.username}'",
                details={
                    "username": entity.username,
                    "existing_staff_id": existing.id,
                }
            )

        # Validar que el email sea único
        existing = self.staff_repo.get_by_email(entity.email)
        if existing:
            raise ValidationException(
                f"Ya existe un usuario con el email '{entity.email}'",
                details={
                    "email": entity.email,
                    "existing_staff_id": existing.id,
                }
            )

        # Validar que el trigram sea único (si se provee)
        if entity.trigram:
            existing = self.staff_repo.get_by_trigram(entity.trigram)
            if existing:
                raise ValidationException(
                    f"Ya existe un usuario con el trigram '{entity.trigram}'",
                    details={
                        "trigram": entity.trigram,
                        "existing_staff_id": existing.id,
                    }
                )

        logger.debug("Validación de creación exitosa")

    def validate_update(self, entity: Staff) -> None:
        """
        Valida reglas de negocio antes de actualizar un usuario.

        Args:
            entity: Usuario a validar

        Raises:
            ValidationException: Si la validación falla
        """
        logger.debug(f"Validando actualización de staff id={entity.id}")

        # Validar que el username sea único (excluyendo el mismo usuario)
        existing = self.staff_repo.get_by_username(entity.username)
        if existing and existing.id != entity.id:
            raise ValidationException(
                f"Ya existe otro usuario con el username '{entity.username}'",
                details={
                    "username": entity.username,
                    "current_staff_id": entity.id,
                    "existing_staff_id": existing.id,
                }
            )

        # Validar que el email sea único
        existing = self.staff_repo.get_by_email(entity.email)
        if existing and existing.id != entity.id:
            raise ValidationException(
                f"Ya existe otro usuario con el email '{entity.email}'",
                details={
                    "email": entity.email,
                    "current_staff_id": entity.id,
                    "existing_staff_id": existing.id,
                }
            )

        # Validar que el trigram sea único (si se provee)
        if entity.trigram:
            existing = self.staff_repo.get_by_trigram(entity.trigram)
            if existing and existing.id != entity.id:
                raise ValidationException(
                    f"Ya existe otro usuario con el trigram '{entity.trigram}'",
                    details={
                        "trigram": entity.trigram,
                        "current_staff_id": entity.id,
                        "existing_staff_id": existing.id,
                    }
                )

        logger.debug("Validación de actualización exitosa")

    def get_by_username(self, username: str) -> StaffResponse:
        """
        Busca un usuario por username.

        Args:
            username: Username a buscar

        Returns:
            Usuario encontrado

        Raises:
            NotFoundException: Si no se encuentra el usuario

        Example:
            staff = service.get_by_username("jdoe")
        """
        logger.info(f"Servicio: buscando staff por username='{username}'")

        staff = self.staff_repo.get_by_username(username)
        if not staff:
            raise NotFoundException(
                f"No se encontró usuario con username '{username}'",
                details={"username": username}
            )

        return self.response_schema.model_validate(staff)

    def get_by_email(self, email: str) -> StaffResponse:
        """
        Busca un usuario por email.

        Args:
            email: Email a buscar

        Returns:
            Usuario encontrado

        Raises:
            NotFoundException: Si no se encuentra el usuario

        Example:
            staff = service.get_by_email("john.doe@akgroup.com")
        """
        logger.info(f"Servicio: buscando staff por email='{email}'")

        staff = self.staff_repo.get_by_email(email)
        if not staff:
            raise NotFoundException(
                f"No se encontró usuario con email '{email}'",
                details={"email": email}
            )

        return self.response_schema.model_validate(staff)

    def get_by_trigram(self, trigram: str) -> StaffResponse:
        """
        Busca un usuario por trigram.

        Args:
            trigram: Trigram a buscar

        Returns:
            Usuario encontrado

        Raises:
            NotFoundException: Si no se encuentra el usuario

        Example:
            staff = service.get_by_trigram("JDO")
        """
        logger.info(f"Servicio: buscando staff por trigram='{trigram}'")

        staff = self.staff_repo.get_by_trigram(trigram)
        if not staff:
            raise NotFoundException(
                f"No se encontró usuario con trigram '{trigram}'",
                details={"trigram": trigram}
            )

        return self.response_schema.model_validate(staff)

    def get_active_staff(self, skip: int = 0, limit: int = 100) -> list[StaffResponse]:
        """
        Obtiene solo los usuarios activos.

        Args:
            skip: Registros a saltar
            limit: Número máximo de registros

        Returns:
            Lista de usuarios activos

        Example:
            active_staff = service.get_active_staff()
        """
        logger.info("Servicio: obteniendo staff activo")

        staff_list = self.staff_repo.get_active_staff(skip, limit)
        return [self.response_schema.model_validate(s) for s in staff_list]

    def get_admins(self, skip: int = 0, limit: int = 100) -> list[StaffResponse]:
        """
        Obtiene solo los administradores.

        Args:
            skip: Registros a saltar
            limit: Número máximo de registros

        Returns:
            Lista de administradores

        Example:
            admins = service.get_admins()
        """
        logger.info("Servicio: obteniendo administradores")

        admins = self.staff_repo.get_admins(skip, limit)
        return [self.response_schema.model_validate(s) for s in admins]

    def get_active_admins(self) -> list[StaffResponse]:
        """
        Obtiene solo los administradores activos.

        Returns:
            Lista de administradores activos

        Example:
            active_admins = service.get_active_admins()
        """
        logger.info("Servicio: obteniendo administradores activos")

        admins = self.staff_repo.get_active_admins()
        return [self.response_schema.model_validate(s) for s in admins]

    def search_by_name(self, name: str) -> list[StaffResponse]:
        """
        Busca usuarios por nombre.

        Args:
            name: Texto a buscar

        Returns:
            Lista de usuarios que coinciden

        Example:
            staff_list = service.search_by_name("john")
        """
        logger.info(f"Servicio: buscando staff por nombre='{name}'")

        staff_list = self.staff_repo.search_by_name(name)
        return [self.response_schema.model_validate(s) for s in staff_list]

    def get_by_position(self, position: str) -> list[StaffResponse]:
        """
        Busca usuarios por posición/cargo.

        Args:
            position: Cargo a buscar

        Returns:
            Lista de usuarios que coinciden

        Example:
            managers = service.get_by_position("gerente")
        """
        logger.info(f"Servicio: buscando staff por posición='{position}'")

        staff_list = self.staff_repo.get_by_position(position)
        return [self.response_schema.model_validate(s) for s in staff_list]
