"""
Repositorio para Note (sistema polimórfico de notas).

Maneja el acceso a datos para notas asociadas a cualquier entidad del sistema.
"""

from collections.abc import Sequence
from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session

from src.backend.models.core.notes import Note, NotePriority
from src.backend.repositories.base import BaseRepository
from src.backend.utils.logger import logger


class NoteRepository(BaseRepository[Note]):
    """
    Repositorio para Note con métodos específicos.

    Además de los métodos CRUD base, proporciona métodos
    para búsquedas específicas de notas polimórficas.

    Example:
        repo = NoteRepository(session)
        notes = repo.get_by_entity("company", 123)
        urgent = repo.get_urgent_notes("product", 456)
    """

    def __init__(self, session: Session):
        """
        Inicializa el repositorio de Note.

        Args:
            session: Sesión de SQLAlchemy
        """
        super().__init__(session, Note)

    def get_by_entity(
        self,
        entity_type: str,
        entity_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[Note]:
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
            notes = repo.get_by_entity("company", 123)
            for note in notes:
                print(f"{note.title}: {note.content}")
        """
        logger.debug(
            f"Obteniendo notas de {entity_type} id={entity_id} - "
            f"skip={skip}, limit={limit}"
        )

        stmt = (
            select(Note)
            .filter(
                Note.entity_type == entity_type.lower(),
                Note.entity_id == entity_id
            )
            .order_by(Note.priority.desc(), Note.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        notes = self.session.execute(stmt).scalars().all()

        logger.debug(f"Encontradas {len(notes)} nota(s)")
        return notes

    def get_by_priority(
        self,
        entity_type: str,
        entity_id: int,
        priority: NotePriority
    ) -> Sequence[Note]:
        """
        Obtiene notas de una entidad filtradas por prioridad.

        Args:
            entity_type: Tipo de entidad
            entity_id: ID de la entidad
            priority: Prioridad de las notas

        Returns:
            Lista de notas con la prioridad especificada

        Example:
            high_priority = repo.get_by_priority(
                "company", 123, NotePriority.HIGH
            )
        """
        logger.debug(
            f"Obteniendo notas de {entity_type} id={entity_id} "
            f"con prioridad={priority.name}"
        )

        stmt = (
            select(Note)
            .filter(
                Note.entity_type == entity_type.lower(),
                Note.entity_id == entity_id,
                Note.priority == priority
            )
            .order_by(Note.created_at.desc())
        )
        notes = self.session.execute(stmt).scalars().all()

        logger.debug(f"Encontradas {len(notes)} nota(s) con prioridad {priority.name}")
        return notes

    def get_urgent_notes(
        self,
        entity_type: str,
        entity_id: int
    ) -> Sequence[Note]:
        """
        Obtiene solo las notas urgentes de una entidad.

        Args:
            entity_type: Tipo de entidad
            entity_id: ID de la entidad

        Returns:
            Lista de notas urgentes

        Example:
            urgent = repo.get_urgent_notes("product", 456)
        """
        return self.get_by_priority(entity_type, entity_id, NotePriority.URGENT)

    def get_high_priority_notes(
        self,
        entity_type: str,
        entity_id: int
    ) -> Sequence[Note]:
        """
        Obtiene notas de alta prioridad y urgentes de una entidad.

        Args:
            entity_type: Tipo de entidad
            entity_id: ID de la entidad

        Returns:
            Lista de notas de alta prioridad y urgentes

        Example:
            important = repo.get_high_priority_notes("quote", 789)
        """
        logger.debug(
            f"Obteniendo notas de alta prioridad/urgentes de "
            f"{entity_type} id={entity_id}"
        )

        stmt = (
            select(Note)
            .filter(
                Note.entity_type == entity_type.lower(),
                Note.entity_id == entity_id,
                Note.priority.in_([NotePriority.HIGH, NotePriority.URGENT])
            )
            .order_by(Note.priority.desc(), Note.created_at.desc())
        )
        notes = self.session.execute(stmt).scalars().all()

        logger.debug(f"Encontradas {len(notes)} nota(s) importantes")
        return notes

    def get_by_category(
        self,
        entity_type: str,
        entity_id: int,
        category: str
    ) -> Sequence[Note]:
        """
        Obtiene notas de una entidad filtradas por categoría.

        Args:
            entity_type: Tipo de entidad
            entity_id: ID de la entidad
            category: Categoría de las notas

        Returns:
            Lista de notas de la categoría especificada

        Example:
            technical_notes = repo.get_by_category(
                "product", 456, "Technical"
            )
        """
        logger.debug(
            f"Obteniendo notas de {entity_type} id={entity_id} "
            f"con categoría='{category}'"
        )

        stmt = (
            select(Note)
            .filter(
                Note.entity_type == entity_type.lower(),
                Note.entity_id == entity_id,
                Note.category == category
            )
            .order_by(Note.created_at.desc())
        )
        notes = self.session.execute(stmt).scalars().all()

        logger.debug(f"Encontradas {len(notes)} nota(s) de categoría '{category}'")
        return notes

    def search_content(
        self,
        entity_type: str,
        entity_id: int,
        search_term: str
    ) -> Sequence[Note]:
        """
        Busca notas por contenido o título.

        Args:
            entity_type: Tipo de entidad
            entity_id: ID de la entidad
            search_term: Término a buscar

        Returns:
            Lista de notas que coinciden

        Example:
            notes = repo.search_content("company", 123, "cliente prefiere")
        """
        logger.debug(
            f"Buscando '{search_term}' en notas de {entity_type} id={entity_id}"
        )

        search_pattern = f"%{search_term}%"
        stmt = (
            select(Note)
            .filter(
                Note.entity_type == entity_type.lower(),
                Note.entity_id == entity_id,
                or_(
                    Note.content.ilike(search_pattern),
                    Note.title.ilike(search_pattern)
                )
            )
            .order_by(Note.created_at.desc())
        )
        notes = self.session.execute(stmt).scalars().all()

        logger.debug(f"Encontradas {len(notes)} nota(s)")
        return notes

    def get_all_by_type(
        self,
        entity_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[Note]:
        """
        Obtiene todas las notas de un tipo de entidad específico.

        Útil para obtener todas las notas de todas las empresas, productos, etc.

        Args:
            entity_type: Tipo de entidad
            skip: Registros a saltar
            limit: Número máximo de registros

        Returns:
            Lista de notas del tipo especificado

        Example:
            all_company_notes = repo.get_all_by_type("company")
        """
        logger.debug(
            f"Obteniendo todas las notas de tipo {entity_type} - "
            f"skip={skip}, limit={limit}"
        )

        stmt = (
            select(Note)
            .filter(Note.entity_type == entity_type.lower())
            .order_by(Note.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        notes = self.session.execute(stmt).scalars().all()

        logger.debug(f"Encontradas {len(notes)} nota(s) de tipo {entity_type}")
        return notes

    def count_by_entity(self, entity_type: str, entity_id: int) -> int:
        """
        Cuenta las notas de una entidad específica.

        Args:
            entity_type: Tipo de entidad
            entity_id: ID de la entidad

        Returns:
            Número de notas

        Example:
            count = repo.count_by_entity("company", 123)
            print(f"La empresa tiene {count} notas")
        """
        logger.debug(f"Contando notas de {entity_type} id={entity_id}")

        stmt = (
            select(func.count(Note.id))
            .filter(
                Note.entity_type == entity_type.lower(),
                Note.entity_id == entity_id
            )
        )
        count = self.session.execute(stmt).scalar() or 0

        logger.debug(f"{entity_type} id={entity_id} tiene {count} nota(s)")
        return count

    def get_recent_notes(
        self,
        entity_type: str,
        entity_id: int,
        days: int = 7
    ) -> Sequence[Note]:
        """
        Obtiene las notas recientes de una entidad.

        Args:
            entity_type: Tipo de entidad
            entity_id: ID de la entidad
            days: Número de días hacia atrás (default: 7)

        Returns:
            Lista de notas recientes

        Example:
            recent = repo.get_recent_notes("company", 123, days=30)
        """
        import pendulum

        logger.debug(
            f"Obteniendo notas recientes ({days} días) de "
            f"{entity_type} id={entity_id}"
        )

        cutoff_date = pendulum.now("UTC").subtract(days=days)

        stmt = (
            select(Note)
            .filter(
                Note.entity_type == entity_type.lower(),
                Note.entity_id == entity_id,
                Note.created_at >= cutoff_date
            )
            .order_by(Note.created_at.desc())
        )
        notes = self.session.execute(stmt).scalars().all()

        logger.debug(f"Encontradas {len(notes)} nota(s) recientes")
        return notes
