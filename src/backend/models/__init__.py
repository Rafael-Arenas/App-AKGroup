"""
Models package - Sistema de modelos SQLAlchemy de AK Group.

Este es el punto de entrada principal para todos los modelos del sistema.
Organizado en 4 categorías:

1. base/ - Infraestructura base (Base, Mixins, Validators)
2. lookups/ - Tablas de catálogo (Country, Currency, etc.)
3. core/ - Modelos fundamentales (Staff, Company, Product, etc.)
4. business/ - Modelos de negocio (Quote, Order, Invoice, etc.)

Usage:
    # Importar desde el package principal
    from models import Base, metadata
    from models import Country, Currency
    from models import Product, Company
    from models import Quote, Order, InvoiceSII, DeliveryOrder

    # O importar directamente de subcarpetas
    from models.base import Base, TimestampMixin, EmailValidator
    from models.lookups import Country, City, Currency
    from models.business import Quote, QuoteProduct, Order

Fases de implementación:
    ✅ Fase 1: Base infrastructure (base/)
    ✅ Fase 2: Lookup tables (lookups/)
    ✅ Fase 3: Core models (core/)
    ✅ Fase 4: Business models (business/) - COMPLETADO
"""

# ========== FASE 1: BASE INFRASTRUCTURE ==========
from .base import (
    NAMING_CONVENTION,
    ActiveMixin,
    AuditMixin,
    Base,
    BaseModel,
    DecimalValidator,
    EmailValidator,
    PhoneValidator,
    RutValidator,
    SoftDeleteMixin,
    TimestampMixin,
    UrlValidator,
    metadata,
)

# ========== FASE 2: LOOKUP TABLES ==========
from .lookups import (
    City,
    CompanyType,
    Country,
    Currency,
    FamilyType,
    Incoterm,
    Matter,
    OrderStatus,
    PaymentStatus,
    PaymentType,
    QuoteStatus,
    SalesType,
    Unit,
)

# ========== FASE 3: CORE MODELS ========== (100% Completado)
from .core import (
    Address,
    AddressType,
    Plant,
    Company,
    CompanyRut,
    CompanyTypeEnum,
    Contact,
    Note,
    NotePriority,
    PriceCalculationMode,
    Product,
    ProductComponent,
    ProductType,
    Service,
    Staff,
)

# ========== FASE 4: BUSINESS MODELS ========== (✅ Completado)
from .business import (
    DeliveryDate,
    DeliveryOrder,
    InvoiceExport,
    InvoiceSII,
    Order,
    PaymentCondition,
    Quote,
    QuoteProduct,
    Transport,
)

__all__ = [
    # Base infrastructure
    "Base",
    "metadata",
    "NAMING_CONVENTION",
    "BaseModel",
    # Mixins
    "TimestampMixin",
    "AuditMixin",
    "SoftDeleteMixin",
    "ActiveMixin",
    # Validators
    "EmailValidator",
    "PhoneValidator",
    "RutValidator",
    "UrlValidator",
    "DecimalValidator",
    # Lookup tables
    "Country",
    "City",
    "CompanyType",
    "Incoterm",
    "Currency",
    "Unit",
    "FamilyType",
    "Matter",
    "SalesType",
    "PaymentType",
    "QuoteStatus",
    "OrderStatus",
    "PaymentStatus",
    # Core models (Fase 3 - 100% Completado)
    "Staff",
    "Note",
    "NotePriority",
    "Company",
    "CompanyRut",
    "CompanyTypeEnum",
    "Plant",
    "Contact",
    "Service",
    "Address",
    "AddressType",
    "Product",
    "ProductComponent",
    "ProductType",
    "PriceCalculationMode",
    # Business models (Fase 4 - ✅ Completado)
    "Quote",
    "QuoteProduct",
    "Order",
    "InvoiceSII",
    "InvoiceExport",
    "DeliveryOrder",
    "DeliveryDate",
    "Transport",
    "PaymentCondition",
]

# Metadata para Alembic
# En migrations/env.py:
#   from models import Base
#   target_metadata = Base.metadata
