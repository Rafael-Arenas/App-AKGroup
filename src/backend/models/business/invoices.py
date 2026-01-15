"""
Invoice models for AK Group business management system.

This module contains invoice models for both Chilean SII (domestic) invoices
and export invoices with their specific requirements.
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
    from ..core.companies import Company, Plant
    from ..core.staff import Staff
    from ..lookups.business import Currency, Incoterm
    from ..lookups.geo import Country
    from ..lookups.status import PaymentStatus
    from .orders import Order


class InvoiceSII(Base, TimestampMixin, AuditMixin, ActiveMixin):
    """
    Chilean SII domestic invoices.

    Manages invoices for Chilean domestic sales according to SII
    (Servicio de Impuestos Internos) requirements.
    """

    __tablename__ = "invoices_sii"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True)

    # Invoice identification
    invoice_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        comment="SII invoice number (folio)",
    )
    revision: Mapped[str] = mapped_column(
        String(10), default="A", comment="Invoice revision (A, B, C...)"
    )
    invoice_type: Mapped[str] = mapped_column(
        String(10),
        default="33",
        comment="SII document type (33=Factura, 34=Exenta, 56=Nota Débito, 61=Nota Crédito)",
    )

    # Related entities
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="RESTRICT"),
        index=True,
        comment="Source order",
    )
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"),
        index=True,
        comment="Customer company",
    )
    plant_id: Mapped[int | None] = mapped_column(
        ForeignKey("plants.id", ondelete="SET NULL"), comment="Customer plant"
    )
    staff_id: Mapped[int] = mapped_column(
        ForeignKey("staff.id", ondelete="RESTRICT"),
        comment="Staff member who created invoice",
    )

    # Payment status
    payment_status_id: Mapped[int] = mapped_column(
        ForeignKey("payment_statuses.id", ondelete="RESTRICT"),
        index=True,
        comment="Payment status",
    )

    # Important dates
    invoice_date: Mapped[date] = mapped_column(
        Date, index=True, comment="Invoice issue date"
    )
    due_date: Mapped[date | None] = mapped_column(Date, comment="Payment due date")
    paid_date: Mapped[date | None] = mapped_column(
        Date, comment="Date invoice was fully paid"
    )

    # Currency
    currency_id: Mapped[int] = mapped_column(
        ForeignKey("currencies.id", ondelete="RESTRICT"),
        comment="Invoice currency (usually CLP)",
    )
    exchange_rate: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 6), comment="Exchange rate if not CLP"
    )

    # Financial amounts
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), comment="Taxable base amount"
    )
    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), comment="IVA amount (usually 19%)"
    )
    total: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), comment="Total including tax"
    )
    net_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), comment="Net amount"
    )
    exempt_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), comment="Tax-exempt amount"
    )

    # Payment info
    payment_terms: Mapped[str | None] = mapped_column(
        String(200), comment="Payment terms description"
    )

    # SII specific fields
    sii_status: Mapped[str | None] = mapped_column(
        String(50),
        index=True,
        comment="SII system status (pending, accepted, rejected)",
    )
    sii_track_id: Mapped[str | None] = mapped_column(
        String(100), comment="SII tracking ID"
    )
    sii_xml: Mapped[str | None] = mapped_column(Text, comment="XML sent to SII")

    # Notes
    notes: Mapped[str | None] = mapped_column(Text, comment="Additional notes")

    # Relationships
    order: Mapped["Order"] = relationship(
        "Order", back_populates="invoices_sii", foreign_keys=[order_id]
    )
    company: Mapped["Company"] = relationship(
        "Company", back_populates="invoices_sii", foreign_keys=[company_id]
    )
    plant: Mapped["Plant | None"] = relationship("Plant", foreign_keys=[plant_id])
    staff: Mapped["Staff"] = relationship("Staff", foreign_keys=[staff_id])
    payment_status: Mapped["PaymentStatus"] = relationship("PaymentStatus")
    currency: Mapped["Currency"] = relationship("Currency")

    # Table constraints
    __table_args__ = (
        CheckConstraint("subtotal >= 0", name="ck_invoice_sii_subtotal_positive"),
        CheckConstraint("tax_amount >= 0", name="ck_invoice_sii_tax_positive"),
        CheckConstraint("total >= 0", name="ck_invoice_sii_total_positive"),
        CheckConstraint("net_amount >= 0", name="ck_invoice_sii_net_positive"),
        CheckConstraint("exempt_amount >= 0", name="ck_invoice_sii_exempt_positive"),
        CheckConstraint(
            "invoice_type IN ('33', '34', '56', '61', '39', '41')",
            name="ck_invoice_sii_type_valid",
        ),
        Index("ix_invoice_sii_company_date", "company_id", "invoice_date"),
        Index("ix_invoice_sii_status_date", "payment_status_id", "invoice_date"),
        Index("ix_invoice_sii_sii_status", "sii_status"),
    )

    # Validation
    @validates("invoice_number")
    def validate_invoice_number(self, key: str, value: str) -> str:
        """Validate invoice number format."""
        if not value or not value.strip():
            raise ValueError("Invoice number cannot be empty")
        return value.strip()

    @validates("invoice_type")
    def validate_invoice_type(self, key: str, value: str) -> str:
        """Validate invoice type is valid SII document type."""
        valid_types = {"33", "34", "56", "61", "39", "41"}
        if value not in valid_types:
            raise ValueError(
                f"Invoice type must be one of {valid_types}, got '{value}'"
            )
        return value

    # Business methods
    @property
    def is_overdue(self) -> bool:
        """Check if invoice payment is overdue."""
        if self.due_date is None or self.paid_date is not None:
            return False
        return date.today() > self.due_date

    @property
    def days_overdue(self) -> int | None:
        """Calculate days overdue."""
        if not self.is_overdue:
            return None
        delta = date.today() - self.due_date
        return delta.days

    @property
    def is_paid(self) -> bool:
        """Check if invoice is fully paid."""
        return self.paid_date is not None

    def __repr__(self) -> str:
        """String representation."""
        return f"<InvoiceSII(id={self.id}, number='{self.invoice_number}', type='{self.invoice_type}', total={self.total})>"


class InvoiceExport(Base, TimestampMixin, AuditMixin, ActiveMixin):
    """
    Export invoices (facturas de exportación).

    Manages invoices for international sales (exports) with specific
    requirements for Chilean customs and international trade.
    """

    __tablename__ = "invoices_export"

    # Primary key
    id: Mapped[int] = mapped_column(primary_key=True)

    # Invoice identification
    invoice_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        comment="Export invoice number",
    )
    revision: Mapped[str] = mapped_column(
        String(10), default="A", comment="Invoice revision (A, B, C...)"
    )
    invoice_type: Mapped[str] = mapped_column(
        String(10),
        default="110",
        comment="SII export document type (110=Factura Export, 111=Nota Débito, 112=Nota Crédito)",
    )

    # Related entities
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="RESTRICT"),
        index=True,
        comment="Source order",
    )
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="RESTRICT"),
        index=True,
        comment="Foreign customer company",
    )
    plant_id: Mapped[int | None] = mapped_column(
        ForeignKey("plants.id", ondelete="SET NULL"), comment="Customer plant"
    )
    staff_id: Mapped[int] = mapped_column(
        ForeignKey("staff.id", ondelete="RESTRICT"),
        comment="Staff member who created invoice",
    )

    # Payment status
    payment_status_id: Mapped[int] = mapped_column(
        ForeignKey("payment_statuses.id", ondelete="RESTRICT"),
        index=True,
        comment="Payment status",
    )

    # Important dates
    invoice_date: Mapped[date] = mapped_column(
        Date, index=True, comment="Invoice issue date"
    )
    due_date: Mapped[date | None] = mapped_column(Date, comment="Payment due date")
    paid_date: Mapped[date | None] = mapped_column(
        Date, comment="Date invoice was fully paid"
    )
    shipping_date: Mapped[date | None] = mapped_column(
        Date, comment="Date goods were shipped"
    )

    # Currency and exchange
    currency_id: Mapped[int] = mapped_column(
        ForeignKey("currencies.id", ondelete="RESTRICT"),
        comment="Invoice currency (usually USD, EUR)",
    )
    exchange_rate: Mapped[Decimal] = mapped_column(
        Numeric(12, 6), comment="Exchange rate to CLP at invoice date"
    )

    # Shipping terms and destination
    incoterm_id: Mapped[int] = mapped_column(
        ForeignKey("incoterms.id", ondelete="RESTRICT"),
        comment="International shipping terms (required for exports)",
    )
    country_id: Mapped[int] = mapped_column(
        ForeignKey("countries.id", ondelete="RESTRICT"), comment="Destination country"
    )
    port_of_loading: Mapped[str | None] = mapped_column(
        String(100), comment="Port where goods are loaded"
    )
    port_of_discharge: Mapped[str | None] = mapped_column(
        String(100), comment="Destination port"
    )

    # Financial amounts
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), comment="Subtotal in foreign currency"
    )
    total: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        default=Decimal("0.00"),
        comment="Total in foreign currency (exports usually tax-exempt)",
    )
    total_clp: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), comment="Total converted to CLP"
    )
    freight_cost: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), comment="International freight cost"
    )
    insurance_cost: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00"), comment="Insurance cost"
    )

    # Payment and documentation
    payment_terms: Mapped[str | None] = mapped_column(
        String(200), comment="Payment terms description"
    )
    letter_of_credit: Mapped[str | None] = mapped_column(
        String(100), comment="Letter of credit reference"
    )
    customs_declaration: Mapped[str | None] = mapped_column(
        String(100), comment="Customs declaration number (DIN)"
    )
    bill_of_lading: Mapped[str | None] = mapped_column(
        String(100), comment="Bill of lading number (B/L)"
    )

    # Notes
    notes: Mapped[str | None] = mapped_column(Text, comment="Additional notes")

    # Relationships
    order: Mapped["Order"] = relationship(
        "Order", back_populates="invoices_export", foreign_keys=[order_id]
    )
    company: Mapped["Company"] = relationship(
        "Company", back_populates="invoices_export", foreign_keys=[company_id]
    )
    plant: Mapped["Plant | None"] = relationship("Plant", foreign_keys=[plant_id])
    staff: Mapped["Staff"] = relationship("Staff", foreign_keys=[staff_id])
    payment_status: Mapped["PaymentStatus"] = relationship("PaymentStatus")
    currency: Mapped["Currency"] = relationship("Currency")
    incoterm: Mapped["Incoterm"] = relationship("Incoterm")
    country: Mapped["Country"] = relationship("Country")

    # Table constraints
    __table_args__ = (
        CheckConstraint("subtotal >= 0", name="ck_invoice_export_subtotal_positive"),
        CheckConstraint("total >= 0", name="ck_invoice_export_total_positive"),
        CheckConstraint("total_clp >= 0", name="ck_invoice_export_total_clp_positive"),
        CheckConstraint("freight_cost >= 0", name="ck_invoice_export_freight_positive"),
        CheckConstraint(
            "insurance_cost >= 0", name="ck_invoice_export_insurance_positive"
        ),
        CheckConstraint(
            "exchange_rate > 0", name="ck_invoice_export_exchange_rate_positive"
        ),
        CheckConstraint(
            "invoice_type IN ('110', '111', '112')",
            name="ck_invoice_export_type_valid",
        ),
        Index("ix_invoice_export_company_date", "company_id", "invoice_date"),
        Index("ix_invoice_export_status_date", "payment_status_id", "invoice_date"),
        Index("ix_invoice_export_country", "country_id"),
    )

    # Validation
    @validates("invoice_number")
    def validate_invoice_number(self, key: str, value: str) -> str:
        """Validate invoice number format."""
        if not value or not value.strip():
            raise ValueError("Invoice number cannot be empty")
        return value.strip()

    @validates("invoice_type")
    def validate_invoice_type(self, key: str, value: str) -> str:
        """Validate invoice type is valid export document type."""
        valid_types = {"110", "111", "112"}
        if value not in valid_types:
            raise ValueError(
                f"Export invoice type must be one of {valid_types}, got '{value}'"
            )
        return value

    @validates("exchange_rate")
    def validate_exchange_rate(self, key: str, value: Decimal) -> Decimal:
        """Validate exchange rate is positive."""
        if value <= 0:
            raise ValueError(f"Exchange rate must be positive, got {value}")
        return value

    # Business methods
    def calculate_clp_total(self) -> None:
        """Calculate total in CLP using exchange rate."""
        self.total_clp = (self.total * self.exchange_rate).quantize(Decimal("0.01"))

    @property
    def is_overdue(self) -> bool:
        """Check if invoice payment is overdue."""
        if self.due_date is None or self.paid_date is not None:
            return False
        return date.today() > self.due_date

    @property
    def days_overdue(self) -> int | None:
        """Calculate days overdue."""
        if not self.is_overdue:
            return None
        delta = date.today() - self.due_date
        return delta.days

    @property
    def is_paid(self) -> bool:
        """Check if invoice is fully paid."""
        return self.paid_date is not None

    def __repr__(self) -> str:
        """String representation."""
        return f"<InvoiceExport(id={self.id}, number='{self.invoice_number}', total={self.total}, total_clp={self.total_clp})>"
