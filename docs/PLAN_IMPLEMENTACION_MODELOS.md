# Plan de Implementación de Modelos - AK Group

**Fecha de Creación**: 2025-01-25
**Versión**: 1.0
**Proyecto**: App-AKGroup - Sistema de Gestión Empresarial
**Arquitectura Base**: Sistema Unificado de Productos + Estructura Modular

---

## 📋 Índice

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Arquitectura Propuesta](#arquitectura-propuesta)
3. [Fases de Implementación](#fases-de-implementación)
4. [Orden de Implementación](#orden-de-implementación)
5. [Plan Detallado por Fase](#plan-detallado-por-fase)
6. [Migraciones de Base de Datos](#migraciones-de-base-de-datos)
7. [Testing Strategy](#testing-strategy)
8. [Criterios de Aceptación](#criterios-de-aceptación)
9. [Cronograma Estimado](#cronograma-estimado)
10. [Riesgos y Mitigación](#riesgos-y-mitigación)

---

## 1. Resumen Ejecutivo

### 🎯 Objetivo

Implementar un sistema de modelos SQLAlchemy moderno, escalable y mantenible, basado en:

1. **Sistema Unificado de Productos**: Tabla única polimórfica (`products`) que reemplaza `articles` y `nomenclatures`
2. **Estructura Modular**: Organización en subcarpetas (`base/`, `lookups/`, `core/`, `business/`)
3. **Best Practices**: Mixins, validaciones, índices, constraints, auditoría completa

### 📊 Alcance

- **31 modelos** organizados en 4 categorías
- **14 archivos** Python distribuidos en subcarpetas
- **~1950 líneas** de código estimadas
- **Migración completa** desde estructura actual

### ✅ Beneficios Esperados

| Aspecto | Mejora |
|---------|--------|
| **Mantenibilidad** | +80% (código organizado por dominio) |
| **Performance** | +40% (índices optimizados, menos JOINs) |
| **Escalabilidad** | +90% (arquitectura modular) |
| **Integridad de Datos** | +100% (constraints, validaciones, auditoría) |
| **Flexibilidad** | +70% (sistema unificado de productos) |

---

## 2. Arquitectura Propuesta

### 📁 Estructura de Carpetas

```
models/
├── __init__.py                 # Exporta todos los modelos
│
├── base/                       # 🔧 Infraestructura Base (Sin dependencias)
│   ├── __init__.py
│   ├── base.py                 # Base declarativa + naming conventions
│   ├── mixins.py               # TimestampMixin, AuditMixin, SoftDeleteMixin, ActiveMixin
│   └── validators.py           # EmailValidator, PhoneValidator, RutValidator
│
├── lookups/                    # 📚 Tablas de Catálogo (Depende: base/)
│   ├── __init__.py
│   └── lookups.py              # 12 modelos lookup
│
├── core/                       # ⚙️ Modelos Fundamentales (Depende: base/, lookups/)
│   ├── __init__.py
│   ├── staff.py                # Staff (usuarios del sistema)
│   ├── notes.py                # Note (sistema polimórfico)
│   ├── companies.py            # Company, CompanyRut, Branch
│   ├── contacts.py             # Contact, Service
│   ├── addresses.py            # Address
│   └── products.py             # ⭐ Product, ProductComponent (Sistema Unificado)
│
└── business/                   # 💼 Modelos de Negocio (Depende: base/, lookups/, core/)
    ├── __init__.py
    ├── quotes.py               # Quote, QuoteProduct
    ├── orders.py               # Order
    ├── invoices.py             # InvoiceSII, InvoiceExport
    └── delivery.py             # DeliveryOrder, DeliveryDate, Transport, PaymentCondition
```

### 🔄 Flujo de Dependencias

```
┌─────────────────────────────────────────┐
│  base/ (Base, Mixins, Validators)       │
│  - Sin dependencias externas            │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│  lookups/ (Country, Currency, etc.)     │
│  - Depende solo de: base/               │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│  core/ (Staff, Company, Product, etc.)  │
│  - Depende de: base/, lookups/          │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│  business/ (Quote, Order, Invoice)      │
│  - Depende de: base/, lookups/, core/   │
└─────────────────────────────────────────┘
```

### ⭐ Sistema Unificado de Productos

**Concepto Clave**: Una sola tabla `products` con polimorfismo de tipo

```
┌─────────────────────────────────────────────────────────────┐
│                        PRODUCTS                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   ARTICLE    │  │ NOMENCLATURE │  │   SERVICE    │     │
│  │  (simple)    │  │  (compuesto) │  │   (futuro)   │     │
│  │              │  │              │  │              │     │
│  │ - Tornillo   │  │ - Kit        │  │ - Montaje    │     │
│  │ - Placa      │  │ - Ensamblaje │  │ - Pintura    │     │
│  │ - Tuerca     │  │ - Conjunto   │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                           ▲                                 │
│                    product_type (Enum)                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  PRODUCT_COMPONENTS (BOM)                   │
│                                                              │
│  parent_id (NOMENCLATURE) ──┬──> child_id (ARTICLE/NOMEN)  │
│  quantity                   │                                │
│  sequence                   │                                │
│                                                              │
│  Ejemplo:                                                    │
│  Kit-001 (parent) ───2x───> Tornillo (child)                │
│  Kit-001 (parent) ───4x───> Tuerca (child)                  │
│  Ensamblaje ──────1x─────> Kit-001 (child)                  │
└─────────────────────────────────────────────────────────────┘
```

**Ventajas**:
- ✅ Código único (DRY)
- ✅ Queries simples (menos JOINs)
- ✅ Fácil conversión entre tipos
- ✅ BOM jerárquico ilimitado
- ✅ Cálculo automático de precios

---

## 3. Fases de Implementación

### 📦 Fase 1: Fundamentos (Semana 1)
**Objetivo**: Crear infraestructura base sin dependencias

- ✅ Crear estructura de carpetas
- ✅ Implementar `base.py` con naming conventions
- ✅ Implementar mixins reutilizables
- ✅ Implementar validadores comunes
- ✅ Testing de fundamentos

### 📚 Fase 2: Lookups (Semana 1-2)
**Objetivo**: Tablas de catálogo y referencia

- ✅ Implementar 12 modelos lookup
- ✅ Datos de seed para lookups
- ✅ Testing de lookups
- ✅ Migración inicial

### ⚙️ Fase 3: Core Models (Semana 2-3)
**Objetivo**: Modelos fundamentales del sistema

- ✅ Staff (usuarios)
- ✅ Note (sistema polimórfico)
- ✅ Company, CompanyRut, Branch
- ✅ Contact, Service
- ✅ Address
- ✅ ⭐ **Product, ProductComponent** (sistema unificado)
- ✅ Testing completo de core

### 💼 Fase 4: Business Models (Semana 3-4)
**Objetivo**: Flujo de negocio completo

- ✅ Quote, QuoteProduct
- ✅ Order
- ✅ InvoiceSII, InvoiceExport
- ✅ DeliveryOrder, DeliveryDate, Transport, PaymentCondition
- ✅ Testing de flujo completo

### 🔄 Fase 5: Migración de Datos (Semana 4-5)
**Objetivo**: Migrar datos desde sistema actual

- ✅ Scripts de migración
- ✅ Validación de datos
- ✅ Testing de migración
- ✅ Rollback plan

### 🚀 Fase 6: Integración y Deployment (Semana 5-6)
**Objetivo**: Integrar con aplicación y desplegar

- ✅ Integración con repositorios
- ✅ Integración con servicios
- ✅ Integración con UI
- ✅ Testing end-to-end
- ✅ Deployment gradual

---

## 4. Orden de Implementación

### 📝 Orden Detallado de Archivos

#### 1️⃣ **base/** (Día 1-2)

```
1. base/base.py
   - MetaData con naming_convention
   - Base declarativa
   - BaseModel con __repr__ y to_dict()

2. base/mixins.py
   - TimestampMixin (created_at, updated_at)
   - AuditMixin (created_by, updated_by)
   - SoftDeleteMixin (deleted_at, is_deleted)
   - ActiveMixin (is_active)

3. base/validators.py
   - EmailValidator
   - PhoneValidator
   - RutValidator

4. base/__init__.py
   - Exporta todo
```

#### 2️⃣ **lookups/** (Día 3)

```
5. lookups/lookups.py (12 modelos)
   - Country (países)
   - City (ciudades) → FK: Country
   - CompanyType (tipos de empresa)
   - Incoterm (términos comerciales)
   - Currency (monedas)
   - Unit (unidades de medida)
   - FamilyType (familias de productos)
   - Matter (materiales)
   - SalesType (tipos de venta)
   - QuoteStatus (estados de cotización)
   - OrderStatus (estados de orden)
   - PaymentStatus (estados de pago)

6. lookups/__init__.py
```

#### 3️⃣ **core/** (Día 4-10)

```
7. core/staff.py (Día 4)
   - Staff (usuarios del sistema)

8. core/notes.py (Día 4)
   - Note (sistema polimórfico de notas)

9. core/companies.py (Día 5-6)
   - Company
   - CompanyRut
   - Branch

10. core/contacts.py (Día 6)
    - Contact
    - Service

11. core/addresses.py (Día 7)
    - Address

12. core/products.py (Día 8-10) ⭐ CRÍTICO
    - ProductType (Enum)
    - PriceCalculationMode (Enum)
    - Product (modelo unificado)
    - ProductComponent (BOM)
    - Métodos:
      * get_bom_tree()
      * get_flat_bom()
      * get_total_weight()
      * calculated_cost
      * calculated_price
      * effective_cost
      * effective_price
      * margin_percentage
      * prevent_cycles()

13. core/__init__.py
```

#### 4️⃣ **business/** (Día 11-15)

```
14. business/quotes.py (Día 11-12)
    - Quote
    - QuoteProduct (junction table)

15. business/orders.py (Día 12-13)
    - Order

16. business/invoices.py (Día 13-14)
    - InvoiceSII
    - InvoiceExport

17. business/delivery.py (Día 14-15)
    - DeliveryOrder
    - DeliveryDate
    - Transport
    - PaymentCondition

18. business/__init__.py
```

#### 5️⃣ **models/__init__.py** (Día 15)

```
19. models/__init__.py
    - Importa y exporta todos los modelos
    - Configuración de metadata
```

---

## 5. Plan Detallado por Fase

### 📦 FASE 1: Fundamentos (Día 1-2)

#### Día 1: Base Infrastructure

**Archivo: `models/base/base.py`**

```python
"""
Base declarativa y naming conventions para SQLAlchemy.
"""
from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base
from typing import Any

# Naming convention for automatic constraint naming
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)


class BaseModel:
    """Base class for all models with common methods."""

    id: int  # Type hint for IDE support

    def __repr__(self) -> str:
        """String representation."""
        return f"<{self.__class__.__name__}(id={self.id})>"

    def to_dict(self, exclude: set[str] | None = None) -> dict[str, Any]:
        """Convert to dictionary."""
        exclude = exclude or set()
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
            if column.name not in exclude
        }


Base = declarative_base(cls=BaseModel, metadata=metadata)
```

**Checklist**:
- [ ] Crear archivo `base.py`
- [ ] Definir NAMING_CONVENTION
- [ ] Crear BaseModel con __repr__ y to_dict()
- [ ] Crear Base declarativa
- [ ] Escribir docstrings
- [ ] Testing básico

---

**Archivo: `models/base/mixins.py`**

```python
"""
Mixins reutilizables para modelos SQLAlchemy.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, Boolean, event
from sqlalchemy.orm import declarative_mixin, declared_attr, Session


@declarative_mixin
class TimestampMixin:
    """Añade created_at y updated_at automáticos."""

    @declared_attr
    def created_at(cls) -> Column:
        return Column(
            DateTime(timezone=True),
            nullable=False,
            default=lambda: datetime.now(timezone.utc),
            comment="UTC timestamp of creation",
        )

    @declared_attr
    def updated_at(cls) -> Column:
        return Column(
            DateTime(timezone=True),
            nullable=False,
            default=lambda: datetime.now(timezone.utc),
            onupdate=lambda: datetime.now(timezone.utc),
            comment="UTC timestamp of last update",
        )


@declarative_mixin
class AuditMixin:
    """Añade created_by y updated_by para auditoría."""

    @declared_attr
    def created_by_id(cls) -> Column:
        return Column(
            Integer,
            nullable=True,
            comment="User ID who created this record",
        )

    @declared_attr
    def updated_by_id(cls) -> Column:
        return Column(
            Integer,
            nullable=True,
            comment="User ID who last updated this record",
        )


@declarative_mixin
class SoftDeleteMixin:
    """Añade soft delete functionality."""

    @declared_attr
    def is_deleted(cls) -> Column:
        return Column(
            Boolean,
            nullable=False,
            default=False,
            comment="Soft delete flag",
        )

    @declared_attr
    def deleted_at(cls) -> Column:
        return Column(
            DateTime(timezone=True),
            nullable=True,
            comment="UTC timestamp of deletion",
        )

    @declared_attr
    def deleted_by_id(cls) -> Column:
        return Column(
            Integer,
            nullable=True,
            comment="User ID who deleted this record",
        )


@declarative_mixin
class ActiveMixin:
    """Añade flag is_active."""

    @declared_attr
    def is_active(cls) -> Column:
        return Column(
            Boolean,
            nullable=False,
            default=True,
            index=True,
            comment="Active status flag",
        )


# Event listener para auto-update de updated_at
@event.listens_for(Session, "before_flush")
def receive_before_flush(session: Session, flush_context, instances):
    """Auto-set updated_at on flush."""
    for instance in session.dirty:
        if hasattr(instance, "updated_at"):
            instance.updated_at = datetime.now(timezone.utc)
```

**Checklist**:
- [ ] Crear archivo `mixins.py`
- [ ] Implementar TimestampMixin
- [ ] Implementar AuditMixin
- [ ] Implementar SoftDeleteMixin
- [ ] Implementar ActiveMixin
- [ ] Event listener para updated_at
- [ ] Testing de mixins

---

#### Día 2: Validators

**Archivo: `models/base/validators.py`**

```python
"""
Validadores comunes para campos de modelos.
"""
import re
from typing import Optional


class EmailValidator:
    """Validador de emails."""

    @staticmethod
    def validate(value: Optional[str]) -> Optional[str]:
        """Validate email format."""
        if not value:
            return value

        value = value.strip().lower()
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        if not re.match(pattern, value):
            raise ValueError(f"Invalid email format: {value}")

        return value


class PhoneValidator:
    """Validador de teléfonos (formato E.164)."""

    @staticmethod
    def validate(value: Optional[str]) -> Optional[str]:
        """Validate phone number (E.164 format)."""
        if not value:
            return value

        # Remove common separators
        clean = re.sub(r"[\s\-\(\)\.]+", "", value)

        # E.164: +[country][number], 8-15 digits
        if not re.match(r"^\+?[0-9]{8,15}$", clean):
            raise ValueError(
                f"Phone must be 8-15 digits, optionally starting with +. Got: {value}"
            )

        return value


class RutValidator:
    """Validador de RUT chileno."""

    @staticmethod
    def validate(value: Optional[str]) -> Optional[str]:
        """Validate Chilean RUT format and check digit."""
        if not value:
            return value

        # Remove formatting
        rut = re.sub(r"[^\dKk]", "", value)

        if len(rut) < 2:
            raise ValueError(f"RUT too short: {value}")

        # Split number and check digit
        number = rut[:-1]
        check_digit = rut[-1].upper()

        # Calculate expected check digit
        reversed_digits = map(int, reversed(number))
        factors = [2, 3, 4, 5, 6, 7]
        s = sum(d * factors[i % 6] for i, d in enumerate(reversed_digits))
        expected = 11 - (s % 11)

        if expected == 11:
            expected_digit = "0"
        elif expected == 10:
            expected_digit = "K"
        else:
            expected_digit = str(expected)

        if check_digit != expected_digit:
            raise ValueError(f"Invalid RUT check digit: {value}")

        # Return formatted RUT
        return f"{number}-{check_digit}"
```

**Checklist**:
- [ ] Crear archivo `validators.py`
- [ ] Implementar EmailValidator
- [ ] Implementar PhoneValidator
- [ ] Implementar RutValidator
- [ ] Testing de validadores

---

**Archivo: `models/base/__init__.py`**

```python
"""Base infrastructure exports."""
from models.base.base import Base, metadata, NAMING_CONVENTION, BaseModel
from models.base.mixins import (
    TimestampMixin,
    AuditMixin,
    SoftDeleteMixin,
    ActiveMixin,
)
from models.base.validators import EmailValidator, PhoneValidator, RutValidator

__all__ = [
    "Base",
    "metadata",
    "NAMING_CONVENTION",
    "BaseModel",
    "TimestampMixin",
    "AuditMixin",
    "SoftDeleteMixin",
    "ActiveMixin",
    "EmailValidator",
    "PhoneValidator",
    "RutValidator",
]
```

**Checklist**:
- [ ] Crear `__init__.py`
- [ ] Exportar todo correctamente
- [ ] Verificar imports

---

### 📚 FASE 2: Lookups (Día 3)

**Archivo: `models/lookups/lookups.py`**

```python
"""
Lookup tables (reference data).
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Index, Text
from sqlalchemy.orm import relationship
from models.base import Base, TimestampMixin, ActiveMixin


class Country(Base, TimestampMixin):
    """Countries."""
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    iso_code_alpha2 = Column(String(2), unique=True)
    iso_code_alpha3 = Column(String(3), unique=True)

    cities = relationship("City", back_populates="country")
    companies = relationship("Company", back_populates="country")


class City(Base, TimestampMixin):
    """Cities."""
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, index=True)
    country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)

    country = relationship("Country", back_populates="cities")
    companies = relationship("Company", back_populates="city")
    branches = relationship("Branch", back_populates="city")

    __table_args__ = (
        Index("uq_city_name_country", "name", "country_id", unique=True),
    )


class CompanyType(Base, TimestampMixin):
    """Company types (client, supplier, partner, etc.)."""
    __tablename__ = "company_types"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)

    companies = relationship("Company", back_populates="company_type")


class Incoterm(Base, TimestampMixin, ActiveMixin):
    """International Commercial Terms (Incoterms 2020)."""
    __tablename__ = "incoterms"

    id = Column(Integer, primary_key=True)
    code = Column(String(3), nullable=False, unique=True)  # EXW, FOB, CIF, etc.
    name = Column(String(100), nullable=False)
    description = Column(Text)


class Currency(Base, TimestampMixin, ActiveMixin):
    """Currencies (ISO 4217)."""
    __tablename__ = "currencies"

    id = Column(Integer, primary_key=True)
    code = Column(String(3), nullable=False, unique=True)  # CLP, EUR, USD
    name = Column(String(50), nullable=False)
    symbol = Column(String(5))


class Unit(Base, TimestampMixin, ActiveMixin):
    """Units of measurement."""
    __tablename__ = "units"

    id = Column(Integer, primary_key=True)
    code = Column(String(10), nullable=False, unique=True)  # kg, pcs, m, etc.
    name = Column(String(50), nullable=False)
    description = Column(Text)


class FamilyType(Base, TimestampMixin):
    """Product family types."""
    __tablename__ = "family_types"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)

    products = relationship("Product", back_populates="family_type")


class Matter(Base, TimestampMixin):
    """Materials (steel, aluminum, plastic, etc.)."""
    __tablename__ = "matters"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)

    products = relationship("Product", back_populates="matter")


class SalesType(Base, TimestampMixin):
    """Sales types (retail, wholesale, export, etc.)."""
    __tablename__ = "sales_types"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    description = Column(Text)

    products = relationship("Product", back_populates="sales_type")


class QuoteStatus(Base, TimestampMixin):
    """Quote statuses."""
    __tablename__ = "quote_statuses"

    id = Column(Integer, primary_key=True)
    code = Column(String(20), nullable=False, unique=True)  # draft, sent, accepted, etc.
    name = Column(String(50), nullable=False)
    description = Column(Text)


class OrderStatus(Base, TimestampMixin):
    """Order statuses."""
    __tablename__ = "order_statuses"

    id = Column(Integer, primary_key=True)
    code = Column(String(20), nullable=False, unique=True)
    name = Column(String(50), nullable=False)
    description = Column(Text)


class PaymentStatus(Base, TimestampMixin):
    """Payment statuses."""
    __tablename__ = "payment_statuses"

    id = Column(Integer, primary_key=True)
    code = Column(String(20), nullable=False, unique=True)
    name = Column(String(50), nullable=False)
    description = Column(Text)
```

**Checklist**:
- [ ] Crear `lookups.py` con 12 modelos
- [ ] Implementar Country
- [ ] Implementar City (FK: Country)
- [ ] Implementar CompanyType
- [ ] Implementar Incoterm (ActiveMixin)
- [ ] Implementar Currency (ActiveMixin)
- [ ] Implementar Unit (ActiveMixin)
- [ ] Implementar FamilyType
- [ ] Implementar Matter
- [ ] Implementar SalesType
- [ ] Implementar QuoteStatus
- [ ] Implementar OrderStatus
- [ ] Implementar PaymentStatus
- [ ] Crear `__init__.py`
- [ ] Testing de lookups

---

### ⚙️ FASE 3: Core Models (Día 4-10)

#### Día 4: Staff y Notes

**Archivo: `models/core/staff.py`**

```python
"""Staff (users) model."""
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import validates
from models.base import Base, TimestampMixin, AuditMixin, EmailValidator


class Staff(Base, TimestampMixin, AuditMixin):
    """System users/staff."""
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(100), nullable=False, unique=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    is_admin = Column(Boolean, nullable=False, default=False)

    @validates("email")
    def validate_email(self, key, value):
        return EmailValidator.validate(value)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
```

**Checklist**:
- [ ] Crear `staff.py`
- [ ] Implementar Staff model
- [ ] Validación de email
- [ ] Testing

---

**Archivo: `models/core/notes.py`**

```python
"""Polymorphic notes system."""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Index
from models.base import Base, TimestampMixin, AuditMixin


class Note(Base, TimestampMixin, AuditMixin):
    """Polymorphic notes for any entity."""
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)

    # Polymorphic fields
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)

    # Note content
    title = Column(String(200))
    content = Column(Text, nullable=False)

    # Priority/Category
    priority = Column(String(20), default="normal")  # low, normal, high, urgent
    category = Column(String(50))  # General, Technical, Commercial, etc.

    __table_args__ = (
        Index("ix_note_entity", "entity_type", "entity_id"),
    )
```

**Checklist**:
- [ ] Crear `notes.py`
- [ ] Implementar Note polimórfico
- [ ] Testing

---

#### Día 5-6: Companies

**Archivo: `models/core/companies.py`** (ver MEJORAS_MODELOS.md para código completo)

**Checklist**:
- [ ] Crear `companies.py`
- [ ] Implementar Company
- [ ] Implementar CompanyRut
- [ ] Implementar Branch
- [ ] Validaciones (trigram, phone, website)
- [ ] Relaciones bidireccionales
- [ ] Testing

---

#### Día 7: Addresses y Contacts

**Archivo: `models/core/addresses.py`** (ver MEJORAS_MODELOS.md)

**Archivo: `models/core/contacts.py`**

**Checklist**:
- [ ] Crear `addresses.py`
- [ ] Implementar Address model
- [ ] Crear `contacts.py`
- [ ] Implementar Contact model
- [ ] Implementar Service model
- [ ] Testing

---

#### Día 8-10: ⭐ Products (CRÍTICO)

**Archivo: `models/core/products.py`**

Este es el modelo más complejo y crítico del sistema. Ver `PRODUCT_SYSTEM_DETAILED.md` para especificación completa.

**Estructura**:

```python
# Enums
class ProductType(str, Enum):
    ARTICLE = "article"
    NOMENCLATURE = "nomenclature"
    SERVICE = "service"

class PriceCalculationMode(str, Enum):
    AUTO = "auto"
    MANUAL = "manual"

# Modelo principal
class Product(Base, TimestampMixin, AuditMixin, SoftDeleteMixin, ActiveMixin):
    """Unified product table (articles, nomenclatures, services)."""

    # 40+ campos
    # Properties calculadas
    # Métodos de BOM
    # Validaciones

class ProductComponent(Base, TimestampMixin):
    """BOM relationships (parent contains child)."""

    # Prevención de ciclos
    # Validaciones
```

**Features Clave**:
1. Tabla única polimórfica
2. BOM jerárquico ilimitado
3. Cálculo automático de precios desde componentes
4. Prevención de ciclos
5. Stock management
6. Métodos: `get_bom_tree()`, `get_flat_bom()`, `get_total_weight()`

**Checklist**:
- [ ] Crear `products.py`
- [ ] Implementar ProductType enum
- [ ] Implementar PriceCalculationMode enum
- [ ] Implementar Product model (40+ campos)
- [ ] Implementar properties calculadas (effective_cost, effective_price, margin)
- [ ] Implementar get_bom_tree()
- [ ] Implementar get_flat_bom()
- [ ] Implementar get_total_weight()
- [ ] Implementar get_depth()
- [ ] Implementar ProductComponent model
- [ ] Implementar prevent_cycles()
- [ ] Validaciones de product_type
- [ ] Validaciones de stock
- [ ] Testing exhaustivo
- [ ] Performance testing

---

### 💼 FASE 4: Business Models (Día 11-15)

#### Día 11-12: Quotes

**Archivo: `models/business/quotes.py`**

```python
"""Quote models."""
from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from models.base import Base, TimestampMixin, AuditMixin, ActiveMixin


class Quote(Base, TimestampMixin, AuditMixin, ActiveMixin):
    """Sales quotes."""
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True)
    quote_number = Column(String(50), nullable=False, unique=True, index=True)
    subject = Column(String(200), nullable=False)

    # Company
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)

    # Status
    status_id = Column(Integer, ForeignKey("quote_statuses.id"), nullable=False)

    # Dates
    quote_date = Column(Date, nullable=False)
    valid_until = Column(Date)

    # Totals (calculated)
    subtotal = Column(DECIMAL(15, 2))
    tax_amount = Column(DECIMAL(15, 2))
    total = Column(DECIMAL(15, 2))

    # Relationships
    company = relationship("Company", back_populates="quotes")
    status = relationship("QuoteStatus")
    products = relationship("QuoteProduct", back_populates="quote", cascade="all, delete-orphan")


class QuoteProduct(Base, TimestampMixin):
    """Products in a quote (junction table)."""
    __tablename__ = "quote_products"

    id = Column(Integer, primary_key=True)
    quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    quantity = Column(DECIMAL(10, 3), nullable=False)
    unit_price = Column(DECIMAL(15, 2), nullable=False)
    discount_percentage = Column(DECIMAL(5, 2), default=0)
    subtotal = Column(DECIMAL(15, 2), nullable=False)

    quote = relationship("Quote", back_populates="products")
    product = relationship("Product")
```

**Checklist**:
- [ ] Crear `quotes.py`
- [ ] Implementar Quote
- [ ] Implementar QuoteProduct
- [ ] Cálculo de totales
- [ ] Testing

---

#### Día 12-13: Orders

**Archivo: `models/business/orders.py`**

Similar a Quote pero con orden de compra/venta.

**Checklist**:
- [ ] Crear `orders.py`
- [ ] Implementar Order
- [ ] Relación con Quote
- [ ] Testing

---

#### Día 13-14: Invoices

**Archivo: `models/business/invoices.py`**

```python
"""Invoice models."""
# InvoiceSII (facturas SII Chile)
# InvoiceExport (facturas de exportación)
```

**Checklist**:
- [ ] Crear `invoices.py`
- [ ] Implementar InvoiceSII
- [ ] Implementar InvoiceExport
- [ ] Testing

---

#### Día 14-15: Delivery

**Archivo: `models/business/delivery.py`**

```python
"""Delivery and transport models."""
# DeliveryOrder
# DeliveryDate
# Transport
# PaymentCondition
```

**Checklist**:
- [ ] Crear `delivery.py`
- [ ] Implementar DeliveryOrder
- [ ] Implementar DeliveryDate
- [ ] Implementar Transport
- [ ] Implementar PaymentCondition
- [ ] Testing

---

### 🔄 FASE 5: Migración (Semana 4-5)

**Script: `migrations/migrate_data.py`**

```python
"""
Data migration from old structure to new unified system.
"""

# 1. Migrar articles → products (type=ARTICLE)
# 2. Migrar nomenclatures → products (type=NOMENCLATURE)
# 3. Migrar artinomen → product_components
# 4. Migrar nomennomen → product_components
# 5. Validar integridad
```

**Checklist**:
- [ ] Script de migración de articles
- [ ] Script de migración de nomenclatures
- [ ] Script de migración de relaciones
- [ ] Validación de datos migrados
- [ ] Testing de migración
- [ ] Rollback plan
- [ ] Backup antes de migración

---

## 6. Migraciones de Base de Datos

### Crear Migraciones con Alembic

```bash
# Fase 1: Base
alembic revision --autogenerate -m "create_base_infrastructure"

# Fase 2: Lookups
alembic revision --autogenerate -m "create_lookup_tables"
alembic revision -m "seed_lookup_data"

# Fase 3: Core
alembic revision --autogenerate -m "create_core_models"

# Fase 4: Business
alembic revision --autogenerate -m "create_business_models"

# Fase 5: Migraciones especiales
alembic revision -m "migrate_articles_to_products"
alembic revision -m "migrate_nomenclatures_to_products"
alembic revision -m "migrate_relationships"
```

### Orden de Aplicación

```bash
# Desarrollo
alembic upgrade head

# Producción (gradual)
alembic upgrade +1  # Una por una
alembic upgrade head  # O todas
```

---

## 7. Testing Strategy

### Estructura de Tests

```
tests/
├── models/
│   ├── base/
│   │   ├── test_mixins.py
│   │   └── test_validators.py
│   ├── lookups/
│   │   └── test_lookups.py
│   ├── core/
│   │   ├── test_staff.py
│   │   ├── test_companies.py
│   │   ├── test_addresses.py
│   │   ├── test_contacts.py
│   │   └── test_products.py  # ⭐ Más importante
│   └── business/
│       ├── test_quotes.py
│       ├── test_orders.py
│       ├── test_invoices.py
│       └── test_delivery.py
```

### Testing de Products (Crítico)

```python
# tests/models/core/test_products.py

def test_create_article():
    """Test creating simple article."""

def test_create_nomenclature():
    """Test creating nomenclature with components."""

def test_bom_tree():
    """Test BOM hierarchy generation."""

def test_prevent_cycles():
    """Test cycle prevention in BOM."""

def test_calculated_price():
    """Test automatic price calculation from components."""

def test_calculated_cost():
    """Test automatic cost calculation."""

def test_flat_bom():
    """Test flattened BOM generation."""

def test_total_weight():
    """Test recursive weight calculation."""

def test_stock_management():
    """Test stock operations."""

def test_validation_errors():
    """Test validation raises errors correctly."""
```

---

## 8. Criterios de Aceptación

### Por Fase

#### Fase 1: Fundamentos
- [ ] Base declarativa funciona
- [ ] Mixins se heredan correctamente
- [ ] Validadores funcionan y lanzan errores apropiados
- [ ] Tests pasan al 100%

#### Fase 2: Lookups
- [ ] 12 tablas creadas
- [ ] Datos seed cargados
- [ ] Relaciones funcionan
- [ ] Tests pasan

#### Fase 3: Core Models
- [ ] Todos los modelos core creados
- [ ] Product system funciona completamente
- [ ] BOM jerárquico funciona
- [ ] Prevención de ciclos funciona
- [ ] Cálculos de precios correctos
- [ ] Tests pasan

#### Fase 4: Business Models
- [ ] Flujo Quote → Order → Invoice funciona
- [ ] Relaciones correctas
- [ ] Tests pasan

#### Fase 5: Migración
- [ ] Todos los datos migrados sin pérdida
- [ ] Validación pasa al 100%
- [ ] Rollback probado

#### Fase 6: Integración
- [ ] Repositorios funcionan con nuevos modelos
- [ ] Servicios integrados
- [ ] UI funciona
- [ ] Tests end-to-end pasan
- [ ] Performance aceptable

---

## 9. Cronograma Estimado

| Fase | Duración | Días | Dependencias |
|------|----------|------|--------------|
| **Fase 1: Fundamentos** | 2 días | 1-2 | Ninguna |
| **Fase 2: Lookups** | 1 día | 3 | Fase 1 |
| **Fase 3: Core** | 7 días | 4-10 | Fase 1, 2 |
| **Fase 4: Business** | 5 días | 11-15 | Fase 1, 2, 3 |
| **Fase 5: Migración** | 5 días | 16-20 | Todas anteriores |
| **Fase 6: Integración** | 10 días | 21-30 | Todas anteriores |
| **TOTAL** | **30 días** | **~6 semanas** | |

### Hitos Clave

- **Semana 1**: Fundamentos + Lookups + Core (Staff, Notes, Companies)
- **Semana 2**: Core (Products ⭐) + Testing
- **Semana 3**: Business models completos
- **Semana 4**: Migración de datos
- **Semana 5-6**: Integración y deployment

---

## 10. Riesgos y Mitigación

### Riesgos Identificados

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| **Ciclos en BOM no detectados** | Media | Alto | - Implementar método prevent_cycles() robusto<br>- Testing exhaustivo de casos edge<br>- Validación en multiple niveles |
| **Pérdida de datos en migración** | Baja | Crítico | - Backup completo antes de migrar<br>- Migración en staging primero<br>- Validación exhaustiva post-migración<br>- Rollback plan documentado |
| **Performance en BOM profundos** | Media | Medio | - Limitar profundidad máxima (default: 10)<br>- Caching de cálculos<br>- Índices optimizados<br>- Lazy loading apropiado |
| **Validaciones rompen datos existentes** | Alta | Medio | - Migración progresiva<br>- Validaciones opcionales al inicio<br>- Limpieza de datos antes de validar |
| **Relaciones circulares entre modelos** | Baja | Alto | - Diseño cuidadoso de dependencias<br>- Imports condicionales si necesario<br>- Forward references |

---

## 📝 Notas Finales

### Prioridades

1. **Crítico**: Product system (core/products.py)
2. **Alto**: Base infrastructure, Companies, Quotes
3. **Medio**: Resto de core, Business models
4. **Bajo**: Optimizaciones, features adicionales

### Contacto y Soporte

- **Documentación completa**: Ver `PRODUCT_SYSTEM_DETAILED.md`
- **Mejoras de modelos**: Ver `MEJORAS_MODELOS.md`
- **Estructura**: Ver `MODELS_STRUCTURE.md`

---

**Última actualización**: 2025-01-25
**Próxima revisión**: Al completar Fase 1
**Estado**: ✅ Plan aprobado, listo para implementación
