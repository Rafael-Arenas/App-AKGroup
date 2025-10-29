"""
Contact models - Company contacts and services.

Modelos para gestionar contactos y servicios/departamentos de empresas:
- Contact: Persona de contacto en una empresa
- Service: Servicio o departamento (ventas, compras, soporte, etc.)
"""

from typing import Optional

from sqlalchemy import Column, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship, validates

from ..base import (
    ActiveMixin,
    AuditMixin,
    Base,
    EmailValidator,
    PhoneValidator,
    TimestampMixin,
)


class Contact(Base, TimestampMixin, AuditMixin, ActiveMixin):
    """
    Contacto de una empresa.

    Representa una persona de contacto asociada a una empresa
    (vendedor, comprador, gerente, etc.)

    Attributes:
        id: Primary key
        first_name: Nombre(s)
        last_name: Apellido(s)
        email: Email de contacto
        phone: Teléfono
        mobile: Teléfono móvil
        position: Cargo/posición
        company_id: FK a companies
        service_id: FK a services (departamento)

    Relationships:
        company: Empresa a la que pertenece
        service: Servicio/departamento

    Properties:
        full_name: Nombre completo

    Example:
        >>> contact = Contact(
        ...     first_name="Juan",
        ...     last_name="Pérez",
        ...     email="jperez@example.com",
        ...     phone="+56912345678",
        ...     position="Gerente de Ventas",
        ...     company_id=1
        ... )
    """

    __tablename__ = "contacts"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Personal Information
    first_name = Column(
        String(50),
        nullable=False,
        comment="First name(s)",
    )

    last_name = Column(
        String(50),
        nullable=False,
        comment="Last name(s)",
    )

    # Contact Information
    email = Column(
        String(100),
        nullable=True,
        index=True,
        comment="Email address",
    )

    phone = Column(
        String(20),
        nullable=True,
        comment="Phone number",
    )

    mobile = Column(
        String(20),
        nullable=True,
        comment="Mobile phone number",
    )

    # Professional Information
    position = Column(
        String(100),
        nullable=True,
        comment="Job position/title",
    )

    # Foreign Keys
    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Company this contact belongs to",
    )

    service_id = Column(
        Integer,
        ForeignKey("services.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Service/department this contact belongs to",
    )

    # Relationships
    company = relationship("Company", back_populates="contacts")
    service = relationship("Service", back_populates="contacts", lazy="joined")

    # Indexes
    __table_args__ = (
        Index("ix_contact_company_active", "company_id", "is_active"),
        # Note: email already has index=True in column definition (line 82)
        # Index("ix_contact_email", "email"),
    )

    # Validators
    @validates("first_name", "last_name")
    def validate_name(self, key: str, value: str) -> str:
        """Valida nombres."""
        if not value or len(value.strip()) == 0:
            raise ValueError(f"{key} cannot be empty")
        return value.strip()

    @validates("email")
    def validate_email(self, key: str, value: Optional[str]) -> Optional[str]:
        """Valida email."""
        return EmailValidator.validate(value)

    @validates("phone", "mobile")
    def validate_phone(self, key: str, value: Optional[str]) -> Optional[str]:
        """Valida teléfonos."""
        return PhoneValidator.validate(value)

    # Properties
    @property
    def full_name(self) -> str:
        """Nombre completo del contacto."""
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"<Contact(id={self.id}, name={self.full_name}, company_id={self.company_id})>"


class Service(Base, TimestampMixin, ActiveMixin):
    """
    Servicio o departamento.

    Representa un departamento, área o servicio de una empresa
    (Ventas, Compras, Soporte Técnico, etc.)

    Attributes:
        id: Primary key
        name: Nombre del servicio/departamento
        description: Descripción

    Relationships:
        contacts: Contactos de este servicio

    Example:
        >>> service = Service(
        ...     name="Ventas",
        ...     description="Departamento de ventas"
        ... )
    """

    __tablename__ = "services"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Service Information
    name = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="Service/department name",
    )

    description = Column(
        String(200),
        nullable=True,
        comment="Service description",
    )

    # Relationships
    contacts = relationship(
        "Contact",
        back_populates="service",
        lazy="select",
    )

    # Validators
    @validates("name")
    def validate_name(self, key: str, value: str) -> str:
        """Valida nombre de servicio."""
        if not value or len(value.strip()) == 0:
            raise ValueError("Service name cannot be empty")
        return value.strip()

    def __repr__(self) -> str:
        return f"<Service(id={self.id}, name={self.name})>"
