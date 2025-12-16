"""
Quote models for AK Group business management system.

This module contains the Quote and QuoteProduct models for managing sales quotes.
Part of Phase 4: Business Models implementation.
"""

from datetime import date
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import (
    Column,
    Integer,
    String,
    DECIMAL,
    ForeignKey,
    Date,
    Text,
    Index,
    CheckConstraint,
)
from sqlalchemy.orm import relationship, validates

from ..base import Base, TimestampMixin, AuditMixin, ActiveMixin


class Quote(Base, TimestampMixin, AuditMixin, ActiveMixin):
    """
    Sales quotes model.

    Manages customer quotes with products, pricing, and status tracking.
    Supports conversion to orders and maintains complete audit trail.

    Attributes:
        id: Primary key
        quote_number: Unique quote identifier (e.g., "Q-2025-001")
        subject: Quote subject/title
        unit: Unit of measure (e.g., pcs, kg)
        revision: Quote revision number (e.g., "A", "B", "C")
        company_id: Foreign key to Company (customer)
        company_rut_id: Foreign key to CompanyRut (specific customer RUT)
        contact_id: Foreign key to Contact (customer contact person)
        plant_id: Foreign key to Plant (customer plant)
        staff_id: Foreign key to Staff (sales person)
        status_id: Foreign key to QuoteStatus
        quote_date: Date quote was created
        valid_until: Quote expiration date
        shipping_date: Estimated shipping date
        incoterm_id: Foreign key to Incoterm (shipping terms)
        currency_id: Foreign key to Currency
        exchange_rate: Exchange rate at time of quote
        subtotal: Sum of all line items before tax
        tax_percentage: Tax rate percentage (e.g., 19 for 19%)
        tax_amount: Calculated tax amount
        total: Total amount including tax
        notes: Additional notes/comments
        internal_notes: Internal notes (not visible to customer)
    """

    __tablename__ = "quotes"

    # Primary key
    id = Column(Integer, primary_key=True)

    # Quote identification
    quote_number = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        comment="Unique quote number (e.g., Q-2025-001)",
    )
    subject = Column(
        String(200), nullable=False, comment="Quote subject or description"
    )
    revision = Column(
        String(10), nullable=False, default="A", comment="Quote revision (A, B, C...)"
    )

    unit = Column(
        String(20),
        nullable=True,
        comment="Unit (Unidad)",
    )

    # Related entities (FK to core models)
    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Customer company",
    )
    company_rut_id = Column(
        Integer,
        ForeignKey("company_ruts.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
        comment="Specific customer RUT for this quote",
    )
    contact_id = Column(
        Integer,
        ForeignKey("contacts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Customer contact person",
    )
    plant_id = Column(
        Integer,
        ForeignKey("plants.id", ondelete="SET NULL"),
        nullable=True,
        comment="Customer plant",
    )
    staff_id = Column(
        Integer,
        ForeignKey("staff.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Sales person responsible",
    )

    # Status (FK to lookup table)
    status_id = Column(
        Integer,
        ForeignKey("quote_statuses.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Quote status (draft, sent, accepted, rejected)",
    )

    # Important dates
    quote_date = Column(Date, nullable=False, index=True, comment="Quote creation date")
    valid_until = Column(Date, nullable=True, comment="Quote expiration date")
    shipping_date = Column(Date, nullable=True, comment="Estimated shipping date")

    # Shipping and currency
    incoterm_id = Column(
        Integer,
        ForeignKey("incoterms.id", ondelete="SET NULL"),
        nullable=True,
        comment="Shipping terms (EXW, FOB, CIF, etc.)",
    )
    currency_id = Column(
        Integer,
        ForeignKey("currencies.id", ondelete="RESTRICT"),
        nullable=False,
        comment="Quote currency",
    )
    exchange_rate = Column(
        DECIMAL(12, 6),
        nullable=True,
        comment="Exchange rate at time of quote",
    )

    # Financial totals (calculated from QuoteProduct items)
    subtotal = Column(
        DECIMAL(15, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Sum of all line items before tax",
    )
    tax_percentage = Column(
        DECIMAL(5, 2),
        nullable=False,
        default=Decimal("19.00"),
        comment="Tax percentage (e.g., 19 for IVA in Chile)",
    )
    tax_amount = Column(
        DECIMAL(15, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Calculated tax amount",
    )
    total = Column(
        DECIMAL(15, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Total amount including tax",
    )

    # Notes
    notes = Column(Text, nullable=True, comment="Customer-visible notes")
    internal_notes = Column(Text, nullable=True, comment="Internal notes only")

    # Relationships
    # NOTE: These will work once core models are implemented
    company = relationship("Company", back_populates="quotes", foreign_keys=[company_id])
    company_rut = relationship("CompanyRut", foreign_keys=[company_rut_id])
    contact = relationship("Contact", foreign_keys=[contact_id])
    plant = relationship("Plant", foreign_keys=[plant_id])
    staff = relationship("Staff", foreign_keys=[staff_id])
    status = relationship("QuoteStatus")
    incoterm = relationship("Incoterm")
    currency = relationship("Currency")

    # Quote products (line items)
    products = relationship(
        "QuoteProduct",
        back_populates="quote",
        cascade="all, delete-orphan",
        order_by="QuoteProduct.sequence",
    )

    # Converted order (if quote was accepted)
    order = relationship("Order", back_populates="quote", uselist=False)

    # Polymorphic notes
    # notes_collection = relationship(
    #     "Note",
    #     primaryjoin="and_(Note.entity_type=='quote', foreign(Note.entity_id)==Quote.id)",
    #     viewonly=True
    # )

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
        """
        Calculate subtotal, tax, and total from quote products.

        This should be called after adding/modifying quote products.
        """
        self.subtotal = sum(
            (item.subtotal or Decimal("0.00")) for item in self.products
        )
        self.tax_amount = (self.subtotal * self.tax_percentage / Decimal("100")).quantize(
            Decimal("0.01")
        )
        self.total = self.subtotal + self.tax_amount

    @property
    def is_expired(self) -> bool:
        """Check if quote has expired."""
        if self.valid_until is None:
            return False
        return date.today() > self.valid_until

    @property
    def days_until_expiry(self) -> Optional[int]:
        """Calculate days until quote expires."""
        if self.valid_until is None:
            return None
        delta = self.valid_until - date.today()
        return delta.days

    def __repr__(self) -> str:
        """String representation."""
        return f"<Quote(id={self.id}, number='{self.quote_number}', revision='{self.revision}', total={self.total})>"


class QuoteProduct(Base, TimestampMixin):
    """
    Products/line items in a quote.

    Junction table between Quote and Product with quantity, pricing,
    and discount information.

    Attributes:
        id: Primary key
        quote_id: Foreign key to Quote
        product_id: Foreign key to Product
        sequence: Display order (for sorting line items)
        quantity: Quantity ordered
        unit_price: Price per unit (may differ from product.price)
        discount_percentage: Discount applied to this line
        discount_amount: Calculated discount amount
        subtotal: Line total (quantity * unit_price - discount)
        notes: Line item specific notes
    """

    __tablename__ = "quote_products"

    # Primary key
    id = Column(Integer, primary_key=True)

    # Foreign keys
    quote_id = Column(
        Integer,
        ForeignKey("quotes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Parent quote",
    )
    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Product being quoted",
    )

    # Line item details
    sequence = Column(
        Integer, nullable=False, default=1, comment="Display order of line items"
    )

    # Quantities and pricing
    quantity = Column(
        DECIMAL(10, 3),
        nullable=False,
        comment="Quantity being quoted",
    )
    unit_price = Column(
        DECIMAL(15, 2),
        nullable=False,
        comment="Price per unit (snapshot at quote time)",
    )

    # Discounts
    discount_percentage = Column(
        DECIMAL(5, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Discount percentage for this line",
    )
    discount_amount = Column(
        DECIMAL(15, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Calculated discount amount",
    )

    # Calculated total
    subtotal = Column(
        DECIMAL(15, 2),
        nullable=False,
        comment="Line total (quantity * unit_price - discount)",
    )

    # Notes
    notes = Column(Text, nullable=True, comment="Line item specific notes")

    # Relationships
    quote = relationship("Quote", back_populates="products")
    product = relationship("Product")

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
        """
        Calculate line item subtotal.

        Formula: (quantity * unit_price) - discount_amount
        Or: (quantity * unit_price) * (1 - discount_percentage/100)
        """
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
