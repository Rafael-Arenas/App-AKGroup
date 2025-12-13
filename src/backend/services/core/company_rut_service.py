"""
Servicio de lógica de negocio para CompanyRut.

Implementa validaciones y reglas de negocio para RUTs de empresas.
"""

from sqlalchemy.orm import Session

from src.backend.models.core.companies import CompanyRut
from src.backend.repositories.core.company_rut_repository import CompanyRutRepository
from src.shared.schemas.core.company_rut import CompanyRutCreate, CompanyRutUpdate, CompanyRutResponse
from src.backend.services.base import BaseService
from src.backend.exceptions.service import ValidationException
from src.backend.exceptions.repository import NotFoundException
from src.backend.utils.logger import logger


class CompanyRutService(BaseService[CompanyRut, CompanyRutCreate, CompanyRutUpdate, CompanyRutResponse]):
    """
    Servicio para CompanyRut con validaciones de negocio.

    Maneja la lógica de negocio para RUTs, incluyendo:
    - Validación de unicidad de RUT
    - Gestión de RUT principal
    - Validación de datos de RUT

    Example:
        service = CompanyRutService(repository, session)
        rut = service.create(CompanyRutCreate(...), user_id=1)
    """

    def __init__(
        self,
        repository: CompanyRutRepository,
        session: Session,
    ):
        """
        Inicializa el servicio de CompanyRut.

        Args:
            repository: Repositorio de CompanyRut
            session: Sesión de SQLAlchemy
        """
        super().__init__(
            repository=repository,
            session=session,
            model=CompanyRut,
            response_schema=CompanyRutResponse,
        )
        # Cast para tener acceso a métodos específicos de CompanyRutRepository
        self.rut_repo: CompanyRutRepository = repository

    def validate_create(self, entity: CompanyRut) -> None:
        """
        Valida reglas de negocio antes de crear un RUT.

        Args:
            entity: RUT a validar

        Raises:
            ValidationException: Si la validación falla
        """
        logger.debug(f"Validando creación de RUT: {entity.rut}")

        # Validar que el RUT sea único
        existing = self.rut_repo.get_by_rut(entity.rut)
        if existing:
            raise ValidationException(
                f"Ya existe un RUT '{entity.rut}' para la empresa '{existing.company.name}'",
                details={
                    "rut": entity.rut,
                    "existing_company_id": existing.company_id,
                    "existing_company_name": existing.company.name,
                }
            )

        # Si es el primer RUT de la empresa, debe ser principal
        company_ruts = self.rut_repo.get_by_company(entity.company_id)
        if not company_ruts and not entity.is_main:
            logger.info("Es el primer RUT de la empresa, estableciendo como principal")
            entity.is_main = True

        logger.debug("Validación de creación exitosa")

    def validate_update(self, entity: CompanyRut) -> None:
        """
        Valida reglas de negocio antes de actualizar un RUT.

        Args:
            entity: RUT a validar

        Raises:
            ValidationException: Si la validación falla
        """
        logger.debug(f"Validando actualización de RUT id={entity.id}")

        # Validar que el RUT sea único (excluyendo el mismo RUT)
        if entity.rut:
            existing = self.rut_repo.get_by_rut(entity.rut)
            if existing and existing.id != entity.id:
                raise ValidationException(
                    f"Ya existe el RUT '{entity.rut}' para la empresa '{existing.company.name}'",
                    details={
                        "rut": entity.rut,
                        "current_rut_id": entity.id,
                        "existing_company_id": existing.company_id,
                        "existing_company_name": existing.company.name,
                    }
                )

        logger.debug("Validación de actualización exitosa")

    def get_by_company(self, company_id: int) -> list[CompanyRutResponse]:
        """
        Obtiene todos los RUTs de una empresa.

        Args:
            company_id: ID de la empresa

        Returns:
            Lista de RUTs

        Example:
            ruts = service.get_by_company(company_id=1)
        """
        logger.info(f"Servicio: obteniendo RUTs de empresa id={company_id}")

        ruts = self.rut_repo.get_by_company(company_id)
        return [self.response_schema.model_validate(r) for r in ruts]

    def get_main_rut(self, company_id: int) -> CompanyRutResponse:
        """
        Obtiene el RUT principal de una empresa.

        Args:
            company_id: ID de la empresa

        Returns:
            RUT principal

        Raises:
            NotFoundException: Si no se encuentra RUT principal

        Example:
            main_rut = service.get_main_rut(company_id=1)
        """
        logger.info(f"Servicio: obteniendo RUT principal de empresa id={company_id}")

        rut = self.rut_repo.get_main_rut(company_id)
        if not rut:
            raise NotFoundException(
                f"No se encontró RUT principal para la empresa id={company_id}",
                details={"company_id": company_id}
            )

        return self.response_schema.model_validate(rut)

    def get_by_rut(self, rut: str) -> CompanyRutResponse:
        """
        Busca un RUT por su valor.

        Args:
            rut: RUT a buscar

        Returns:
            RUT encontrado

        Raises:
            NotFoundException: Si no se encuentra el RUT

        Example:
            rut = service.get_by_rut("76123456-7")
        """
        logger.info(f"Servicio: buscando RUT={rut}")

        rut_entity = self.rut_repo.get_by_rut(rut)
        if not rut_entity:
            raise NotFoundException(
                f"No se encontró RUT '{rut}'",
                details={"rut": rut}
            )

        return self.response_schema.model_validate(rut_entity)

    def set_as_main(self, rut_id: int, user_id: int) -> CompanyRutResponse:
        """
        Establece un RUT como principal.

        Args:
            rut_id: ID del RUT a establecer como principal
            user_id: ID del usuario que realiza la acción

        Returns:
            RUT actualizado

        Raises:
            NotFoundException: Si no se encuentra el RUT

        Example:
            main_rut = service.set_as_main(rut_id=5, user_id=1)
        """
        logger.info(f"Servicio: estableciendo RUT id={rut_id} como principal")

        try:
            # Usar transacción para asegurar consistencia
            with self.session.begin_nested():
                self.rut_repo.set_as_main(rut_id)
                
                # Obtener el RUT actualizado
                rut = self.rut_repo.get_by_id(rut_id)
                if not rut:
                    raise NotFoundException(
                        f"No se encontró RUT con id={rut_id}",
                        details={"rut_id": rut_id}
                    )

                # Actualizar campos de auditoría
                rut.updated_by = user_id
                
                logger.success(f"RUT {rut.rut} establecido como principal")
                return self.response_schema.model_validate(rut)

        except Exception as e:
            logger.error(f"Error al establecer RUT como principal: {e}")
            raise

    def get_secondary_ruts(self, company_id: int) -> list[CompanyRutResponse]:
        """
        Obtiene los RUTs secundarios de una empresa.

        Args:
            company_id: ID de la empresa

        Returns:
            Lista de RUTs secundarios

        Example:
            secondary = service.get_secondary_ruts(company_id=1)
        """
        logger.info(f"Servicio: obteniendo RUTs secundarios de empresa id={company_id}")

        ruts = self.rut_repo.get_secondary_ruts(company_id)
        return [self.response_schema.model_validate(r) for r in ruts]
