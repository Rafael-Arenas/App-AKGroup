"""
Company models - Business entities.

Modelos para gestión de empresas (clientes, proveedores, partners):
    - Company: Empresa principal
    - CompanyRut: RUTs asociados a una empresa (múltiples)
    - Plant: Plantas de una empresa
    - CompanyTypeEnum: Enum para tipos de empresa
"""

import enum
import re
from typing import Optional

from sqlalchemy import Boolean, Column, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship, validates

from ..base import (
    ActiveMixin,
    AuditMixin,
    Base,
    PhoneValidator,
    RutValidator,
    TimestampMixin,
    UrlValidator,
)


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
        """
        Retorna el nombre para mostrar en español.

        Returns:
            Nombre en español del tipo de empresa

        Example:
            >>> CompanyTypeEnum.CLIENT.display_name
            'Cliente'
        """
        names = {
            CompanyTypeEnum.CLIENT: "Cliente",
            CompanyTypeEnum.SUPPLIER: "Proveedor",
        }
        return names[self]

    @property
    def description(self) -> str:
        """
        Retorna la descripción del tipo de empresa.

        Returns:
            Descripción detallada

        Example:
            >>> CompanyTypeEnum.CLIENT.description
            'Empresa que adquiere productos o servicios'
        """
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

    Example:
        >>> company = Company(
        ...     name="AK Group SpA",
        ...     trigram="AKG",
        ...     phone="+56912345678",
        ...     website="https://akgroup.cl",
        ...     company_type_id=1,  # Cliente
        ...     country_id=1  # Chile
        ... )
    """

    __tablename__ = "companies"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Company Information
    name = Column(
        String(200),
        nullable=False,
        index=True,
        comment="Company legal name",
    )

    trigram = Column(
        String(3),
        nullable=False,
        unique=True,
        index=True,
        comment="Three-letter unique company code",
    )

    main_address = Column(
        Text,
        nullable=True,
        comment="Primary business address (full text)",
    )

    phone = Column(
        String(20),
        nullable=True,
        comment="Main phone number (E.164 format recommended)",
    )

    website = Column(
        String(200),
        nullable=True,
        comment="Company website URL",
    )

    intracommunity_number = Column(
        String(50),
        nullable=True,
        comment="EU intracommunity VAT number",
    )

    # Foreign Keys
    company_type_id = Column(
        Integer,
        ForeignKey("company_types.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Type of company (client, supplier, etc.)",
    )

    country_id = Column(
        Integer,
        ForeignKey("countries.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
        comment="Country of company registration",
    )

    city_id = Column(
        Integer,
        ForeignKey("cities.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
        comment="City of main office",
    )

    # Relationships
    company_type = relationship("CompanyType", back_populates="companies", lazy="joined")
    country = relationship("Country", back_populates="companies", lazy="joined")
    city = relationship("City", back_populates="companies", lazy="joined")

    @property
    def company_type_enum(self) -> Optional[CompanyTypeEnum]:
        """
        Retorna el tipo de empresa como Enum.

        Convierte el nombre de la tabla company_types al Enum correspondiente.

        Returns:
            CompanyTypeEnum o None si no existe company_type

        Example:
            >>> company = Company(...)
            >>> if company.company_type_enum == CompanyTypeEnum.CLIENT:
            ...     print("Es cliente")
        """
        if not self.company_type:
            return None
        try:
            return CompanyTypeEnum[self.company_type.name.upper()]
        except (KeyError, AttributeError):
            return None

    ruts = relationship(
        "CompanyRut",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="select",
    )

    plants = relationship(
        "Plant",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="select",
    )

    addresses = relationship(
        "Address",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="select",
    )

    contacts = relationship(
        "Contact",
        back_populates="company",
        cascade="all, delete-orphan",
        lazy="select",
    )

    products = relationship(
        "Product",
        back_populates="company",
        lazy="select",
    )

    quotes = relationship(
        "Quote",
        back_populates="company",
        lazy="select",
    )

    orders = relationship(
        "Order",
        back_populates="company",
        lazy="select",
    )

    invoices_sii = relationship(
        "InvoiceSII",
        back_populates="company",
        lazy="select",
    )

    invoices_export = relationship(
        "InvoiceExport",
        back_populates="company",
        lazy="select",
    )

    # Indexes
    __table_args__ = (
        Index("ix_companies_name_trgm", "name"),  # Para búsqueda full-text
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
    def validate_phone(self, key: str, value: Optional[str]) -> Optional[str]:
        """Valida teléfono."""
        return PhoneValidator.validate(value)

    @validates("website")
    def validate_website(self, key: str, value: Optional[str]) -> Optional[str]:
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

    Example:
        >>> rut = CompanyRut(
        ...     rut="76.123.456-7",
        ...     is_main=True,
        ...     company_id=1
        ... )
        >>> print(rut.rut)
        '76123456-7'
    """

    __tablename__ = "company_ruts"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # RUT Information
    rut = Column(
        String(12),
        nullable=False,
        unique=True,
        index=True,
        comment="Chilean RUT (format: 12345678-9)",
    )

    is_main = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Whether this is the main RUT for the company",
    )

    # Foreign Keys
    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Company this RUT belongs to",
    )

    # Relationships
    company = relationship("Company", back_populates="ruts")

    # Indexes
    __table_args__ = (
        Index("ix_company_rut_company_main", "company_id", "is_main"),
    )

    # Validators
    @validates("rut")
    def validate_rut(self, key: str, value: str) -> str:
        """
        Valida RUT chileno con dígito verificador.

        Args:
            key: Nombre del campo
            value: RUT a validar

        Returns:
            RUT normalizado (sin puntos, con guión)

        Raises:
            ValueError: Si el RUT es inválido
        """
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

    Example:
        >>> plant = Plant(
        ...     name="Planta Santiago Centro",
        ...     address="Av. Providencia 123",
        ...     phone="+56912345678",
        ...     company_id=1,
        ...     city_id=5
        ... )
    """

    __tablename__ = "plants"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Plant Information
    name = Column(
        String(100),
        nullable=False,
        comment="Plant name",
    )

    address = Column(
        Text,
        nullable=True,
        comment="Plant address (full text)",
    )

    phone = Column(
        String(20),
        nullable=True,
        comment="Plant phone number",
    )

    email = Column(
        String(100),
        nullable=True,
        comment="Plant contact email",
    )

    # Foreign Keys
    company_id = Column(
        Integer,
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Company this plant belongs to",
    )

    city_id = Column(
        Integer,
        ForeignKey("cities.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
        comment="City where plant is located",
    )

    # Relationships
    company = relationship("Company", back_populates="plants")
    city = relationship("City", back_populates="plants", lazy="joined")

    # Indexes
    __table_args__ = (
        Index("ix_plant_company_active", "company_id", "is_active"),
    )

    # Validators
    @validates("name")
    def validate_name(self, key: str, value: str) -> str:
        """Valida nombre de planta."""
        if not value or len(value.strip()) < 2:
            raise ValueError("Plant name must be at least 2 characters")
        return value.strip()

    @validates("phone")
    def validate_phone(self, key: str, value: Optional[str]) -> Optional[str]:
        """Valida teléfono."""
        return PhoneValidator.validate(value)

    def __repr__(self) -> str:
        return f"<Plant(id={self.id}, name={self.name}, company_id={self.company_id})>"
