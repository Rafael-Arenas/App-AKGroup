"""
Order models for AK Group business management system.

This module contains the Order model for managing purchase and sales orders.
Orders can be created from accepted quotes or standalone.
Part of Phase 4: Business Models implementation.
"""

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
    from ..core.addresses import Address
    from ..core.companies import Company, CompanyRut, Plant
    from ..core.contacts import Contact
    from ..core.products import Product
    from ..core.staff import Staff
    from ..lookups.business import Currency, Incoterm
    from ..lookups.status import OrderStatus, PaymentStatus
    from .delivery import DeliveryOrder
    from .invoices import InvoiceExport, InvoiceSII
    from .quotes import Quote


class Order(Base, TimestampMixin, AuditMixin, ActiveMixin):
    """
    Purchase and sales orders model.

    Manages customer orders (purchase orders from customer perspective,
    sales orders from company perspective). Can be created from an
    accepted quote or created standalone.
    """

    __tablename__ = "orders"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True)

    # Order identification
    order_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        comment="Unique order number (e.g., O-2025-001)",
    )
    revision: Mapped[str] = mapped_column(
        String(10), default="A", comment="Order revision (A, B, C...)"
    )
    order_type: Mapped[str] = mapped_column(
        String(20), default="sales", comment="Order type: 'sales' or 'purchase'"
    )

    # Reference to quote (if order created from quote)
    quote_id: Mapped[int | None] = mapped_column(
        ForeignKey("quotes.id", ondelete="SET NULL"),
        unique=True,
        index=True,
        comment="Source quote if order created from accepted quote",
    )

    # Customer reference numbers
    customer_quote_number: Mapped[str | None] = mapped_column(
        String(100), index=True, comment="Customer's quote/reference number"
    )
    customer_po_number: Mapped[str | None] = mapped_column(
        String(100), index=True, comment="Customer's purchase order number"
    )
    project_number: Mapped[str | None] = mapped_column(
        String(100), index=True, comment="Project number/identifier"
    )

    # Related entities (FK to core models)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"),
        index=True,
        comment="Customer or supplier company",
    )
    contact_id: Mapped[int | None] = mapped_column(
        ForeignKey("contacts.id", ondelete="SET NULL"),
        index=True,
        comment="Contact person",
    )
    plant_id: Mapped[int | None] = mapped_column(
        ForeignKey("plants.id", ondelete="SET NULL"), comment="Company plant"
    )
    company_rut_id: Mapped[int | None] = mapped_column(
        ForeignKey("company_ruts.id", ondelete="RESTRICT"),
        index=True,
        comment="Specific customer RUT for this order",
    )

    # Address information
    shipping_address_id: Mapped[int | None] = mapped_column(
        ForeignKey("addresses.id", ondelete="SET NULL"),
        index=True,
        comment="Shipping/delivery address",
    )
    billing_address_id: Mapped[int | None] = mapped_column(
        ForeignKey("addresses.id", ondelete="SET NULL"),
        index=True,
        comment="Billing/invoice address",
    )

    staff_id: Mapped[int] = mapped_column(
        ForeignKey("staff.id", ondelete="RESTRICT"),
        index=True,
        comment="Staff member managing this order",
    )

    # Status (FK to lookup tables)
    status_id: Mapped[int] = mapped_column(
        ForeignKey("order_statuses.id", ondelete="RESTRICT"),
        index=True,
        comment="Order status",
    )
    payment_status_id: Mapped[int] = mapped_column(
        ForeignKey("payment_statuses.id", ondelete="RESTRICT"),
        index=True,
        comment="Payment status",
    )

    # Important dates
    order_date: Mapped[date] = mapped_column(
        Date, index=True, comment="Date order was placed"
    )
    required_date: Mapped[date | None] = mapped_column(
        Date, comment="Date customer requires delivery"
    )
    promised_date: Mapped[date | None] = mapped_column(
        Date, comment="Date we promised to deliver"
    )
    shipped_date: Mapped[date | None] = mapped_column(
        Date, comment="Actual shipping date"
    )
    completed_date: Mapped[date | None] = mapped_column(
        Date, comment="Date order was completed"
    )

    # Shipping and currency
    incoterm_id: Mapped[int | None] = mapped_column(
        ForeignKey("incoterms.id", ondelete="SET NULL"),
        comment="Shipping terms (EXW, FOB, CIF, etc.)",
    )
    currency_id: Mapped[int] = mapped_column(
        ForeignKey("currencies.id", ondelete="RESTRICT"), comment="Order currency"
    )
    exchange_rate: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 6), comment="Exchange rate at time of order"
    )

    # Financial information
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), comment="Total before tax"
    )
    tax_percentage: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), default=Decimal("19.00"), comment="Tax percentage"
    )
    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), comment="Calculated tax amount"
    )
    shipping_cost: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), comment="Shipping/freight cost"
    )
    other_costs: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), comment="Other additional costs"
    )
    total: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), comment="Grand total"
    )

    # Payment and export info
    payment_terms: Mapped[str | None] = mapped_column(
        String(200), comment="Payment terms description"
    )
    is_export: Mapped[bool] = mapped_column(
        default=False, index=True, comment="Is export order"
    )

    # Notes
    notes: Mapped[str | None] = mapped_column(Text, comment="Customer-visible notes")
    internal_notes: Mapped[str | None] = mapped_column(
        Text, comment="Internal notes only"
    )

    # Relationships
    quote: Mapped["Quote | None"] = relationship(
        "Quote", back_populates="order", foreign_keys=[quote_id]
    )
    company: Mapped["Company"] = relationship(
        "Company", back_populates="orders", foreign_keys=[company_id]
    )
    company_rut: Mapped["CompanyRut | None"] = relationship(
        "CompanyRut", foreign_keys=[company_rut_id]
    )
    contact: Mapped["Contact | None"] = relationship(
        "Contact", foreign_keys=[contact_id]
    )
    plant: Mapped["Plant | None"] = relationship("Plant", foreign_keys=[plant_id])
    shipping_address: Mapped["Address | None"] = relationship(
        "Address", foreign_keys=[shipping_address_id]
    )
    billing_address: Mapped["Address | None"] = relationship(
        "Address", foreign_keys=[billing_address_id]
    )
    staff: Mapped["Staff"] = relationship("Staff", foreign_keys=[staff_id])
    status: Mapped["OrderStatus"] = relationship("OrderStatus")
    payment_status: Mapped["PaymentStatus"] = relationship("PaymentStatus")
    incoterm: Mapped["Incoterm | None"] = relationship("Incoterm")
    currency: Mapped["Currency"] = relationship("Currency")

    # Related documents
    invoices_sii: Mapped[list["InvoiceSII"]] = relationship(
        "InvoiceSII", back_populates="order"
    )
    invoices_export: Mapped[list["InvoiceExport"]] = relationship(
        "InvoiceExport", back_populates="order"
    )
    delivery_orders: Mapped[list["DeliveryOrder"]] = relationship(
        "DeliveryOrder", back_populates="order", cascade="all, delete-orphan"
    )

    # Order products (line items)
    products: Mapped[list["OrderProduct"]] = relationship(
        "OrderProduct",
        back_populates="order",
        cascade="all, delete-orphan",
        order_by="OrderProduct.sequence",
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
            raise ValueError(f"Order type must be one of {valid_types}, got '{value}'")
        return value

    @validates("tax_percentage")
    def validate_tax_percentage(self, key: str, value: Decimal) -> Decimal:
        """Validate tax percentage is within valid range."""
        if value < 0 or value > 100:
            raise ValueError(f"Tax percentage must be between 0 and 100, got {value}")
        return value

    # Business methods
    def calculate_totals(self) -> None:
        """Calculate subtotal from products, tax, and total."""
        if self.products:
            self.subtotal = sum(
                (item.subtotal or Decimal("0.00")) for item in self.products
            )

        self.tax_amount = (
            self.subtotal * self.tax_percentage / Decimal("100")
        ).quantize(Decimal("0.01"))
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
    def days_until_required(self) -> int | None:
        """Calculate days until required date."""
        if self.required_date is None or self.completed_date is not None:
            return None
        delta = self.required_date - date.today()
        return delta.days

    @property
    def processing_days(self) -> int | None:
        """Calculate days from order to completion."""
        if self.completed_date is None:
            return None
        delta = self.completed_date - self.order_date
        return delta.days

    def create_from_quote(self, quote: "Quote") -> None:
        """Populate order from an accepted quote."""
        self.quote_id = quote.id
        self.company_id = quote.company_id
        self.company_rut_id = quote.company_rut_id
        self.contact_id = quote.contact_id
        self.plant_id = quote.plant_id
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


class OrderProduct(Base, TimestampMixin):
    """
    Products/line items in an order.

    Junction table between Order and Product with quantity, pricing,
    and discount information.
    """

    __tablename__ = "order_products"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True)

    # Foreign keys
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        index=True,
        comment="Parent order",
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="RESTRICT"),
        index=True,
        comment="Product being ordered",
    )

    # Line item details
    sequence: Mapped[int] = mapped_column(
        default=1, comment="Display order of line items"
    )

    # Quantities and pricing
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 3), comment="Quantity being ordered"
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), comment="Price per unit"
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
    order: Mapped["Order"] = relationship("Order", back_populates="products")
    product: Mapped["Product"] = relationship("Product")

    # Table constraints
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_order_product_quantity_positive"),
        CheckConstraint("unit_price >= 0", name="ck_order_product_price_positive"),
        CheckConstraint(
            "discount_percentage >= 0 AND discount_percentage <= 100",
            name="ck_order_product_discount_percentage_valid",
        ),
        CheckConstraint(
            "discount_amount >= 0", name="ck_order_product_discount_positive"
        ),
        CheckConstraint("subtotal >= 0", name="ck_order_product_subtotal_positive"),
        Index("ix_order_product_order", "order_id", "sequence"),
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
        return f"<OrderProduct(id={self.id}, order_id={self.order_id}, product_id={self.product_id}, qty={self.quantity}, subtotal={self.subtotal})>"
