"""
Servicio de lógica de negocio para Note (sistema polimórfico de notas).

Implementa validaciones y reglas de negocio para notas.
"""

from sqlalchemy.orm import Session

from src.models.core.notes import Note, NotePriority
from src.repositories.core.note_repository import NoteRepository
from src.schemas.core.note import NoteCreate, NoteUpdate, NoteResponse
from src.services.base import BaseService
from src.exceptions.service import ValidationException
from src.utils.logger import logger


class NoteService(BaseService[Note, NoteCreate, NoteUpdate, NoteResponse]):
    """
    Servicio para Note con validaciones de negocio.

    Maneja la lógica de negocio para notas polimórficas, incluyendo:
    - Validación de tipo de entidad
    - Validación de contenido
    - Reglas de negocio específicas

    Example:
        service = NoteService(repository, session)
        note = service.create(NoteCreate(...), user_id=1)
    """

    def __init__(
        self,
        repository: NoteRepository,
        session: Session,
    ):
        """
        Inicializa el servicio de Note.

        Args:
            repository: Repositorio de Note
            session: Sesión de SQLAlchemy
        """
        super().__init__(
            repository=repository,
            session=session,
            model=Note,
            response_schema=NoteResponse,
        )
        # Cast para tener acceso a métodos específicos de NoteRepository
        self.note_repo: NoteRepository = repository

    def validate_create(self, entity: Note) -> None:
        """
        Valida reglas de negocio antes de crear una nota.

        Args:
            entity: Nota a validar

        Raises:
            ValidationException: Si la validación falla
        """
        logger.debug(
            f"Validando creación de nota para {entity.entity_type} "
            f"id={entity.entity_id}"
        )

        # Validar que el contenido no esté vacío
        if not entity.content or len(entity.content.strip()) == 0:
            raise ValidationException(
                "El contenido de la nota no puede estar vacío",
                details={"content": entity.content}
            )

        logger.debug("Validación de creación exitosa")

    def validate_update(self, entity: Note) -> None:
        """
        Valida reglas de negocio antes de actualizar una nota.

        Args:
            entity: Nota a validar

        Raises:
            ValidationException: Si la validación falla
        """
        logger.debug(f"Validando actualización de nota id={entity.id}")

        # Validar que el contenido no esté vacío (si se actualiza)
        if entity.content is not None and len(entity.content.strip()) == 0:
            raise ValidationException(
                "El contenido de la nota no puede estar vacío",
                details={"note_id": entity.id}
            )

        logger.debug("Validación de actualización exitosa")

    def get_by_entity(
        self,
        entity_type: str,
        entity_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> list[NoteResponse]:
        """
        Obtiene todas las notas de una entidad específica.

        Args:
            entity_type: Tipo de entidad (company, product, quote, etc.)
            entity_id: ID de la entidad
            skip: Registros a saltar
            limit: Número máximo de registros

        Returns:
            Lista de notas de la entidad

        Example:
            notes = service.get_by_entity("company", 123)
        """
        logger.info(
            f"Servicio: obteniendo notas de {entity_type} id={entity_id}"
        )

        notes = self.note_repo.get_by_entity(entity_type, entity_id, skip, limit)
        return [self.response_schema.model_validate(n) for n in notes]

    def get_by_priority(
        self,
        entity_type: str,
        entity_id: int,
        priority: NotePriority
    ) -> list[NoteResponse]:
        """
        Obtiene notas de una entidad filtradas por prioridad.

        Args:
            entity_type: Tipo de entidad
            entity_id: ID de la entidad
            priority: Prioridad de las notas

        Returns:
            Lista de notas con la prioridad especificada

        Example:
            high_notes = service.get_by_priority(
                "company", 123, NotePriority.HIGH
            )
        """
        logger.info(
            f"Servicio: obteniendo notas de {entity_type} id={entity_id} "
            f"con prioridad={priority.value}"
        )

        notes = self.note_repo.get_by_priority(entity_type, entity_id, priority)
        return [self.response_schema.model_validate(n) for n in notes]

    def get_urgent_notes(
        self,
        entity_type: str,
        entity_id: int
    ) -> list[NoteResponse]:
        """
        Obtiene solo las notas urgentes de una entidad.

        Args:
            entity_type: Tipo de entidad
            entity_id: ID de la entidad

        Returns:
            Lista de notas urgentes

        Example:
            urgent = service.get_urgent_notes("product", 456)
        """
        logger.info(
            f"Servicio: obteniendo notas urgentes de {entity_type} id={entity_id}"
        )

        notes = self.note_repo.get_urgent_notes(entity_type, entity_id)
        return [self.response_schema.model_validate(n) for n in notes]

    def get_high_priority_notes(
        self,
        entity_type: str,
        entity_id: int
    ) -> list[NoteResponse]:
        """
        Obtiene notas de alta prioridad y urgentes de una entidad.

        Args:
            entity_type: Tipo de entidad
            entity_id: ID de la entidad

        Returns:
            Lista de notas de alta prioridad y urgentes

        Example:
            important = service.get_high_priority_notes("quote", 789)
        """
        logger.info(
            f"Servicio: obteniendo notas importantes de {entity_type} id={entity_id}"
        )

        notes = self.note_repo.get_high_priority_notes(entity_type, entity_id)
        return [self.response_schema.model_validate(n) for n in notes]

    def get_by_category(
        self,
        entity_type: str,
        entity_id: int,
        category: str
    ) -> list[NoteResponse]:
        """
        Obtiene notas de una entidad filtradas por categoría.

        Args:
            entity_type: Tipo de entidad
            entity_id: ID de la entidad
            category: Categoría de las notas

        Returns:
            Lista de notas de la categoría especificada

        Example:
            technical = service.get_by_category("product", 456, "Technical")
        """
        logger.info(
            f"Servicio: obteniendo notas de {entity_type} id={entity_id} "
            f"con categoría='{category}'"
        )

        notes = self.note_repo.get_by_category(entity_type, entity_id, category)
        return [self.response_schema.model_validate(n) for n in notes]

    def search_content(
        self,
        entity_type: str,
        entity_id: int,
        search_term: str
    ) -> list[NoteResponse]:
        """
        Busca notas por contenido o título.

        Args:
            entity_type: Tipo de entidad
            entity_id: ID de la entidad
            search_term: Término a buscar

        Returns:
            Lista de notas que coinciden

        Example:
            notes = service.search_content("company", 123, "cliente prefiere")
        """
        logger.info(
            f"Servicio: buscando '{search_term}' en notas de "
            f"{entity_type} id={entity_id}"
        )

        notes = self.note_repo.search_content(entity_type, entity_id, search_term)
        return [self.response_schema.model_validate(n) for n in notes]

    def get_all_by_type(
        self,
        entity_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[NoteResponse]:
        """
        Obtiene todas las notas de un tipo de entidad específico.

        Args:
            entity_type: Tipo de entidad
            skip: Registros a saltar
            limit: Número máximo de registros

        Returns:
            Lista de notas del tipo especificado

        Example:
            all_company_notes = service.get_all_by_type("company")
        """
        logger.info(f"Servicio: obteniendo todas las notas de tipo {entity_type}")

        notes = self.note_repo.get_all_by_type(entity_type, skip, limit)
        return [self.response_schema.model_validate(n) for n in notes]

    def count_by_entity(self, entity_type: str, entity_id: int) -> int:
        """
        Cuenta las notas de una entidad específica.

        Args:
            entity_type: Tipo de entidad
            entity_id: ID de la entidad

        Returns:
            Número de notas

        Example:
            count = service.count_by_entity("company", 123)
        """
        logger.info(f"Servicio: contando notas de {entity_type} id={entity_id}")
        return self.note_repo.count_by_entity(entity_type, entity_id)

    def get_recent_notes(
        self,
        entity_type: str,
        entity_id: int,
        days: int = 7
    ) -> list[NoteResponse]:
        """
        Obtiene las notas recientes de una entidad.

        Args:
            entity_type: Tipo de entidad
            entity_id: ID de la entidad
            days: Número de días hacia atrás (default: 7)

        Returns:
            Lista de notas recientes

        Example:
            recent = service.get_recent_notes("company", 123, days=30)
        """
        logger.info(
            f"Servicio: obteniendo notas recientes ({days} días) de "
            f"{entity_type} id={entity_id}"
        )

        notes = self.note_repo.get_recent_notes(entity_type, entity_id, days)
        return [self.response_schema.model_validate(n) for n in notes]
