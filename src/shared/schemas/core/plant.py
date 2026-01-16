from __future__ import annotations

"""
Schemas de Pydantic para Plant (Plantas/Sucursales).

Define los schemas de validación para operaciones CRUD sobre plantas.
"""


from pydantic import Field, field_validator

from src.shared.schemas.base import BaseSchema, BaseResponse
from src.shared.schemas.core.address import AddressResponse  # Si necesitamos reusar partes o city


class PlantCreate(BaseSchema):
    """
    Schema para crear una nueva planta.
    """

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Nombre de la planta"
    )
    address: str | None = Field(
        None,
        description="Dirección de la planta"
    )
    phone: str | None = Field(
        None,
        max_length=20,
        description="Teléfono de la planta"
    )
    email: str | None = Field(
        None,
        max_length=100,
        description="Email de contacto"
    )
    company_id: int = Field(
        ...,
        gt=0,
        description="ID de la empresa"
    )
    city_id: int | None = Field(
        None,
        gt=0,
        description="ID de la ciudad"
    )
    is_active: bool = Field(
        default=True,
        description="Si la planta está activa"
    )

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v.strip()


class PlantUpdate(BaseSchema):
    """
    Schema para actualizar una planta.
    """

    name: str | None = Field(None, min_length=2, max_length=100)
    address: str | None = None
    phone: str | None = Field(None, max_length=20)
    email: str | None = Field(None, max_length=100)
    city_id: int | None = Field(None, gt=0)
    is_active: bool | None = None

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: str | None) -> str | None:
        if v is not None:
            if not v.strip():
                raise ValueError("El nombre no puede estar vacío")
            return v.strip()
        return v


class PlantResponse(BaseResponse):
    """
    Schema para respuesta de planta.
    """

    name: str
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    company_id: int
    city_id: int | None = None
    city_name: str | None = None  # Helper field si se une con city
    is_active: bool
