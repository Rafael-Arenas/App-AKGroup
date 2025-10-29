"""
Repositorio para Contact.

Maneja el acceso a datos para contactos de empresas.
"""

from typing import Optional, List

from sqlalchemy.orm import Session

from src.backend.models.core.contacts import Contact
from src.backend.repositories.base import BaseRepository
from src.backend.utils.logger import logger


class ContactRepository(BaseRepository[Contact]):
    """
    Repositorio para Contact con métodos específicos.

    Además de los métodos CRUD base, proporciona métodos
    para búsquedas específicas de contactos.

    Example:
        repo = ContactRepository(session)
        contacts = repo.get_by_company(company_id=1)
        contact = repo.get_by_email("jperez@example.com")
    """

    def __init__(self, session: Session):
        """
        Inicializa el repositorio de Contact.

        Args:
            session: Sesión de SQLAlchemy
        """
        super().__init__(session, Contact)

    def get_by_company(self, company_id: int) -> List[Contact]:
        """
        Obtiene todos los contactos de una empresa.

        Args:
            company_id: ID de la empresa

        Returns:
            Lista de contactos

        Example:
            contacts = repo.get_by_company(company_id=1)
            for contact in contacts:
                print(f"{contact.full_name} - {contact.email}")
        """
        logger.debug(f"Obteniendo contactos de empresa id={company_id}")

        contacts = (
            self.session.query(Contact)
            .filter(Contact.company_id == company_id)
            .order_by(Contact.last_name, Contact.first_name)
            .all()
        )

        logger.debug(f"Encontrados {len(contacts)} contacto(s)")
        return contacts

    def get_active_contacts(self, company_id: int) -> List[Contact]:
        """
        Obtiene solo los contactos activos de una empresa.

        Args:
            company_id: ID de la empresa

        Returns:
            Lista de contactos activos

        Example:
            active_contacts = repo.get_active_contacts(company_id=1)
        """
        logger.debug(f"Obteniendo contactos activos de empresa id={company_id}")

        contacts = (
            self.session.query(Contact)
            .filter(
                Contact.company_id == company_id,
                Contact.is_active == True
            )
            .order_by(Contact.last_name, Contact.first_name)
            .all()
        )

        logger.debug(f"Encontrados {len(contacts)} contacto(s) activo(s)")
        return contacts

    def get_by_email(self, email: str) -> Optional[Contact]:
        """
        Busca un contacto por email.

        Args:
            email: Email a buscar

        Returns:
            Contact si existe, None en caso contrario

        Example:
            contact = repo.get_by_email("jperez@example.com")
            if contact:
                print(f"Contacto encontrado: {contact.full_name}")
        """
        logger.debug(f"Buscando contacto por email: {email}")

        contact = (
            self.session.query(Contact)
            .filter(Contact.email == email.lower())
            .first()
        )

        if contact:
            logger.debug(f"Contacto encontrado: {contact.full_name}")
        else:
            logger.debug(f"No se encontró contacto con email={email}")

        return contact

    def search_by_name(self, company_id: int, name: str) -> List[Contact]:
        """
        Busca contactos por nombre dentro de una empresa.

        Busca en first_name y last_name.

        Args:
            company_id: ID de la empresa
            name: Texto a buscar

        Returns:
            Lista de contactos que coinciden

        Example:
            contacts = repo.search_by_name(company_id=1, name="juan")
        """
        logger.debug(
            f"Buscando contactos con nombre '{name}' en empresa id={company_id}"
        )

        search_pattern = f"%{name}%"
        contacts = (
            self.session.query(Contact)
            .filter(
                Contact.company_id == company_id,
                (Contact.first_name.ilike(search_pattern)) |
                (Contact.last_name.ilike(search_pattern))
            )
            .order_by(Contact.last_name, Contact.first_name)
            .all()
        )

        logger.debug(f"Encontrados {len(contacts)} contacto(s)")
        return contacts

    def get_by_service(self, service_id: int) -> List[Contact]:
        """
        Obtiene todos los contactos de un servicio/departamento.

        Args:
            service_id: ID del servicio

        Returns:
            Lista de contactos del servicio

        Example:
            sales_contacts = repo.get_by_service(service_id=1)
        """
        logger.debug(f"Obteniendo contactos del servicio id={service_id}")

        contacts = (
            self.session.query(Contact)
            .filter(Contact.service_id == service_id)
            .order_by(Contact.last_name, Contact.first_name)
            .all()
        )

        logger.debug(f"Encontrados {len(contacts)} contacto(s)")
        return contacts

    def get_by_position(self, company_id: int, position: str) -> List[Contact]:
        """
        Busca contactos por posición/cargo dentro de una empresa.

        Args:
            company_id: ID de la empresa
            position: Cargo a buscar

        Returns:
            Lista de contactos que coinciden

        Example:
            managers = repo.get_by_position(company_id=1, position="gerente")
        """
        logger.debug(
            f"Buscando contactos con posición '{position}' "
            f"en empresa id={company_id}"
        )

        search_pattern = f"%{position}%"
        contacts = (
            self.session.query(Contact)
            .filter(
                Contact.company_id == company_id,
                Contact.position.ilike(search_pattern)
            )
            .order_by(Contact.last_name, Contact.first_name)
            .all()
        )

        logger.debug(f"Encontrados {len(contacts)} contacto(s)")
        return contacts

    def search_by_phone(self, phone: str) -> List[Contact]:
        """
        Busca contactos por número de teléfono.

        Args:
            phone: Número de teléfono a buscar

        Returns:
            Lista de contactos que coinciden

        Example:
            contacts = repo.search_by_phone("+56912345678")
        """
        logger.debug(f"Buscando contactos con teléfono: {phone}")

        # Buscar en phone y mobile
        contacts = (
            self.session.query(Contact)
            .filter(
                (Contact.phone == phone) |
                (Contact.mobile == phone)
            )
            .all()
        )

        logger.debug(f"Encontrados {len(contacts)} contacto(s)")
        return contacts

    def get_primary_contacts(self, company_id: int) -> List[Contact]:
        """
        Obtiene los contactos principales de una empresa.

        Retorna contactos activos, ordenados por último nombre.

        Args:
            company_id: ID de la empresa

        Returns:
            Lista de contactos principales (activos)

        Example:
            primary = repo.get_primary_contacts(company_id=1)
        """
        return self.get_active_contacts(company_id)
