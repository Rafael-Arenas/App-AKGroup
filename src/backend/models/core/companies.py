"""
Company models - Business entities.

Modelos para gestión de empresas (clientes, proveedores, partners):
    - Company: Empresa principal
    - CompanyRut: RUTs asociados a una empresa (múltiples)
    - Plant: Plantas de una empresa
    - CompanyTypeEnum: Enum para tipos de empresa
"""

import enum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from ..base import (
    ActiveMixin,
    AuditMixin,
    Base,
    PhoneValidator,
    RutValidator,
    TimestampMixin,
    UrlValidator,
)

if TYPE_CHECKING:
    from ..business.delivery import DeliveryOrder
    from ..business.invoices import InvoiceExport, InvoiceSII
    from ..business.orders import Order
    from ..business.quotes import Quote
    from ..lookups.business import CompanyType
    from ..lookups.geo import City, Country
    from .addresses import Address
    from .contacts import Contact
    from .products import Product


class CompanyTypeEnum(str, enum.Enum):
    """
    Tipos de empresa.

    Enum que representa los tipos de empresa en el sistema.
    Los valores se sincronizan con la tabla company_types.

    Attributes:
        CLIENT: Empresa cliente
        SUPPLIER: Empresa proveedora

    Example:
        >>> company.company_type_enum = CompanyTypeEnum.CLIENT
        >>> if company.company_type_enum == CompanyTypeEnum.SUPPLIER:
        ...     print("Es proveedor")
    """

    CLIENT = "CLIENT"
    SUPPLIER = "SUPPLIER"

    @property
    def display_name(self) -> str:
        """Retorna el nombre para mostrar en español."""
        names = {
            CompanyTypeEnum.CLIENT: "Cliente",
            CompanyTypeEnum.SUPPLIER: "Proveedor",
        }
        return names[self]

    @property
    def description(self) -> str:
        """Retorna la descripción del tipo de empresa."""
        descriptions = {
            CompanyTypeEnum.CLIENT: "Empresa que adquiere productos o servicios",
            CompanyTypeEnum.SUPPLIER: "Empresa que provee productos o servicios",
        }
        return descriptions[self]


class Company(Base, TimestampMixin, AuditMixin, ActiveMixin):
    """
    Empresa (cliente, proveedor, partner, etc.)

    Representa una entidad empresarial que puede ser cliente, proveedor,
    partner o empresa interna.

    Attributes:
        id: Primary key
        name: Nombre legal de la empresa
        trigram: Código único de 3 letras
        main_address: Dirección principal
        phone: Teléfono principal
        website: Sitio web
        intracommunity_number: Número intracomunitario (UE)
        company_type_id: FK a company_types
        country_id: FK a countries
        city_id: FK a cities

    Relationships:
        company_type: Tipo de empresa
        country: País de registro
        city: Ciudad de sede principal
        ruts: RUTs asociados
        plants: Plantas/Sucursales
        addresses: Direcciones
        contacts: Contactos
        products: Productos asociados
        quotes: Cotizaciones
        orders: Órdenes
    """

    __tablename__ = "companies"

    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Company Information
    name: Mapped[str] = mapped_column(
        String(200), index=True, comment="Company legal name"
    )
    trigram: Mapped[str] = mapped_column(
        String(3), unique=True, index=True, comment="Three-letter unique company code"
    )
    main_address: Mapped[str | None] = mapped_column(
        Text, comment="Primary business address (full text)"
    )
    phone: Mapped[str | None] = mapped_column(
        String(20), comment="Main phone number (E.164 format recommended)"
    )
    website: Mapped[str | None] = mapped_column(
        String(200), comment="Company website URL"
    )
    intracommunity_number: Mapped[str | None] = mapped_column(
        String(50), comment="EU intracommunity VAT number"
    )

    # Foreign Keys
    company_type_id: Mapped[int] = mapped_column(
        ForeignKey("company_types.id", ondelete="RESTRICT"),
        index=True,
        comment="Type of company (client, supplier, etc.)",
    )
    country_id: Mapped[int | None] = mapped_column(
        ForeignKey("countries.id", ondelete="RESTRICT"),
        index=True,
        comment="Country of company registration",
    )
    city_id: Mapped[int | None] = mapped_column(
        ForeignKey("cities.id", ondelete="RESTRICT"),
        index=True,
        comment="City of main office",
    )

    # Relationships - Lookups
    company_type: Mapped["CompanyType"] = relationship(
        "CompanyType", back_populates="companies", lazy="joined"
    )
    country: Mapped["Country | None"] = relationship(
        "Country", back_populates="companies", lazy="joined"
    )
    city: Mapped["City | None"] = relationship(
        "City", back_populates="companies", lazy="joined"
    )

    @property
    def company_type_enum(self) -> CompanyTypeEnum | None:
        """Retorna el tipo de empresa como Enum."""
        if not self.company_type:
            return None

        name_upper = self.company_type.name.upper()
        if "CLIENT" in name_upper or "CLIENTE" in name_upper:
            return CompanyTypeEnum.CLIENT
        if "SUPPLIER" in name_upper or "PROVEEDOR" in name_upper:
            return CompanyTypeEnum.SUPPLIER

        try:
            return CompanyTypeEnum[name_upper]
        except (KeyError, AttributeError):
            return None

    # Relationships - Collections
    ruts: Mapped[list["CompanyRut"]] = relationship(
        "CompanyRut",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="select",
    )
    plants: Mapped[list["Plant"]] = relationship(
        "Plant",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="select",
    )
    addresses: Mapped[list["Address"]] = relationship(
        "Address",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="select",
    )
    contacts: Mapped[list["Contact"]] = relationship(
        "Contact",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="select",
    )
    products: Mapped[list["Product"]] = relationship(
        "Product", back_populates="company", lazy="select"
    )
    quotes: Mapped[list["Quote"]] = relationship(
        "Quote", back_populates="company", lazy="select"
    )
    orders: Mapped[list["Order"]] = relationship(
        "Order", back_populates="company", lazy="select"
    )
    invoices_sii: Mapped[list["InvoiceSII"]] = relationship(
        "InvoiceSII", back_populates="company", lazy="select"
    )
    invoices_export: Mapped[list["InvoiceExport"]] = relationship(
        "InvoiceExport", back_populates="company", lazy="select"
    )

    # Indexes
    __table_args__ = (
        Index("ix_companies_name_trgm", "name"),
        Index("ix_companies_type_country", "company_type_id", "country_id"),
    )

    # Validators
    @validates("name")
    def validate_name(self, key: str, value: str) -> str:
        """Valida nombre de empresa."""
        if not value or len(value.strip()) < 2:
            raise ValueError("Company name must be at least 2 characters")
        return value.strip()

    @validates("trigram")
    def validate_trigram(self, key: str, value: str) -> str:
        """Valida trigrama (3 letras, único)."""
        if not value or len(value) != 3:
            raise ValueError("Trigram must be exactly 3 characters")
        if not value.isalpha():
            raise ValueError("Trigram must contain only letters")
        return value.upper()

    @validates("phone")
    def validate_phone(self, key: str, value: str | None) -> str | None:
        """Valida teléfono."""
        return PhoneValidator.validate(value)

    @validates("website")
    def validate_website(self, key: str, value: str | None) -> str | None:
        """Valida URL del sitio web."""
        return UrlValidator.validate(value)

    def __repr__(self) -> str:
        return f"<Company(id={self.id}, name={self.name}, trigram={self.trigram})>"


class CompanyRut(Base, TimestampMixin, AuditMixin):
    """
    RUT asociado a una empresa.

    Una empresa puede tener múltiples RUTs (ej: matriz y sucursales).
    Almacena RUTs chilenos validados.

    Attributes:
        id: Primary key
        rut: RUT chileno (formato: 12345678-9)
        is_main: Si es el RUT principal de la empresa
        company_id: FK a companies

    Relationships:
        company: Empresa a la que pertenece
    """

    __tablename__ = "company_ruts"

    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # RUT Information
    rut: Mapped[str] = mapped_column(
        String(12),
        unique=True,
        index=True,
        comment="Chilean RUT (format: 12345678-9)",
    )
    is_main: Mapped[bool] = mapped_column(
        default=False, comment="Whether this is the main RUT for the company"
    )

    # Foreign Keys
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        index=True,
        comment="Company this RUT belongs to",
    )

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="ruts")

    # Indexes
    __table_args__ = (
        Index("ix_company_rut_company_main", "company_id", "is_main"),
    )

    # Validators
    @validates("rut")
    def validate_rut(self, key: str, value: str) -> str:
        """Valida RUT chileno con dígito verificador."""
        return RutValidator.validate(value)

    def __repr__(self) -> str:
        return f"<CompanyRut(id={self.id}, rut={self.rut}, main={self.is_main})>"


class Plant(Base, TimestampMixin, AuditMixin, ActiveMixin):
    """
    Planta de una empresa.

    Representa una sede, oficina, planta o sucursal de una empresa.

    Attributes:
        id: Primary key
        name: Nombre de la planta
        address: Dirección de la planta
        phone: Teléfono de la planta
        email: Email de contacto
        company_id: FK a companies
        city_id: FK a cities

    Relationships:
        company: Empresa matriz
        city: Ciudad donde está ubicada
    """

    __tablename__ = "plants"

    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Plant Information
    name: Mapped[str] = mapped_column(String(100), comment="Plant name")
    address: Mapped[str | None] = mapped_column(
        Text, comment="Plant address (full text)"
    )
    phone: Mapped[str | None] = mapped_column(String(20), comment="Plant phone number")
    email: Mapped[str | None] = mapped_column(String(100), comment="Plant contact email")

    # Foreign Keys
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"),
        index=True,
        comment="Company this plant belongs to",
    )
    city_id: Mapped[int | None] = mapped_column(
        ForeignKey("cities.id", ondelete="RESTRICT"),
        index=True,
        comment="City where plant is located",
    )

    # Relationships
    company: Mapped["Company"] = relationship("Company", back_populates="plants")
    city: Mapped["City | None"] = relationship(
        "City", back_populates="plants", lazy="joined"
    )

    # Indexes
    __table_args__ = (Index("ix_plant_company_active", "company_id", "is_active"),)

    # Validators
    @validates("name")
    def validate_name(self, key: str, value: str) -> str:
        """Valida nombre de planta."""
        if not value or len(value.strip()) < 2:
            raise ValueError("Plant name must be at least 2 characters")
        return value.strip()

    @validates("phone")
    def validate_phone(self, key: str, value: str | None) -> str | None:
        """Valida teléfono."""
        return PhoneValidator.validate(value)

    def __repr__(self) -> str:
        return f"<Plant(id={self.id}, name={self.name}, company_id={self.company_id})>"
