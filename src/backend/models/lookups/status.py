from sqlalchemy import CheckConstraint, Column, String
from sqlalchemy.orm import relationship
from .base import LookupBase

class QuoteStatus(LookupBase):
    """
    Estados de cotización.
    """
    __tablename__ = "quote_statuses"

    code = Column(
        String(20),
        nullable=False,
        unique=True,
        index=True,
        comment="Status code (e.g., draft, sent, accepted)",
    )

    # Relationships
    quotes = relationship("Quote", back_populates="status", lazy="select")

    __table_args__ = (
        CheckConstraint(
            "length(trim(code)) > 0",
            name="code_not_empty",
        ),
        CheckConstraint(
            "length(trim(name)) > 0",
            name="name_not_empty",
        ),
    )

class OrderStatus(LookupBase):
    """
    Estados de orden.
    """
    __tablename__ = "order_statuses"

    code = Column(
        String(20),
        nullable=False,
        unique=True,
        index=True,
        comment="Status code",
    )

    # Relationships
    orders = relationship("Order", back_populates="status", lazy="select")

    __table_args__ = (
        CheckConstraint(
            "length(trim(code)) > 0",
            name="code_not_empty",
        ),
        CheckConstraint(
            "length(trim(name)) > 0",
            name="name_not_empty",
        ),
    )

class PaymentStatus(LookupBase):
    """
    Estados de pago.
    """
    __tablename__ = "payment_statuses"

    code = Column(
        String(20),
        nullable=False,
        unique=True,
        index=True,
        comment="Status code",
    )

    __table_args__ = (
        CheckConstraint(
            "length(trim(code)) > 0",
            name="code_not_empty",
        ),
        CheckConstraint(
            "length(trim(name)) > 0",
            name="name_not_empty",
        ),
    )
