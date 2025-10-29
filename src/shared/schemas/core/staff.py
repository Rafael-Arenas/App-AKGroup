"""
Schemas de Pydantic para Staff (usuarios del sistema).

Define los schemas de validación para operaciones CRUD sobre usuarios/staff.
"""

from typing import Optional

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
    trigram: Optional[str] = Field(
        None,
        min_length=3,
        max_length=3,
        pattern=r'^[A-Z]{3}$',
        description="Código de 3 letras (opcional, debe ser único)"
    )
    phone: Optional[str] = Field(
        None,
        max_length=20,
        pattern=r'^\+?[1-9]\d{1,14}$',
        description="Teléfono en formato E.164"
    )
    position: Optional[str] = Field(
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
    def trigram_uppercase(cls, v: Optional[str]) -> Optional[str]:
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
    def normalize_position(cls, v: Optional[str]) -> Optional[str]:
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

    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        pattern=r'^[a-z0-9_-]+$'
    )
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    trigram: Optional[str] = Field(
        None,
        min_length=3,
        max_length=3,
        pattern=r'^[A-Z]{3}$'
    )
    phone: Optional[str] = Field(
        None,
        max_length=20,
        pattern=r'^\+?[1-9]\d{1,14}$'
    )
    position: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None

    @field_validator('username')
    @classmethod
    def username_lowercase(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return v.lower().strip()
        return v

    @field_validator('email')
    @classmethod
    def email_lowercase(cls, v: Optional[EmailStr]) -> Optional[str]:
        if v:
            return str(v).lower().strip()
        return v

    @field_validator('first_name', 'last_name')
    @classmethod
    def name_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            if not v.strip():
                raise ValueError("El nombre no puede estar vacío")
            return v.strip()
        return v

    @field_validator('trigram')
    @classmethod
    def trigram_uppercase(cls, v: Optional[str]) -> Optional[str]:
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
    def normalize_position(cls, v: Optional[str]) -> Optional[str]:
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
    trigram: Optional[str] = None
    phone: Optional[str] = None
    position: Optional[str] = None
    is_active: bool
    is_admin: bool

    # Computed field - full name
    @property
    def full_name(self) -> str:
        """Nombre completo del usuario."""
        return f"{self.first_name} {self.last_name}"
