"""
Address model - Company addresses.

Modelo para gestionar direcciones de empresas (entregas, facturación, etc.)
"""

from typing import Optional

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship, validates

from src.shared.enums import AddressType
from ..base import AuditMixin, Base, TimestampMixin


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
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Address Fields
    address = Column(
        Text,
        nullable=False,
        comment="Full address text including street, number, and details",
    )

    city = Column(
        String(100),
        nullable=True,
        comment="City name",
    )

    postal_code = Column(
        String(20),
        nullable=True,
        comment="Postal or ZIP code",
    )

    country = Column(
        String(100),
        nullable=True,
        comment="Country name",
    )

    # Metadata
    is_default = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether this is the default address for the company",
    )

    address_type = Column(
        SQLEnum(AddressType),
        nullable=False,
        default=AddressType.DELIVERY,
        index=True,
        comment="Type: delivery, billing, headquarters, branch",
    )

    # Foreign Keys
    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Company owning this address",
    )

    # Relationships
    company = relationship(
        "Company",
        back_populates="addresses",
        lazy="joined",
    )

    # Indexes for performance
    __table_args__ = (
        Index("ix_addresses_company_id_is_default", "company_id", "is_default"),
        # Note: address_type already has index=True in column definition
        CheckConstraint(
            "length(trim(address)) >= 5", name="address_min_length"
        ),
    )

    # Validators
    @validates("address")
    def validate_address(self, key: str, value: str) -> str:
        """
        Valida campo de dirección.

        Args:
            key: Nombre del campo
            value: Dirección a validar

        Returns:
            Dirección validada y normalizada

        Raises:
            ValueError: Si la dirección es muy corta o vacía
        """
        if not value or len(value.strip()) < 5:
            raise ValueError("Address must be at least 5 characters long")
        return value.strip()

    def __repr__(self) -> str:
        return f"<Address(id={self.id}, company_id={self.company_id}, type={self.address_type.value})>"
