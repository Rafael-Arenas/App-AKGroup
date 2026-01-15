"""
Address model - Company addresses.

Modelo para gestionar direcciones de empresas (entregas, facturación, etc.)
"""

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Enum as SQLEnum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from src.shared.enums import AddressType

from ..base import AuditMixin, Base, TimestampMixin

if TYPE_CHECKING:
    from .companies import Company


class Address(Base, TimestampMixin, AuditMixin):
    """
    Dirección de una empresa.

    Representa una dirección física asociada a una empresa,
    puede ser de entrega, facturación, sede, etc.

    Attributes:
        id: Primary key
        address: Dirección completa (calle, número, detalles)
        city: Ciudad
        postal_code: Código postal
        country: País
        is_default: Si es la dirección por defecto
        address_type: Tipo de dirección
        company_id: FK a companies

    Relationships:
        company: Empresa a la que pertenece

    Example:
        >>> address = Address(
        ...     address="Av. Providencia 1234, Oficina 501",
        ...     city="Santiago",
        ...     postal_code="7500000",
        ...     country="Chile",
        ...     is_default=True,
        ...     address_type=AddressType.DELIVERY,
        ...     company_id=1
        ... )
    """

    __tablename__ = "addresses"

    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Address Fields
    address: Mapped[str] = mapped_column(
        Text, comment="Full address text including street, number, and details"
    )
    city: Mapped[str | None] = mapped_column(String(100), comment="City name")
    postal_code: Mapped[str | None] = mapped_column(
        String(20), comment="Postal or ZIP code"
    )
    country: Mapped[str | None] = mapped_column(String(100), comment="Country name")

    # Metadata
    is_default: Mapped[bool] = mapped_column(
        default=False, comment="Whether this is the default address for the company"
    )
    address_type: Mapped[AddressType] = mapped_column(
        SQLEnum(AddressType),
        default=AddressType.DELIVERY,
        index=True,
        comment="Type: delivery, billing, headquarters, plant",
    )

    # Foreign Keys
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        index=True,
        comment="Company owning this address",
    )

    # Relationships
    company: Mapped["Company"] = relationship(
        "Company", back_populates="addresses", lazy="joined"
    )

    # Indexes
    __table_args__ = (
        Index("ix_addresses_company_id_is_default", "company_id", "is_default"),
        CheckConstraint("length(trim(address)) >= 5", name="address_min_length"),
    )

    # Validators
    @validates("address")
    def validate_address(self, key: str, value: str) -> str:
        """Valida campo de dirección."""
        if not value or len(value.strip()) < 5:
            raise ValueError("Address must be at least 5 characters long")
        return value.strip()

    def __repr__(self) -> str:
        return f"<Address(id={self.id}, company_id={self.company_id}, type={self.address_type.value})>"
