"""
Repositorio para Address.

Maneja el acceso a datos para direcciones de empresas.
"""

from collections.abc import Sequence

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from src.backend.models.core.addresses import Address, AddressType
from src.backend.repositories.base import BaseRepository
from src.backend.utils.logger import logger


class AddressRepository(BaseRepository[Address]):
    """
    Repositorio para Address con métodos específicos.

    Además de los métodos CRUD base, proporciona métodos
    para búsquedas específicas de direcciones.

    Example:
        repo = AddressRepository(session)
        addresses = repo.get_by_company(company_id=1)
        default_addr = repo.get_default_address(company_id=1)
    """

    def __init__(self, session: Session):
        """
        Inicializa el repositorio de Address.

        Args:
            session: Sesión de SQLAlchemy
        """
        super().__init__(session, Address)

    def get_by_company(self, company_id: int) -> Sequence[Address]:
        """
        Obtiene todas las direcciones de una empresa.

        Args:
            company_id: ID de la empresa

        Returns:
            Lista de direcciones

        Example:
            addresses = repo.get_by_company(company_id=1)
            for addr in addresses:
                print(f"{addr.address_type.value}: {addr.address}")
        """
        logger.debug(f"Obteniendo direcciones de empresa id={company_id}")

        stmt = (
            select(Address)
            .filter(Address.company_id == company_id)
            .order_by(Address.is_default.desc(), Address.created_at.desc())
        )
        addresses = self.session.execute(stmt).scalars().all()

        logger.debug(f"Encontradas {len(addresses)} dirección(es)")
        return addresses

    def get_default_address(self, company_id: int) -> Address | None:
        """
        Obtiene la dirección por defecto de una empresa.

        Args:
            company_id: ID de la empresa

        Returns:
            Address por defecto si existe, None en caso contrario

        Example:
            default_addr = repo.get_default_address(company_id=1)
            if default_addr:
                print(f"Default: {default_addr.address}")
        """
        logger.debug(f"Obteniendo dirección por defecto de empresa id={company_id}")

        stmt = select(Address).filter(
            Address.company_id == company_id,
            Address.is_default.is_(True)
        )
        address = self.session.execute(stmt).scalar_one_or_none()

        if address:
            logger.debug(f"Dirección por defecto encontrada: id={address.id}")
        else:
            logger.debug("No se encontró dirección por defecto")

        return address

    def get_by_type(
        self,
        company_id: int,
        address_type: AddressType
    ) -> Sequence[Address]:
        """
        Obtiene direcciones de una empresa por tipo.

        Args:
            company_id: ID de la empresa
            address_type: Tipo de dirección (delivery, billing, etc.)

        Returns:
            Lista de direcciones del tipo especificado

        Example:
            delivery_addrs = repo.get_by_type(
                company_id=1,
                address_type=AddressType.DELIVERY
            )
        """
        logger.debug(
            f"Obteniendo direcciones tipo={address_type.value} "
            f"de empresa id={company_id}"
        )

        stmt = (
            select(Address)
            .filter(
                Address.company_id == company_id,
                Address.address_type == address_type
            )
            .order_by(Address.is_default.desc(), Address.created_at.desc())
        )
        addresses = self.session.execute(stmt).scalars().all()

        logger.debug(f"Encontradas {len(addresses)} dirección(es) tipo {address_type.value}")
        return addresses

    def get_delivery_addresses(self, company_id: int) -> Sequence[Address]:
        """
        Obtiene solo las direcciones de entrega de una empresa.

        Args:
            company_id: ID de la empresa

        Returns:
            Lista de direcciones de entrega

        Example:
            delivery_addrs = repo.get_delivery_addresses(company_id=1)
        """
        return self.get_by_type(company_id, AddressType.DELIVERY)

    def get_billing_addresses(self, company_id: int) -> Sequence[Address]:
        """
        Obtiene solo las direcciones de facturación de una empresa.

        Args:
            company_id: ID de la empresa

        Returns:
            Lista de direcciones de facturación

        Example:
            billing_addrs = repo.get_billing_addresses(company_id=1)
        """
        return self.get_by_type(company_id, AddressType.BILLING)

    def search_by_city(self, company_id: int, city: str) -> Sequence[Address]:
        """
        Busca direcciones por ciudad dentro de una empresa.

        Args:
            company_id: ID de la empresa
            city: Ciudad a buscar

        Returns:
            Lista de direcciones que coinciden

        Example:
            santiago_addrs = repo.search_by_city(company_id=1, city="Santiago")
        """
        logger.debug(f"Buscando direcciones en ciudad '{city}' de empresa id={company_id}")

        search_pattern = f"%{city}%"
        stmt = (
            select(Address)
            .filter(
                Address.company_id == company_id,
                Address.city.ilike(search_pattern)
            )
            .order_by(Address.is_default.desc())
        )
        addresses = self.session.execute(stmt).scalars().all()

        logger.debug(f"Encontradas {len(addresses)} dirección(es) en '{city}'")
        return addresses

    def set_default_address(self, address_id: int, company_id: int) -> None:
        """
        Establece una dirección como por defecto para una empresa.

        Primero remueve el flag is_default de todas las direcciones de la empresa,
        luego lo establece en la dirección especificada.

        Args:
            address_id: ID de la dirección a marcar como default
            company_id: ID de la empresa

        Note:
            Esta operación hace flush() pero NO commit().

        Example:
            repo.set_default_address(address_id=5, company_id=1)
            session.commit()
        """
        logger.debug(
            f"Estableciendo dirección id={address_id} como default "
            f"para empresa id={company_id}"
        )

        # Remover is_default de todas las direcciones de la empresa
        stmt = update(Address).filter(Address.company_id == company_id).values(is_default=False)
        self.session.execute(stmt)

        # Establecer la nueva dirección por defecto
        address = self.get_by_id(address_id)
        if address and address.company_id == company_id:
            address.is_default = True
            self.session.flush()
            logger.info(f"Dirección id={address_id} marcada como default")
        else:
            logger.warning(
                f"No se pudo establecer dirección id={address_id} como default"
            )

    def get_by_postal_code(
        self,
        company_id: int,
        postal_code: str
    ) -> Sequence[Address]:
        """
        Busca direcciones por código postal.

        Args:
            company_id: ID de la empresa
            postal_code: Código postal a buscar

        Returns:
            Lista de direcciones que coinciden

        Example:
            addresses = repo.get_by_postal_code(company_id=1, postal_code="7500000")
        """
        logger.debug(
            f"Buscando direcciones con código postal '{postal_code}' "
            f"de empresa id={company_id}"
        )

        stmt = (
            select(Address)
            .filter(
                Address.company_id == company_id,
                Address.postal_code == postal_code
            )
        )
        addresses = self.session.execute(stmt).scalars().all()

        logger.debug(f"Encontradas {len(addresses)} dirección(es)")
        return addresses
