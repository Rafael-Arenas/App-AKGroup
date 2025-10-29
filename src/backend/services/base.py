"""
Servicio base implementando lógica de negocio común.

Proporciona operaciones de negocio genéricas que son heredadas por
todos los servicios específicos de la aplicación.
"""

from typing import Generic, TypeVar, Optional, List

from sqlalchemy.orm import Session

from src.backend.repositories.base import IRepository
from src.shared.schemas.base import BaseSchema
from src.backend.exceptions.repository import NotFoundException
from src.backend.exceptions.service import ValidationException
from src.backend.utils.logger import logger

# TypeVars para tipos genéricos
T = TypeVar("T")  # Modelo SQLAlchemy
CreateSchema = TypeVar("CreateSchema", bound=BaseSchema)
UpdateSchema = TypeVar("UpdateSchema", bound=BaseSchema)
ResponseSchema = TypeVar("ResponseSchema", bound=BaseSchema)


class BaseService(Generic[T, CreateSchema, UpdateSchema, ResponseSchema]):
    """
    Servicio base implementando lógica de negocio común.

    Los servicios orquestan operaciones de negocio, validan reglas,
    y coordinan múltiples repositorios si es necesario.

    Attributes:
        repository: Repositorio para acceso a datos
        session: Sesión de SQLAlchemy para transacciones
        model: Clase del modelo SQLAlchemy
        response_schema: Clase del schema de respuesta Pydantic

    Example:
        class CompanyService(BaseService[Company, CompanyCreate, CompanyUpdate, CompanyResponse]):
            def validate_trigram_unique(self, trigram: str):
                if self.repository.get_by_trigram(trigram):
                    raise ValidationException("Trigram ya existe")
    """

    def __init__(
        self,
        repository: IRepository[T],
        session: Session,
        model: type[T],
        response_schema: type[ResponseSchema],
    ):
        """
        Inicializa el servicio.

        Args:
            repository: Repositorio para acceso a datos
            session: Sesión de SQLAlchemy
            model: Clase del modelo SQLAlchemy
            response_schema: Clase del schema de respuesta
        """
        self.repository = repository
        self.session = session
        self.model = model
        self.response_schema = response_schema

    def get_by_id(self, id: int) -> ResponseSchema:
        """
        Obtiene una entidad por ID.

        Args:
            id: ID de la entidad

        Returns:
            Entidad como schema de respuesta

        Raises:
            NotFoundException: Si la entidad no existe

        Example:
            company = company_service.get_by_id(123)
            print(company.name)
        """
        logger.debug(f"Servicio: obteniendo {self.model.__name__} id={id}")

        entity = self.repository.get_by_id(id)
        if not entity:
            raise NotFoundException(
                f"{self.model.__name__} no encontrado",
                details={"id": id}
            )

        return self.response_schema.model_validate(entity)

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ResponseSchema]:
        """
        Obtiene todas las entidades con paginación.

        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros

        Returns:
            Lista de entidades como schemas de respuesta

        Example:
            companies = company_service.get_all(skip=0, limit=50)
            for company in companies:
                print(company.name)
        """
        logger.debug(f"Servicio: obteniendo {self.model.__name__}(s) - skip={skip}, limit={limit}")

        entities = self.repository.get_all(skip=skip, limit=limit)
        return [self.response_schema.model_validate(e) for e in entities]

    def create(self, schema: CreateSchema, user_id: int) -> ResponseSchema:
        """
        Crea una nueva entidad con validación.

        Args:
            schema: Schema de creación con datos validados
            user_id: ID del usuario que crea la entidad

        Returns:
            Entidad creada como schema de respuesta

        Raises:
            ValidationException: Si la validación falla

        Note:
            Esta operación NO hace commit. El commit debe ser manejado
            por el facade o controlador.

        Example:
            schema = CompanyCreate(name="Test", trigram="TST")
            company = company_service.create(schema, user_id=1)
        """
        logger.info(f"Servicio: creando {self.model.__name__}")

        try:
            # Establecer contexto de usuario para auditoría
            self.session.info["user_id"] = user_id

            # Crear entidad desde schema
            entity_data = schema.model_dump()
            entity = self.model(**entity_data)

            # Validar reglas de negocio (override en subclases)
            self.validate_create(entity)

            # Guardar
            created = self.repository.create(entity)

            logger.success(f"{self.model.__name__} creado exitosamente: id={created.id}")
            return self.response_schema.model_validate(created)

        except ValidationException:
            raise
        except Exception as e:
            logger.error(f"Error al crear {self.model.__name__}: {str(e)}")
            raise

    def update(self, id: int, schema: UpdateSchema, user_id: int) -> ResponseSchema:
        """
        Actualiza una entidad existente.

        Args:
            id: ID de la entidad a actualizar
            schema: Schema de actualización con datos validados
            user_id: ID del usuario que actualiza

        Returns:
            Entidad actualizada como schema de respuesta

        Raises:
            NotFoundException: Si la entidad no existe
            ValidationException: Si la validación falla

        Note:
            Esta operación NO hace commit.

        Example:
            schema = CompanyUpdate(name="Nuevo Nombre")
            company = company_service.update(123, schema, user_id=1)
        """
        logger.info(f"Servicio: actualizando {self.model.__name__} id={id}")

        try:
            # Establecer contexto de usuario
            self.session.info["user_id"] = user_id

            # Obtener entidad existente
            entity = self.repository.get_by_id(id)
            if not entity:
                raise NotFoundException(
                    f"{self.model.__name__} no encontrado",
                    details={"id": id}
                )

            # Actualizar campos (solo los que no son None)
            update_data = schema.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(entity, field, value)

            # Validar reglas de negocio
            self.validate_update(entity)

            # Guardar
            updated = self.repository.update(entity)

            logger.success(f"{self.model.__name__} actualizado exitosamente: id={updated.id}")
            return self.response_schema.model_validate(updated)

        except (NotFoundException, ValidationException):
            raise
        except Exception as e:
            logger.error(f"Error al actualizar {self.model.__name__} id={id}: {str(e)}")
            raise

    def delete(self, id: int, user_id: int, soft: bool = True) -> None:
        """
        Elimina una entidad.

        Args:
            id: ID de la entidad a eliminar
            user_id: ID del usuario que elimina
            soft: Si True, hace soft delete; si False, hard delete

        Raises:
            NotFoundException: Si la entidad no existe

        Note:
            Esta operación NO hace commit.

        Example:
            # Soft delete (recomendado)
            company_service.delete(123, user_id=1, soft=True)

            # Hard delete (permanente)
            company_service.delete(123, user_id=1, soft=False)
        """
        logger.info(f"Servicio: eliminando {self.model.__name__} id={id} (soft={soft})")

        try:
            self.session.info["user_id"] = user_id

            if soft and hasattr(self.model, "is_deleted"):
                self.repository.soft_delete(id, user_id)
                logger.success(f"{self.model.__name__} marcado como eliminado: id={id}")
            else:
                self.repository.delete(id)
                logger.warning(f"{self.model.__name__} eliminado permanentemente: id={id}")

        except NotFoundException:
            raise
        except Exception as e:
            logger.error(f"Error al eliminar {self.model.__name__} id={id}: {str(e)}")
            raise

    def count(self) -> int:
        """
        Cuenta el total de entidades.

        Returns:
            Número total de entidades

        Example:
            total = company_service.count()
            print(f"Total: {total}")
        """
        return self.repository.count()

    def exists(self, id: int) -> bool:
        """
        Verifica si existe una entidad.

        Args:
            id: ID a verificar

        Returns:
            True si existe, False en caso contrario

        Example:
            if company_service.exists(123):
                print("Existe")
        """
        return self.repository.exists(id)

    # Métodos para sobrescribir en subclases
    def validate_create(self, entity: T) -> None:
        """
        Valida reglas de negocio antes de crear.

        Sobrescribir en subclases para agregar validaciones específicas.

        Args:
            entity: Entidad a validar

        Raises:
            ValidationException: Si la validación falla

        Example:
            def validate_create(self, entity: Company):
                if self.repository.get_by_trigram(entity.trigram):
                    raise ValidationException("Trigram ya existe")
        """
        pass

    def validate_update(self, entity: T) -> None:
        """
        Valida reglas de negocio antes de actualizar.

        Sobrescribir en subclases para agregar validaciones específicas.

        Args:
            entity: Entidad a validar

        Raises:
            ValidationException: Si la validación falla
        """
        pass
