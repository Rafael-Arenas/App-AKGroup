from sqlalchemy import CheckConstraint, Column, String, Text, Integer
from sqlalchemy.orm import relationship
from .base import LookupBase, ActiveLookupBase

class CompanyType(LookupBase):
    """
    Tipos de empresa (cliente, proveedor, etc.).
    """
    __tablename__ = "company_types"

    name = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        comment="Company type name",
    )

    # Relationships
    companies = relationship("Company", back_populates="company_type", lazy="select")

    __table_args__ = (
        CheckConstraint(
            "length(trim(name)) > 0",
            name="name_not_empty",
        ),
    )

class Incoterm(ActiveLookupBase):
    """
    International Commercial Terms (Incoterms 2020).
    """
    __tablename__ = "incoterms"

    code = Column(
        String(3),
        nullable=False,
        unique=True,
        index=True,
        comment="Incoterm code (e.g., EXW, FOB, CIF)",
    )

    __table_args__ = (
        CheckConstraint(
            "length(code) = 3",
            name="code_exact_length",
        ),
        CheckConstraint(
            "length(trim(name)) > 0",
            name="name_not_empty",
        ),
    )

class Currency(ActiveLookupBase):
    """
    Monedas (ISO 4217).
    """
    __tablename__ = "currencies"

    code = Column(
        String(3),
        nullable=False,
        unique=True,
        index=True,
        comment="ISO 4217 currency code (e.g., CLP, EUR, USD)",
    )

    symbol = Column(
        String(5),
        comment="Currency symbol (e.g., $, €, US$)",
    )

    __table_args__ = (
        CheckConstraint(
            "length(code) = 3",
            name="code_exact_length",
        ),
        CheckConstraint(
            "length(trim(name)) > 0",
            name="name_not_empty",
        ),
    )

class SalesType(LookupBase):
    """
    Tipos de venta (retail, wholesale, etc.).
    """
    __tablename__ = "sales_types"

    name = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        comment="Sales type name",
    )

    # Relationships
    products = relationship("Product", back_populates="sales_type", lazy="select")

    __table_args__ = (
        CheckConstraint(
            "length(trim(name)) > 0",
            name="name_not_empty",
        ),
    )

class PaymentType(ActiveLookupBase):
    """
    Tipos de pago (30 días, Contado, etc.).
    """
    __tablename__ = "payment_types"

    code = Column(
        String(20),
        nullable=False,
        unique=True,
        index=True,
        comment="Payment type code",
    )

    days = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Number of days for this payment type",
    )

    # Relationships
    payment_conditions = relationship("PaymentCondition", back_populates="payment_type", lazy="select")

    __table_args__ = (
        CheckConstraint(
            "length(trim(code)) > 0",
            name="payment_type_code_not_empty",
        ),
        CheckConstraint(
            "length(trim(name)) > 0",
            name="payment_type_name_not_empty",
        ),
        CheckConstraint(
            "days >= 0",
            name="payment_type_days_non_negative",
        ),
    )
