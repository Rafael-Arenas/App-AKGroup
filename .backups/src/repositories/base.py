"""
Repositorio base implementando el patrón Repository.

Proporciona operaciones CRUD genéricas que son heredadas por
todos los repositorios específicos de la aplicación.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Generic, TypeVar, Optional, List

from sqlalchemy.orm import Session

from src.exceptions.repository import NotFoundException
from src.utils.logger import logger

# TypeVar genérico para el modelo
T = TypeVar("T")


class IRepository(ABC, Generic[T]):
    """
    Interfaz de repositorio que define el contrato para acceso a datos.

    Todos los repositorios deben implementar estos métodos para garantizar
    una API consistente de acceso a datos.
    """

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        """Obtener entidad por ID."""
        pass

    @abstractmethod
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
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
            def get_by_trigram(self, trigram: str) -> Optional[Company]:
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

    def get_by_id(self, id: int) -> Optional[T]:
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
        entity = self.session.query(self.model).filter(self.model.id == id).first()

        if entity:
            logger.debug(f"{self.model.__name__} encontrado: id={id}")
        else:
            logger.debug(f"{self.model.__name__} no encontrado: id={id}")

        return entity

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """
        Obtiene todas las entidades con paginación.

        Args:
            skip: Número de registros a saltar (offset)
            limit: Número máximo de registros a retornar

        Returns:
            Lista de entidades

        Example:
            # Obtener primera página (registros 0-99)
            companies = repository.get_all(skip=0, limit=100)

            # Obtener segunda página (registros 100-199)
            companies = repository.get_all(skip=100, limit=100)
        """
        logger.debug(f"Obteniendo {self.model.__name__} - skip={skip}, limit={limit}")
        entities = self.session.query(self.model).offset(skip).limit(limit).all()
        logger.debug(f"Encontrados {len(entities)} {self.model.__name__}(s)")
        return entities

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
            Entidad actualizada

        Raises:
            NotFoundException: Si la entidad no existe

        Note:
            Esta operación hace flush() pero NO commit().

        Example:
            company = repository.get_by_id(123)
            company.name = "Nuevo Nombre"
            updated = repository.update(company)
            session.commit()
        """
        logger.debug(f"Actualizando {self.model.__name__} con id={entity.id}")

        # Verificar que existe
        existing = self.get_by_id(entity.id)
        if not existing:
            raise NotFoundException(
                f"{self.model.__name__} no encontrado",
                details={"id": entity.id}
            )

        self.session.merge(entity)
        self.session.flush()
        logger.info(f"{self.model.__name__} actualizado: id={entity.id}")
        return entity

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
        count = self.session.query(self.model).count()
        logger.debug(f"Total {self.model.__name__}: {count}")
        return count

    def exists(self, id: int) -> bool:
        """
        Verifica si existe una entidad con el ID dado.

        Args:
            id: ID a verificar

        Returns:
            True si existe, False en caso contrario

        Example:
            if repository.exists(123):
                print("La empresa existe")
        """
        exists = self.session.query(self.model).filter(self.model.id == id).count() > 0
        logger.debug(f"{self.model.__name__} id={id} existe: {exists}")
        return exists
