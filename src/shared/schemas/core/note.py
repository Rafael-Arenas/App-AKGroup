"""
Schemas de Pydantic para Note (sistema polimórfico de notas).

Define los schemas de validación para operaciones CRUD sobre notas.
"""

from typing import Optional

from pydantic import Field, field_validator

from src.shared.enums import NotePriority
from src.shared.schemas.base import BaseSchema, BaseResponse


# ============================================================================
# NOTE SCHEMAS
# ============================================================================

class NoteCreate(BaseSchema):
    """
    Schema para crear una nueva nota.

    Example:
        # Nota para una empresa
        data = NoteCreate(
            entity_type="company",
            entity_id=123,
            title="Recordatorio",
            content="Cliente prefiere entregas los martes",
            priority=NotePriority.NORMAL,
            category="Commercial"
        )

        # Nota para un producto
        data = NoteCreate(
            entity_type="product",
            entity_id=456,
            content="Revisar stock mínimo",
            priority=NotePriority.HIGH
        )
    """

    entity_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Tipo de entidad (company, product, quote, order, etc.)"
    )
    entity_id: int = Field(
        ...,
        gt=0,
        description="ID de la entidad"
    )
    title: Optional[str] = Field(
        None,
        max_length=200,
        description="Título opcional de la nota"
    )
    content: str = Field(
        ...,
        min_length=1,
        description="Contenido de la nota"
    )
    priority: NotePriority = Field(
        default=NotePriority.NORMAL,
        description="Prioridad (low, normal, high, urgent)"
    )
    category: Optional[str] = Field(
        None,
        max_length=50,
        description="Categoría opcional (Technical, Commercial, etc.)"
    )

    @field_validator('entity_type')
    @classmethod
    def entity_type_lowercase(cls, v: str) -> str:
        """Convierte el tipo de entidad a minúsculas."""
        if not v.strip():
            raise ValueError("El tipo de entidad no puede estar vacío")
        return v.strip().lower()

    @field_validator('content')
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        """Asegura que el contenido no sea solo espacios."""
        if not v.strip():
            raise ValueError("El contenido de la nota no puede estar vacío")
        return v.strip()

    @field_validator('title', 'category')
    @classmethod
    def normalize_text(cls, v: Optional[str]) -> Optional[str]:
        """Normaliza texto opcional."""
        if v:
            return v.strip()
        return v


class NoteUpdate(BaseSchema):
    """
    Schema para actualizar una nota.

    Todos los campos son opcionales - solo los campos provistos serán actualizados.

    Example:
        data = NoteUpdate(
            content="Contenido actualizado",
            priority=NotePriority.URGENT
        )
    """

    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    priority: Optional[NotePriority] = None
    category: Optional[str] = Field(None, max_length=50)

    @field_validator('content')
    @classmethod
    def content_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError("El contenido de la nota no puede estar vacío")
            return v.strip()
        return v

    @field_validator('title', 'category')
    @classmethod
    def normalize_text(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return v.strip()
        return v


class NoteResponse(BaseResponse):
    """
    Schema para respuesta de nota.

    Incluye todos los campos de la nota.

    Example:
        note = NoteResponse.model_validate(note_orm)
        print(f"{note.entity_type}:{note.entity_id}")
        print(note.content)
    """

    entity_type: str
    entity_id: int
    title: Optional[str] = None
    content: str
    priority: NotePriority
    category: Optional[str] = None
