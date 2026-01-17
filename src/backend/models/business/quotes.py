"""
Quote models for AK Group business management system.

This module contains the Quote and QuoteProduct models for managing sales quotes.
Part of Phase 4: Business Models implementation.
"""

import pendulum
from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from ..base import ActiveMixin, AuditMixin, Base, TimestampMixin

if TYPE_CHECKING:
    from ..core.companies import Company, CompanyRut, Plant
    from ..core.contacts import Contact
    from ..core.products import Product
    from ..core.staff import Staff
    from ..lookups.business import Currency, Incoterm
    from ..lookups.status import QuoteStatus
    from .orders import Order


class Quote(Base, TimestampMixin, AuditMixin, ActiveMixin):
    """
    Sales quotes model.

    Manages customer quotes with products, pricing, and status tracking.
    Supports conversion to orders and maintains complete audit trail.
    """

    __tablename__ = "quotes"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True)

    # Quote identification
    quote_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        comment="Unique quote number (e.g., Q-2025-001)",
    )
    subject: Mapped[str] = mapped_column(
        String(200), comment="Quote subject or description"
    )
    revision: Mapped[str] = mapped_column(
        String(10), default="A", comment="Quote revision (A, B, C...)"
    )
    unit: Mapped[str | None] = mapped_column(String(20), comment="Unit (Unidad)")

    # Related entities (FK to core models)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"),
        index=True,
        comment="Customer company",
    )
    company_rut_id: Mapped[int | None] = mapped_column(
        ForeignKey("company_ruts.id", ondelete="RESTRICT"),
        index=True,
        comment="Specific customer RUT for this quote",
    )
    contact_id: Mapped[int | None] = mapped_column(
        ForeignKey("contacts.id", ondelete="SET NULL"),
        index=True,
        comment="Customer contact person",
    )
    plant_id: Mapped[int | None] = mapped_column(
        ForeignKey("plants.id", ondelete="SET NULL"), comment="Customer plant"
    )
    staff_id: Mapped[int] = mapped_column(
        ForeignKey("staff.id", ondelete="RESTRICT"),
        index=True,
        comment="Sales person responsible",
    )

    # Status (FK to lookup table)
    status_id: Mapped[int] = mapped_column(
        ForeignKey("quote_statuses.id", ondelete="RESTRICT"),
        index=True,
        comment="Quote status (draft, sent, accepted, rejected)",
    )

    # Important dates
    quote_date: Mapped[date] = mapped_column(
        Date, index=True, comment="Quote creation date"
    )
    valid_until: Mapped[date | None] = mapped_column(
        Date, comment="Quote expiration date"
    )
    shipping_date: Mapped[date | None] = mapped_column(
        Date, comment="Estimated shipping date"
    )

    # Shipping and currency
    incoterm_id: Mapped[int | None] = mapped_column(
        ForeignKey("incoterms.id", ondelete="SET NULL"),
        comment="Shipping terms (EXW, FOB, CIF, etc.)",
    )
    currency_id: Mapped[int] = mapped_column(
        ForeignKey("currencies.id", ondelete="RESTRICT"), comment="Quote currency"
    )
    exchange_rate: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 6), comment="Exchange rate at time of quote"
    )

    # Financial totals
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        default=Decimal("0.00"),
        comment="Sum of all line items before tax",
    )
    tax_percentage: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=Decimal("19.00"),
        comment="Tax percentage (e.g., 19 for IVA in Chile)",
    )
    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), comment="Calculated tax amount"
    )
    total: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), comment="Total amount including tax"
    )

    # Notes
    notes: Mapped[str | None] = mapped_column(Text, comment="Customer-visible notes")
    internal_notes: Mapped[str | None] = mapped_column(
        Text, comment="Internal notes only"
    )

    # Relationships
    company: Mapped["Company"] = relationship(
        "Company", back_populates="quotes", foreign_keys=[company_id]
    )
    company_rut: Mapped["CompanyRut | None"] = relationship(
        "CompanyRut", foreign_keys=[company_rut_id]
    )
    contact: Mapped["Contact | None"] = relationship(
        "Contact", foreign_keys=[contact_id]
    )
    plant: Mapped["Plant | None"] = relationship("Plant", foreign_keys=[plant_id])
    staff: Mapped["Staff"] = relationship("Staff", foreign_keys=[staff_id])
    status: Mapped["QuoteStatus"] = relationship("QuoteStatus")
    incoterm: Mapped["Incoterm | None"] = relationship("Incoterm")
    currency: Mapped["Currency"] = relationship("Currency")

    # Quote products (line items)
    products: Mapped[list["QuoteProduct"]] = relationship(
        "QuoteProduct",
        back_populates="quote",
        cascade="all, delete-orphan",
        order_by="QuoteProduct.sequence",
    )

    # Converted order (if quote was accepted)
    order: Mapped["Order | None"] = relationship(
        "Order", back_populates="quote", uselist=False
    )

    # Table constraints
    __table_args__ = (
        CheckConstraint("subtotal >= 0", name="ck_quote_subtotal_positive"),
        CheckConstraint("tax_amount >= 0", name="ck_quote_tax_positive"),
        CheckConstraint("total >= 0", name="ck_quote_total_positive"),
        CheckConstraint(
            "tax_percentage >= 0 AND tax_percentage <= 100",
            name="ck_quote_tax_percentage_valid",
        ),
        Index("ix_quote_company_date", "company_id", "quote_date"),
        Index("ix_quote_status_date", "status_id", "quote_date"),
    )

    # Validation
    @validates("quote_number")
    def validate_quote_number(self, key: str, value: str) -> str:
        """Validate quote number format."""
        if not value or not value.strip():
            raise ValueError("Quote number cannot be empty")
        return value.strip().upper()

    @validates("revision")
    def validate_revision(self, key: str, value: str) -> str:
        """Validate revision format."""
        if not value or not value.strip():
            raise ValueError("Revision cannot be empty")
        return value.strip().upper()

    @validates("tax_percentage")
    def validate_tax_percentage(self, key: str, value: Decimal) -> Decimal:
        """Validate tax percentage is within valid range."""
        if value < 0 or value > 100:
            raise ValueError(f"Tax percentage must be between 0 and 100, got {value}")
        return value

    # Business methods
    def calculate_totals(self) -> None:
        """Calculate subtotal, tax, and total from quote products."""
        self.subtotal = sum(
            (item.subtotal or Decimal("0.00")) for item in self.products
        )
        self.tax_amount = (
            self.subtotal * self.tax_percentage / Decimal("100")
        ).quantize(Decimal("0.01"))
        self.total = self.subtotal + self.tax_amount

    @property
    def is_expired(self) -> bool:
        """Check if quote has expired."""
        if self.valid_until is None:
            return False
        return pendulum.today("UTC").date() > self.valid_until

    @property
    def days_until_expiry(self) -> int | None:
        """Calculate days until quote expires."""
        if self.valid_until is None:
            return None
        delta = self.valid_until - pendulum.today("UTC").date()
        return delta.days

    def __repr__(self) -> str:
        """String representation."""
        return f"<Quote(id={self.id}, number='{self.quote_number}', revision='{self.revision}', total={self.total})>"


class QuoteProduct(Base, TimestampMixin):
    """
    Products/line items in a quote.

    Junction table between Quote and Product with quantity, pricing,
    and discount information.
    """

    __tablename__ = "quote_products"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True)

    # Foreign keys
    quote_id: Mapped[int] = mapped_column(
        ForeignKey("quotes.id", ondelete="CASCADE"),
        index=True,
        comment="Parent quote",
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"),
        index=True,
        comment="Product being quoted",
    )

    # Line item details
    sequence: Mapped[int] = mapped_column(
        default=1, comment="Display order of line items"
    )

    # Quantities and pricing
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 3), comment="Quantity being quoted"
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), comment="Price per unit (snapshot at quote time)"
    )

    # Discounts
    discount_percentage: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=Decimal("0.00"), comment="Discount percentage for this line"
    )
    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), comment="Calculated discount amount"
    )

    # Calculated total
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), comment="Line total (quantity * unit_price - discount)"
    )

    # Notes
    notes: Mapped[str | None] = mapped_column(Text, comment="Line item specific notes")

    # Relationships
    quote: Mapped["Quote"] = relationship("Quote", back_populates="products")
    product: Mapped["Product"] = relationship("Product")

    # Table constraints
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_quote_product_quantity_positive"),
        CheckConstraint("unit_price >= 0", name="ck_quote_product_price_positive"),
        CheckConstraint(
            "discount_percentage >= 0 AND discount_percentage <= 100",
            name="ck_quote_product_discount_percentage_valid",
        ),
        CheckConstraint(
            "discount_amount >= 0", name="ck_quote_product_discount_positive"
        ),
        CheckConstraint("subtotal >= 0", name="ck_quote_product_subtotal_positive"),
        Index("ix_quote_product_quote", "quote_id", "sequence"),
    )

    # Validation
    @validates("quantity")
    def validate_quantity(self, key: str, value: Decimal) -> Decimal:
        """Validate quantity is positive."""
        if value <= 0:
            raise ValueError(f"Quantity must be positive, got {value}")
        return value

    @validates("unit_price")
    def validate_unit_price(self, key: str, value: Decimal) -> Decimal:
        """Validate unit price is non-negative."""
        if value < 0:
            raise ValueError(f"Unit price cannot be negative, got {value}")
        return value

    @validates("discount_percentage")
    def validate_discount_percentage(self, key: str, value: Decimal) -> Decimal:
        """Validate discount percentage is within valid range."""
        if value < 0 or value > 100:
            raise ValueError(
                f"Discount percentage must be between 0 and 100, got {value}"
            )
        return value

    # Business methods
    def calculate_subtotal(self) -> None:
        """Calculate line item subtotal."""
        line_total = self.quantity * self.unit_price

        if self.discount_percentage > 0:
            self.discount_amount = (
                line_total * self.discount_percentage / Decimal("100")
            ).quantize(Decimal("0.01"))
        else:
            self.discount_amount = Decimal("0.00")

        self.subtotal = (line_total - self.discount_amount).quantize(Decimal("0.01"))

    @property
    def effective_unit_price(self) -> Decimal:
        """Calculate effective unit price after discount."""
        if self.quantity == 0:
            return Decimal("0.00")
        return (self.subtotal / self.quantity).quantize(Decimal("0.01"))

    def __repr__(self) -> str:
        """String representation."""
        return f"<QuoteProduct(id={self.id}, quote_id={self.quote_id}, product_id={self.product_id}, qty={self.quantity}, subtotal={self.subtotal})>"
