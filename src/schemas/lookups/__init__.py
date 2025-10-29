"""
Lookup schemas package.

Provides Pydantic validation schemas for all 12 lookup/reference tables.
"""

from src.schemas.lookups.lookup import (
    CountryCreate,
    CountryUpdate,
    CountryResponse,
    CityCreate,
    CityUpdate,
    CityResponse,
    CompanyTypeCreate,
    CompanyTypeUpdate,
    CompanyTypeResponse,
    IncotermCreate,
    IncotermUpdate,
    IncotermResponse,
    CurrencyCreate,
    CurrencyUpdate,
    CurrencyResponse,
    UnitCreate,
    UnitUpdate,
    UnitResponse,
    FamilyTypeCreate,
    FamilyTypeUpdate,
    FamilyTypeResponse,
    MatterCreate,
    MatterUpdate,
    MatterResponse,
    SalesTypeCreate,
    SalesTypeUpdate,
    SalesTypeResponse,
    QuoteStatusCreate,
    QuoteStatusUpdate,
    QuoteStatusResponse,
    OrderStatusCreate,
    OrderStatusUpdate,
    OrderStatusResponse,
    PaymentStatusCreate,
    PaymentStatusUpdate,
    PaymentStatusResponse,
)

__all__ = [
    # Country schemas
    "CountryCreate",
    "CountryUpdate",
    "CountryResponse",
    # City schemas
    "CityCreate",
    "CityUpdate",
    "CityResponse",
    # CompanyType schemas
    "CompanyTypeCreate",
    "CompanyTypeUpdate",
    "CompanyTypeResponse",
    # Incoterm schemas
    "IncotermCreate",
    "IncotermUpdate",
    "IncotermResponse",
    # Currency schemas
    "CurrencyCreate",
    "CurrencyUpdate",
    "CurrencyResponse",
    # Unit schemas
    "UnitCreate",
    "UnitUpdate",
    "UnitResponse",
    # FamilyType schemas
    "FamilyTypeCreate",
    "FamilyTypeUpdate",
    "FamilyTypeResponse",
    # Matter schemas
    "MatterCreate",
    "MatterUpdate",
    "MatterResponse",
    # SalesType schemas
    "SalesTypeCreate",
    "SalesTypeUpdate",
    "SalesTypeResponse",
    # QuoteStatus schemas
    "QuoteStatusCreate",
    "QuoteStatusUpdate",
    "QuoteStatusResponse",
    # OrderStatus schemas
    "OrderStatusCreate",
    "OrderStatusUpdate",
    "OrderStatusResponse",
    # PaymentStatus schemas
    "PaymentStatusCreate",
    "PaymentStatusUpdate",
    "PaymentStatusResponse",
]
