"""
Lookup tables exports.

Este módulo exporta todos los modelos de tablas de catálogo/referencia.

Usage:
    from models.lookups import Country, Currency, Incoterm

    # Query lookups
    chile = session.query(Country).filter_by(iso_code_alpha2="CL").first()
    active_currencies = session.query(Currency).filter_by(is_active=True).all()
"""

from .lookups import (
    City,
    CompanyType,
    Country,
    Currency,
    FamilyType,
    Incoterm,
    Matter,
    OrderStatus,
    PaymentStatus,
    QuoteStatus,
    SalesType,
    Unit,
)

__all__ = [
    # Geographic
    "Country",
    "City",
    # Company
    "CompanyType",
    # Trade
    "Incoterm",
    "Currency",
    "Unit",
    # Product classification
    "FamilyType",
    "Matter",
    "SalesType",
    # Status
    "QuoteStatus",
    "OrderStatus",
    "PaymentStatus",
]
