from __future__ import annotations

"""
Schemas de Pydantic para Contact.

Define los schemas de validación para operaciones CRUD sobre contactos.
"""


from pydantic import Field, field_validator, EmailStr

from src.shared.schemas.base import BaseSchema, BaseResponse


# ============================================================================
# CONTACT SCHEMAS
# ============================================================================

class ContactCreate(BaseSchema):
    """
    Schema para crear un nuevo contacto.

    Todos los campos requeridos deben ser provistos.

    Example:
        data = ContactCreate(
            first_name="Juan",
            last_name="Pérez",
            email="jperez@example.com",
            phone="+56912345678",
            position="Gerente de Ventas",
            company_id=1,
            service_id=1
        )
    """

    first_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Nombre(s)"
    )
    last_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Apellido(s)"
    )
    email: EmailStr | None = Field(
        None,
        description="Email de contacto"
    )
    phone: str | None = Field(
        None,
        max_length=20,
        pattern=r'^\+?[1-9]\d{1,14}$',
        description="Teléfono en formato E.164"
    )
    mobile: str | None = Field(
        None,
        max_length=20,
        pattern=r'^\+?[1-9]\d{1,14}$',
        description="Teléfono móvil en formato E.164"
    )
    position: str | None = Field(
        None,
        max_length=100,
        description="Cargo/posición"
    )
    company_id: int = Field(
        ...,
        gt=0,
        description="ID de la empresa"
    )
    service_id: int | None = Field(
        None,
        gt=0,
        description="ID del servicio/departamento"
    )

    @field_validator('first_name', 'last_name')
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        """Asegura que los nombres no sean solo espacios."""
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v.strip()

    @field_validator('email')
    @classmethod
    def email_lowercase(cls, v: EmailStr | None) -> str | None:
        """Convierte el email a minúsculas."""
        if v:
            return str(v).lower().strip()
        return v

    @field_validator('position')
    @classmethod
    def normalize_position(cls, v: str | None) -> str | None:
        """Normaliza el cargo."""
        if v:
            return v.strip()
        return v


class ContactUpdate(BaseSchema):
    """
    Schema para actualizar un contacto.

    Todos los campos son opcionales - solo los campos provistos serán actualizados.

    Example:
        data = ContactUpdate(
            email="nuevo_email@example.com",
            phone="+56912345678"
        )
    """

    first_name: str | None = Field(None, min_length=1, max_length=50)
    last_name: str | None = Field(None, min_length=1, max_length=50)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=20, pattern=r'^\+?[1-9]\d{1,14}$')
    mobile: str | None = Field(None, max_length=20, pattern=r'^\+?[1-9]\d{1,14}$')
    position: str | None = Field(None, max_length=100)
    service_id: int | None = Field(None, gt=0)
    is_active: bool | None = None

    @field_validator('first_name', 'last_name')
    @classmethod
    def name_not_empty(cls, v: str | None) -> str | None:
        if v is not None:
            if not v.strip():
                raise ValueError("El nombre no puede estar vacío")
            return v.strip()
        return v

    @field_validator('email')
    @classmethod
    def email_lowercase(cls, v: EmailStr | None) -> str | None:
        if v:
            return str(v).lower().strip()
        return v

    @field_validator('position')
    @classmethod
    def normalize_position(cls, v: str | None) -> str | None:
        if v:
            return v.strip()
        return v


class ContactResponse(BaseResponse):
    """
    Schema para respuesta de contacto.

    Incluye todos los campos del contacto.

    Example:
        contact = ContactResponse.model_validate(contact_orm)
        print(contact.full_name)
        print(contact.email)
    """

    first_name: str
    last_name: str
    email: str | None = None
    phone: str | None = None
    mobile: str | None = None
    position: str | None = None
    company_id: int
    service_id: int | None = None
    is_active: bool

    # Computed field - full name
    @property
    def full_name(self) -> str:
        """Nombre completo del contacto."""
        return f"{self.first_name} {self.last_name}"
