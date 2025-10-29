"""
Schemas de Pydantic para Service (departamentos/servicios).

Define los schemas de validación para operaciones CRUD sobre servicios.
"""

from typing import Optional

from pydantic import Field, field_validator

from src.schemas.base import BaseSchema, BaseResponse


# ============================================================================
# SERVICE SCHEMAS
# ============================================================================

class ServiceCreate(BaseSchema):
    """
    Schema para crear un nuevo servicio/departamento.

    Example:
        data = ServiceCreate(
            name="Ventas",
            description="Departamento de ventas"
        )
    """

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Nombre del servicio/departamento"
    )
    description: Optional[str] = Field(
        None,
        max_length=200,
        description="Descripción del servicio"
    )

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        """Asegura que el nombre no sea solo espacios."""
        if not v.strip():
            raise ValueError("El nombre del servicio no puede estar vacío")
        return v.strip()

    @field_validator('description')
    @classmethod
    def normalize_description(cls, v: Optional[str]) -> Optional[str]:
        """Normaliza la descripción."""
        if v:
            return v.strip()
        return v


class ServiceUpdate(BaseSchema):
    """
    Schema para actualizar un servicio/departamento.

    Todos los campos son opcionales - solo los campos provistos serán actualizados.

    Example:
        data = ServiceUpdate(
            description="Nueva descripción"
        )
    """

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=200)
    is_active: Optional[bool] = None

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError("El nombre del servicio no puede estar vacío")
            return v.strip()
        return v

    @field_validator('description')
    @classmethod
    def normalize_description(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return v.strip()
        return v


class ServiceResponse(BaseResponse):
    """
    Schema para respuesta de servicio/departamento.

    Incluye todos los campos del servicio.

    Example:
        service = ServiceResponse.model_validate(service_orm)
        print(service.name)
        print(service.description)
    """

    name: str
    description: Optional[str] = None
    is_active: bool
