"""
Repositorio para Country (tabla lookup de países).

Maneja el acceso a datos para países.
"""

from typing import Optional, List
from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from src.backend.models.lookups import Country
from src.backend.repositories.base import BaseRepository
from src.backend.utils.logger import logger


class CountryRepository(BaseRepository[Country]):
    """
    Repositorio para Country con métodos específicos.

    Proporciona métodos para búsquedas de países por nombre y código ISO.

    Example:
        repo = CountryRepository(session)
        country = repo.get_by_name("Chile")
        country = repo.get_by_iso_code("CL")
    """

    def __init__(self, session: Session):
        """
        Inicializa el repositorio de Country.

        Args:
            session: Sesión de SQLAlchemy
        """
        super().__init__(session, Country)

    def get_by_name(self, name: str) -> Optional[Country]:
        """
        Busca un país por nombre.

        Args:
            name: Nombre del país

        Returns:
            Country si existe, None en caso contrario

        Example:
            country = repo.get_by_name("Chile")
            if country:
                print(f"País encontrado: {country.name} ({country.iso_code_alpha2})")
        """
        logger.debug(f"Buscando país por nombre: {name}")

        stmt = select(Country).filter(Country.name == name.strip())
        country = self.session.execute(stmt).scalar_one_or_none()

        if country:
            logger.debug(f"País encontrado: {country.name}")
        else:
            logger.debug(f"No se encontró país con nombre='{name}'")

        return country

    def get_by_iso_code(self, iso_code: str) -> Optional[Country]:
        """
        Busca un país por código ISO (alpha-2 o alpha-3).

        Args:
            iso_code: Código ISO del país (CL, CHL, etc.)

        Returns:
            Country si existe, None en caso contrario

        Example:
            country = repo.get_by_iso_code("CL")
            country = repo.get_by_iso_code("CHL")
        """
        logger.debug(f"Buscando país por código ISO: {iso_code}")

        iso_code = iso_code.strip().upper()

        stmt = select(Country).filter(
            or_(
                Country.iso_code_alpha2 == iso_code,
                Country.iso_code_alpha3 == iso_code
            )
        )
        country = self.session.execute(stmt).scalar_one_or_none()

        if country:
            logger.debug(f"País encontrado: {country.name}")
        else:
            logger.debug(f"No se encontró país con código ISO='{iso_code}'")

        return country

    def search_by_name(self, name: str) -> List[Country]:
        """
        Busca países por nombre (búsqueda parcial).

        Args:
            name: Texto a buscar

        Returns:
            Lista de países que coinciden

        Example:
            countries = repo.search_by_name("chi")
            for country in countries:
                print(country.name)
        """
        logger.debug(f"Buscando países por nombre: {name}")

        search_pattern = f"%{name}%"
        stmt = (
            select(Country)
            .filter(Country.name.ilike(search_pattern))
            .order_by(Country.name)
        )
        countries = list(self.session.execute(stmt).scalars().all())

        logger.debug(f"Encontrados {len(countries)} país(es)")
        return countries

    def get_all_ordered(self, skip: int = 0, limit: int = 300) -> List[Country]:
        """
        Obtiene todos los países ordenados alfabéticamente.

        Args:
            skip: Registros a saltar
            limit: Número máximo de registros (default 300)

        Returns:
            Lista de países ordenados

        Example:
            countries = repo.get_all_ordered()
        """
        logger.debug(f"Obteniendo países ordenados - skip={skip}, limit={limit}")

        stmt = (
            select(Country)
            .order_by(Country.name)
            .offset(skip)
            .limit(limit)
        )
        countries = list(self.session.execute(stmt).scalars().all())

        logger.debug(f"Encontrados {len(countries)} país(es)")
        return countries
