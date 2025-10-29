"""
Servicio de lógica de negocio para Address.

Implementa validaciones y reglas de negocio para direcciones de empresas.
"""

from sqlalchemy.orm import Session

from src.backend.models.core.addresses import Address, AddressType
from src.backend.repositories.core.address_repository import AddressRepository
from src.shared.schemas.core.address import AddressCreate, AddressUpdate, AddressResponse
from src.backend.services.base import BaseService
from src.backend.exceptions.service import ValidationException, BusinessRuleException
from src.backend.exceptions.repository import NotFoundException
from src.backend.utils.logger import logger


class AddressService(BaseService[Address, AddressCreate, AddressUpdate, AddressResponse]):
    """
    Servicio para Address con validaciones de negocio.

    Maneja la lógica de negocio para direcciones, incluyendo:
    - Validación de unicidad de dirección por defecto
    - Validación de existencia de empresa
    - Reglas de negocio específicas

    Example:
        service = AddressService(repository, session)
        address = service.create(AddressCreate(...), user_id=1)
    """

    def __init__(
        self,
        repository: AddressRepository,
        session: Session,
    ):
        """
        Inicializa el servicio de Address.

        Args:
            repository: Repositorio de Address
            session: Sesión de SQLAlchemy
        """
        super().__init__(
            repository=repository,
            session=session,
            model=Address,
            response_schema=AddressResponse,
        )
        # Cast para tener acceso a métodos específicos de AddressRepository
        self.address_repo: AddressRepository = repository

    def validate_create(self, entity: Address) -> None:
        """
        Valida reglas de negocio antes de crear una dirección.

        Args:
            entity: Dirección a validar

        Raises:
            ValidationException: Si la validación falla
        """
        logger.debug(
            f"Validando creación de dirección para empresa id={entity.company_id}"
        )

        # Si se marca como default, verificar que no haya otra default
        if entity.is_default:
            existing_default = self.address_repo.get_default_address(entity.company_id)
            if existing_default:
                # Remover el flag default de la existente
                logger.debug(
                    f"Removiendo flag default de dirección id={existing_default.id}"
                )
                existing_default.is_default = False

        logger.debug("Validación de creación exitosa")

    def validate_update(self, entity: Address) -> None:
        """
        Valida reglas de negocio antes de actualizar una dirección.

        Args:
            entity: Dirección a validar

        Raises:
            ValidationException: Si la validación falla
        """
        logger.debug(f"Validando actualización de dirección id={entity.id}")

        # Si se marca como default, remover flag de otras direcciones
        if entity.is_default:
            existing_default = self.address_repo.get_default_address(entity.company_id)
            if existing_default and existing_default.id != entity.id:
                logger.debug(
                    f"Removiendo flag default de dirección id={existing_default.id}"
                )
                existing_default.is_default = False

        logger.debug("Validación de actualización exitosa")

    def get_by_company(self, company_id: int) -> list[AddressResponse]:
        """
        Obtiene todas las direcciones de una empresa.

        Args:
            company_id: ID de la empresa

        Returns:
            Lista de direcciones

        Example:
            addresses = service.get_by_company(company_id=1)
        """
        logger.info(f"Servicio: obteniendo direcciones de empresa id={company_id}")

        addresses = self.address_repo.get_by_company(company_id)
        return [self.response_schema.model_validate(a) for a in addresses]

    def get_default_address(self, company_id: int) -> AddressResponse:
        """
        Obtiene la dirección por defecto de una empresa.

        Args:
            company_id: ID de la empresa

        Returns:
            Dirección por defecto

        Raises:
            NotFoundException: Si no se encuentra dirección por defecto

        Example:
            default_addr = service.get_default_address(company_id=1)
        """
        logger.info(
            f"Servicio: obteniendo dirección por defecto de empresa id={company_id}"
        )

        address = self.address_repo.get_default_address(company_id)
        if not address:
            raise NotFoundException(
                f"No se encontró dirección por defecto para empresa id={company_id}",
                details={"company_id": company_id}
            )

        return self.response_schema.model_validate(address)

    def get_by_type(
        self,
        company_id: int,
        address_type: AddressType
    ) -> list[AddressResponse]:
        """
        Obtiene direcciones de una empresa por tipo.

        Args:
            company_id: ID de la empresa
            address_type: Tipo de dirección

        Returns:
            Lista de direcciones del tipo especificado

        Example:
            delivery_addrs = service.get_by_type(
                company_id=1,
                address_type=AddressType.DELIVERY
            )
        """
        logger.info(
            f"Servicio: obteniendo direcciones tipo={address_type.value} "
            f"de empresa id={company_id}"
        )

        addresses = self.address_repo.get_by_type(company_id, address_type)
        return [self.response_schema.model_validate(a) for a in addresses]

    def get_delivery_addresses(self, company_id: int) -> list[AddressResponse]:
        """
        Obtiene direcciones de entrega de una empresa.

        Args:
            company_id: ID de la empresa

        Returns:
            Lista de direcciones de entrega

        Example:
            delivery_addrs = service.get_delivery_addresses(company_id=1)
        """
        logger.info(f"Servicio: obteniendo direcciones de entrega de empresa id={company_id}")

        addresses = self.address_repo.get_delivery_addresses(company_id)
        return [self.response_schema.model_validate(a) for a in addresses]

    def get_billing_addresses(self, company_id: int) -> list[AddressResponse]:
        """
        Obtiene direcciones de facturación de una empresa.

        Args:
            company_id: ID de la empresa

        Returns:
            Lista de direcciones de facturación

        Example:
            billing_addrs = service.get_billing_addresses(company_id=1)
        """
        logger.info(
            f"Servicio: obteniendo direcciones de facturación de empresa id={company_id}"
        )

        addresses = self.address_repo.get_billing_addresses(company_id)
        return [self.response_schema.model_validate(a) for a in addresses]

    def set_default_address(self, address_id: int, company_id: int, user_id: int) -> AddressResponse:
        """
        Establece una dirección como por defecto.

        Args:
            address_id: ID de la dirección
            company_id: ID de la empresa
            user_id: ID del usuario que realiza la operación

        Returns:
            Dirección actualizada

        Raises:
            NotFoundException: Si la dirección no existe
            BusinessRuleException: Si la dirección no pertenece a la empresa

        Example:
            address = service.set_default_address(
                address_id=5,
                company_id=1,
                user_id=1
            )
        """
        logger.info(
            f"Servicio: estableciendo dirección id={address_id} como default "
            f"para empresa id={company_id}"
        )

        try:
            self.session.info["user_id"] = user_id

            # Verificar que la dirección existe
            address = self.address_repo.get_by_id(address_id)
            if not address:
                raise NotFoundException(
                    f"Dirección no encontrada",
                    details={"address_id": address_id}
                )

            # Verificar que pertenece a la empresa
            if address.company_id != company_id:
                raise BusinessRuleException(
                    "La dirección no pertenece a la empresa especificada",
                    details={
                        "address_id": address_id,
                        "address_company_id": address.company_id,
                        "requested_company_id": company_id
                    }
                )

            # Establecer como default
            self.address_repo.set_default_address(address_id, company_id)

            logger.success(f"Dirección id={address_id} establecida como default")

            # Retornar la dirección actualizada
            updated_address = self.address_repo.get_by_id(address_id)
            return self.response_schema.model_validate(updated_address)

        except (NotFoundException, BusinessRuleException):
            raise
        except Exception as e:
            logger.error(f"Error al establecer dirección default: {str(e)}")
            raise

    def search_by_city(self, company_id: int, city: str) -> list[AddressResponse]:
        """
        Busca direcciones por ciudad.

        Args:
            company_id: ID de la empresa
            city: Ciudad a buscar

        Returns:
            Lista de direcciones que coinciden

        Example:
            addresses = service.search_by_city(company_id=1, city="Santiago")
        """
        logger.info(
            f"Servicio: buscando direcciones en ciudad '{city}' "
            f"de empresa id={company_id}"
        )

        addresses = self.address_repo.search_by_city(company_id, city)
        return [self.response_schema.model_validate(a) for a in addresses]
