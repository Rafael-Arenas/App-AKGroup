from __future__ import annotations

"""
Schemas de Pydantic para Company, CompanyRut y Plant.

Define los schemas de validación para operaciones CRUD sobre empresas,
sus RUTs y plantas.
"""

from typing import Any
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
    phone: str | None = Field(
        None,
        pattern=r'^\+?[1-9]\d{1,14}$',
        description="Teléfono en formato E.164"
    )
    website: str | None = Field(
        None,
        max_length=200,
        description="Sitio web de la empresa"
    )
    company_type_id: int = Field(
        ...,
        gt=0,
        description="ID del tipo de empresa (customer, supplier, both)"
    )
    country_id: int | None = Field(
        None,
        gt=0,
        description="ID del país"
    )
    city_id: int | None = Field(
        None,
        gt=0,
        description="ID de la ciudad"
    )
    intracommunity_number: str | None = Field(
        None,
        max_length=50,
        description="Número intracomunitario (UE)"
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

    name: str | None = Field(None, min_length=2, max_length=200)
    trigram: str | None = Field(None, min_length=3, max_length=3)
    phone: str | None = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    website: str | None = Field(None, max_length=200)
    company_type_id: int | None = Field(None, gt=0)
    country_id: int | None = Field(None, gt=0)
    city_id: int | None = Field(None, gt=0)
    is_active: bool | None = None
    intracommunity_number: str | None = Field(None, max_length=50)

    @field_validator('trigram')
    @classmethod
    def trigram_uppercase(cls, v: str | None) -> str | None:
        if v:
            return v.upper().strip()
        return v

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: str | None) -> str | None:
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
    main_address: str | None = None
    phone: str | None = None
    website: str | None = None
    intracommunity_number: str | None = None
    company_type_id: int
    country_id: int | None = None
    city_id: int | None = None
    is_active: bool

    # Campos calculados para nombres de relaciones
    company_type: str | None = None
    country_name: str | None = None
    city_name: str | None = None

    # Relaciones opcionales (eager loading)
    ruts: list[CompanyRutResponse] | None = []
    plants: list[PlantResponse] | None = []

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
# PLANT SCHEMAS
# ============================================================================

class PlantCreate(BaseSchema):
    """
    Schema para crear una planta/sucursal.

    Example:
        data = PlantCreate(
            company_id=1,
            name="Planta Santiago",
            address="Av. Principal 123"
        )
    """

    company_id: int = Field(..., gt=0, description="ID de la empresa")
    name: str = Field(..., min_length=2, max_length=200, description="Nombre de la planta")
    address: str | None = Field(None, max_length=500, description="Dirección de la planta")
    phone: str | None = Field(None, pattern=r'^\+?[1-9]\d{1,14}$', description="Teléfono")
    email: str | None = Field(None, max_length=100, description="Email")
    city_id: int | None = Field(None, gt=0, description="ID de la ciudad")

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        """Asegura que el nombre no sea solo espacios."""
        if not v.strip():
            raise ValueError("El nombre de la planta no puede estar vacío")
        return v.strip()

    @field_validator('email')
    @classmethod
    def email_lowercase(cls, v: str | None) -> str | None:
        """Normaliza email a minúsculas."""
        if v:
            return v.lower().strip()
        return v


class PlantUpdate(BaseSchema):
    """
    Schema para actualizar una planta.

    Todos los campos son opcionales.

    Example:
        data = PlantUpdate(name="Nuevo Nombre", phone="+56912345678")
    """

    name: str | None = Field(None, min_length=2, max_length=200)
    address: str | None = Field(None, max_length=500)
    phone: str | None = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    email: str | None = Field(None, max_length=100)
    city_id: int | None = Field(None, gt=0)
    is_active: bool | None = None

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: str | None) -> str | None:
        if v and not v.strip():
            raise ValueError("El nombre de la planta no puede estar vacío")
        return v.strip() if v else v

    @field_validator('email')
    @classmethod
    def email_lowercase(cls, v: str | None) -> str | None:
        if v:
            return v.lower().strip()
        return v


class PlantResponse(BaseResponse):
    """
    Schema para respuesta de planta.

    Example:
        plant = PlantResponse.model_validate(plant_orm)
        print(plant.name)
    """

    company_id: int
    name: str
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    city_id: int | None = None
    is_active: bool
