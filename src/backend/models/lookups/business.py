"""
Business-related lookup models.

This module contains lookup tables for business entities:
CompanyType, Incoterm, Currency, SalesType, PaymentType.
"""

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import ActiveLookupBase, LookupBase

if TYPE_CHECKING:
    from ..business.delivery import PaymentCondition
    from ..core.companies import Company
    from ..core.products import Product


class CompanyType(LookupBase):
    """
    Tipos de empresa (cliente, proveedor, etc.).

    Attributes:
        id: Primary key (inherited)
        name: Company type name
        description: Description (inherited)
    """

    __tablename__ = "company_types"

    name: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, comment="Company type name"
    )

    # Relationships
    companies: Mapped[list["Company"]] = relationship(
        "Company", back_populates="company_type", lazy="select"
    )

    __table_args__ = (CheckConstraint("length(trim(name)) > 0", name="name_not_empty"),)


class Incoterm(ActiveLookupBase):
    """
    International Commercial Terms (Incoterms 2020).

    Attributes:
        id: Primary key (inherited)
        name: Full Incoterm name (inherited)
        description: Description (inherited)
        code: Three-letter Incoterm code (e.g., EXW, FOB, CIF)
        is_active: Whether this incoterm is active (inherited)
    """

    __tablename__ = "incoterms"

    code: Mapped[str] = mapped_column(
        String(3),
        unique=True,
        index=True,
        comment="Incoterm code (e.g., EXW, FOB, CIF)",
    )

    __table_args__ = (
        CheckConstraint("length(code) = 3", name="code_exact_length"),
        CheckConstraint("length(trim(name)) > 0", name="name_not_empty"),
    )


class Currency(ActiveLookupBase):
    """
    Monedas (ISO 4217).

    Attributes:
        id: Primary key (inherited)
        name: Currency name (inherited)
        description: Description (inherited)
        code: ISO 4217 currency code (e.g., CLP, EUR, USD)
        symbol: Currency symbol (e.g., $, €, US$)
        is_active: Whether this currency is active (inherited)
    """

    __tablename__ = "currencies"

    code: Mapped[str] = mapped_column(
        String(3),
        unique=True,
        index=True,
        comment="ISO 4217 currency code (e.g., CLP, EUR, USD)",
    )
    symbol: Mapped[str | None] = mapped_column(
        String(5), comment="Currency symbol (e.g., $, €, US$)"
    )

    __table_args__ = (
        CheckConstraint("length(code) = 3", name="code_exact_length"),
        CheckConstraint("length(trim(name)) > 0", name="name_not_empty"),
    )


class SalesType(LookupBase):
    """
    Tipos de venta (retail, wholesale, etc.).

    Attributes:
        id: Primary key (inherited)
        name: Sales type name
        description: Description (inherited)
    """

    __tablename__ = "sales_types"

    name: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, comment="Sales type name"
    )

    # Relationships
    products: Mapped[list["Product"]] = relationship(
        "Product", back_populates="sales_type", lazy="select"
    )

    __table_args__ = (CheckConstraint("length(trim(name)) > 0", name="name_not_empty"),)


class PaymentType(ActiveLookupBase):
    """
    Tipos de pago (30 días, Contado, etc.).

    Attributes:
        id: Primary key (inherited)
        name: Payment type name (inherited)
        description: Description (inherited)
        code: Payment type code
        days: Number of days for this payment type
        is_active: Whether this payment type is active (inherited)
    """

    __tablename__ = "payment_types"

    code: Mapped[str] = mapped_column(
        String(20), unique=True, index=True, comment="Payment type code"
    )
    days: Mapped[int] = mapped_column(
        default=0, comment="Number of days for this payment type"
    )

    # Relationships
    payment_conditions: Mapped[list["PaymentCondition"]] = relationship(
        "PaymentCondition", back_populates="payment_type", lazy="select"
    )

    __table_args__ = (
        CheckConstraint("length(trim(code)) > 0", name="payment_type_code_not_empty"),
        CheckConstraint("length(trim(name)) > 0", name="payment_type_name_not_empty"),
        CheckConstraint("days >= 0", name="payment_type_days_non_negative"),
    )
