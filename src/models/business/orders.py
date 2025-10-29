"""
Order models for AK Group business management system.

This module contains the Order model for managing purchase and sales orders.
Orders can be created from accepted quotes or standalone.
Part of Phase 4: Business Models implementation.
"""

from datetime import date
from decimal import Decimal
from typing import Optional

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
    Boolean,
)
from sqlalchemy.orm import relationship, validates

# Import base infrastructure (Phases 1-3 are complete)
from src.models.base import Base, TimestampMixin, AuditMixin, ActiveMixin


class Order(Base, TimestampMixin, AuditMixin, ActiveMixin):
    """
    Purchase and sales orders model.

    Manages customer orders (purchase orders from customer perspective,
    sales orders from company perspective). Can be created from an
    accepted quote or created standalone.

    Attributes:
        id: Primary key
        order_number: Unique order identifier (e.g., "O-2025-001")
        revision: Order revision number (e.g., "A", "B", "C")
        order_type: Type of order ('sales' or 'purchase')
        quote_id: Foreign key to Quote (if created from quote)
        customer_quote_number: Customer's quote/reference number
        project_number: Project number/identifier
        company_id: Foreign key to Company (customer/supplier)
        contact_id: Foreign key to Contact
        branch_id: Foreign key to Branch
        shipping_address_id: Foreign key to Address (shipping address)
        billing_address_id: Foreign key to Address (billing address)
        staff_id: Foreign key to Staff (order manager)
        status_id: Foreign key to OrderStatus
        payment_status_id: Foreign key to PaymentStatus
        order_date: Date order was placed
        required_date: Date customer needs the order
        promised_date: Date we promised delivery
        shipped_date: Actual shipping date
        completed_date: Date order was completed
        incoterm_id: Foreign key to Incoterm
        currency_id: Foreign key to Currency
        exchange_rate: Exchange rate at time of order
        subtotal: Total before tax
        tax_percentage: Tax rate percentage
        tax_amount: Calculated tax amount
        shipping_cost: Shipping/freight cost
        other_costs: Other additional costs
        total: Grand total
        payment_terms: Payment terms description
        is_export: Whether this is an export order
        notes: Customer-visible notes
        internal_notes: Internal notes only
    """

    __tablename__ = "orders"

    # Primary key
    id = Column(Integer, primary_key=True)

    # Order identification
    order_number = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        comment="Unique order number (e.g., O-2025-001)",
    )
    revision = Column(
        String(10),
        nullable=False,
        default="A",
        comment="Order revision (A, B, C...)",
    )
    order_type = Column(
        String(20),
        nullable=False,
        default="sales",
        comment="Order type: 'sales' or 'purchase'",
    )

    # Reference to quote (if order created from quote)
    quote_id = Column(
        Integer,
        ForeignKey("quotes.id", ondelete="SET NULL"),
        nullable=True,
        unique=True,
        index=True,
        comment="Source quote if order created from accepted quote",
    )

    # Customer reference numbers
    customer_quote_number = Column(
        String(100),
        nullable=True,
        index=True,
        comment="Customer's quote/reference number",
    )
    project_number = Column(
        String(100),
        nullable=True,
        index=True,
        comment="Project number/identifier",
    )

    # Related entities (FK to core models)
    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Customer or supplier company",
    )
    contact_id = Column(
        Integer,
        ForeignKey("contacts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Contact person",
    )
    branch_id = Column(
        Integer,
        ForeignKey("branches.id", ondelete="SET NULL"),
        nullable=True,
        comment="Company branch",
    )

    # Address information
    shipping_address_id = Column(
        Integer,
        ForeignKey("addresses.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Shipping/delivery address",
    )
    billing_address_id = Column(
        Integer,
        ForeignKey("addresses.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Billing/invoice address",
    )

    staff_id = Column(
        Integer,
        ForeignKey("staff.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Staff member managing this order",
    )

    # Status (FK to lookup tables)
    status_id = Column(
        Integer,
        ForeignKey("order_statuses.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Order status (pending, confirmed, processing, shipped, completed, cancelled)",
    )
    payment_status_id = Column(
        Integer,
        ForeignKey("payment_statuses.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Payment status (unpaid, partial, paid, overdue)",
    )

    # Important dates
    order_date = Column(
        Date, nullable=False, index=True, comment="Date order was placed"
    )
    required_date = Column(
        Date, nullable=True, comment="Date customer requires delivery"
    )
    promised_date = Column(
        Date, nullable=True, comment="Date we promised to deliver"
    )
    shipped_date = Column(Date, nullable=True, comment="Actual shipping date")
    completed_date = Column(Date, nullable=True, comment="Date order was completed")

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
        comment="Order currency",
    )
    exchange_rate = Column(
        DECIMAL(12, 6),
        nullable=True,
        comment="Exchange rate at time of order",
    )

    # Financial information
    subtotal = Column(
        DECIMAL(15, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Total before tax",
    )
    tax_percentage = Column(
        DECIMAL(5, 2),
        nullable=False,
        default=Decimal("19.00"),
        comment="Tax percentage",
    )
    tax_amount = Column(
        DECIMAL(15, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Calculated tax amount",
    )
    shipping_cost = Column(
        DECIMAL(15, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Shipping/freight cost",
    )
    other_costs = Column(
        DECIMAL(15, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Other additional costs",
    )
    total = Column(
        DECIMAL(15, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Grand total",
    )

    # Payment and export info
    payment_terms = Column(
        String(200), nullable=True, comment="Payment terms description"
    )
    is_export = Column(
        Boolean, nullable=False, default=False, index=True, comment="Is export order"
    )

    # Notes
    notes = Column(Text, nullable=True, comment="Customer-visible notes")
    internal_notes = Column(Text, nullable=True, comment="Internal notes only")

    # Relationships
    quote = relationship("Quote", back_populates="order", foreign_keys=[quote_id])
    company = relationship("Company", back_populates="orders", foreign_keys=[company_id])
    contact = relationship("Contact", foreign_keys=[contact_id])
    branch = relationship("Branch", foreign_keys=[branch_id])
    shipping_address = relationship("Address", foreign_keys=[shipping_address_id])
    billing_address = relationship("Address", foreign_keys=[billing_address_id])
    staff = relationship("Staff", foreign_keys=[staff_id])
    status = relationship("OrderStatus")
    payment_status = relationship("PaymentStatus")
    incoterm = relationship("Incoterm")
    currency = relationship("Currency")

    # Related documents
    invoices_sii = relationship("InvoiceSII", back_populates="order")
    invoices_export = relationship("InvoiceExport", back_populates="order")
    delivery_orders = relationship(
        "DeliveryOrder", back_populates="order", cascade="all, delete-orphan"
    )

    # Table constraints
    __table_args__ = (
        CheckConstraint("subtotal >= 0", name="ck_order_subtotal_positive"),
        CheckConstraint("tax_amount >= 0", name="ck_order_tax_positive"),
        CheckConstraint("shipping_cost >= 0", name="ck_order_shipping_positive"),
        CheckConstraint("other_costs >= 0", name="ck_order_other_costs_positive"),
        CheckConstraint("total >= 0", name="ck_order_total_positive"),
        CheckConstraint(
            "tax_percentage >= 0 AND tax_percentage <= 100",
            name="ck_order_tax_percentage_valid",
        ),
        CheckConstraint(
            "order_type IN ('sales', 'purchase')", name="ck_order_type_valid"
        ),
        Index("ix_order_company_date", "company_id", "order_date"),
        Index("ix_order_status_date", "status_id", "order_date"),
        Index("ix_order_payment_status", "payment_status_id"),
    )

    # Validation
    @validates("order_number")
    def validate_order_number(self, key: str, value: str) -> str:
        """Validate order number format."""
        if not value or not value.strip():
            raise ValueError("Order number cannot be empty")
        return value.strip().upper()

    @validates("order_type")
    def validate_order_type(self, key: str, value: str) -> str:
        """Validate order type is valid."""
        valid_types = {"sales", "purchase"}
        if value not in valid_types:
            raise ValueError(
                f"Order type must be one of {valid_types}, got '{value}'"
            )
        return value

    @validates("tax_percentage")
    def validate_tax_percentage(self, key: str, value: Decimal) -> Decimal:
        """Validate tax percentage is within valid range."""
        if value < 0 or value > 100:
            raise ValueError(f"Tax percentage must be between 0 and 100, got {value}")
        return value

    # Business methods
    def calculate_totals(self) -> None:
        """
        Calculate tax, and total.

        Formula: total = subtotal + tax_amount + shipping_cost + other_costs
        """
        self.tax_amount = (self.subtotal * self.tax_percentage / Decimal("100")).quantize(
            Decimal("0.01")
        )
        self.total = (
            self.subtotal + self.tax_amount + self.shipping_cost + self.other_costs
        ).quantize(Decimal("0.01"))

    @property
    def is_overdue(self) -> bool:
        """Check if order delivery is overdue."""
        if self.promised_date is None or self.completed_date is not None:
            return False
        return date.today() > self.promised_date

    @property
    def days_until_required(self) -> Optional[int]:
        """Calculate days until required date."""
        if self.required_date is None or self.completed_date is not None:
            return None
        delta = self.required_date - date.today()
        return delta.days

    @property
    def processing_days(self) -> Optional[int]:
        """Calculate days from order to completion."""
        if self.completed_date is None:
            return None
        delta = self.completed_date - self.order_date
        return delta.days

    def create_from_quote(self, quote: "Quote") -> None:
        """
        Populate order from an accepted quote.

        Args:
            quote: Source quote to copy data from

        Note:
            This copies core information but doesn't copy line items.
            Line items should be handled separately.
        """
        self.quote_id = quote.id
        self.company_id = quote.company_id
        self.contact_id = quote.contact_id
        self.branch_id = quote.branch_id
        self.staff_id = quote.staff_id
        self.incoterm_id = quote.incoterm_id
        self.currency_id = quote.currency_id
        self.exchange_rate = quote.exchange_rate
        self.subtotal = quote.subtotal
        self.tax_percentage = quote.tax_percentage
        self.tax_amount = quote.tax_amount
        self.total = quote.total
        self.notes = quote.notes

    def __repr__(self) -> str:
        """String representation."""
        return f"<Order(id={self.id}, number='{self.order_number}', type='{self.order_type}', total={self.total})>"
