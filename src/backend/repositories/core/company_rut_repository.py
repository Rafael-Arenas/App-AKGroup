"""
Repositorio para CompanyRut.

Maneja el acceso a datos para RUTs de empresas.
"""

from collections.abc import Sequence
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from src.backend.models.core.companies import CompanyRut
from src.backend.repositories.base import BaseRepository
from src.backend.utils.logger import logger


class CompanyRutRepository(BaseRepository[CompanyRut]):
    """
    Repositorio para CompanyRut con métodos específicos.

    Además de los métodos CRUD base, proporciona métodos
    para búsquedas específicas de RUTs.

    Example:
        repo = CompanyRutRepository(session)
        ruts = repo.get_by_company(company_id=1)
        main_rut = repo.get_main_rut(company_id=1)
    """

    def __init__(self, session: Session):
        """
        Inicializa el repositorio de CompanyRut.

        Args:
            session: Sesión de SQLAlchemy
        """
        super().__init__(session, CompanyRut)

    def get_by_company(self, company_id: int) -> Sequence[CompanyRut]:
        """
        Obtiene todos los RUTs de una empresa.

        Args:
            company_id: ID de la empresa

        Returns:
            Lista de RUTs

        Example:
            ruts = repo.get_by_company(company_id=1)
            for rut in ruts:
                print(f"{rut.rut} - {'Principal' if rut.is_main else 'Secundario'}")
        """
        logger.debug(f"Obteniendo RUTs de empresa id={company_id}")

        stmt = (
            select(CompanyRut)
            .filter(CompanyRut.company_id == company_id)
            .order_by(CompanyRut.is_main.desc(), CompanyRut.created_at)
        )
        ruts = self.session.execute(stmt).scalars().all()

        logger.debug(f"Encontrados {len(ruts)} RUT(s)")
        return ruts

    def get_main_rut(self, company_id: int) -> CompanyRut | None:
        """
        Obtiene el RUT principal de una empresa.

        Args:
            company_id: ID de la empresa

        Returns:
            RUT principal si existe, None en caso contrario

        Example:
            main_rut = repo.get_main_rut(company_id=1)
            if main_rut:
                print(f"RUT principal: {main_rut.rut}")
        """
        logger.debug(f"Obteniendo RUT principal de empresa id={company_id}")

        stmt = select(CompanyRut).filter(
            CompanyRut.company_id == company_id,
            CompanyRut.is_main == True
        )
        rut = self.session.execute(stmt).scalar_one_or_none()

        if rut:
            logger.debug(f"RUT principal encontrado: {rut.rut}")
        else:
            logger.debug(f"No se encontró RUT principal para empresa id={company_id}")

        return rut

    def get_by_rut(self, rut: str) -> CompanyRut | None:
        """
        Busca un RUT por su valor.

        Args:
            rut: RUT a buscar

        Returns:
            CompanyRut si existe, None en caso contrario

        Example:
            rut = repo.get_by_rut("76123456-7")
            if rut:
                print(f"RUT encontrado para empresa: {rut.company.name}")
        """
        logger.debug(f"Buscando RUT: {rut}")

        from src.backend.models.base.validators import RutValidator
        normalized_rut = RutValidator.validate(rut)

        stmt = select(CompanyRut).filter(CompanyRut.rut == normalized_rut)
        company_rut = self.session.execute(stmt).scalar_one_or_none()

        if company_rut:
            logger.debug(f"RUT encontrado: {company_rut.rut}")
        else:
            logger.debug(f"No se encontró RUT={rut}")

        return company_rut

    def set_as_main(self, rut_id: int) -> None:
        """
        Establece un RUT como principal, desmarcando los demás.

        Args:
            rut_id: ID del RUT a establecer como principal

        Example:
            repo.set_as_main(rut_id=5)
        """
        logger.debug(f"Estableciendo RUT id={rut_id} como principal")

        # Obtener el RUT a establecer como principal
        rut = self.get_by_id(rut_id)
        if not rut:
            raise ValueError(f"No existe RUT con id={rut_id}")

        # Desmarcar todos los RUTs de la empresa
        stmt = (
            update(CompanyRut)
            .filter(
                CompanyRut.company_id == rut.company_id,
                CompanyRut.is_main == True
            )
            .values(is_main=False)
        )
        self.session.execute(stmt)

        # Marcar el RUT seleccionado como principal
        rut.is_main = True

        logger.debug(f"RUT {rut.rut} establecido como principal")

    def get_secondary_ruts(self, company_id: int) -> Sequence[CompanyRut]:
        """
        Obtiene los RUTs secundarios de una empresa.

        Args:
            company_id: ID de la empresa

        Returns:
            Lista de RUTs secundarios

        Example:
            secondary = repo.get_secondary_ruts(company_id=1)
        """
        logger.debug(f"Obteniendo RUTs secundarios de empresa id={company_id}")

        stmt = (
            select(CompanyRut)
            .filter(
                CompanyRut.company_id == company_id,
                CompanyRut.is_main == False
            )
            .order_by(CompanyRut.created_at)
        )
        ruts = self.session.execute(stmt).scalars().all()

        logger.debug(f"Encontrados {len(ruts)} RUT(s) secundario(s)")
        return ruts
