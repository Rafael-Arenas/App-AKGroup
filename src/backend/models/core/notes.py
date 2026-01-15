"""
Note model - Polymorphic notes system.

Sistema polimórfico de notas que puede asociarse a cualquier entidad
del sistema (Company, Product, Quote, Order, etc.)
"""

import warnings
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLEnum, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, validates

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
        >>> note = Note(
        ...     entity_type="company",
        ...     entity_id=123,
        ...     title="Recordatorio",
        ...     content="Cliente prefiere entregas los martes",
        ...     priority=NotePriority.NORMAL,
        ...     category="Commercial"
        ... )
    """

    __tablename__ = "notes"

    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Polymorphic fields
    entity_type: Mapped[str] = mapped_column(
        String(50),
        index=True,
        comment="Type of entity this note belongs to (company, product, quote, etc.)",
    )
    entity_id: Mapped[int] = mapped_column(
        index=True, comment="ID of the entity this note belongs to"
    )

    # Note content
    title: Mapped[str | None] = mapped_column(
        String(200), comment="Optional title for the note"
    )
    content: Mapped[str] = mapped_column(Text, comment="Note content/body")

    # Classification
    priority: Mapped[NotePriority] = mapped_column(
        SQLEnum(NotePriority),
        default=NotePriority.NORMAL,
        index=True,
        comment="Priority level: low, normal, high, urgent",
    )
    category: Mapped[str | None] = mapped_column(
        String(50),
        index=True,
        comment="Optional category (Technical, Commercial, Administrative, etc.)",
    )

    # Indexes
    __table_args__ = (
        Index("ix_note_entity", "entity_type", "entity_id"),
        Index("ix_note_priority_type", "priority", "entity_type"),
    )

    # Validators
    @validates("entity_type")
    def validate_entity_type(self, key: str, value: str) -> str:
        """Valida el tipo de entidad."""
        if not value or len(value.strip()) == 0:
            raise ValueError("entity_type cannot be empty")

        normalized = value.strip().lower()

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
            warnings.warn(
                f"entity_type '{normalized}' is not in known types: {valid_types}",
                UserWarning,
                stacklevel=2,
            )

        return normalized

    @validates("entity_id")
    def validate_entity_id(self, key: str, value: int) -> int:
        """Valida el ID de entidad."""
        if value is None or value <= 0:
            raise ValueError("entity_id must be a positive integer")
        return value

    @validates("content")
    def validate_content(self, key: str, value: str) -> str:
        """Valida el contenido de la nota."""
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
