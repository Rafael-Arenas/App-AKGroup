"""
Repositorio para Company, CompanyRut y Branch.

Maneja el acceso a datos para empresas, sus RUTs y sucursales.
"""

from typing import Optional, List

from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from src.backend.models.core.companies import Company, CompanyRut, Branch
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

        company = (
            self.session.query(Company)
            .filter(Company.trigram == trigram.upper())
            .first()
        )

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
        companies = (
            self.session.query(Company)
            .filter(Company.name.ilike(search_pattern))
            .order_by(Company.name)
            .all()
        )

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

        query = self.session.query(Company).filter(Company.company_type_id == company_type_id)

        # Aplicar filtro de estado si se especifica
        if is_active is not None:
            query = query.filter(Company.is_active == is_active)

        companies = query.offset(skip).limit(limit).all()

        logger.debug(f"Encontradas {len(companies)} empresa(s) del tipo {company_type_id}")
        return companies

    def get_with_branches(self, company_id: int) -> Optional[Company]:
        """
        Obtiene una empresa con sus sucursales cargadas (eager loading).

        Args:
            company_id: ID de la empresa

        Returns:
            Company con branches cargadas, None si no existe

        Example:
            company = repo.get_with_branches(123)
            if company:
                for branch in company.branches:
                    print(branch.name)
        """
        logger.debug(f"Obteniendo empresa id={company_id} con sucursales")

        company = (
            self.session.query(Company)
            .options(selectinload(Company.branches))
            .filter(Company.id == company_id)
            .first()
        )

        if company:
            logger.debug(f"Empresa encontrada con {len(company.branches)} sucursal(es)")

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

        company = (
            self.session.query(Company)
            .options(selectinload(Company.ruts))
            .filter(Company.id == company_id)
            .first()
        )

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
                print(f"Sucursales: {len(company.branches)}")
                print(f"RUTs: {len(company.ruts)}")
        """
        logger.debug(f"Obteniendo empresa id={company_id} con todas las relaciones")

        company = (
            self.session.query(Company)
            .options(
                selectinload(Company.branches),
                selectinload(Company.ruts),
            )
            .filter(Company.id == company_id)
            .first()
        )

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

        companies = (
            self.session.query(Company)
            .filter(Company.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

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

        company_rut = (
            self.session.query(CompanyRut)
            .filter(CompanyRut.rut == rut.upper())
            .first()
        )

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

        ruts = (
            self.session.query(CompanyRut)
            .filter(CompanyRut.company_id == company_id)
            .all()
        )

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

        primary_rut = (
            self.session.query(CompanyRut)
            .filter(
                CompanyRut.company_id == company_id,
                CompanyRut.is_main == True
            )
            .first()
        )

        return primary_rut


class BranchRepository(BaseRepository[Branch]):
    """
    Repositorio para Branch (sucursales).

    Maneja las sucursales de empresas.

    Example:
        repo = BranchRepository(session)
        branches = repo.get_by_company(company_id=1)
    """

    def __init__(self, session: Session):
        super().__init__(session, Branch)

    def get_by_company(self, company_id: int) -> List[Branch]:
        """
        Obtiene todas las sucursales de una empresa.

        Args:
            company_id: ID de la empresa

        Returns:
            Lista de sucursales
        """
        logger.debug(f"Obteniendo sucursales de empresa id={company_id}")

        branches = (
            self.session.query(Branch)
            .filter(Branch.company_id == company_id)
            .order_by(Branch.name)
            .all()
        )

        logger.debug(f"Encontradas {len(branches)} sucursal(es)")
        return branches

    def get_active_branches(self, company_id: int) -> List[Branch]:
        """
        Obtiene solo las sucursales activas de una empresa.

        Args:
            company_id: ID de la empresa

        Returns:
            Lista de sucursales activas
        """
        logger.debug(f"Obteniendo sucursales activas de empresa id={company_id}")

        branches = (
            self.session.query(Branch)
            .filter(
                Branch.company_id == company_id,
                Branch.is_active == True
            )
            .order_by(Branch.name)
            .all()
        )

        logger.debug(f"Encontradas {len(branches)} sucursal(es) activa(s)")
        return branches

    def search_by_name(self, company_id: int, name: str) -> List[Branch]:
        """
        Busca sucursales por nombre dentro de una empresa.

        Args:
            company_id: ID de la empresa
            name: Texto a buscar

        Returns:
            Lista de sucursales que coinciden
        """
        logger.debug(f"Buscando sucursales de empresa id={company_id} por nombre: {name}")

        search_pattern = f"%{name}%"
        branches = (
            self.session.query(Branch)
            .filter(
                Branch.company_id == company_id,
                Branch.name.ilike(search_pattern)
            )
            .order_by(Branch.name)
            .all()
        )

        logger.debug(f"Encontradas {len(branches)} sucursal(es)")
        return branches
