from __future__ import annotations

"""
Schemas de Pydantic para Address.

Define los schemas de validación para operaciones CRUD sobre direcciones.
"""


from pydantic import Field, field_validator

from src.shared.enums import AddressType
from src.shared.schemas.base import BaseSchema, BaseResponse


# ============================================================================
# ADDRESS SCHEMAS
# ============================================================================

class AddressCreate(BaseSchema):
    """
    Schema para crear una nueva dirección.

    Todos los campos requeridos deben ser provistos.

    Example:
        data = AddressCreate(
            address="Av. Providencia 1234, Oficina 501",
            city="Santiago",
            postal_code="7500000",
            country="Chile",
            is_default=True,
            address_type=AddressType.DELIVERY,
            company_id=1
        )
    """

    address: str = Field(
        ...,
        min_length=5,
        description="Dirección completa (calle, número, detalles)"
    )
    city: str | None = Field(
        None,
        max_length=100,
        description="Ciudad"
    )
    postal_code: str | None = Field(
        None,
        max_length=20,
        description="Código postal"
    )
    country: str | None = Field(
        None,
        max_length=100,
        description="País"
    )
    is_default: bool = Field(
        default=False,
        description="Si es la dirección por defecto"
    )
    address_type: AddressType = Field(
        default=AddressType.DELIVERY,
        description="Tipo de dirección (delivery, billing, headquarters, plant)"
    )
    company_id: int = Field(
        ...,
        gt=0,
        description="ID de la empresa"
    )

    @field_validator('address')
    @classmethod
    def address_not_empty(cls, v: str) -> str:
        """Asegura que la dirección no sea solo espacios."""
        if not v.strip():
            raise ValueError("La dirección no puede estar vacía")
        if len(v.strip()) < 5:
            raise ValueError("La dirección debe tener al menos 5 caracteres")
        return v.strip()

    @field_validator('city', 'country')
    @classmethod
    def normalize_text(cls, v: str | None) -> str | None:
        """Normaliza texto (trim)."""
        if v:
            return v.strip()
        return v

    @field_validator('postal_code')
    @classmethod
    def normalize_postal_code(cls, v: str | None) -> str | None:
        """Normaliza código postal (trim, uppercase)."""
        if v:
            return v.strip().upper()
        return v


class AddressUpdate(BaseSchema):
    """
    Schema para actualizar una dirección.

    Todos los campos son opcionales - solo los campos provistos serán actualizados.

    Example:
        data = AddressUpdate(
            address="Nueva dirección 456",
            city="Valparaíso"
        )
    """

    address: str | None = Field(None, min_length=5)
    city: str | None = Field(None, max_length=100)
    postal_code: str | None = Field(None, max_length=20)
    country: str | None = Field(None, max_length=100)
    is_default: bool | None = None
    address_type: AddressType | None = None

    @field_validator('address')
    @classmethod
    def address_not_empty(cls, v: str | None) -> str | None:
        if v is not None:
            if not v.strip():
                raise ValueError("La dirección no puede estar vacía")
            if len(v.strip()) < 5:
                raise ValueError("La dirección debe tener al menos 5 caracteres")
            return v.strip()
        return v

    @field_validator('city', 'country')
    @classmethod
    def normalize_text(cls, v: str | None) -> str | None:
        if v:
            return v.strip()
        return v

    @field_validator('postal_code')
    @classmethod
    def normalize_postal_code(cls, v: str | None) -> str | None:
        if v:
            return v.strip().upper()
        return v


class AddressResponse(BaseResponse):
    """
    Schema para respuesta de dirección.

    Incluye todos los campos de la dirección.

    Example:
        address = AddressResponse.model_validate(address_orm)
        print(address.address)
        print(address.city)
    """

    address: str
    city: str | None = None
    postal_code: str | None = None
    country: str | None = None
    is_default: bool
    address_type: AddressType
    company_id: int
