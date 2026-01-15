"""
Repositorio para Staff (usuarios del sistema).

Maneja el acceso a datos para usuarios/staff del sistema.
"""

from typing import Optional, List
from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from src.backend.models.core.staff import Staff
from src.backend.repositories.base import BaseRepository
from src.backend.utils.logger import logger


class StaffRepository(BaseRepository[Staff]):
    """
    Repositorio para Staff con métodos específicos.

    Además de los métodos CRUD base, proporciona métodos
    para búsquedas específicas de usuarios del sistema.

    Example:
        repo = StaffRepository(session)
        staff = repo.get_by_username("jdoe")
        admins = repo.get_admins()
    """

    def __init__(self, session: Session):
        """
        Inicializa el repositorio de Staff.

        Args:
            session: Sesión de SQLAlchemy
        """
        super().__init__(session, Staff)

    def get_by_username(self, username: str) -> Optional[Staff]:
        """
        Busca un usuario por username.

        Args:
            username: Username a buscar

        Returns:
            Staff si existe, None en caso contrario

        Example:
            staff = repo.get_by_username("jdoe")
            if staff:
                print(f"Usuario encontrado: {staff.full_name}")
        """
        logger.debug(f"Buscando staff por username: {username}")

        stmt = select(Staff).filter(Staff.username == username.lower())
        staff = self.session.execute(stmt).scalar_one_or_none()

        if staff:
            logger.debug(f"Staff encontrado: {staff.full_name} (id={staff.id})")
        else:
            logger.debug(f"No se encontró staff con username='{username}'")

        return staff

    def get_by_email(self, email: str) -> Optional[Staff]:
        """
        Busca un usuario por email.

        Args:
            email: Email a buscar

        Returns:
            Staff si existe, None en caso contrario

        Example:
            staff = repo.get_by_email("john.doe@akgroup.com")
            if staff:
                print(f"Usuario encontrado: {staff.full_name}")
        """
        logger.debug(f"Buscando staff por email: {email}")

        stmt = select(Staff).filter(Staff.email == email.lower())
        staff = self.session.execute(stmt).scalar_one_or_none()

        if staff:
            logger.debug(f"Staff encontrado: {staff.full_name}")
        else:
            logger.debug(f"No se encontró staff con email='{email}'")

        return staff

    def get_by_trigram(self, trigram: str) -> Optional[Staff]:
        """
        Busca un usuario por trigram.

        Args:
            trigram: Trigram de 3 letras

        Returns:
            Staff si existe, None en caso contrario

        Example:
            staff = repo.get_by_trigram("JDO")
            if staff:
                print(f"Usuario encontrado: {staff.full_name}")
        """
        logger.debug(f"Buscando staff por trigram: {trigram}")

        stmt = select(Staff).filter(Staff.trigram == trigram.upper())
        staff = self.session.execute(stmt).scalar_one_or_none()

        if staff:
            logger.debug(f"Staff encontrado: {staff.full_name} (trigram={trigram})")
        else:
            logger.debug(f"No se encontró staff con trigram='{trigram}'")

        return staff

    def get_active_staff(self, skip: int = 0, limit: int = 100) -> List[Staff]:
        """
        Obtiene solo los usuarios activos.

        Args:
            skip: Registros a saltar
            limit: Número máximo de registros

        Returns:
            Lista de usuarios activos

        Example:
            active_staff = repo.get_active_staff()
        """
        logger.debug(f"Obteniendo staff activo - skip={skip}, limit={limit}")

        stmt = (
            select(Staff)
            .filter(Staff.is_active == True)
            .order_by(Staff.last_name, Staff.first_name)
            .offset(skip)
            .limit(limit)
        )
        staff_list = list(self.session.execute(stmt).scalars().all())

        logger.debug(f"Encontrados {len(staff_list)} usuario(s) activo(s)")
        return staff_list

    def get_admins(self, skip: int = 0, limit: int = 100) -> List[Staff]:
        """
        Obtiene solo los usuarios administradores.

        Args:
            skip: Registros a saltar
            limit: Número máximo de registros

        Returns:
            Lista de administradores

        Example:
            admins = repo.get_admins()
        """
        logger.debug(f"Obteniendo administradores - skip={skip}, limit={limit}")

        stmt = (
            select(Staff)
            .filter(Staff.is_admin == True)
            .order_by(Staff.last_name, Staff.first_name)
            .offset(skip)
            .limit(limit)
        )
        admins = list(self.session.execute(stmt).scalars().all())

        logger.debug(f"Encontrados {len(admins)} administrador(es)")
        return admins

    def get_active_admins(self) -> List[Staff]:
        """
        Obtiene solo los administradores activos.

        Returns:
            Lista de administradores activos

        Example:
            active_admins = repo.get_active_admins()
        """
        logger.debug("Obteniendo administradores activos")

        stmt = (
            select(Staff)
            .filter(
                Staff.is_admin == True,
                Staff.is_active == True
            )
            .order_by(Staff.last_name, Staff.first_name)
        )
        admins = list(self.session.execute(stmt).scalars().all())

        logger.debug(f"Encontrados {len(admins)} administrador(es) activo(s)")
        return admins

    def search_by_name(self, name: str) -> List[Staff]:
        """
        Busca usuarios por nombre.

        Busca en first_name y last_name.

        Args:
            name: Texto a buscar

        Returns:
            Lista de usuarios que coinciden

        Example:
            staff_list = repo.search_by_name("john")
        """
        logger.debug(f"Buscando staff por nombre: {name}")

        search_pattern = f"%{name}%"
        stmt = (
            select(Staff)
            .filter(
                or_(
                    Staff.first_name.ilike(search_pattern),
                    Staff.last_name.ilike(search_pattern)
                )
            )
            .order_by(Staff.last_name, Staff.first_name)
        )
        staff_list = list(self.session.execute(stmt).scalars().all())

        logger.debug(f"Encontrados {len(staff_list)} usuario(s)")
        return staff_list

    def get_by_position(self, position: str) -> List[Staff]:
        """
        Busca usuarios por posición/cargo.

        Args:
            position: Cargo a buscar

        Returns:
            Lista de usuarios que coinciden

        Example:
            managers = repo.get_by_position("gerente")
        """
        logger.debug(f"Buscando staff por posición: {position}")

        search_pattern = f"%{position}%"
        stmt = (
            select(Staff)
            .filter(Staff.position.ilike(search_pattern))
            .order_by(Staff.last_name, Staff.first_name)
        )
        staff_list = list(self.session.execute(stmt).scalars().all())

        logger.debug(f"Encontrados {len(staff_list)} usuario(s)")
        return staff_list
