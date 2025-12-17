"""
Schemas de Pydantic para Plant (Plantas/Sucursales).

Define los schemas de validación para operaciones CRUD sobre plantas.
"""

from typing import Optional

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
    address: Optional[str] = Field(
        None,
        description="Dirección de la planta"
    )
    phone: Optional[str] = Field(
        None,
        max_length=20,
        description="Teléfono de la planta"
    )
    email: Optional[str] = Field(
        None,
        max_length=100,
        description="Email de contacto"
    )
    company_id: int = Field(
        ...,
        gt=0,
        description="ID de la empresa"
    )
    city_id: Optional[int] = Field(
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

    name: Optional[str] = Field(None, min_length=2, max_length=100)
    address: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    city_id: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: Optional[str]) -> Optional[str]:
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
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    company_id: int
    city_id: Optional[int] = None
    city_name: Optional[str] = None  # Helper field si se une con city
    is_active: bool
