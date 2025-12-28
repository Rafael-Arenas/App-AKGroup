"""
Delivery and logistics models for AK Group business management system.

This module contains models for managing delivery orders, delivery dates,
transport information, and payment conditions.
Part of Phase 4: Business Models implementation.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    DECIMAL,
    ForeignKey,
    Date,
    DateTime,
    Text,
    Index,
    CheckConstraint,
    Boolean,
)
from sqlalchemy.orm import relationship, validates

# Import base infrastructure (Phases 1-3 are complete)
from ..base import Base, TimestampMixin, AuditMixin, ActiveMixin


class DeliveryOrder(Base, TimestampMixin, AuditMixin, ActiveMixin):
    """
    Delivery orders (guías de despacho).

    Manages delivery documentation for shipping goods to customers.
    Links orders to actual deliveries with transport and address details.

    Attributes:
        id: Primary key
        delivery_number: Unique delivery order number
        revision: Delivery order revision number (e.g., "A", "B", "C")
        order_id: Foreign key to Order
        company_id: Foreign key to Company (customer)
        address_id: Foreign key to Address (delivery address)
        transport_id: Foreign key to Transport
        staff_id: Foreign key to Staff (responsible)
        delivery_date: Planned delivery date
        actual_delivery_date: Actual delivery date
        status: Delivery status (pending, in_transit, delivered, cancelled)
        tracking_number: Carrier tracking number
        delivery_instructions: Special delivery instructions
        signature_name: Name of person who received delivery
        signature_id: ID of person who received delivery
        signature_datetime: Date and time of receipt
        notes: Additional notes
    """

    __tablename__ = "delivery_orders"

    # Primary key
    id = Column(Integer, primary_key=True)

    # Delivery identification
    delivery_number = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        comment="Unique delivery order number (e.g., GD-2025-001)",
    )
    revision = Column(
        String(10),
        nullable=False,
        default="A",
        comment="Delivery order revision (A, B, C...)",
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
    address_id = Column(
        Integer,
        ForeignKey("addresses.id", ondelete="RESTRICT"),
        nullable=False,
        comment="Delivery address",
    )
    transport_id = Column(
        Integer,
        ForeignKey("transports.id", ondelete="SET NULL"),
        nullable=True,
        comment="Transport/carrier information",
    )
    staff_id = Column(
        Integer,
        ForeignKey("staff.id", ondelete="RESTRICT"),
        nullable=False,
        comment="Staff member responsible",
    )

    # Delivery dates
    delivery_date = Column(
        Date, nullable=False, index=True, comment="Planned delivery date"
    )
    actual_delivery_date = Column(
        Date, nullable=True, comment="Actual delivery date"
    )

    # Status and tracking
    status = Column(
        String(50),
        nullable=False,
        default="pending",
        index=True,
        comment="Delivery status (pending, in_transit, delivered, cancelled)",
    )
    tracking_number = Column(
        String(100), nullable=True, comment="Carrier tracking number"
    )

    # Delivery details
    delivery_instructions = Column(
        Text, nullable=True, comment="Special delivery instructions"
    )

    # Receipt/signature information
    signature_name = Column(
        String(200), nullable=True, comment="Name of person who received delivery"
    )
    signature_id = Column(
        String(50), nullable=True, comment="ID of person who received delivery"
    )
    signature_datetime = Column(
        DateTime(timezone=True), nullable=True, comment="Date and time of receipt"
    )

    # Notes
    notes = Column(Text, nullable=True, comment="Additional notes")

    # Relationships
    order = relationship("Order", back_populates="delivery_orders", foreign_keys=[order_id])
    company = relationship("Company", foreign_keys=[company_id])
    address = relationship("Address", foreign_keys=[address_id])
    transport = relationship("Transport", back_populates="delivery_orders", foreign_keys=[transport_id])
    staff = relationship("Staff", foreign_keys=[staff_id])
    delivery_dates = relationship(
        "DeliveryDate", back_populates="delivery_order", cascade="all, delete-orphan"
    )

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'in_transit', 'delivered', 'cancelled')",
            name="ck_delivery_order_status_valid",
        ),
        Index("ix_delivery_order_company_date", "company_id", "delivery_date"),
        Index("ix_delivery_order_status_date", "status", "delivery_date"),
    )

    # Validation
    @validates("delivery_number")
    def validate_delivery_number(self, key: str, value: str) -> str:
        """Validate delivery number format."""
        if not value or not value.strip():
            raise ValueError("Delivery number cannot be empty")
        return value.strip().upper()

    @validates("status")
    def validate_status(self, key: str, value: str) -> str:
        """Validate status is valid."""
        valid_statuses = {"pending", "in_transit", "delivered", "cancelled"}
        if value not in valid_statuses:
            raise ValueError(
                f"Status must be one of {valid_statuses}, got '{value}'"
            )
        return value

    # Business methods
    @property
    def is_delivered(self) -> bool:
        """Check if delivery is completed."""
        return self.status == "delivered" and self.actual_delivery_date is not None

    @property
    def is_late(self) -> bool:
        """Check if delivery is late."""
        if self.is_delivered:
            return self.actual_delivery_date > self.delivery_date
        return date.today() > self.delivery_date

    @property
    def days_late(self) -> Optional[int]:
        """Calculate days late for delivery."""
        if not self.is_late:
            return None
        if self.is_delivered:
            delta = self.actual_delivery_date - self.delivery_date
        else:
            delta = date.today() - self.delivery_date
        return delta.days

    def mark_delivered(
        self, signature_name: str, signature_id: str, notes: Optional[str] = None
    ) -> None:
        """
        Mark delivery as completed with signature.

        Args:
            signature_name: Name of person receiving delivery
            signature_id: ID of person receiving delivery
            notes: Optional notes about delivery
        """
        self.status = "delivered"
        self.actual_delivery_date = date.today()
        self.signature_name = signature_name
        self.signature_id = signature_id
        self.signature_datetime = datetime.now()
        if notes:
            self.notes = notes

    def __repr__(self) -> str:
        """String representation."""
        return f"<DeliveryOrder(id={self.id}, number='{self.delivery_number}', status='{self.status}')>"


class DeliveryDate(Base, TimestampMixin):
    """
    Delivery date tracking for multi-part deliveries.

    Allows tracking multiple delivery dates for a single delivery order,
    useful when an order is delivered in multiple shipments.

    Attributes:
        id: Primary key
        delivery_order_id: Foreign key to DeliveryOrder
        planned_date: Planned delivery date for this shipment
        actual_date: Actual delivery date
        quantity: Quantity delivered in this shipment
        status: Status of this delivery date
        notes: Notes specific to this delivery
    """

    __tablename__ = "delivery_dates"

    # Primary key
    id = Column(Integer, primary_key=True)

    # Foreign key
    delivery_order_id = Column(
        Integer,
        ForeignKey("delivery_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Parent delivery order",
    )

    # Dates
    planned_date = Column(
        Date, nullable=False, index=True, comment="Planned delivery date"
    )
    actual_date = Column(Date, nullable=True, comment="Actual delivery date")

    # Delivery details
    quantity = Column(
        DECIMAL(10, 3),
        nullable=True,
        comment="Quantity delivered in this shipment",
    )
    status = Column(
        String(50),
        nullable=False,
        default="pending",
        comment="Status (pending, completed, cancelled)",
    )

    # Notes
    notes = Column(Text, nullable=True, comment="Notes for this delivery")

    # Relationships
    delivery_order = relationship("DeliveryOrder", back_populates="delivery_dates")

    # Table constraints
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_delivery_date_quantity_positive"),
        CheckConstraint(
            "status IN ('pending', 'completed', 'cancelled')",
            name="ck_delivery_date_status_valid",
        ),
        Index("ix_delivery_date_order_date", "delivery_order_id", "planned_date"),
    )

    # Validation
    @validates("status")
    def validate_status(self, key: str, value: str) -> str:
        """Validate status is valid."""
        valid_statuses = {"pending", "completed", "cancelled"}
        if value not in valid_statuses:
            raise ValueError(
                f"Status must be one of {valid_statuses}, got '{value}'"
            )
        return value

    @validates("quantity")
    def validate_quantity(self, key: str, value: Optional[Decimal]) -> Optional[Decimal]:
        """Validate quantity is positive if provided."""
        if value is not None and value <= 0:
            raise ValueError(f"Quantity must be positive, got {value}")
        return value

    def __repr__(self) -> str:
        """String representation."""
        return f"<DeliveryDate(id={self.id}, delivery_order_id={self.delivery_order_id}, planned={self.planned_date})>"


class Transport(Base, TimestampMixin, ActiveMixin):
    """
    Transport/carrier information.

    Manages information about transport companies and methods used
    for deliveries.

    Attributes:
        id: Primary key
        name: Transport company name
        delivery_number: Delivery tracking/reference number
        transport_type: Type of transport (own, carrier, courier, etc.)
        contact_name: Contact person at transport company
        contact_phone: Contact phone number
        contact_email: Contact email
        website: Transport company website
        notes: Additional notes
    """

    __tablename__ = "transports"

    # Primary key
    id = Column(Integer, primary_key=True)

    # Company information
    name = Column(
        String(200),
        nullable=False,
        unique=True,
        index=True,
        comment="Transport company name",
    )
    delivery_number = Column(
        String(100),
        nullable=True,
        index=True,
        comment="Delivery tracking/reference number",
    )
    transport_type = Column(
        String(50),
        nullable=False,
        default="carrier",
        comment="Type (own, carrier, courier, freight_forwarder)",
    )

    # Contact information
    contact_name = Column(String(200), nullable=True, comment="Contact person name")
    contact_phone = Column(String(50), nullable=True, comment="Contact phone number")
    contact_email = Column(String(100), nullable=True, comment="Contact email")
    website = Column(String(200), nullable=True, comment="Company website")

    # Notes
    notes = Column(Text, nullable=True, comment="Additional notes")

    # Relationships
    delivery_orders = relationship("DeliveryOrder", back_populates="transport")

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "transport_type IN ('own', 'carrier', 'courier', 'freight_forwarder')",
            name="ck_transport_type_valid",
        ),
    )

    # Validation
    @validates("name")
    def validate_name(self, key: str, value: str) -> str:
        """Validate name is not empty."""
        if not value or not value.strip():
            raise ValueError("Transport name cannot be empty")
        return value.strip()

    @validates("transport_type")
    def validate_transport_type(self, key: str, value: str) -> str:
        """Validate transport type is valid."""
        valid_types = {"own", "carrier", "courier", "freight_forwarder"}
        if value not in valid_types:
            raise ValueError(
                f"Transport type must be one of {valid_types}, got '{value}'"
            )
        return value

    def __repr__(self) -> str:
        """String representation."""
        return f"<Transport(id={self.id}, name='{self.name}', type='{self.transport_type}')>"


class PaymentCondition(Base, TimestampMixin, ActiveMixin):
    """
    Payment conditions/terms.

    Manages standard payment conditions that can be applied to
    quotes, orders, and invoices.

    attributes:
        id: Primary key
        payment_condition_number: Short number/code (e.g., "001", "NET30")
        name: Payment condition name
        revision: Payment condition revision number (e.g., "A", "B", "C")
        description: Detailed description
        days_to_pay: Number of days for payment
        percentage_advance: Percentage required as advance payment
        percentage_on_delivery: Percentage due on delivery
        percentage_after_delivery: Percentage due after delivery (with days)
        days_after_delivery: Days after delivery for final payment
        is_default: Whether this is the default payment condition
        notes: Additional notes
    """

    __tablename__ = "payment_conditions"

    # Primary key
    id = Column(Integer, primary_key=True)

    # Identification
    payment_condition_number = Column(
        String(20),
        nullable=False,
        unique=True,
        index=True,
        comment="Short number/code (e.g., 001, NET30, COD)",
    )
    name = Column(
        String(100), nullable=False, comment="Payment condition name"
    )
    revision = Column(
        String(10),
        nullable=False,
        default="A",
        comment="Payment condition revision (A, B, C...)",
    )
    description = Column(Text, nullable=True, comment="Detailed description")

    # Payment terms
    days_to_pay = Column(
        Integer,
        nullable=True,
        comment="Number of days for payment (for NET terms)",
    )
    percentage_advance = Column(
        DECIMAL(5, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Percentage required as advance payment",
    )
    percentage_on_delivery = Column(
        DECIMAL(5, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Percentage due on delivery",
    )
    percentage_after_delivery = Column(
        DECIMAL(5, 2),
        nullable=False,
        default=Decimal("0.00"),
        comment="Percentage due after delivery",
    )
    days_after_delivery = Column(
        Integer,
        nullable=True,
        comment="Days after delivery for final payment",
    )

    # Configuration
    is_default = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether this is the default payment condition",
    )

    # Notes
    notes = Column(Text, nullable=True, comment="Additional notes")

    # Table constraints
    __table_args__ = (
        CheckConstraint(
            "percentage_advance >= 0 AND percentage_advance <= 100",
            name="ck_payment_condition_advance_valid",
        ),
        CheckConstraint(
            "percentage_on_delivery >= 0 AND percentage_on_delivery <= 100",
            name="ck_payment_condition_on_delivery_valid",
        ),
        CheckConstraint(
            "percentage_after_delivery >= 0 AND percentage_after_delivery <= 100",
            name="ck_payment_condition_after_delivery_valid",
        ),
        CheckConstraint(
            "(percentage_advance + percentage_on_delivery + percentage_after_delivery) = 100",
            name="ck_payment_condition_percentages_sum_100",
        ),
    )

    # Validation
    @validates("payment_condition_number")
    def validate_payment_condition_number(self, key: str, value: str) -> str:
        """Validate payment condition number format."""
        if not value or not value.strip():
            raise ValueError("Payment condition number cannot be empty")
        return value.strip().upper()

    @validates("name")
    def validate_name(self, key: str, value: str) -> str:
        """Validate name is not empty."""
        if not value or not value.strip():
            raise ValueError("Payment condition name cannot be empty")
        return value.strip()

    # Business methods
    def validate_percentages(self) -> None:
        """Validate that percentages sum to 100."""
        total = (
            self.percentage_advance
            + self.percentage_on_delivery
            + self.percentage_after_delivery
        )
        if total != Decimal("100.00"):
            raise ValueError(
                f"Payment percentages must sum to 100, got {total}"
            )

    @property
    def summary(self) -> str:
        """Get human-readable summary of payment terms."""
        parts = []
        if self.percentage_advance > 0:
            parts.append(f"{self.percentage_advance}% advance")
        if self.percentage_on_delivery > 0:
            parts.append(f"{self.percentage_on_delivery}% on delivery")
        if self.percentage_after_delivery > 0:
            if self.days_after_delivery:
                parts.append(
                    f"{self.percentage_after_delivery}% {self.days_after_delivery} days after delivery"
                )
            else:
                parts.append(f"{self.percentage_after_delivery}% after delivery")
        if self.days_to_pay and not parts:
            parts.append(f"Net {self.days_to_pay} days")

        return ", ".join(parts) if parts else "Custom terms"

    def __repr__(self) -> str:
        """String representation."""
        return f"<PaymentCondition(id={self.id}, payment_condition_number='{self.payment_condition_number}', name='{self.name}')>"
