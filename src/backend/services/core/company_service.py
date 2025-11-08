"""
Servicio de lógica de negocio para Company.

Implementa validaciones y reglas de negocio para empresas.
"""

from sqlalchemy.orm import Session

from src.backend.models.core.companies import Company
from src.backend.repositories.core.company_repository import CompanyRepository
from src.shared.schemas.core.company import CompanyCreate, CompanyUpdate, CompanyResponse
from src.backend.services.base import BaseService
from src.backend.exceptions.service import ValidationException
from src.backend.utils.logger import logger


class CompanyService(BaseService[Company, CompanyCreate, CompanyUpdate, CompanyResponse]):
    """
    Servicio para Company con validaciones de negocio.

    Maneja la lógica de negocio para empresas, incluyendo:
    - Validación de trigram único
    - Validación de formato de datos
    - Reglas de negocio específicas

    Example:
        service = CompanyService(repository, session, Company, CompanyResponse)
        company = service.create(CompanyCreate(...), user_id=1)
    """

    def __init__(
        self,
        repository: CompanyRepository,
        session: Session,
    ):
        """
        Inicializa el servicio de Company.

        Args:
            repository: Repositorio de Company
            session: Sesión de SQLAlchemy
        """
        super().__init__(
            repository=repository,
            session=session,
            model=Company,
            response_schema=CompanyResponse,
        )
        # Cast para tener acceso a métodos específicos de CompanyRepository
        self.company_repo: CompanyRepository = repository

    def validate_create(self, entity: Company) -> None:
        """
        Valida reglas de negocio antes de crear una empresa.

        Args:
            entity: Empresa a validar

        Raises:
            ValidationException: Si el trigram ya existe
        """
        logger.debug(f"Validando creación de empresa: trigram={entity.trigram}")

        # Validar que el trigram sea único
        existing = self.company_repo.get_by_trigram(entity.trigram)
        if existing:
            raise ValidationException(
                f"Ya existe una empresa con el trigram '{entity.trigram}'",
                details={
                    "trigram": entity.trigram,
                    "existing_company_id": existing.id,
                    "existing_company_name": existing.name,
                }
            )

        logger.debug("Validación de creación exitosa")

    def validate_update(self, entity: Company) -> None:
        """
        Valida reglas de negocio antes de actualizar una empresa.

        Args:
            entity: Empresa a validar

        Raises:
            ValidationException: Si el trigram ya existe en otra empresa
        """
        logger.debug(f"Validando actualización de empresa id={entity.id}")

        # Validar que el trigram sea único (excluyendo la misma empresa)
        existing = self.company_repo.get_by_trigram(entity.trigram)
        if existing and existing.id != entity.id:
            raise ValidationException(
                f"Ya existe otra empresa con el trigram '{entity.trigram}'",
                details={
                    "trigram": entity.trigram,
                    "current_company_id": entity.id,
                    "existing_company_id": existing.id,
                    "existing_company_name": existing.name,
                }
            )

        logger.debug("Validación de actualización exitosa")

    def get_by_trigram(self, trigram: str) -> CompanyResponse:
        """
        Obtiene una empresa por su trigram.

        Args:
            trigram: Trigram de la empresa

        Returns:
            Empresa encontrada

        Raises:
            NotFoundException: Si no se encuentra la empresa

        Example:
            company = service.get_by_trigram("AKG")
        """
        logger.info(f"Servicio: buscando empresa por trigram={trigram}")

        company = self.company_repo.get_by_trigram(trigram)
        if not company:
            from src.backend.exceptions.repository import NotFoundException
            raise NotFoundException(
                f"No se encontró empresa con trigram '{trigram}'",
                details={"trigram": trigram}
            )

        return self.response_schema.model_validate(company)

    def search_by_name(self, name: str) -> list[CompanyResponse]:
        """
        Busca empresas por nombre.

        Args:
            name: Texto a buscar en el nombre

        Returns:
            Lista de empresas encontradas

        Example:
            companies = service.search_by_name("test")
        """
        logger.info(f"Servicio: buscando empresas por nombre='{name}'")

        companies = self.company_repo.search_by_name(name)
        return [self.response_schema.model_validate(c) for c in companies]

    def get_active_companies(self, skip: int = 0, limit: int = 100) -> list[CompanyResponse]:
        """
        Obtiene solo las empresas activas.

        Args:
            skip: Registros a saltar
            limit: Número máximo de registros

        Returns:
            Lista de empresas activas

        Example:
            active_companies = service.get_active_companies()
        """
        logger.info("Servicio: obteniendo empresas activas")

        companies = self.company_repo.get_active_companies(skip, limit)
        return [self.response_schema.model_validate(c) for c in companies]

    def get_by_type(
        self,
        company_type_id: int,
        skip: int = 0,
        limit: int = 100,
        is_active: bool | None = None
    ) -> list[CompanyResponse]:
        """
        Obtiene empresas filtradas por tipo.

        Args:
            company_type_id: ID del tipo de empresa (1=CLIENT, 2=SUPPLIER)
            skip: Registros a saltar
            limit: Número máximo de registros
            is_active: Filtrar por estado activo/inactivo (None = todos)

        Returns:
            Lista de empresas del tipo especificado

        Example:
            clients = service.get_by_type(company_type_id=1)
            active_suppliers = service.get_by_type(company_type_id=2, is_active=True)
        """
        logger.info(
            f"Servicio: obteniendo empresas por tipo={company_type_id}, "
            f"is_active={is_active}"
        )

        companies = self.company_repo.get_by_type(
            company_type_id=company_type_id,
            skip=skip,
            limit=limit,
            is_active=is_active
        )
        return [self.response_schema.model_validate(c) for c in companies]

    def get_with_branches(self, company_id: int) -> CompanyResponse:
        """
        Obtiene una empresa con sus sucursales.

        Args:
            company_id: ID de la empresa

        Returns:
            Empresa con sucursales cargadas

        Raises:
            NotFoundException: Si no se encuentra la empresa

        Example:
            company = service.get_with_branches(123)
            for branch in company.branches:
                print(branch.name)
        """
        logger.info(f"Servicio: obteniendo empresa id={company_id} con sucursales")

        company = self.company_repo.get_with_branches(company_id)
        if not company:
            from src.backend.exceptions.repository import NotFoundException
            raise NotFoundException(
                f"No se encontró empresa con id={company_id}",
                details={"company_id": company_id}
            )

        return self.response_schema.model_validate(company)
