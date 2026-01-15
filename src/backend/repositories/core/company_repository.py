"""
Repositorio para Company, CompanyRut y Plant.

Maneja el acceso a datos para empresas, sus RUTs y plantas.
"""

from typing import Optional, List

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from src.backend.models.core.companies import Company, CompanyRut, Plant
from src.backend.repositories.base import BaseRepository
from src.backend.utils.logger import logger


class CompanyRepository(BaseRepository[Company]):
    """
    Repositorio para Company con métodos específicos.

    Además de los métodos CRUD base, proporciona métodos
    para búsquedas específicas de empresas.

    Example:
        repo = CompanyRepository(session, Company)
        company = repo.get_by_trigram("AKG")
        companies = repo.search_by_name("test")
    """

    def __init__(self, session: Session):
        """
        Inicializa el repositorio de Company.

        Args:
            session: Sesión de SQLAlchemy
        """
        super().__init__(session, Company)

    def get_by_trigram(self, trigram: str) -> Optional[Company]:
        """
        Busca una empresa por su trigram.

        Args:
            trigram: Trigram de 3 letras (ej: "AKG")

        Returns:
            Company si existe, None en caso contrario

        Example:
            company = repo.get_by_trigram("AKG")
            if company:
                print(f"Empresa encontrada: {company.name}")
        """
        logger.debug(f"Buscando empresa por trigram: {trigram}")
        stmt = select(Company).filter(Company.trigram == trigram.upper())
        company = self.session.execute(stmt).scalar_one_or_none()

        if company:
            logger.debug(f"Empresa encontrada: {company.name} (trigram={trigram})")
        else:
            logger.debug(f"No se encontró empresa con trigram={trigram}")

        return company

    def search_by_name(self, name: str) -> List[Company]:
        """
        Busca empresas por nombre (búsqueda parcial).

        Args:
            name: Texto a buscar en el nombre

        Returns:
            Lista de empresas que coinciden

        Example:
            companies = repo.search_by_name("test")
            for company in companies:
                print(company.name)
        """
        logger.debug(f"Buscando empresas por nombre: {name}")
        search_pattern = f"%{name}%"
        stmt = (
            select(Company)
            .filter(Company.name.ilike(search_pattern))
            .order_by(Company.name)
        )
        companies = list(self.session.execute(stmt).scalars().all())

        logger.debug(f"Encontradas {len(companies)} empresa(s) con nombre '{name}'")
        return companies

    def get_by_type(
        self,
        company_type_id: int,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[Company]:
        """
        Obtiene empresas filtradas por tipo y opcionalmente por estado.

        Args:
            company_type_id: ID del tipo de empresa (1=CLIENT, 2=SUPPLIER)
            skip: Registros a saltar
            limit: Máximo de registros
            is_active: Filtrar por estado activo/inactivo (None = todos)

        Returns:
            Lista de empresas del tipo especificado

        Example:
            # Obtener solo clientes activos
            clients = repo.get_by_type(company_type_id=1, is_active=True)
        """
        logger.debug(f"Obteniendo empresas por tipo: {company_type_id}, is_active={is_active}")

        stmt = select(Company).filter(Company.company_type_id == company_type_id)

        # Aplicar filtro de estado si se especifica
        if is_active is not None:
            stmt = stmt.filter(Company.is_active == is_active)

        companies = list(self.session.execute(stmt.offset(skip).limit(limit)).scalars().all())

        logger.debug(f"Encontradas {len(companies)} empresa(s) del tipo {company_type_id}")
        return companies

    def get_with_plants(self, company_id: int) -> Optional[Company]:
        """
        Obtiene una empresa con sus plantas cargadas (eager loading).

        Args:
            company_id: ID de la empresa

        Returns:
            Company con plants cargadas, None si no existe

        Example:
            company = repo.get_with_plants(123)
            if company:
                for plant in company.plants:
                    print(plant.name)
        """
        logger.debug(f"Obteniendo empresa id={company_id} con plantas")

        stmt = (
            select(Company)
            .options(selectinload(Company.plants))
            .filter(Company.id == company_id)
        )
        company = self.session.execute(stmt).scalar_one_or_none()

        if company:
            logger.debug(f"Empresa encontrada con {len(company.plants)} planta(s)")

        return company

    def get_with_ruts(self, company_id: int) -> Optional[Company]:
        """
        Obtiene una empresa con sus RUTs cargados (eager loading).

        Args:
            company_id: ID de la empresa

        Returns:
            Company con RUTs cargados, None si no existe

        Example:
            company = repo.get_with_ruts(123)
            if company:
                for rut in company.ruts:
                    print(rut.rut)
        """
        logger.debug(f"Obteniendo empresa id={company_id} con RUTs")
        stmt = (
            select(Company)
            .options(selectinload(Company.ruts))
            .filter(Company.id == company_id)
        )
        company = self.session.execute(stmt).scalar_one_or_none()

        if company:
            logger.debug(f"Empresa encontrada con {len(company.ruts)} RUT(s)")

        return company

    def get_with_relations(self, company_id: int) -> Optional[Company]:
        """
        Obtiene una empresa con todas sus relaciones cargadas.

        Args:
            company_id: ID de la empresa

        Returns:
            Company con todas las relaciones, None si no existe

        Example:
            company = repo.get_with_relations(123)
            if company:
                print(f"Plantas: {len(company.plants)}")
                print(f"RUTs: {len(company.ruts)}")
        """
        logger.debug(f"Obteniendo empresa id={company_id} con todas las relaciones")
        stmt = (
            select(Company)
            .options(
                selectinload(Company.plants),
                selectinload(Company.ruts),
            )
            .filter(Company.id == company_id)
        )
        company = self.session.execute(stmt).scalar_one_or_none()

        return company

    def get_active_companies(self, skip: int = 0, limit: int = 100) -> List[Company]:
        """
        Obtiene solo las empresas activas.

        Args:
            skip: Registros a saltar
            limit: Número máximo de registros

        Returns:
            Lista de empresas activas

        Example:
            active_companies = repo.get_active_companies()
        """
        logger.debug(f"Obteniendo empresas activas - skip={skip}, limit={limit}")
        stmt = (
            select(Company)
            .filter(Company.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        companies = list(self.session.execute(stmt).scalars().all())

        logger.debug(f"Encontradas {len(companies)} empresa(s) activa(s)")
        return companies


class CompanyRutRepository(BaseRepository[CompanyRut]):
    """
    Repositorio para CompanyRut.

    Maneja los RUTs múltiples de empresas.

    Example:
        repo = CompanyRutRepository(session)
        rut = repo.get_by_rut("12345678-9")
    """

    def __init__(self, session: Session):
        super().__init__(session, CompanyRut)

    def get_by_rut(self, rut: str) -> Optional[CompanyRut]:
        """
        Busca un RUT específico.

        Args:
            rut: RUT en formato 12345678-9

        Returns:
            CompanyRut si existe, None en caso contrario
        """
        logger.debug(f"Buscando RUT: {rut}")
        stmt = select(CompanyRut).filter(CompanyRut.rut == rut.upper())
        company_rut = self.session.execute(stmt).scalar_one_or_none()

        return company_rut

    def get_by_company(self, company_id: int) -> List[CompanyRut]:
        """
        Obtiene todos los RUTs de una empresa.

        Args:
            company_id: ID de la empresa

        Returns:
            Lista de RUTs de la empresa
        """
        logger.debug(f"Obteniendo RUTs de empresa id={company_id}")
        stmt = select(CompanyRut).filter(CompanyRut.company_id == company_id)
        ruts = list(self.session.execute(stmt).scalars().all())

        logger.debug(f"Encontrados {len(ruts)} RUT(s)")
        return ruts

    def get_primary_rut(self, company_id: int) -> Optional[CompanyRut]:
        """
        Obtiene el RUT principal de una empresa.

        Args:
            company_id: ID de la empresa

        Returns:
            RUT principal si existe, None en caso contrario
        """
        logger.debug(f"Obteniendo RUT principal de empresa id={company_id}")
        stmt = select(CompanyRut).filter(
            CompanyRut.company_id == company_id,
            CompanyRut.is_main == True
        )
        primary_rut = self.session.execute(stmt).scalar_one_or_none()

        return primary_rut


class PlantRepository(BaseRepository[Plant]):
    """
    Repositorio para Plant (plantas/sucursales).

    Maneja las plantas de empresas.

    Example:
        repo = PlantRepository(session)
        plants = repo.get_by_company(company_id=1)
    """

    def __init__(self, session: Session):
        super().__init__(session, Plant)

    def get_by_company(self, company_id: int) -> List[Plant]:
        """
        Obtiene todas las plantas de una empresa.

        Args:
            company_id: ID de la empresa

        Returns:
            Lista de plantas
        """
        logger.debug(f"Obteniendo plantas de empresa id={company_id}")
        stmt = select(Plant).filter(Plant.company_id == company_id).order_by(Plant.name)
        plants = list(self.session.execute(stmt).scalars().all())

        logger.debug(f"Encontradas {len(plants)} planta(s)")
        return plants

    def get_active_plants(self, company_id: int) -> List[Plant]:
        """
        Obtiene solo las plantas activas de una empresa.

        Args:
            company_id: ID de la empresa

        Returns:
            Lista de plantas activas
        """
        logger.debug(f"Obteniendo plantas activas de empresa id={company_id}")
        stmt = select(Plant).filter(
            Plant.company_id == company_id,
            Plant.is_active == True
        ).order_by(Plant.name)
        plants = list(self.session.execute(stmt).scalars().all())

        logger.debug(f"Encontradas {len(plants)} planta(s) activa(s)")
        return plants

    def search_by_name(self, company_id: int, name: str) -> List[Plant]:
        """
        Busca plantas por nombre dentro de una empresa.

        Args:
            company_id: ID de la empresa
            name: Texto a buscar

        Returns:
            Lista de plantas que coinciden
        """
        logger.debug(f"Buscando plantas de empresa id={company_id} por nombre: {name}")
        search_pattern = f"%{name}%"
        stmt = select(Plant).filter(
            Plant.company_id == company_id,
            Plant.name.ilike(search_pattern)
        ).order_by(Plant.name)
        plants = list(self.session.execute(stmt).scalars().all())

        logger.debug(f"Encontradas {len(plants)} planta(s)")
        return plants
