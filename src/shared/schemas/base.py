"""
Schemas base de Pydantic para la aplicación.

Define schemas base que son heredados por todos los demás schemas
para mantener consistencia en validación y serialización.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """
    Schema base para todos los schemas de Pydantic.

    Configura comportamientos comunes para todos los schemas:
    - from_attributes: Permite crear schemas desde objetos ORM
    - validate_assignment: Valida al asignar valores después de creación
    - str_strip_whitespace: Elimina espacios en blanco de strings
    - use_enum_values: Usa valores de enums en lugar de nombres

    Example:
        class CompanyCreate(BaseSchema):
            name: str
            trigram: str
    """

    model_config = ConfigDict(
        from_attributes=True,  # ORM mode - permite Company.model_validate(orm_obj)
        validate_assignment=True,  # Validar cuando se asignan valores
        str_strip_whitespace=True,  # Quitar espacios en blanco automáticamente
        use_enum_values=True,  # Usar valores de enum en lugar de nombres
    )


class TimestampResponse(BaseSchema):
    """
    Schema con campos de timestamp.

    Para modelos que usan TimestampMixin (created_at, updated_at).

    Example:
        class CompanyResponse(TimestampResponse):
            id: int
            name: str
            # created_at y updated_at se heredan
    """

    created_at: datetime
    updated_at: datetime


class BaseResponse(TimestampResponse):
    """
    Schema base para respuestas con ID, timestamps y auditoría.

    Incluye campos comunes para todas las respuestas:
    - id: Identificador único
    - created_at: Fecha de creación
    - updated_at: Fecha de última actualización
    - created_by: ID del usuario que creó el registro
    - updated_by: ID del usuario que modificó el registro

    Example:
        class CompanyResponse(BaseResponse):
            name: str
            trigram: str
            # id, created_at, updated_at, created_by, updated_by se heredan
    """

    id: int
    created_by: Optional[int] = None
    updated_by: Optional[int] = None


class PaginatedResponse(BaseSchema):
    """
    Schema para respuestas paginadas.

    Attributes:
        items: Lista de items de la página actual
        total: Total de items en la base de datos
        page: Número de página actual (1-indexed)
        page_size: Tamaño de página
        total_pages: Total de páginas

    Example:
        PaginatedResponse(
            items=[company1, company2, company3],
            total=150,
            page=1,
            page_size=10,
            total_pages=15
        )
    """

    items: list
    total: int
    page: int
    page_size: int
    total_pages: int


class MessageResponse(BaseSchema):
    """
    Schema para respuestas simples con mensaje.

    Útil para operaciones DELETE o confirmaciones.

    Example:
        MessageResponse(
            message="Empresa eliminada exitosamente",
            details={"company_id": 123}
        )
    """

    message: str
    details: Optional[dict] = None
