# Arquitectura Monorepo - App-AKGroup

## Visión General

App-AKGroup utiliza una arquitectura monorepo que separa el backend (FastAPI) del frontend (Flet), compartiendo código común (schemas Pydantic, excepciones, constantes).

```
┌─────────────────────────────────────────────────────────────┐
│                      App-AKGroup Monorepo                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────┐      ┌────────────┐      ┌────────────┐   │
│  │            │      │            │      │            │   │
│  │  Frontend  │◄────►│   Shared   │◄────►│  Backend   │   │
│  │   (Flet)   │      │  (Schemas) │      │ (FastAPI)  │   │
│  │            │      │            │      │            │   │
│  └────────────┘      └────────────┘      └────────────┘   │
│       │                                         │           │
│       │                                         │           │
│       │ HTTP/REST                               │           │
│       └─────────────────────────────────────────┘           │
│                                                              │
│                      ┌────────────┐                         │
│                      │  Database  │                         │
│                      │  (SQLite/  │                         │
│                      │   MySQL)   │                         │
│                      └────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Componentes Principales

### 1. Shared (Código Compartido)

**Propósito**: Código que ambos, frontend y backend, necesitan compartir.

**Contenido**:
- **Schemas Pydantic**: DTOs (Data Transfer Objects) para validación y serialización
- **Excepciones**: Clases de excepción personalizadas
- **Constantes**: Valores constantes compartidos (tipos, estados, etc.)

**Estructura**:
```
src/shared/
├── __init__.py
├── constants.py
├── exceptions/
│   ├── __init__.py
│   ├── base.py
│   ├── repository.py
│   └── service.py
└── schemas/
    ├── __init__.py
    ├── base.py
    ├── core/
    │   ├── __init__.py
    │   ├── company.py
    │   ├── product.py
    │   └── ...
    ├── business/
    │   ├── __init__.py
    │   ├── quote.py
    │   └── ...
    └── lookups/
        ├── __init__.py
        └── lookup.py
```

**Principios**:
- Sin dependencias de FastAPI o Flet
- Solo Pydantic y librerías estándar
- Importable desde backend y frontend

---

### 2. Backend (FastAPI API)

**Propósito**: API REST que maneja la lógica de negocio y acceso a datos.

**Arquitectura**: Clean Architecture / Layered Architecture

```
┌─────────────────────────────────────────────┐
│              API Layer (FastAPI)             │
│  ┌───────────────────────────────────────┐  │
│  │  Routes (companies, products, etc.)   │  │
│  └─────────┬─────────────────────┘  │
│                    │                         │
│  ┌─────────────────▼─────────────────────┐  │
│  │        Service Layer (Business)       │  │
│  │  ┌─────────────────────────────────┐  │  │
│  │  │  CompanyService, ProductService │  │  │
│  │  └───────────────┬─────────────────┘  │  │
│  └──────────────────┼─────────────────────┘  │
│                     │                         │
│  ┌──────────────────▼──────────────────────┐ │
│  │     Repository Layer (Data Access)      │ │
│  │  ┌────────────────────────────────────┐ │ │
│  │  │  CompanyRepo, ProductRepo, etc.    │ │ │
│  │  └──────────────┬─────────────────────┘ │ │
│  └─────────────────┼───────────────────────┘ │
│                    │                         │
│  ┌─────────────────▼─────────────────────┐  │
│  │       Models Layer (SQLAlchemy)       │  │
│  │  ┌─────────────────────────────────┐  │  │
│  │  │  Company, Product, Branch, etc. │  │  │
│  │  └─────────────────────────────────┘  │  │
│  └───────────────────────────────────────┘  │
│                    │                         │
│  ┌─────────────────▼─────────────────────┐  │
│  │          Database (SQLAlchemy)        │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

**Capas**:

1. **API Layer** (`api/v1/*.py`)
   - Endpoints FastAPI
   - Request/Response handling
   - Dependency injection
   - Error handling

2. **Service Layer** (`services/`)
   - Lógica de negocio
   - Validaciones complejas
   - Orquestación de repositorios
   - Transacciones

3. **Repository Layer** (`repositories/`)
   - Acceso a datos
   - Queries SQL
   - CRUD operations
   - Patrón Repository

4. **Model Layer** (`models/`)
   - Definiciones SQLAlchemy
   - Relaciones
   - Constraints
   - Validators

**Estructura**:
```
src/backend/
├── __init__.py
├── main.py                    # Entry point FastAPI
├── api/
│   ├── __init__.py
│   ├── dependencies.py        # DI containers
│   ├── error_handlers.py      # Exception handlers
│   └── v1/
│       ├── __init__.py
│       ├── companies.py
│       ├── products.py
│       └── ...
├── services/
│   ├── __init__.py
│   ├── base.py               # BaseService
│   ├── core/
│   │   ├── __init__.py
│   │   ├── company_service.py
│   │   └── ...
│   └── business/
│       ├── __init__.py
│       └── ...
├── repositories/
│   ├── __init__.py
│   ├── base.py               # BaseRepository
│   ├── core/
│   │   ├── __init__.py
│   │   ├── company_repository.py
│   │   └── ...
│   └── business/
│       └── ...
├── models/
│   ├── __init__.py
│   ├── base/
│   │   ├── __init__.py
│   │   ├── base.py           # Base SQLAlchemy model
│   │   ├── mixins.py         # TimestampMixin, SoftDeleteMixin
│   │   └── validators.py     # Custom validators
│   ├── core/
│   │   ├── __init__.py
│   │   ├── companies.py
│   │   └── ...
│   └── lookups/
│       └── ...
├── database/
│   ├── __init__.py
│   ├── engine.py             # SQLAlchemy engine
│   ├── session.py            # Session factory
│   └── connection.py         # Connection utilities
├── config/
│   ├── __init__.py
│   └── settings.py           # Pydantic Settings
└── utils/
    ├── __init__.py
    └── logger.py             # Loguru config
```

**Principios SOLID**:
- **Single Responsibility**: Cada capa tiene una responsabilidad clara
- **Open/Closed**: Extensible mediante herencia/interfaces
- **Liskov Substitution**: Repositorios intercambiables
- **Interface Segregation**: Interfaces específicas (IRepository)
- **Dependency Inversion**: Depende de abstracciones, no implementaciones

---

### 3. Frontend (Flet Desktop App)

**Propósito**: Aplicación de escritorio cross-platform para interactuar con la API.

**Arquitectura**: MVVM-like (Model-View-ViewModel)

```
┌──────────────────────────────────────────────┐
│              Flet Application                │
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │         Views (UI Components)          │ │
│  │  ┌──────────────────────────────────┐  │ │
│  │  │  CompanyListView, ProductView    │  │ │
│  │  └──────────────┬───────────────────┘  │ │
│  └─────────────────┼───────────────────────┘ │
│                    │                         │
│  ┌─────────────────▼─────────────────────┐  │
│  │      Services (API Clients)           │  │
│  │  ┌────────────────────────────────┐   │  │
│  │  │  CompanyAPI, ProductAPI, etc.  │   │  │
│  │  └──────────────┬─────────────────┘   │  │
│  └─────────────────┼───────────────────────┘ │
│                    │ HTTP/REST               │
│  ┌─────────────────▼─────────────────────┐  │
│  │        Backend API (FastAPI)          │  │
│  └───────────────────────────────────────┘  │
└──────────────────────────────────────────────┘
```

**Capas**:

1. **Views** (`views/`)
   - Componentes de UI (páginas)
   - Manejo de eventos de usuario
   - Renderizado de datos
   - Navegación

2. **Components** (`components/`)
   - Componentes reutilizables
   - Data tables, forms, dialogs
   - Navigation bar
   - Custom controls

3. **Services** (`services/`)
   - Clientes HTTP (httpx)
   - Llamadas a API REST
   - Manejo de respuestas
   - Cache (futuro)

4. **Utils** (`utils/`)
   - Helpers
   - Formatters
   - Validators
   - Logger

**Estructura**:
```
src/frontend/
├── __init__.py
├── main.py                    # Entry point Flet
├── app.py                     # App class principal
├── config/
│   ├── __init__.py
│   └── settings.py
├── views/
│   ├── __init__.py
│   ├── base_view.py          # BaseView abstract
│   ├── home_view.py
│   ├── companies/
│   │   ├── __init__.py
│   │   ├── companies_list_view.py
│   │   ├── company_detail_view.py
│   │   └── company_form_view.py
│   ├── products/
│   │   ├── __init__.py
│   │   ├── products_list_view.py
│   │   └── product_detail_view.py
│   └── settings/
│       ├── __init__.py
│       └── settings_view.py
├── components/
│   ├── __init__.py
│   ├── navigation.py         # NavBar, Drawer
│   ├── data_table.py         # DataTable custom
│   ├── form_fields.py        # TextField, Dropdown custom
│   └── dialogs.py            # Alert, Confirm, etc.
├── services/
│   ├── __init__.py
│   ├── base_api_client.py    # BaseAPIClient
│   ├── company_api.py        # CompanyAPIClient
│   ├── product_api.py        # ProductAPIClient
│   └── auth_api.py           # (futuro)
├── utils/
│   ├── __init__.py
│   ├── logger.py
│   ├── validators.py
│   └── formatters.py
└── assets/
    ├── logo.png
    └── icons/
```

**Patrones**:
- **Composition over Inheritance**: Componentes compuestos
- **Observer**: Flet reactivity
- **Strategy**: Diferentes vistas según contexto
- **Facade**: API clients simplifican comunicación

---

## Flujo de Datos

### Request Flow (Frontend → Backend)

```
┌─────────────┐
│   User      │
│   Action    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   View      │
│  (Button    │
│   Click)    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  API Client │ ◄─── Usa schemas compartidos
│  (httpx)    │
└──────┬──────┘
       │ HTTP POST /api/v1/companies
       │ Body: CompanyCreate schema
       ▼
┌─────────────┐
│  FastAPI    │
│  Endpoint   │ ◄─── Valida con schemas compartidos
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Service    │ ◄─── Business logic
│  Layer      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Repository  │ ◄─── Data access
│  Layer      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Database   │
└─────────────┘
```

### Response Flow (Backend → Frontend)

```
┌─────────────┐
│  Database   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Repository  │ ◄─── Returns ORM model
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Service    │ ◄─── Converts to schema
│  Layer      │      (CompanyResponse)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  FastAPI    │ ◄─── Serializes to JSON
│  Response   │
└──────┬──────┘
       │ HTTP 200 OK
       │ Body: CompanyResponse JSON
       ▼
┌─────────────┐
│  API Client │ ◄─── Deserializes to schema
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   View      │ ◄─── Renders data
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   User      │
│   Sees Data │
└─────────────┘
```

---

## Ventajas de esta Arquitectura

### 1. Separación de Responsabilidades

- **Backend**: Solo se preocupa de lógica de negocio y datos
- **Frontend**: Solo se preocupa de UI/UX
- **Shared**: DTOs garantizan contrato entre ambos

### 2. Desarrollo Independiente

- Equipos pueden trabajar en paralelo
- Frontend puede mockear API
- Backend puede testear sin frontend

### 3. Reutilización de Código

- Schemas Pydantic compartidos
- No duplicar validaciones
- Tipos consistentes

### 4. Testabilidad

- Cada capa es testeable independientemente
- Mocks fáciles con interfaces
- Tests unitarios y de integración separados

### 5. Escalabilidad

- Backend puede servir múltiples frontends (web, mobile, desktop)
- Puede separarse en microservicios en el futuro
- Frontend puede distribuirse independientemente

### 6. Mantenibilidad

- Cambios en una capa no afectan otras
- Código organizado y predecible
- Fácil onboarding de nuevos desarrolladores

---

## Tecnologías y Librerías

### Backend
- **FastAPI**: Framework web moderno y rápido
- **SQLAlchemy**: ORM robusto
- **Alembic**: Migraciones de base de datos
- **Pydantic**: Validación de datos
- **Uvicorn**: ASGI server
- **Loguru**: Logging avanzado

### Frontend
- **Flet**: Framework para apps desktop (Flutter)
- **httpx**: Cliente HTTP async
- **Pydantic**: Validación (compartido)

### Shared
- **Pydantic**: Schemas y validación
- **Python 3.13**: Type hints modernos

### Dev Tools
- **Poetry**: Gestión de dependencias
- **Black**: Formateo de código
- **Ruff**: Linting rápido
- **MyPy**: Type checking
- **Pytest**: Testing

---

## Convenciones de Código

### Imports

**Orden**:
1. Standard library
2. Third-party
3. Local application

**Estilo**:
- Imports absolutos desde raíz del proyecto
- No usar imports relativos

```python
# ✅ Correcto
from src.shared.schemas.core.company import CompanyCreate
from src.backend.services.core.company_service import CompanyService

# ❌ Incorrecto
from ..schemas.company import CompanyCreate
from ...services import CompanyService
```

### Naming

- **Módulos/Paquetes**: `snake_case`
- **Clases**: `PascalCase`
- **Funciones/Variables**: `snake_case`
- **Constantes**: `UPPER_SNAKE_CASE`
- **Privadas**: `_prefix`

### Type Hints

Siempre usar type hints completos:

```python
def get_company(company_id: int) -> Company | None:
    """Obtiene una empresa por ID."""
    pass

async def create_company(data: CompanyCreate) -> CompanyResponse:
    """Crea una nueva empresa."""
    pass
```

### Docstrings

Estilo Google/NumPy con secciones:
- Args
- Returns
- Raises
- Example

```python
def calculate_total(items: list[dict], tax: float = 0.19) -> Decimal:
    """
    Calcula el total con impuestos.

    Args:
        items: Lista de items con precios
        tax: Tasa de impuesto (default: 0.19)

    Returns:
        Total calculado con impuestos

    Raises:
        ValueError: Si items está vacío

    Example:
        >>> calculate_total([{"price": 100}], 0.19)
        Decimal("119.00")
    """
    pass
```

---

## Consideraciones de Seguridad

### Backend

1. **Autenticación**: JWT tokens (futuro)
2. **Autorización**: RBAC (futuro)
3. **Validación**: Pydantic en todos los inputs
4. **SQL Injection**: SQLAlchemy ORM previene
5. **CORS**: Configurado correctamente
6. **Secrets**: Nunca en código, usar .env

### Frontend

1. **API URL**: Configurable por entorno
2. **Tokens**: Almacenar de forma segura
3. **Inputs**: Validar antes de enviar
4. **HTTPS**: Solo en producción

---

## Performance

### Backend

1. **Async/Await**: SQLAlchemy async donde posible
2. **Connection Pooling**: Configurado en engine
3. **Lazy Loading**: Cuidado con N+1 queries
4. **Caching**: Redis (futuro)
5. **Pagination**: Implementado en todos los listados

### Frontend

1. **Lazy Loading**: Cargar datos solo cuando necesario
2. **Caching**: Cache de respuestas (futuro)
3. **Debouncing**: En búsquedas
4. **Virtual Scrolling**: Para listas largas
5. **Image Optimization**: Comprimir assets

---

## Deployment

### Backend

```bash
# Desarrollo
uvicorn src.backend.main:app --reload

# Producción
uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend

```bash
# Desarrollo
python src/frontend/main.py

# Build para distribución
flet build macos   # Para macOS
flet build windows # Para Windows
flet build linux   # Para Linux
```

---

## Próximos Pasos

1. **Autenticación**: Implementar JWT
2. **Autorización**: RBAC con roles
3. **Tests E2E**: Playwright/Selenium
4. **CI/CD**: GitHub Actions
5. **Docker**: Containerización
6. **Monitoring**: Prometheus + Grafana
7. **Documentación API**: OpenAPI/Swagger (ya está)
8. **Frontend State Management**: Provider pattern

---

## Referencias

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Flet Docs](https://flet.dev/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [Python 3.13 Release Notes](https://docs.python.org/3.13/whatsnew/3.13.html)

---

**Última actualización**: 2025-10-29
