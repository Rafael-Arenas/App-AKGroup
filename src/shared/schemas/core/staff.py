from __future__ import annotations

"""
Schemas de Pydantic para Staff (usuarios del sistema).

Define los schemas de validación para operaciones CRUD sobre usuarios/staff.
"""


from pydantic import Field, field_validator, EmailStr

from src.shared.schemas.base import BaseSchema, BaseResponse


# ============================================================================
# STAFF SCHEMAS
# ============================================================================

class StaffCreate(BaseSchema):
    """
    Schema para crear un nuevo usuario del sistema.

    Todos los campos requeridos deben ser provistos.

    Example:
        data = StaffCreate(
            username="jdoe",
            email="john.doe@akgroup.com",
            first_name="John",
            last_name="Doe",
            trigram="JDO",
            phone="+56912345678",
            position="Gerente de Ventas",
            is_admin=False
        )
    """

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r'^[a-z0-9_-]+$',
        description="Username único (solo lowercase, números, guiones y underscores)"
    )
    email: EmailStr = Field(
        ...,
        description="Email único del usuario"
    )
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
    trigram: str | None = Field(
        None,
        min_length=3,
        max_length=3,
        pattern=r'^[A-Z]{3}$',
        description="Código de 3 letras (opcional, debe ser único)"
    )
    phone: str | None = Field(
        None,
        max_length=20,
        pattern=r'^\+?[1-9]\d{1,14}$',
        description="Teléfono en formato E.164"
    )
    position: str | None = Field(
        None,
        max_length=100,
        description="Cargo/posición"
    )
    is_admin: bool = Field(
        default=False,
        description="Si el usuario tiene permisos de administrador"
    )

    @field_validator('username')
    @classmethod
    def username_lowercase(cls, v: str) -> str:
        """Convierte el username a minúsculas y normaliza."""
        return v.lower().strip()

    @field_validator('email')
    @classmethod
    def email_lowercase(cls, v: EmailStr) -> str:
        """Convierte el email a minúsculas."""
        return str(v).lower().strip()

    @field_validator('first_name', 'last_name')
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        """Asegura que los nombres no sean solo espacios."""
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v.strip()

    @field_validator('trigram')
    @classmethod
    def trigram_uppercase(cls, v: str | None) -> str | None:
        """Convierte el trigram a mayúsculas."""
        if v:
            v = v.strip()
            if len(v) != 3:
                raise ValueError("El trigram debe tener exactamente 3 caracteres")
            if not v.isalpha():
                raise ValueError("El trigram solo puede contener letras")
            return v.upper()
        return v

    @field_validator('position')
    @classmethod
    def normalize_position(cls, v: str | None) -> str | None:
        """Normaliza el cargo."""
        if v:
            return v.strip()
        return v


class StaffUpdate(BaseSchema):
    """
    Schema para actualizar un usuario.

    Todos los campos son opcionales - solo los campos provistos serán actualizados.

    Example:
        data = StaffUpdate(
            email="new_email@akgroup.com",
            position="Gerente General"
        )
    """

    username: str | None = Field(
        None,
        min_length=3,
        max_length=50,
        pattern=r'^[a-z0-9_-]+$'
    )
    email: EmailStr | None = None
    first_name: str | None = Field(None, min_length=1, max_length=50)
    last_name: str | None = Field(None, min_length=1, max_length=50)
    trigram: str | None = Field(
        None,
        min_length=3,
        max_length=3,
        pattern=r'^[A-Z]{3}$'
    )
    phone: str | None = Field(
        None,
        max_length=20,
        pattern=r'^\+?[1-9]\d{1,14}$'
    )
    position: str | None = Field(None, max_length=100)
    is_active: bool | None = None
    is_admin: bool | None = None

    @field_validator('username')
    @classmethod
    def username_lowercase(cls, v: str | None) -> str | None:
        if v:
            return v.lower().strip()
        return v

    @field_validator('email')
    @classmethod
    def email_lowercase(cls, v: EmailStr | None) -> str | None:
        if v:
            return str(v).lower().strip()
        return v

    @field_validator('first_name', 'last_name')
    @classmethod
    def name_not_empty(cls, v: str | None) -> str | None:
        if v is not None:
            if not v.strip():
                raise ValueError("El nombre no puede estar vacío")
            return v.strip()
        return v

    @field_validator('trigram')
    @classmethod
    def trigram_uppercase(cls, v: str | None) -> str | None:
        if v:
            v = v.strip()
            if len(v) != 3:
                raise ValueError("El trigram debe tener exactamente 3 caracteres")
            if not v.isalpha():
                raise ValueError("El trigram solo puede contener letras")
            return v.upper()
        return v

    @field_validator('position')
    @classmethod
    def normalize_position(cls, v: str | None) -> str | None:
        if v:
            return v.strip()
        return v


class StaffResponse(BaseResponse):
    """
    Schema para respuesta de usuario del sistema.

    Incluye todos los campos del usuario.

    Example:
        staff = StaffResponse.model_validate(staff_orm)
        print(staff.username)
        print(staff.full_name)
    """

    username: str
    email: str
    first_name: str
    last_name: str
    trigram: str | None = None
    phone: str | None = None
    position: str | None = None
    is_active: bool
    is_admin: bool

    # Computed field - full name
    @property
    def full_name(self) -> str:
        """Nombre completo del usuario."""
        return f"{self.first_name} {self.last_name}"
