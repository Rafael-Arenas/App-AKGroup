"""
Note model - Polymorphic notes system.

Sistema polimórfico de notas que puede asociarse a cualquier entidad
del sistema (Company, Product, Quote, Order, etc.)
"""

from sqlalchemy import Column, Enum as SQLEnum, Index, Integer, String, Text
from sqlalchemy.orm import validates

from src.shared.enums import NotePriority
from ..base import AuditMixin, Base, TimestampMixin


class Note(Base, TimestampMixin, AuditMixin):
    """
    Sistema polimórfico de notas.

    Permite agregar notas/comentarios a cualquier entidad del sistema
    usando un patrón polimórfico con entity_type + entity_id.

    Attributes:
        id: Primary key
        entity_type: Tipo de entidad (ej: "company", "product", "quote")
        entity_id: ID de la entidad
        title: Título opcional de la nota
        content: Contenido de la nota
        priority: Prioridad (low, normal, high, urgent)
        category: Categoría opcional (ej: "Technical", "Commercial")

    Example:
        >>> # Nota para una empresa
        >>> note = Note(
        ...     entity_type="company",
        ...     entity_id=123,
        ...     title="Recordatorio",
        ...     content="Cliente prefiere entregas los martes",
        ...     priority=NotePriority.NORMAL,
        ...     category="Commercial"
        ... )
        >>>
        >>> # Nota para un producto
        >>> note = Note(
        ...     entity_type="product",
        ...     entity_id=456,
        ...     content="Revisar stock mínimo",
        ...     priority=NotePriority.HIGH
        ... )

    Usage en queries:
        >>> # Obtener todas las notas de una empresa
        >>> company_notes = session.query(Note).filter(
        ...     Note.entity_type == "company",
        ...     Note.entity_id == company_id
        ... ).all()
        >>>
        >>> # Notas urgentes de un producto
        >>> urgent_notes = session.query(Note).filter(
        ...     Note.entity_type == "product",
        ...     Note.entity_id == product_id,
        ...     Note.priority == NotePriority.URGENT
        ... ).all()
    """

    __tablename__ = "notes"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Polymorphic fields
    entity_type = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Type of entity this note belongs to (company, product, quote, etc.)",
    )

    entity_id = Column(
        Integer,
        nullable=False,
        index=True,
        comment="ID of the entity this note belongs to",
    )

    # Note content
    title = Column(
        String(200),
        nullable=True,
        comment="Optional title for the note",
    )

    content = Column(
        Text,
        nullable=False,
        comment="Note content/body",
    )

    # Classification
    priority = Column(
        SQLEnum(NotePriority),
        nullable=False,
        default=NotePriority.NORMAL,
        index=True,
        comment="Priority level: low, normal, high, urgent",
    )

    category = Column(
        String(50),
        nullable=True,
        index=True,
        comment="Optional category (Technical, Commercial, Administrative, etc.)",
    )

    # Indexes
    __table_args__ = (
        # Índice compuesto para búsqueda eficiente por entidad
        Index("ix_note_entity", "entity_type", "entity_id"),
        # Índice para filtrar por prioridad y tipo
        Index("ix_note_priority_type", "priority", "entity_type"),
    )

    # Validators
    @validates("entity_type")
    def validate_entity_type(self, key: str, value: str) -> str:
        """
        Valida el tipo de entidad.

        Args:
            key: Nombre del campo
            value: Tipo de entidad

        Returns:
            Tipo de entidad normalizado (lowercase)

        Raises:
            ValueError: Si el tipo está vacío
        """
        if not value or len(value.strip()) == 0:
            raise ValueError("entity_type cannot be empty")

        # Normalizar a lowercase
        normalized = value.strip().lower()

        # Validar tipos conocidos (opcional, puede comentarse para más flexibilidad)
        valid_types = {
            "company",
            "product",
            "quote",
            "order",
            "invoice",
            "contact",
            "address",
            "plant",
        }

        if normalized not in valid_types:
            # Warning: tipo no reconocido, pero permitido
            import warnings

            warnings.warn(
                f"entity_type '{normalized}' is not in known types: {valid_types}",
                UserWarning,
            )

        return normalized

    @validates("entity_id")
    def validate_entity_id(self, key: str, value: int) -> int:
        """
        Valida el ID de entidad.

        Args:
            key: Nombre del campo
            value: ID de entidad

        Returns:
            ID validado

        Raises:
            ValueError: Si el ID es inválido
        """
        if value is None or value <= 0:
            raise ValueError("entity_id must be a positive integer")

        return value

    @validates("content")
    def validate_content(self, key: str, value: str) -> str:
        """
        Valida el contenido de la nota.

        Args:
            key: Nombre del campo
            value: Contenido

        Returns:
            Contenido validado

        Raises:
            ValueError: Si el contenido está vacío
        """
        if not value or len(value.strip()) == 0:
            raise ValueError("Note content cannot be empty")

        return value.strip()

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<Note(id={self.id}, "
            f"entity={self.entity_type}:{self.entity_id}, "
            f"priority={self.priority.value})>"
        )
