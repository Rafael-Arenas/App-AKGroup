"""
Schemas de Pydantic para Company, CompanyRut y Branch.

Define los schemas de validación para operaciones CRUD sobre empresas,
sus RUTs y sucursales.
"""

from typing import Optional, List
from pydantic import Field, field_validator, HttpUrl

from src.schemas.base import BaseSchema, BaseResponse


# ============================================================================
# COMPANY SCHEMAS
# ============================================================================

class CompanyCreate(BaseSchema):
    """
    Schema para crear una nueva empresa.

    Todos los campos requeridos deben ser provistos.
    Los campos opcionales pueden agregarse posteriormente.

    Example:
        data = CompanyCreate(
            name="AK Group",
            trigram="AKG",
            company_type_id=1
        )
    """

    name: str = Field(
        ...,
        min_length=2,
        max_length=200,
        description="Nombre legal de la empresa"
    )
    trigram: str = Field(
        ...,
        min_length=3,
        max_length=3,
        description="Código de 3 letras de la empresa"
    )
    phone: Optional[str] = Field(
        None,
        pattern=r'^\+?[1-9]\d{1,14}$',
        description="Teléfono en formato E.164"
    )
    website: Optional[str] = Field(
        None,
        max_length=200,
        description="Sitio web de la empresa"
    )
    company_type_id: int = Field(
        ...,
        gt=0,
        description="ID del tipo de empresa (customer, supplier, both)"
    )
    country_id: Optional[int] = Field(
        None,
        gt=0,
        description="ID del país"
    )

    @field_validator('trigram')
    @classmethod
    def trigram_uppercase(cls, v: str) -> str:
        """Convierte el trigram a mayúsculas."""
        return v.upper().strip()

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        """Asegura que el nombre no sea solo espacios."""
        if not v.strip():
            raise ValueError("El nombre de la empresa no puede estar vacío")
        return v.strip()


class CompanyUpdate(BaseSchema):
    """
    Schema para actualizar una empresa.

    Todos los campos son opcionales - solo los campos provistos serán actualizados.

    Example:
        data = CompanyUpdate(name="Nuevo Nombre", phone="+56912345678")
    """

    name: Optional[str] = Field(None, min_length=2, max_length=200)
    trigram: Optional[str] = Field(None, min_length=3, max_length=3)
    phone: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    website: Optional[str] = Field(None, max_length=200)
    company_type_id: Optional[int] = Field(None, gt=0)
    country_id: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None

    @field_validator('trigram')
    @classmethod
    def trigram_uppercase(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return v.upper().strip()
        return v

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v and not v.strip():
            raise ValueError("El nombre de la empresa no puede estar vacío")
        return v.strip() if v else v


class CompanyResponse(BaseResponse):
    """
    Schema para respuesta de empresa.

    Incluye todos los campos de la empresa más relaciones opcionales.

    Example:
        company = CompanyResponse.model_validate(company_orm)
        print(company.name)
        print(company.trigram)
    """

    name: str
    trigram: str
    phone: Optional[str] = None
    website: Optional[str] = None
    company_type_id: int
    country_id: Optional[int] = None
    is_active: bool

    # Relaciones opcionales (eager loading)
    ruts: Optional[List['CompanyRutResponse']] = []
    branches: Optional[List['BranchResponse']] = []


# ============================================================================
# COMPANY RUT SCHEMAS
# ============================================================================

class CompanyRutCreate(BaseSchema):
    """
    Schema para agregar un RUT a una empresa.

    Example:
        data = CompanyRutCreate(
            rut="12345678-9",
            is_primary=True
        )
    """

    rut: str = Field(
        ...,
        min_length=9,
        max_length=12,
        pattern=r'^\d{1,8}-[\dkK]$',
        description="RUT en formato 12345678-9"
    )
    is_primary: bool = Field(
        default=False,
        description="Si es el RUT principal de la empresa"
    )

    @field_validator('rut')
    @classmethod
    def rut_format(cls, v: str) -> str:
        """Formatea el RUT correctamente."""
        return v.strip().upper()


class CompanyRutResponse(BaseResponse):
    """
    Schema para respuesta de RUT de empresa.

    Example:
        rut = CompanyRutResponse.model_validate(rut_orm)
        print(rut.rut)
    """

    company_id: int
    rut: str
    is_primary: bool


# ============================================================================
# BRANCH SCHEMAS
# ============================================================================

class BranchCreate(BaseSchema):
    """
    Schema para crear una sucursal.

    Example:
        data = BranchCreate(
            company_id=1,
            name="Sucursal Santiago",
            address="Av. Principal 123"
        )
    """

    company_id: int = Field(..., gt=0, description="ID de la empresa")
    name: str = Field(..., min_length=2, max_length=200, description="Nombre de la sucursal")
    address: Optional[str] = Field(None, max_length=500, description="Dirección de la sucursal")
    phone: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$', description="Teléfono")
    email: Optional[str] = Field(None, max_length=100, description="Email")
    city_id: Optional[int] = Field(None, gt=0, description="ID de la ciudad")

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("El nombre de la sucursal no puede estar vacío")
        return v.strip()

    @field_validator('email')
    @classmethod
    def email_lowercase(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return v.lower().strip()
        return v


class BranchUpdate(BaseSchema):
    """
    Schema para actualizar una sucursal.

    Todos los campos son opcionales.

    Example:
        data = BranchUpdate(name="Nuevo Nombre", phone="+56912345678")
    """

    name: Optional[str] = Field(None, min_length=2, max_length=200)
    address: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    email: Optional[str] = Field(None, max_length=100)
    city_id: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v and not v.strip():
            raise ValueError("El nombre de la sucursal no puede estar vacío")
        return v.strip() if v else v

    @field_validator('email')
    @classmethod
    def email_lowercase(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return v.lower().strip()
        return v


class BranchResponse(BaseResponse):
    """
    Schema para respuesta de sucursal.

    Example:
        branch = BranchResponse.model_validate(branch_orm)
        print(branch.name)
    """

    company_id: int
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    city_id: Optional[int] = None
    is_active: bool
