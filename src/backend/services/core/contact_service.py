"""
Servicio de lógica de negocio para Contact.

Implementa validaciones y reglas de negocio para contactos de empresas.
"""

from sqlalchemy.orm import Session

from src.backend.models.core.contacts import Contact
from src.backend.repositories.core.contact_repository import ContactRepository
from src.shared.schemas.core.contact import ContactCreate, ContactUpdate, ContactResponse
from src.backend.services.base import BaseService
from src.backend.exceptions.service import ValidationException
from src.backend.exceptions.repository import NotFoundException
from src.backend.utils.logger import logger


class ContactService(BaseService[Contact, ContactCreate, ContactUpdate, ContactResponse]):
    """
    Servicio para Contact con validaciones de negocio.

    Maneja la lógica de negocio para contactos, incluyendo:
    - Validación de unicidad de email
    - Validación de datos de contacto
    - Reglas de negocio específicas

    Example:
        service = ContactService(repository, session)
        contact = service.create(ContactCreate(...), user_id=1)
    """

    def __init__(
        self,
        repository: ContactRepository,
        session: Session,
    ):
        """
        Inicializa el servicio de Contact.

        Args:
            repository: Repositorio de Contact
            session: Sesión de SQLAlchemy
        """
        super().__init__(
            repository=repository,
            session=session,
            model=Contact,
            response_schema=ContactResponse,
        )
        # Cast para tener acceso a métodos específicos de ContactRepository
        self.contact_repo: ContactRepository = repository

    def validate_create(self, entity: Contact) -> None:
        """
        Valida reglas de negocio antes de crear un contacto.

        Args:
            entity: Contacto a validar

        Raises:
            ValidationException: Si la validación falla
        """
        logger.debug(
            f"Validando creación de contacto: {entity.first_name} {entity.last_name}"
        )

        # Validar que el email sea único (si se provee)
        if entity.email:
            existing = self.contact_repo.get_by_email(entity.email)
            if existing:
                raise ValidationException(
                    f"Ya existe un contacto con el email '{entity.email}'",
                    details={
                        "email": entity.email,
                        "existing_contact_id": existing.id,
                        "existing_contact_name": existing.full_name,
                    }
                )

        logger.debug("Validación de creación exitosa")

    def validate_update(self, entity: Contact) -> None:
        """
        Valida reglas de negocio antes de actualizar un contacto.

        Args:
            entity: Contacto a validar

        Raises:
            ValidationException: Si la validación falla
        """
        logger.debug(f"Validando actualización de contacto id={entity.id}")

        # Validar que el email sea único (excluyendo el mismo contacto)
        if entity.email:
            existing = self.contact_repo.get_by_email(entity.email)
            if existing and existing.id != entity.id:
                raise ValidationException(
                    f"Ya existe otro contacto con el email '{entity.email}'",
                    details={
                        "email": entity.email,
                        "current_contact_id": entity.id,
                        "existing_contact_id": existing.id,
                        "existing_contact_name": existing.full_name,
                    }
                )

        logger.debug("Validación de actualización exitosa")

    def get_by_company(self, company_id: int) -> list[ContactResponse]:
        """
        Obtiene todos los contactos de una empresa.

        Args:
            company_id: ID de la empresa

        Returns:
            Lista de contactos

        Example:
            contacts = service.get_by_company(company_id=1)
        """
        logger.info(f"Servicio: obteniendo contactos de empresa id={company_id}")

        contacts = self.contact_repo.get_by_company(company_id)
        return [self.response_schema.model_validate(c) for c in contacts]

    def get_active_contacts(self, company_id: int) -> list[ContactResponse]:
        """
        Obtiene solo los contactos activos de una empresa.

        Args:
            company_id: ID de la empresa

        Returns:
            Lista de contactos activos

        Example:
            active_contacts = service.get_active_contacts(company_id=1)
        """
        logger.info(f"Servicio: obteniendo contactos activos de empresa id={company_id}")

        contacts = self.contact_repo.get_active_contacts(company_id)
        return [self.response_schema.model_validate(c) for c in contacts]

    def get_by_email(self, email: str) -> ContactResponse:
        """
        Busca un contacto por email.

        Args:
            email: Email a buscar

        Returns:
            Contacto encontrado

        Raises:
            NotFoundException: Si no se encuentra el contacto

        Example:
            contact = service.get_by_email("jperez@example.com")
        """
        logger.info(f"Servicio: buscando contacto por email={email}")

        contact = self.contact_repo.get_by_email(email)
        if not contact:
            raise NotFoundException(
                f"No se encontró contacto con email '{email}'",
                details={"email": email}
            )

        return self.response_schema.model_validate(contact)

    def search_by_name(self, company_id: int, name: str) -> list[ContactResponse]:
        """
        Busca contactos por nombre.

        Args:
            company_id: ID de la empresa
            name: Texto a buscar

        Returns:
            Lista de contactos que coinciden

        Example:
            contacts = service.search_by_name(company_id=1, name="juan")
        """
        logger.info(
            f"Servicio: buscando contactos con nombre '{name}' "
            f"en empresa id={company_id}"
        )

        contacts = self.contact_repo.search_by_name(company_id, name)
        return [self.response_schema.model_validate(c) for c in contacts]

    def get_by_service(self, service_id: int) -> list[ContactResponse]:
        """
        Obtiene todos los contactos de un servicio/departamento.

        Args:
            service_id: ID del servicio

        Returns:
            Lista de contactos del servicio

        Example:
            sales_contacts = service.get_by_service(service_id=1)
        """
        logger.info(f"Servicio: obteniendo contactos del servicio id={service_id}")

        contacts = self.contact_repo.get_by_service(service_id)
        return [self.response_schema.model_validate(c) for c in contacts]

    def get_by_position(self, company_id: int, position: str) -> list[ContactResponse]:
        """
        Busca contactos por posición/cargo.

        Args:
            company_id: ID de la empresa
            position: Cargo a buscar

        Returns:
            Lista de contactos que coinciden

        Example:
            managers = service.get_by_position(company_id=1, position="gerente")
        """
        logger.info(
            f"Servicio: buscando contactos con posición '{position}' "
            f"en empresa id={company_id}"
        )

        contacts = self.contact_repo.get_by_position(company_id, position)
        return [self.response_schema.model_validate(c) for c in contacts]

    def search_by_phone(self, phone: str) -> list[ContactResponse]:
        """
        Busca contactos por teléfono.

        Args:
            phone: Teléfono a buscar

        Returns:
            Lista de contactos que coinciden

        Example:
            contacts = service.search_by_phone("+56912345678")
        """
        logger.info(f"Servicio: buscando contactos con teléfono {phone}")

        contacts = self.contact_repo.search_by_phone(phone)
        return [self.response_schema.model_validate(c) for c in contacts]
