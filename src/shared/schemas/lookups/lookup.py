"""
Pydantic schemas for lookup/reference tables.

Provides validation schemas for all 12 lookup tables:
- Country
- City
- CompanyType
- Incoterm
- Currency
- Unit
- FamilyType
- Matter
- SalesType
- QuoteStatus
- OrderStatus
- PaymentStatus
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


# ========== COUNTRY SCHEMAS ==========
class CountryBase(BaseModel):
    """Base schema for Country."""

    name: str = Field(..., min_length=2, max_length=100, description="Country name")
    iso_code_alpha2: Optional[str] = Field(
        None, min_length=2, max_length=2, description="ISO 3166-1 alpha-2 code"
    )
    iso_code_alpha3: Optional[str] = Field(
        None, min_length=3, max_length=3, description="ISO 3166-1 alpha-3 code"
    )


class CountryCreate(CountryBase):
    """Schema for creating Country."""

    @field_validator("iso_code_alpha2", "iso_code_alpha3")
    @classmethod
    def uppercase_codes(cls, v: Optional[str]) -> Optional[str]:
        """Convert ISO codes to uppercase."""
        return v.upper() if v else None


class CountryUpdate(BaseModel):
    """Schema for updating Country."""

    name: Optional[str] = Field(None, min_length=2, max_length=100)
    iso_code_alpha2: Optional[str] = Field(None, min_length=2, max_length=2)
    iso_code_alpha3: Optional[str] = Field(None, min_length=3, max_length=3)

    @field_validator("iso_code_alpha2", "iso_code_alpha3")
    @classmethod
    def uppercase_codes(cls, v: Optional[str]) -> Optional[str]:
        """Convert ISO codes to uppercase."""
        return v.upper() if v else None


class CountryResponse(CountryBase):
    """Schema for Country response."""

    id: int

    model_config = ConfigDict(from_attributes=True)


# ========== CITY SCHEMAS ==========
class CityBase(BaseModel):
    """Base schema for City."""

    name: str = Field(..., min_length=2, max_length=100, description="City name")
    country_id: int = Field(..., description="ID of the country")


class CityCreate(CityBase):
    """Schema for creating City."""

    pass


class CityUpdate(BaseModel):
    """Schema for updating City."""

    name: Optional[str] = Field(None, min_length=2, max_length=100)
    country_id: Optional[int] = None


class CityResponse(CityBase):
    """Schema for City response."""

    id: int

    model_config = ConfigDict(from_attributes=True)


# ========== COMPANY TYPE SCHEMAS ==========
class CompanyTypeBase(BaseModel):
    """Base schema for CompanyType."""

    name: str = Field(..., min_length=2, max_length=100, description="Company type name")
    description: Optional[str] = Field(None, max_length=200, description="Description")


class CompanyTypeCreate(CompanyTypeBase):
    """Schema for creating CompanyType."""

    pass


class CompanyTypeUpdate(BaseModel):
    """Schema for updating CompanyType."""

    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=200)


class CompanyTypeResponse(CompanyTypeBase):
    """Schema for CompanyType response."""

    id: int

    model_config = ConfigDict(from_attributes=True)


# ========== INCOTERM SCHEMAS ==========
class IncotermBase(BaseModel):
    """Base schema for Incoterm."""

    code: str = Field(..., min_length=3, max_length=3, description="3-letter Incoterm code")
    name: str = Field(..., min_length=2, max_length=100, description="Full name")
    description: Optional[str] = Field(None, max_length=500, description="Description")


class IncotermCreate(IncotermBase):
    """Schema for creating Incoterm."""

    @field_validator("code")
    @classmethod
    def uppercase_code(cls, v: str) -> str:
        """Convert Incoterm code to uppercase."""
        return v.upper()


class IncotermUpdate(BaseModel):
    """Schema for updating Incoterm."""

    code: Optional[str] = Field(None, min_length=3, max_length=3)
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

    @field_validator("code")
    @classmethod
    def uppercase_code(cls, v: Optional[str]) -> Optional[str]:
        """Convert Incoterm code to uppercase."""
        return v.upper() if v else None


class IncotermResponse(IncotermBase):
    """Schema for Incoterm response."""

    id: int

    model_config = ConfigDict(from_attributes=True)


# ========== CURRENCY SCHEMAS ==========
class CurrencyBase(BaseModel):
    """Base schema for Currency."""

    code: str = Field(..., min_length=3, max_length=3, description="ISO 4217 currency code")
    name: str = Field(..., min_length=2, max_length=100, description="Currency name")
    symbol: Optional[str] = Field(None, max_length=10, description="Currency symbol")


class CurrencyCreate(CurrencyBase):
    """Schema for creating Currency."""

    @field_validator("code")
    @classmethod
    def uppercase_code(cls, v: str) -> str:
        """Convert currency code to uppercase."""
        return v.upper()


class CurrencyUpdate(BaseModel):
    """Schema for updating Currency."""

    code: Optional[str] = Field(None, min_length=3, max_length=3)
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    symbol: Optional[str] = Field(None, max_length=10)

    @field_validator("code")
    @classmethod
    def uppercase_code(cls, v: Optional[str]) -> Optional[str]:
        """Convert currency code to uppercase."""
        return v.upper() if v else None


class CurrencyResponse(CurrencyBase):
    """Schema for Currency response."""

    id: int

    model_config = ConfigDict(from_attributes=True)


# ========== UNIT SCHEMAS ==========
class UnitBase(BaseModel):
    """Base schema for Unit."""

    code: str = Field(..., min_length=1, max_length=10, description="Unit code/abbreviation")
    name: str = Field(..., min_length=2, max_length=100, description="Unit name")
    description: Optional[str] = Field(None, max_length=200, description="Description")


class UnitCreate(UnitBase):
    """Schema for creating Unit."""

    pass


class UnitUpdate(BaseModel):
    """Schema for updating Unit."""

    code: Optional[str] = Field(None, min_length=1, max_length=10)
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=200)


class UnitResponse(UnitBase):
    """Schema for Unit response."""

    id: int

    model_config = ConfigDict(from_attributes=True)


# ========== FAMILY TYPE SCHEMAS ==========
class FamilyTypeBase(BaseModel):
    """Base schema for FamilyType."""

    name: str = Field(..., min_length=2, max_length=100, description="Family type name")
    description: Optional[str] = Field(None, max_length=200, description="Description")


class FamilyTypeCreate(FamilyTypeBase):
    """Schema for creating FamilyType."""

    pass


class FamilyTypeUpdate(BaseModel):
    """Schema for updating FamilyType."""

    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=200)


class FamilyTypeResponse(FamilyTypeBase):
    """Schema for FamilyType response."""

    id: int

    model_config = ConfigDict(from_attributes=True)


# ========== MATTER SCHEMAS ==========
class MatterBase(BaseModel):
    """Base schema for Matter."""

    name: str = Field(..., min_length=2, max_length=100, description="Matter/material name")
    description: Optional[str] = Field(None, max_length=200, description="Description")


class MatterCreate(MatterBase):
    """Schema for creating Matter."""

    pass


class MatterUpdate(BaseModel):
    """Schema for updating Matter."""

    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=200)


class MatterResponse(MatterBase):
    """Schema for Matter response."""

    id: int

    model_config = ConfigDict(from_attributes=True)


# ========== SALES TYPE SCHEMAS ==========
class SalesTypeBase(BaseModel):
    """Base schema for SalesType."""

    name: str = Field(..., min_length=2, max_length=100, description="Sales type name")
    description: Optional[str] = Field(None, max_length=200, description="Description")


class SalesTypeCreate(SalesTypeBase):
    """Schema for creating SalesType."""

    pass


class SalesTypeUpdate(BaseModel):
    """Schema for updating SalesType."""

    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=200)


class SalesTypeResponse(SalesTypeBase):
    """Schema for SalesType response."""

    id: int

    model_config = ConfigDict(from_attributes=True)


# ========== QUOTE STATUS SCHEMAS ==========
class QuoteStatusBase(BaseModel):
    """Base schema for QuoteStatus."""

    name: str = Field(..., min_length=2, max_length=50, description="Quote status name")
    description: Optional[str] = Field(None, max_length=200, description="Description")


class QuoteStatusCreate(QuoteStatusBase):
    """Schema for creating QuoteStatus."""

    pass


class QuoteStatusUpdate(BaseModel):
    """Schema for updating QuoteStatus."""

    name: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=200)


class QuoteStatusResponse(QuoteStatusBase):
    """Schema for QuoteStatus response."""

    id: int

    model_config = ConfigDict(from_attributes=True)


# ========== ORDER STATUS SCHEMAS ==========
class OrderStatusBase(BaseModel):
    """Base schema for OrderStatus."""

    name: str = Field(..., min_length=2, max_length=50, description="Order status name")
    description: Optional[str] = Field(None, max_length=200, description="Description")


class OrderStatusCreate(OrderStatusBase):
    """Schema for creating OrderStatus."""

    pass


class OrderStatusUpdate(BaseModel):
    """Schema for updating OrderStatus."""

    name: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=200)


class OrderStatusResponse(OrderStatusBase):
    """Schema for OrderStatus response."""

    id: int

    model_config = ConfigDict(from_attributes=True)


# ========== PAYMENT STATUS SCHEMAS ==========
class PaymentStatusBase(BaseModel):
    """Base schema for PaymentStatus."""

    name: str = Field(..., min_length=2, max_length=50, description="Payment status name")
    description: Optional[str] = Field(None, max_length=200, description="Description")


class PaymentStatusCreate(PaymentStatusBase):
    """Schema for creating PaymentStatus."""

    pass


class PaymentStatusUpdate(BaseModel):
    """Schema for updating PaymentStatus."""

    name: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = Field(None, max_length=200)


class PaymentStatusResponse(PaymentStatusBase):
    """Schema for PaymentStatus response."""

    id: int

    model_config = ConfigDict(from_attributes=True)
