"""
Schemas de Pydantic para Company, CompanyRut y Branch.

Define los schemas de validación para operaciones CRUD sobre empresas,
sus RUTs y sucursales.
"""

from typing import Optional, List, Any
from pydantic import Field, field_validator, field_serializer, model_validator, HttpUrl
from sqlalchemy import inspect

from src.shared.schemas.base import BaseSchema, BaseResponse


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
    city_id: Optional[int] = Field(
        None,
        gt=0,
        description="ID de la ciudad"
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
    city_id: Optional[int] = Field(None, gt=0)
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
    main_address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    intracommunity_number: Optional[str] = None
    company_type_id: int
    country_id: Optional[int] = None
    city_id: Optional[int] = None
    is_active: bool

    # Campos calculados para nombres de relaciones
    company_type: Optional[str] = None
    country_name: Optional[str] = None
    city_name: Optional[str] = None

    # Relaciones opcionales (eager loading)
    ruts: Optional[List['CompanyRutResponse']] = []
    branches: Optional[List['BranchResponse']] = []

    @model_validator(mode='before')
    @classmethod
    def extract_relationship_names(cls, data: Any) -> Any:
        """Extrae nombres de objetos de relación antes de la validación."""
        if isinstance(data, dict):
            return data

        # Si es un objeto ORM, convertir a diccionario sin modificar el objeto
        if hasattr(data, '__dict__'):
            # Crear un nuevo diccionario con los datos
            result = {}

            # Usar SQLAlchemy inspect para obtener solo columnas, no relaciones
            mapper = inspect(data.__class__)

            # Copiar valores de columnas (no relaciones)
            for column in mapper.columns:
                result[column.name] = getattr(data, column.name, None)

            # Extraer company_type name (de la relación)
            if hasattr(data, 'company_type') and data.company_type is not None:
                if not isinstance(data.company_type, str):
                    result['company_type'] = getattr(data.company_type, 'name', None)

            # Extraer country name (de la relación)
            if hasattr(data, 'country') and data.country is not None:
                result['country_name'] = getattr(data.country, 'name', None)

            # Extraer city name (de la relación)
            if hasattr(data, 'city') and data.city is not None:
                result['city_name'] = getattr(data.city, 'name', None)

            return result

        return data

    @field_serializer('company_type')
    def serialize_company_type(self, company_type: Any, _info):
        """Serializa el objeto CompanyType a string (nombre)."""
        if company_type is None:
            return None
        if isinstance(company_type, str):
            return company_type
        # Si es un objeto ORM, extraer el nombre
        return getattr(company_type, 'name', None)

    @field_serializer('country_name')
    def serialize_country_name(self, country_name: Any, _info):
        """Serializa el objeto Country a string (nombre)."""
        if country_name is None:
            return None
        if isinstance(country_name, str):
            return country_name
        # Si es un objeto ORM, extraer el nombre
        return getattr(country_name, 'name', None)

    @field_serializer('city_name')
    def serialize_city_name(self, city_name: Any, _info):
        """Serializa el objeto City a string (nombre)."""
        if city_name is None:
            return None
        if isinstance(city_name, str):
            return city_name
        # Si es un objeto ORM, extraer el nombre
        return getattr(city_name, 'name', None)


# ============================================================================
# COMPANY RUT SCHEMAS
# ============================================================================

class CompanyRutCreate(BaseSchema):
    """
    Schema para agregar un RUT a una empresa.

    Example:
        data = CompanyRutCreate(
            rut="12345678-9",
            is_main=True
        )
    """

    rut: str = Field(
        ...,
        min_length=9,
        max_length=12,
        pattern=r'^\d{1,8}-[\dkK]$',
        description="RUT en formato 12345678-9"
    )
    is_main: bool = Field(
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
    is_main: bool


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
