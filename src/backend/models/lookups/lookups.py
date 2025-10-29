"""
Lookup tables (tablas de catálogo/referencia).

Este módulo contiene 12 modelos de tablas de referencia (lookups)
que son usadas como catálogos en todo el sistema:

1. Country - Países
2. City - Ciudades
3. CompanyType - Tipos de empresa (cliente, proveedor, etc.)
4. Incoterm - Términos comerciales internacionales
5. Currency - Monedas
6. Unit - Unidades de medida
7. FamilyType - Familias de productos
8. Matter - Materiales/Materias
9. SalesType - Tipos de venta
10. QuoteStatus - Estados de cotización
11. OrderStatus - Estados de orden
12. PaymentStatus - Estados de pago

Estas tablas son relativamente estáticas y se usan como foreign keys
en otros modelos del sistema.
"""

from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import relationship

from ..base import ActiveMixin, Base, TimestampMixin


# ========== 1. COUNTRY ==========
class Country(Base, TimestampMixin):
    """
    Países.

    Tabla de referencia para países del mundo.
    Incluye códigos ISO 3166-1 alpha-2 y alpha-3.

    Attributes:
        id: Primary key
        name: Nombre del país (ej: "Chile", "Francia")
        iso_code_alpha2: Código ISO alpha-2 (ej: "CL", "FR")
        iso_code_alpha3: Código ISO alpha-3 (ej: "CHL", "FRA")

    Relationships:
        cities: Ciudades de este país
        companies: Empresas registradas en este país
    """

    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="Country name",
    )

    iso_code_alpha2 = Column(
        String(2),
        unique=True,
        comment="ISO 3166-1 alpha-2 code (e.g., CL, FR, US)",
    )

    iso_code_alpha3 = Column(
        String(3),
        unique=True,
        comment="ISO 3166-1 alpha-3 code (e.g., CHL, FRA, USA)",
    )

    # Relationships
    cities = relationship("City", back_populates="country", lazy="select")
    companies = relationship("Company", back_populates="country", lazy="select")

    __table_args__ = (
        CheckConstraint(
            "length(trim(name)) >= 2",
            name="name_min_length",
        ),
        CheckConstraint(
            "iso_code_alpha2 IS NULL OR length(iso_code_alpha2) = 2",
            name="alpha2_length",
        ),
        CheckConstraint(
            "iso_code_alpha3 IS NULL OR length(iso_code_alpha3) = 3",
            name="alpha3_length",
        ),
    )


# ========== 2. CITY ==========
class City(Base, TimestampMixin):
    """
    Ciudades.

    Ciudades asociadas a países.
    Una ciudad puede existir en múltiples países (ej: "Santiago" en Chile y España).

    Attributes:
        id: Primary key
        name: Nombre de la ciudad
        country_id: FK a countries

    Relationships:
        country: País al que pertenece
        companies: Empresas ubicadas en esta ciudad
        branches: Sucursales ubicadas en esta ciudad
    """

    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(
        String(100),
        nullable=False,
        index=True,
        comment="City name",
    )

    country_id = Column(
        Integer,
        ForeignKey("countries.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="Country this city belongs to",
    )

    # Relationships
    country = relationship("Country", back_populates="cities", lazy="joined")
    companies = relationship("Company", back_populates="city", lazy="select")
    branches = relationship("Branch", back_populates="city", lazy="select")

    __table_args__ = (
        # Unique constraint compuesto: misma ciudad puede existir en diferentes países
        Index("uq_city_name_country", "name", "country_id", unique=True),
        CheckConstraint(
            "length(trim(name)) >= 2",
            name="name_min_length",
        ),
    )


# ========== 3. COMPANY TYPE ==========
class CompanyType(Base, TimestampMixin):
    """
    Tipos de empresa.

    Clasificación de empresas: cliente, proveedor, partner, interno, etc.

    Attributes:
        id: Primary key
        name: Nombre del tipo (ej: "Cliente", "Proveedor")
        description: Descripción detallada

    Relationships:
        companies: Empresas de este tipo
    """

    __tablename__ = "company_types"

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        comment="Company type name",
    )

    description = Column(
        Text,
        comment="Detailed description of this company type",
    )

    # Relationships
    companies = relationship("Company", back_populates="company_type", lazy="select")

    __table_args__ = (
        CheckConstraint(
            "length(trim(name)) > 0",
            name="name_not_empty",
        ),
    )


# ========== 4. INCOTERM ==========
class Incoterm(Base, TimestampMixin, ActiveMixin):
    """
    International Commercial Terms (Incoterms 2020).

    Términos comerciales internacionales que definen responsabilidades
    entre comprador y vendedor en transacciones internacionales.

    Ver: https://iccwbo.org/resources-for-business/incoterms-rules/

    Attributes:
        id: Primary key
        code: Código del incoterm (ej: "EXW", "FOB", "CIF")
        name: Nombre completo (ej: "Ex Works")
        description: Descripción detallada
        is_active: Si está activo para uso

    Examples:
        - EXW: Ex Works
        - FCA: Free Carrier
        - FOB: Free On Board
        - CIF: Cost Insurance and Freight
    """

    __tablename__ = "incoterms"

    id = Column(Integer, primary_key=True, autoincrement=True)

    code = Column(
        String(3),
        nullable=False,
        unique=True,
        index=True,
        comment="Incoterm code (e.g., EXW, FOB, CIF)",
    )

    name = Column(
        String(100),
        nullable=False,
        comment="Full name (e.g., Ex Works)",
    )

    description = Column(
        Text,
        comment="Detailed description of responsibilities",
    )

    __table_args__ = (
        CheckConstraint(
            "length(code) = 3",
            name="code_exact_length",
        ),
        CheckConstraint(
            "length(trim(name)) > 0",
            name="name_not_empty",
        ),
    )


# ========== 5. CURRENCY ==========
class Currency(Base, TimestampMixin, ActiveMixin):
    """
    Monedas (ISO 4217).

    Monedas utilizadas en el sistema para precios y transacciones.

    Attributes:
        id: Primary key
        code: Código ISO 4217 (ej: "CLP", "EUR", "USD")
        name: Nombre completo (ej: "Chilean Peso", "Euro")
        symbol: Símbolo (ej: "$", "€", "US$")
        is_active: Si está activa para uso

    Examples:
        - CLP: Chilean Peso ($)
        - EUR: Euro (€)
        - USD: US Dollar (US$)
    """

    __tablename__ = "currencies"

    id = Column(Integer, primary_key=True, autoincrement=True)

    code = Column(
        String(3),
        nullable=False,
        unique=True,
        index=True,
        comment="ISO 4217 currency code (e.g., CLP, EUR, USD)",
    )

    name = Column(
        String(50),
        nullable=False,
        comment="Full currency name",
    )

    symbol = Column(
        String(5),
        comment="Currency symbol (e.g., $, €, US$)",
    )

    __table_args__ = (
        CheckConstraint(
            "length(code) = 3",
            name="code_exact_length",
        ),
        CheckConstraint(
            "length(trim(name)) > 0",
            name="name_not_empty",
        ),
    )


# ========== 6. UNIT ==========
class Unit(Base, TimestampMixin, ActiveMixin):
    """
    Unidades de medida.

    Unidades para cantidades de productos (piezas, kg, metros, etc.)

    Attributes:
        id: Primary key
        code: Código de la unidad (ej: "pcs", "kg", "m")
        name: Nombre completo (ej: "Pieces", "Kilogram")
        description: Descripción
        is_active: Si está activa para uso

    Examples:
        - pcs: Pieces (piezas)
        - kg: Kilogram
        - m: Meter
        - l: Liter
    """

    __tablename__ = "units"

    id = Column(Integer, primary_key=True, autoincrement=True)

    code = Column(
        String(10),
        nullable=False,
        unique=True,
        index=True,
        comment="Unit code (e.g., pcs, kg, m, l)",
    )

    name = Column(
        String(50),
        nullable=False,
        comment="Full unit name",
    )

    description = Column(
        Text,
        comment="Detailed description",
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


# ========== 7. FAMILY TYPE ==========
class FamilyType(Base, TimestampMixin):
    """
    Familias de productos.

    Clasificación de productos por familia/categoría.

    Attributes:
        id: Primary key
        name: Nombre de la familia (ej: "Mecánico", "Eléctrico")
        description: Descripción detallada

    Relationships:
        products: Productos de esta familia

    Examples:
        - Mecánico
        - Eléctrico
        - Consumibles
        - Herramientas
    """

    __tablename__ = "family_types"

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="Family type name",
    )

    description = Column(
        Text,
        comment="Detailed description of this family type",
    )

    # Relationships
    products = relationship("Product", back_populates="family_type", lazy="select")

    __table_args__ = (
        CheckConstraint(
            "length(trim(name)) > 0",
            name="name_not_empty",
        ),
    )


# ========== 8. MATTER ==========
class Matter(Base, TimestampMixin):
    """
    Materiales/Materias.

    Tipo de material del producto (acero, aluminio, plástico, etc.)

    Attributes:
        id: Primary key
        name: Nombre del material
        description: Descripción y propiedades

    Relationships:
        products: Productos fabricados con este material

    Examples:
        - Acero inoxidable
        - Aluminio
        - Plástico ABS
        - Madera
    """

    __tablename__ = "matters"

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="Material name",
    )

    description = Column(
        Text,
        comment="Material description and properties",
    )

    # Relationships
    products = relationship("Product", back_populates="matter", lazy="select")

    __table_args__ = (
        CheckConstraint(
            "length(trim(name)) > 0",
            name="name_not_empty",
        ),
    )


# ========== 9. SALES TYPE ==========
class SalesType(Base, TimestampMixin):
    """
    Tipos de venta.

    Clasificación de tipos de venta (retail, wholesale, export, etc.)

    Attributes:
        id: Primary key
        name: Nombre del tipo de venta
        description: Descripción

    Relationships:
        products: Productos asociados a este tipo de venta

    Examples:
        - Retail (venta minorista)
        - Wholesale (venta mayorista)
        - Export (exportación)
        - Domestic (mercado local)
    """

    __tablename__ = "sales_types"

    id = Column(Integer, primary_key=True, autoincrement=True)

    name = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True,
        comment="Sales type name",
    )

    description = Column(
        Text,
        comment="Description of sales type",
    )

    # Relationships
    products = relationship("Product", back_populates="sales_type", lazy="select")

    __table_args__ = (
        CheckConstraint(
            "length(trim(name)) > 0",
            name="name_not_empty",
        ),
    )


# ========== 10. QUOTE STATUS ==========
class QuoteStatus(Base, TimestampMixin):
    """
    Estados de cotización.

    Estados posibles para cotizaciones (draft, sent, accepted, etc.)

    Attributes:
        id: Primary key
        code: Código del estado (ej: "draft", "sent")
        name: Nombre descriptivo
        description: Descripción

    Relationships:
        quotes: Cotizaciones con este estado

    Examples:
        - draft: Borrador
        - sent: Enviada
        - accepted: Aceptada
        - rejected: Rechazada
        - expired: Expirada
    """

    __tablename__ = "quote_statuses"

    id = Column(Integer, primary_key=True, autoincrement=True)

    code = Column(
        String(20),
        nullable=False,
        unique=True,
        index=True,
        comment="Status code (e.g., draft, sent, accepted)",
    )

    name = Column(
        String(50),
        nullable=False,
        comment="Status display name",
    )

    description = Column(
        Text,
        comment="Detailed description",
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


# ========== 11. ORDER STATUS ==========
class OrderStatus(Base, TimestampMixin):
    """
    Estados de orden.

    Estados posibles para órdenes de compra/venta.

    Attributes:
        id: Primary key
        code: Código del estado
        name: Nombre descriptivo
        description: Descripción

    Relationships:
        orders: Órdenes con este estado

    Examples:
        - pending: Pendiente
        - confirmed: Confirmada
        - in_production: En producción
        - shipped: Enviada
        - delivered: Entregada
        - cancelled: Cancelada
    """

    __tablename__ = "order_statuses"

    id = Column(Integer, primary_key=True, autoincrement=True)

    code = Column(
        String(20),
        nullable=False,
        unique=True,
        index=True,
        comment="Status code",
    )

    name = Column(
        String(50),
        nullable=False,
        comment="Status display name",
    )

    description = Column(
        Text,
        comment="Detailed description",
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


# ========== 12. PAYMENT STATUS ==========
class PaymentStatus(Base, TimestampMixin):
    """
    Estados de pago.

    Estados posibles para pagos/condiciones de pago.

    Attributes:
        id: Primary key
        code: Código del estado
        name: Nombre descriptivo
        description: Descripción

    Examples:
        - pending: Pendiente
        - partial: Pago parcial
        - paid: Pagado
        - overdue: Vencido
        - cancelled: Cancelado
    """

    __tablename__ = "payment_statuses"

    id = Column(Integer, primary_key=True, autoincrement=True)

    code = Column(
        String(20),
        nullable=False,
        unique=True,
        index=True,
        comment="Status code",
    )

    name = Column(
        String(50),
        nullable=False,
        comment="Status display name",
    )

    description = Column(
        Text,
        comment="Detailed description",
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
