"""
Invoice models for AK Group business management system.

This module contains invoice models for both Chilean SII (domestic) invoices
and export invoices with their specific requirements.
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
from ..base import Base, TimestampMixin, AuditMixin, ActiveMixin


class InvoiceSII(Base, TimestampMixin, AuditMixin, ActiveMixin):
    """
    Chilean SII domestic invoices.

    Manages invoices for Chilean domestic sales according to SII
    (Servicio de Impuestos Internos) requirements. Includes fields
    specific to Chilean tax documentation.

    Attributes:
        id: Primary key
        invoice_number: SII invoice number (folio)
        revision: Invoice revision number (e.g., "A", "B", "C")
        invoice_type: Document type (33=Factura Electrónica, 34=Factura Exenta, etc.)
        order_id: Foreign key to Order
        company_id: Foreign key to Company (customer)
        branch_id: Foreign key to Branch
        staff_id: Foreign key to Staff
        payment_status_id: Foreign key to PaymentStatus
        invoice_date: Invoice issue date
        due_date: Payment due date
        paid_date: Date invoice was fully paid
        currency_id: Foreign key to Currency
        exchange_rate: Exchange rate if not CLP
        subtotal: Total before tax
        tax_amount: IVA amount (usually 19%)
        total: Total including tax
        net_amount: Net amount (for exempt items)
        exempt_amount: Tax-exempt amount
        payment_terms: Payment terms description
        sii_status: SII system status (pending, accepted, rejected)
        sii_track_id: SII tracking ID
        sii_xml: XML sent to SII
        notes: Additional notes
    """

    __tablename__ = "invoices_sii"

    # Primary key
    id = Column(Integer, primary_key=True)

    # Invoice identification
    invoice_number = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        comment="SII invoice number (folio)",
    )
    revision = Column(
        String(10),
        nullable=False,
        default="A",
        comment="Invoice revision (A, B, C...)",
    )
    invoice_type = Column(
        String(10),
        nullable=False,
        default="33",
        comment="SII document type (33=Factura, 34=Exenta, 56=Nota Débito, 61=Nota Crédito)",
    )

    # Related entities
    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Source order",
    )
    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Customer company",
    )
    branch_id = Column(
        Integer,
        ForeignKey("branches.id", ondelete="SET NULL"),
        nullable=True,
        comment="Customer branch",
    )
    staff_id = Column(
        Integer,
        ForeignKey("staff.id", ondelete="RESTRICT"),
        nullable=False,
        comment="Staff member who created invoice",
    )

    # Payment status
    payment_status_id = Column(
        Integer,
        ForeignKey("payment_statuses.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Payment status",
    )

    # Important dates
    invoice_date = Column(
        Date, nullable=False, index=True, comment="Invoice issue date"
    )
    due_date = Column(Date, nullable=True, comment="Payment due date")
    paid_date = Column(Date, nullable=True, comment="Date invoice was fully paid")

    # Currency
    currency_id = Column(
        Integer,
        ForeignKey("currencies.id", ondelete="RESTRICT"),
        nullable=False,
        comment="Invoice currency (usually CLP)",
    )
    exchange_rate = Column(
        DECIMAL(12, 6),
        nullable=True,
        comment="Exchange rate if not CLP",
    )

    # Financial amounts
    subtotal = Column(
        DECIMAL(15, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Taxable base amount",
    )
    tax_amount = Column(
        DECIMAL(15, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="IVA amount (usually 19%)",
    )
    total = Column(
        DECIMAL(15, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Total including tax",
    )
    net_amount = Column(
        DECIMAL(15, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Net amount",
    )
    exempt_amount = Column(
        DECIMAL(15, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Tax-exempt amount",
    )

    # Payment info
    payment_terms = Column(
        String(200), nullable=True, comment="Payment terms description"
    )

    # SII specific fields
    sii_status = Column(
        String(50),
        nullable=True,
        index=True,
        comment="SII system status (pending, accepted, rejected)",
    )
    sii_track_id = Column(String(100), nullable=True, comment="SII tracking ID")
    sii_xml = Column(Text, nullable=True, comment="XML sent to SII")

    # Notes
    notes = Column(Text, nullable=True, comment="Additional notes")

    # Relationships
    order = relationship("Order", back_populates="invoices_sii", foreign_keys=[order_id])
    company = relationship("Company", back_populates="invoices_sii", foreign_keys=[company_id])
    branch = relationship("Branch", foreign_keys=[branch_id])
    staff = relationship("Staff", foreign_keys=[staff_id])
    payment_status = relationship("PaymentStatus")
    currency = relationship("Currency")

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
        valid_types = {"33", "34", "56", "61", "39", "41"}  # Common SII document types
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
    def days_overdue(self) -> Optional[int]:
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

    Attributes:
        id: Primary key
        invoice_number: Export invoice number
        revision: Invoice revision number (e.g., "A", "B", "C")
        invoice_type: Document type (110=Factura Exportación, 111=Nota Débito Export, 112=Nota Crédito Export)
        order_id: Foreign key to Order
        company_id: Foreign key to Company (foreign customer)
        branch_id: Foreign key to Branch
        staff_id: Foreign key to Staff
        payment_status_id: Foreign key to PaymentStatus
        invoice_date: Invoice issue date
        due_date: Payment due date
        paid_date: Date invoice was fully paid
        shipping_date: Date goods were shipped
        currency_id: Foreign key to Currency (usually USD or EUR)
        exchange_rate: Exchange rate to CLP
        incoterm_id: Foreign key to Incoterm (required for exports)
        country_id: Destination country
        port_of_loading: Port where goods are loaded
        port_of_discharge: Destination port
        subtotal: Total in foreign currency
        total: Total in foreign currency (usually no tax for exports)
        total_clp: Total converted to CLP
        freight_cost: International freight cost
        insurance_cost: Insurance cost
        payment_terms: Payment terms
        letter_of_credit: Letter of credit reference
        customs_declaration: Customs declaration number
        bill_of_lading: Bill of lading number
        notes: Additional notes
    """

    __tablename__ = "invoices_export"

    # Primary key
    id = Column(Integer, primary_key=True)

    # Invoice identification
    invoice_number = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        comment="Export invoice number",
    )
    revision = Column(
        String(10),
        nullable=False,
        default="A",
        comment="Invoice revision (A, B, C...)",
    )
    invoice_type = Column(
        String(10),
        nullable=False,
        default="110",
        comment="SII export document type (110=Factura Export, 111=Nota Débito, 112=Nota Crédito)",
    )

    # Related entities
    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Source order",
    )
    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Foreign customer company",
    )
    branch_id = Column(
        Integer,
        ForeignKey("branches.id", ondelete="SET NULL"),
        nullable=True,
        comment="Customer branch",
    )
    staff_id = Column(
        Integer,
        ForeignKey("staff.id", ondelete="RESTRICT"),
        nullable=False,
        comment="Staff member who created invoice",
    )

    # Payment status
    payment_status_id = Column(
        Integer,
        ForeignKey("payment_statuses.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Payment status",
    )

    # Important dates
    invoice_date = Column(
        Date, nullable=False, index=True, comment="Invoice issue date"
    )
    due_date = Column(Date, nullable=True, comment="Payment due date")
    paid_date = Column(Date, nullable=True, comment="Date invoice was fully paid")
    shipping_date = Column(Date, nullable=True, comment="Date goods were shipped")

    # Currency and exchange
    currency_id = Column(
        Integer,
        ForeignKey("currencies.id", ondelete="RESTRICT"),
        nullable=False,
        comment="Invoice currency (usually USD, EUR)",
    )
    exchange_rate = Column(
        DECIMAL(12, 6),
        nullable=False,
        comment="Exchange rate to CLP at invoice date",
    )

    # Shipping terms and destination
    incoterm_id = Column(
        Integer,
        ForeignKey("incoterms.id", ondelete="RESTRICT"),
        nullable=False,
        comment="International shipping terms (required for exports)",
    )
    country_id = Column(
        Integer,
        ForeignKey("countries.id", ondelete="RESTRICT"),
        nullable=False,
        comment="Destination country",
    )
    port_of_loading = Column(
        String(100), nullable=True, comment="Port where goods are loaded"
    )
    port_of_discharge = Column(
        String(100), nullable=True, comment="Destination port"
    )

    # Financial amounts
    subtotal = Column(
        DECIMAL(15, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Subtotal in foreign currency",
    )
    total = Column(
        DECIMAL(15, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Total in foreign currency (exports usually tax-exempt)",
    )
    total_clp = Column(
        DECIMAL(15, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Total converted to CLP",
    )
    freight_cost = Column(
        DECIMAL(15, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="International freight cost",
    )
    insurance_cost = Column(
        DECIMAL(15, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Insurance cost",
    )

    # Payment and documentation
    payment_terms = Column(
        String(200), nullable=True, comment="Payment terms description"
    )
    letter_of_credit = Column(
        String(100), nullable=True, comment="Letter of credit reference"
    )
    customs_declaration = Column(
        String(100), nullable=True, comment="Customs declaration number (DIN)"
    )
    bill_of_lading = Column(
        String(100), nullable=True, comment="Bill of lading number (B/L)"
    )

    # Notes
    notes = Column(Text, nullable=True, comment="Additional notes")

    # Relationships
    order = relationship("Order", back_populates="invoices_export", foreign_keys=[order_id])
    company = relationship("Company", back_populates="invoices_export", foreign_keys=[company_id])
    branch = relationship("Branch", foreign_keys=[branch_id])
    staff = relationship("Staff", foreign_keys=[staff_id])
    payment_status = relationship("PaymentStatus")
    currency = relationship("Currency")
    incoterm = relationship("Incoterm")
    country = relationship("Country")

    # Table constraints
    __table_args__ = (
        CheckConstraint("subtotal >= 0", name="ck_invoice_export_subtotal_positive"),
        CheckConstraint("total >= 0", name="ck_invoice_export_total_positive"),
        CheckConstraint("total_clp >= 0", name="ck_invoice_export_total_clp_positive"),
        CheckConstraint("freight_cost >= 0", name="ck_invoice_export_freight_positive"),
        CheckConstraint("insurance_cost >= 0", name="ck_invoice_export_insurance_positive"),
        CheckConstraint("exchange_rate > 0", name="ck_invoice_export_exchange_rate_positive"),
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
        valid_types = {"110", "111", "112"}  # Export document types
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
    def days_overdue(self) -> Optional[int]:
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
