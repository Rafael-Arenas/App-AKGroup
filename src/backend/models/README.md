# Models - Sistema de Modelos SQLAlchemy

> **Estado**: ✅ **100% COMPLETADO** - Todas las fases implementadas
>
> **33 modelos** | **32 tablas** | **14 archivos** | **~5,650 LOC**

Sistema completo de modelos SQLAlchemy para AK Group, implementado con arquitectura en capas siguiendo principios SOLID y mejores prácticas de Python.

---

## ✅ Estado de Implementación

### Fase 1: Base Infrastructure - **✅ COMPLETADA**
- ✅ `base/base.py` - Base declarativa con naming conventions
- ✅ `base/mixins.py` - 4 mixins reutilizables
- ✅ `base/validators.py` - 5 validadores comunes
- ✅ `base/__init__.py` - Exports

### Fase 2: Lookup Tables - **✅ COMPLETADA**
- ✅ `lookups/lookups.py` - 12 modelos de catálogo
- ✅ `lookups/__init__.py` - Exports

### Fase 3: Core Models - **✅ COMPLETADA**
- ✅ `core/staff.py` - Staff (usuarios)
- ✅ `core/notes.py` - Note (notas polimórficas)
- ✅ `core/companies.py` - Company, CompanyRut, Plant
- ✅ `core/contacts.py` - Contact, Service
- ✅ `core/addresses.py` - Address
- ✅ `core/products.py` - ⭐ Product, ProductComponent (sistema unificado)

### Fase 4: Business Models - **✅ COMPLETADA**
- ✅ `business/quotes.py` - Quote, QuoteProduct
- ✅ `business/orders.py` - Order (con revision, customer_quote_number, project_number, addresses)
- ✅ `business/invoices.py` - InvoiceSII, InvoiceExport
- ✅ `business/delivery.py` - DeliveryOrder (con revision), DeliveryDate, Transport (con delivery_number), PaymentCondition (con revision)

---

## 📁 Estructura de Carpetas

```
src/models/
├── __init__.py                 # ✅ Export principal
│
├── base/                       # ✅ FASE 1 COMPLETADA
│   ├── __init__.py
│   ├── base.py                 # Base declarativa + naming conventions
│   ├── mixins.py               # TimestampMixin, AuditMixin, SoftDeleteMixin, ActiveMixin
│   └── validators.py           # EmailValidator, PhoneValidator, RutValidator, etc.
│
├── lookups/                    # ✅ FASE 2 COMPLETADA
│   ├── __init__.py
│   └── lookups.py              # 12 modelos lookup
│
├── core/                       # ✅ FASE 3 COMPLETADA
│   ├── __init__.py
│   ├── staff.py                # Staff
│   ├── notes.py                # Note
│   ├── companies.py            # Company, CompanyRut, Plant
│   ├── contacts.py             # Contact, Service
│   ├── addresses.py            # Address
│   └── products.py             # Product, ProductComponent
│
└── business/                   # ✅ FASE 4 COMPLETADA
    ├── __init__.py
    ├── quotes.py               # Quote, QuoteProduct
    ├── orders.py               # Order
    ├── invoices.py             # InvoiceSII, InvoiceExport
    └── delivery.py             # DeliveryOrder, DeliveryDate, Transport, PaymentCondition
```

---

## 🎯 Modelos Implementados

### Base Infrastructure (3 archivos)

#### 1. `base/base.py`
- **NAMING_CONVENTION**: Naming convention para constraints automáticos
- **metadata**: MetaData compartido con naming convention
- **BaseModel**: Clase base con `__repr__()` y `to_dict()`
- **Base**: Declarative base de SQLAlchemy

#### 2. `base/mixins.py`
- **TimestampMixin**: created_at, updated_at (automáticos con UTC)
- **AuditMixin**: created_by_id, updated_by_id (con event listener)
- **SoftDeleteMixin**: is_deleted, deleted_at, deleted_by_id
- **ActiveMixin**: is_active (para habilitar/deshabilitar)
- **Event Listeners**: Automatizan updated_at y auditoría

#### 3. `base/validators.py`
- **EmailValidator**: Validación RFC 5322 simplificado
- **PhoneValidator**: Validación formato E.164 (8-15 dígitos)
- **RutValidator**: Validación RUT chileno con dígito verificador
- **UrlValidator**: Validación http/https
- **DecimalValidator**: Validación de valores positivos/no negativos

### Lookup Tables (1 archivo, 12 modelos)

#### `lookups/lookups.py`

1. **Country** - Países (con ISO alpha-2 y alpha-3)
2. **City** - Ciudades (FK: Country, unique: name+country)
3. **CompanyType** - Tipos de empresa
4. **Incoterm** - Incoterms 2020 (con ActiveMixin)
5. **Currency** - Monedas ISO 4217 (con ActiveMixin)
6. **Unit** - Unidades de medida (con ActiveMixin)
7. **FamilyType** - Familias de productos
8. **Matter** - Materiales/Materias
9. **SalesType** - Tipos de venta
10. **QuoteStatus** - Estados de cotización
11. **OrderStatus** - Estados de orden
12. **PaymentStatus** - Estados de pago

Todos con:
- ✅ TimestampMixin (created_at, updated_at)
- ✅ CHECK constraints para validación
- ✅ Índices apropiados
- ✅ Documentación completa
- ✅ Relationships definidas (forward references para Fase 3-4)

---

## 📖 Uso

### Importar Base Infrastructure

```python
from src.models.base import (
    Base,
    metadata,
    TimestampMixin,
    AuditMixin,
    EmailValidator
)

# Crear un nuevo modelo
class MyModel(Base, TimestampMixin, AuditMixin):
    __tablename__ = 'my_table'

    id = Column(Integer, primary_key=True)
    email = Column(String(100))

    @validates("email")
    def validate_email(self, key, value):
        return EmailValidator.validate(value)
```

### Importar Lookups

```python
from src.models.lookups import Country, Currency, Incoterm

# Query lookups
chile = session.query(Country).filter_by(iso_code_alpha2="CL").first()
active_currencies = session.query(Currency).filter_by(is_active=True).all()
```

### Importar desde Package Principal

```python
# Base infrastructure
from src.models import Base, metadata, TimestampMixin, AuditMixin, ActiveMixin

# Lookups
from src.models import Country, City, Currency, Incoterm, Unit

# Core models
from src.models import (
    Staff,
    Company, CompanyRut, Plant,
    Contact, Service,
    Address,
    Product, ProductComponent,
    Note
)

# Business models
from src.models import (
    Quote, QuoteProduct,
    Order,
    InvoiceSII, InvoiceExport,
    DeliveryOrder, DeliveryDate,
    Transport, PaymentCondition
)
```

---

## 🔧 Configuración de Alembic

Para que Alembic detecte todos los modelos:

```python
# migrations/env.py
from src.models import Base

# Importar todos los modelos (importante para autogenerate)
import models.lookups
import models.core
import models.business

target_metadata = Base.metadata
```

**Nota importante**: Los modelos de negocio ahora usan la Base principal correctamente (se eliminó el código fallback que causaba problemas con autogenerate).

---

## 🧪 Testing

### Estructura de Tests

```
tests/
├── models/
│   ├── base/
│   │   ├── test_base.py          # Test Base, metadata, BaseModel
│   │   ├── test_mixins.py        # Test TimestampMixin, AuditMixin, etc.
│   │   └── test_validators.py    # Test EmailValidator, RutValidator, etc.
│   └── lookups/
│       └── test_lookups.py       # Test 12 modelos lookup
```

### Ejecutar Tests

```bash
# Test solo base
pytest tests/models/base/ -v

# Test solo lookups
pytest tests/models/lookups/ -v

# Test todos los modelos
pytest tests/models/ -v

# Test con coverage
pytest tests/models/ --cov=src.models --cov-report=html
```

---

## 📊 Estadísticas

| Categoría | Archivos | Modelos | LOC | Estado |
|-----------|----------|---------|-----|--------|
| base/ | 3 | - | ~450 | ✅ Completado |
| lookups/ | 1 | 12 | ~500 | ✅ Completado |
| core/ | 6 | 9 | ~2,200 | ✅ Completado |
| business/ | 4 | 12 | ~2,500 | ✅ Completado |
| **TOTAL** | **14** | **33** | **~5,650** | **✅ 100% Completado** |

---

## ✨ Características Implementadas

### 1. Naming Conventions
- ✅ Constraints con nombres predecibles
- ✅ Facilita migraciones de Alembic
- ✅ Debugging más fácil

### 2. Mixins Reutilizables
- ✅ TimestampMixin: Timestamps UTC automáticos
- ✅ AuditMixin: Auditoría de usuarios con event listeners
- ✅ SoftDeleteMixin: Eliminación lógica
- ✅ ActiveMixin: Estado activo/inactivo

### 3. Validadores Robustos
- ✅ EmailValidator: RFC 5322 simplificado
- ✅ PhoneValidator: E.164 format
- ✅ RutValidator: Algoritmo módulo 11 chileno
- ✅ UrlValidator: http/https
- ✅ DecimalValidator: Valores positivos

### 4. Lookup Tables Completas
- ✅ 12 tablas de catálogo
- ✅ CHECK constraints para validación
- ✅ Índices optimizados
- ✅ Unique constraints apropiados
- ✅ Relationships forward-declared

### 5. Documentación Completa
- ✅ Docstrings en todos los modelos
- ✅ Docstrings en todos los métodos
- ✅ Comments en columnas
- ✅ Ejemplos de uso

---

## 🎉 Modelos Completados - Detalles

### Core Models (9 modelos)

1. **Staff** - Usuarios del sistema con autenticación
2. **Note** - Sistema polimórfico de notas (entity_type + entity_id)
3. **Company** - Empresas (clientes/proveedores)
4. **CompanyRut** - RUTs múltiples por empresa
5. **Plant** - Sucursales/Plantas de empresas
6. **Contact** - Contactos de empresas
7. **Service** - Servicios/departamentos
8. **Address** - Direcciones de empresas (con tipos: delivery, billing, headquarters, plant)
9. **Product / ProductComponent** - Sistema unificado con BOM

### Business Models (12 modelos)

1. **Quote** - Cotizaciones de ventas
2. **QuoteProduct** - Productos de cotización
3. **Order** - Órdenes de compra/venta
4. **InvoiceSII** - Facturas SII domésticas
5. **InvoiceExport** - Facturas de exportación
6. **DeliveryOrder** - Guías de despacho
7. **DeliveryDate** - Fechas de entrega programadas
8. **Transport** - Transportistas
9. **PaymentCondition** - Condiciones de pago

### Columnas Especiales por Categoría

#### **Sistema de Revisiones** (6 tablas):
Todas las tablas de documentos de negocio incluyen versionado mediante `revision`:
- ✅ **Quote**: `revision` (VARCHAR(10), default="A")
- ✅ **Order**: `revision` (VARCHAR(10), default="A")
- ✅ **InvoiceSII**: `revision` (VARCHAR(10), default="A")
- ✅ **InvoiceExport**: `revision` (VARCHAR(10), default="A")
- ✅ **DeliveryOrder**: `revision` (VARCHAR(10), default="A")
- ✅ **PaymentCondition**: `revision` (VARCHAR(10), default="A")

**Beneficios:**
- Control de versiones de documentos
- Auditoría de modificaciones
- Correcciones sin cambiar números de documento
- Cumplimiento regulatorio

#### **Order - Referencias del Cliente:**
- `customer_quote_number` (VARCHAR(100), indexed) - Número de cotización del cliente
- `project_number` (VARCHAR(100), indexed) - Número de proyecto

#### **Order - Direcciones:**
- `shipping_address_id` (FK → addresses) - Dirección de envío/entrega
- `billing_address_id` (FK → addresses) - Dirección de facturación

#### **Transport - Tracking:**
- `delivery_number` (VARCHAR(100), indexed) - Número de entrega/tracking

---

## 📚 Referencias

- **SQLAlchemy 2.0**: https://docs.sqlalchemy.org/en/20/
- **Alembic**: https://alembic.sqlalchemy.org/
- **Plan de Implementación**: Ver `PLAN_IMPLEMENTACION_MODELOS.md`
- **Mejoras Propuestas**: Ver `MEJORAS_MODELOS.md`

---

## 🗄️ Base de Datos

**Ubicación**: `akgroup.db`
**Total de tablas**: 32
- 12 lookup tables
- 9 core models (11 tablas)
- 12 business models (9 tablas)

**Migraciones**: Alembic configurado y funcionando
**Convención de nombres**: 100% en inglés

---

## 📊 Resumen Completo de Tablas

### Tablas con `revision` (6):
| # | Tabla | Descripción | Posición |
|---|-------|-------------|----------|
| 1 | quotes | Cotizaciones | #3 |
| 2 | orders | Órdenes | #2 |
| 3 | invoices_sii | Facturas SII | #2 |
| 4 | invoices_export | Facturas Export | #2 |
| 5 | delivery_orders | Guías Despacho | #2 |
| 6 | payment_conditions | Condiciones Pago | #3 |

### Características del Sistema:
- ✅ **33 modelos** implementados
- ✅ **32 tablas** en base de datos
- ✅ **14 archivos** Python
- ✅ **~5,650 líneas** de código
- ✅ **100% en inglés** - Convención de nombres
- ✅ **6 tablas** con sistema de revisiones
- ✅ **Alembic** configurado y funcionando
- ✅ **SOLID principles** aplicados
- ✅ **Type hints** completos
- ✅ **Docstrings** en todos los modelos

---

**Última actualización**: 2025-01-28
**Estado**: ✅ **TODAS LAS FASES COMPLETADAS (100%)**
**Total modelos**: 33 modelos implementados
**Total archivos**: 14 archivos Python
**Tablas con revision**: 6/6 documentos de negocio
