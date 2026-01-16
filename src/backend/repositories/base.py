"""
Repositorio base implementando el patrón Repository.

Proporciona operaciones CRUD genéricas que son heredadas por
todos los repositorios específicos de la aplicación.
"""

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Generic, TypeVar

from sqlalchemy import select, func, exists, literal
from sqlalchemy.orm import DeclarativeBase, Session

from src.backend.exceptions.repository import NotFoundException
from src.backend.utils.logger import logger

# TypeVar genérico con bound a DeclarativeBase para mejor tipado
T = TypeVar("T", bound=DeclarativeBase)


class IRepository(ABC, Generic[T]):
    """
    Interfaz de repositorio que define el contrato para acceso a datos.

    Todos los repositorios deben implementar estos métodos para garantizar
    una API consistente de acceso a datos.
    """

    @abstractmethod
    def get_by_id(self, id: int) -> T | None:
        """Obtener entidad por ID."""
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[T]:
        """Obtener todas las entidades con paginación."""
        pass

    @abstractmethod
    def create(self, entity: T) -> T:
        """Crear nueva entidad."""
        pass

    @abstractmethod
    def update(self, entity: T) -> T:
        """Actualizar entidad existente."""
        pass

    @abstractmethod
    def delete(self, id: int) -> None:
        """Eliminar entidad por ID (hard delete)."""
        pass

    @abstractmethod
    def soft_delete(self, id: int, user_id: int) -> None:
        """Eliminar entidad de forma lógica (soft delete)."""
        pass


class BaseRepository(IRepository[T], Generic[T]):
    """
    Implementación base del patrón Repository.

    Proporciona operaciones CRUD comunes que todos los repositorios heredan.
    Los repositorios específicos pueden sobrescribir o extender estos métodos.

    Attributes:
        session: Sesión de SQLAlchemy para operaciones de DB
        model: Clase del modelo SQLAlchemy

    Example:
        class CompanyRepository(BaseRepository[Company]):
            def get_by_trigram(self, trigram: str) -> Company | None:
                return self.session.query(self.model).filter_by(trigram=trigram).first()
    """

    def __init__(self, session: Session, model: type[T]):
        """
        Inicializa el repositorio.

        Args:
            session: Sesión de SQLAlchemy
            model: Clase del modelo SQLAlchemy
        """
        self.session = session
        self.model = model

    def get_by_id(self, id: int) -> T | None:
        """
        Obtiene una entidad por su ID.

        Args:
            id: ID de la entidad

        Returns:
            Entidad si existe, None en caso contrario

        Example:
            company = repository.get_by_id(123)
            if company:
                print(company.name)
        """
        logger.debug(f"Buscando {self.model.__name__} con id={id}")
        entity = self.session.get(self.model, id)

        if entity:
            logger.debug(f"{self.model.__name__} encontrado: id={id}")
        else:
            logger.debug(f"{self.model.__name__} no encontrado: id={id}")

        return entity

    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
        descending: bool = False,
    ) -> Sequence[T]:
        """
        Obtiene todas las entidades con paginación y ordenamiento.

        Args:
            skip: Número de registros a saltar (offset)
            limit: Número máximo de registros a retornar
            order_by: Nombre de columna para ordenar (default: id)
            descending: Si True, orden descendente

        Returns:
            Lista de entidades

        Example:
            # Obtener primera página (registros 0-99)
            companies = repository.get_all(skip=0, limit=100)

            # Obtener segunda página ordenada por nombre descendente
            companies = repository.get_all(skip=100, limit=100, order_by="name", descending=True)
        """
        logger.debug(f"Obteniendo {self.model.__name__} - skip={skip}, limit={limit}")
        stmt = self._build_query(order_by=order_by, descending=descending, skip=skip, limit=limit)
        result = self.session.execute(stmt)
        entities = result.scalars().all()
        logger.debug(f"Encontrados {len(entities)} {self.model.__name__}(s)")
        return entities

    def find_by(
        self,
        filters: dict | None = None,
        skip: int = 0,
        limit: int = 100,
        order_by: str | None = None,
        descending: bool = False,
    ) -> Sequence[T]:
        """
        Búsqueda genérica con filtros dinámicos.

        Args:
            filters: Diccionario de filtros {columna: valor}
            skip: Número de registros a saltar
            limit: Número máximo de registros
            order_by: Columna para ordenar
            descending: Orden descendente

        Returns:
            Lista de entidades que coinciden

        Example:
            # Buscar empresas activas
            active = repository.find_by(filters={"is_active": True})

            # Buscar por tipo, ordenado por nombre
            by_type = repository.find_by(
                filters={"company_type_id": 1},
                order_by="name",
                limit=50
            )
        """
        logger.debug(f"Buscando {self.model.__name__} con filtros={filters}")
        stmt = self._build_query(
            filters=filters,
            order_by=order_by,
            descending=descending,
            skip=skip,
            limit=limit,
        )
        result = self.session.execute(stmt)
        entities = result.scalars().all()
        logger.debug(f"Encontrados {len(entities)} {self.model.__name__}(s) con filtros")
        return entities

    def _build_query(
        self,
        filters: dict | None = None,
        order_by: str | None = None,
        descending: bool = False,
        skip: int = 0,
        limit: int = 100,
    ):
        """
        Construye query dinámicamente con filtros, ordenamiento y paginación.

        Este es un método helper interno para construir queries de forma consistente.

        Args:
            filters: Diccionario de filtros {columna: valor}
            order_by: Nombre de columna para ordenar
            descending: Si True, orden descendente
            skip: Offset para paginación
            limit: Límite de resultados

        Returns:
            Select statement configurado

        Note:
            Los filtros None son ignorados automáticamente.
            Las columnas inexistentes en filters son ignoradas silenciosamente.
        """
        stmt = select(self.model)

        # Aplicar filtros
        if filters:
            for column_name, value in filters.items():
                if value is not None:
                    column = getattr(self.model, column_name, None)
                    if column is not None:
                        stmt = stmt.filter(column == value)

        # Aplicar ordenamiento
        if order_by:
            column = getattr(self.model, order_by, None)
            if column is not None:
                order = column.desc() if descending else column.asc()
                stmt = stmt.order_by(order)

        # Aplicar paginación
        stmt = stmt.offset(skip).limit(limit)

        return stmt

    def exists(self, id: int) -> bool:
        """
        Verifica si existe una entidad por su ID.

        Más eficiente que get_by_id() ya que solo hace SELECT 1.

        Args:
            id: ID de la entidad

        Returns:
            True si existe, False en caso contrario

        Example:
            if repository.exists(123):
                print("La entidad existe")
        """
        stmt = select(literal(1)).select_from(self.model).filter(self.model.id == id)
        result = self.session.execute(stmt).scalar()
        return result is not None

    def create(self, entity: T) -> T:
        """
        Crea una nueva entidad.

        Args:
            entity: Entidad a crear

        Returns:
            Entidad creada con ID asignado

        Note:
            Esta operación hace flush() pero NO commit().
            El commit debe ser manejado por el servicio o facade.

        Example:
            company = Company(name="Test", trigram="TST")
            created = repository.create(company)
            session.commit()  # Debe hacerse manualmente
        """
        logger.debug(f"Creando {self.model.__name__}")
        self.session.add(entity)
        self.session.flush()  # Obtener ID sin hacer commit
        logger.info(f"{self.model.__name__} creado con id={entity.id}")
        return entity

    def update(self, entity: T) -> T:
        """
        Actualiza una entidad existente.

        Args:
            entity: Entidad a actualizar (debe tener ID)

        Returns:
            Entidad actualizada (merged)

        Raises:
            NotFoundException: Si la entidad no existe

        Note:
            Esta operación hace flush() pero NO commit().
            Usa merge() que es más eficiente que get_by_id() + modificación.

        Example:
            company = repository.get_by_id(123)
            company.name = "Nuevo Nombre"
            updated = repository.update(company)
            session.commit()
        """
        logger.debug(f"Actualizando {self.model.__name__} con id={entity.id}")

        # Verificar existencia con exists() que es más eficiente que get_by_id()
        if not self.exists(entity.id):
            raise NotFoundException(
                f"{self.model.__name__} no encontrado",
                details={"id": entity.id}
            )

        # merge() sincroniza el estado de la entidad con la sesión
        merged = self.session.merge(entity)
        self.session.flush()
        logger.info(f"{self.model.__name__} actualizado: id={entity.id}")
        return merged

    def delete(self, id: int) -> None:
        """
        Elimina una entidad permanentemente (hard delete).

        Args:
            id: ID de la entidad a eliminar

        Raises:
            NotFoundException: Si la entidad no existe

        Note:
            Esta operación hace flush() pero NO commit().

        Warning:
            Esta operación es PERMANENTE. Considera usar soft_delete() en su lugar.

        Example:
            repository.delete(123)
            session.commit()
        """
        logger.debug(f"Eliminando {self.model.__name__} con id={id}")

        entity = self.get_by_id(id)
        if not entity:
            raise NotFoundException(
                f"{self.model.__name__} no encontrado",
                details={"id": id}
            )

        self.session.delete(entity)
        self.session.flush()
        logger.warning(f"{self.model.__name__} eliminado permanentemente: id={id}")

    def soft_delete(self, id: int, user_id: int) -> None:
        """
        Elimina una entidad de forma lógica (soft delete).

        Marca la entidad como eliminada sin borrarla de la base de datos.
        Solo funciona si el modelo tiene SoftDeleteMixin.

        Args:
            id: ID de la entidad a eliminar
            user_id: ID del usuario que realiza la eliminación

        Raises:
            NotFoundException: Si la entidad no existe
            NotImplementedError: Si el modelo no soporta soft delete

        Note:
            Esta operación hace flush() pero NO commit().

        Example:
            repository.soft_delete(123, user_id=1)
            session.commit()
        """
        logger.debug(f"Soft delete {self.model.__name__} con id={id}")

        entity = self.get_by_id(id)
        if not entity:
            raise NotFoundException(
                f"{self.model.__name__} no encontrado",
                details={"id": id}
            )

        # Verificar que el modelo soporta soft delete
        if not hasattr(entity, "is_deleted"):
            raise NotImplementedError(
                f"{self.model.__name__} no soporta soft delete (falta SoftDeleteMixin)"
            )

        entity.is_deleted = True
        entity.deleted_by_id = user_id
        self.session.flush()
        logger.info(f"{self.model.__name__} marcado como eliminado: id={id}")

    def count(self) -> int:
        """
        Cuenta el total de entidades.

        Returns:
            Número total de entidades

        Example:
            total = repository.count()
            print(f"Total de empresas: {total}")
        """
        stmt = select(func.count()).select_from(self.model)
        count = self.session.execute(stmt).scalar() or 0
        logger.debug(f"Total {self.model.__name__}: {count}")
        return count

    # =========================================================================
    # Bulk Operations
    # =========================================================================

    def create_many(self, entities: list[T]) -> list[T]:
        """
        Crea múltiples entidades en una operación.

        Args:
            entities: Lista de entidades a crear

        Returns:
            Lista de entidades creadas con IDs asignados

        Note:
            Esta operación hace flush() pero NO commit().
            Más eficiente que llamar create() múltiples veces.

        Example:
            companies = [
                Company(name="Empresa 1", trigram="EM1"),
                Company(name="Empresa 2", trigram="EM2"),
            ]
            created = repository.create_many(companies)
            session.commit()
        """
        if not entities:
            return []

        logger.debug(f"Creando {len(entities)} {self.model.__name__}(s) en bulk")
        self.session.add_all(entities)
        self.session.flush()
        logger.info(f"{len(entities)} {self.model.__name__}(s) creados en bulk")
        return entities

    def update_many(self, ids: list[int], values: dict) -> int:
        """
        Actualiza múltiples registros por IDs.

        Args:
            ids: Lista de IDs a actualizar
            values: Diccionario con columnas y valores a actualizar

        Returns:
            Número de filas actualizadas

        Note:
            Esta operación hace flush() pero NO commit().
            Usa UPDATE masivo, muy eficiente para actualizaciones simples.

        Example:
            # Desactivar múltiples empresas
            count = repository.update_many(
                ids=[1, 2, 3],
                values={"is_active": False}
            )
            print(f"{count} empresas desactivadas")
            session.commit()
        """
        if not ids or not values:
            return 0

        from sqlalchemy import update

        logger.debug(f"Actualizando {len(ids)} {self.model.__name__}(s) en bulk")
        stmt = update(self.model).where(self.model.id.in_(ids)).values(**values)
        result = self.session.execute(stmt)
        self.session.flush()
        rowcount = result.rowcount
        logger.info(f"{rowcount} {self.model.__name__}(s) actualizados en bulk")
        return rowcount

    def delete_many(self, ids: list[int]) -> int:
        """
        Elimina múltiples registros por IDs.

        Args:
            ids: Lista de IDs a eliminar

        Returns:
            Número de filas eliminadas

        Warning:
            Esta operación es PERMANENTE. Considera usar soft delete.

        Note:
            Esta operación hace flush() pero NO commit().
            Usa DELETE masivo, muy eficiente.

        Example:
            count = repository.delete_many([1, 2, 3])
            print(f"{count} empresas eliminadas")
            session.commit()
        """
        if not ids:
            return 0

        from sqlalchemy import delete

        logger.debug(f"Eliminando {len(ids)} {self.model.__name__}(s) en bulk")
        stmt = delete(self.model).where(self.model.id.in_(ids))
        result = self.session.execute(stmt)
        self.session.flush()
        rowcount = result.rowcount
        logger.warning(f"{rowcount} {self.model.__name__}(s) eliminados permanentemente en bulk")
        return rowcount
