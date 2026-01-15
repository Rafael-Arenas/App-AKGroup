"""
Status lookup models.

This module contains status lookup tables for business entities:
QuoteStatus, OrderStatus, PaymentStatus.
"""

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import LookupBase

if TYPE_CHECKING:
    from ..business.orders import Order
    from ..business.quotes import Quote


class QuoteStatus(LookupBase):
    """
    Estados de cotización.

    Attributes:
        id: Primary key (inherited)
        name: Status display name (inherited)
        description: Description (inherited)
        code: Status code (e.g., draft, sent, accepted)
    """

    __tablename__ = "quote_statuses"

    code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True,
        comment="Status code (e.g., draft, sent, accepted)",
    )

    # Relationships
    quotes: Mapped[list["Quote"]] = relationship(
        "Quote", back_populates="status", lazy="select"
    )

    __table_args__ = (
        CheckConstraint("length(trim(code)) > 0", name="code_not_empty"),
        CheckConstraint("length(trim(name)) > 0", name="name_not_empty"),
    )


class OrderStatus(LookupBase):
    """
    Estados de orden.

    Attributes:
        id: Primary key (inherited)
        name: Status display name (inherited)
        description: Description (inherited)
        code: Status code
    """

    __tablename__ = "order_statuses"

    code: Mapped[str] = mapped_column(
        String(20), unique=True, index=True, comment="Status code"
    )

    # Relationships
    orders: Mapped[list["Order"]] = relationship(
        "Order", back_populates="status", lazy="select"
    )

    __table_args__ = (
        CheckConstraint("length(trim(code)) > 0", name="code_not_empty"),
        CheckConstraint("length(trim(name)) > 0", name="name_not_empty"),
    )


class PaymentStatus(LookupBase):
    """
    Estados de pago.

    Attributes:
        id: Primary key (inherited)
        name: Status display name (inherited)
        description: Description (inherited)
        code: Status code
    """

    __tablename__ = "payment_statuses"

    code: Mapped[str] = mapped_column(
        String(20), unique=True, index=True, comment="Status code"
    )

    __table_args__ = (
        CheckConstraint("length(trim(code)) > 0", name="code_not_empty"),
        CheckConstraint("length(trim(name)) > 0", name="name_not_empty"),
    )
