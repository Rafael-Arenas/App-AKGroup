# Plan de Migración a Arquitectura Monorepo FastAPI + Flet

## Fecha: 2025-10-29

## Objetivo

Reorganizar el proyecto App-AKGroup de una arquitectura monolítica FastAPI a una arquitectura monorepo que separe claramente el backend (FastAPI) del frontend (Flet Desktop App), manteniendo schemas Pydantic compartidos.

---

## 1. Análisis de Estructura Actual

### Estructura Actual Identificada

```
App-AKGroup/
├── src/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── companies.py
│   │   │   ├── products.py
│   │   │   ├── addresses.py
│   │   │   ├── contacts.py
│   │   │   ├── services.py
│   │   │   ├── staff.py
│   │   │   ├── notes.py
│   │   │   ├── quotes.py
│   │   │   ├── orders.py
│   │   │   ├── deliveries.py
│   │   │   ├── invoices.py
│   │   │   └── lookups.py (falta confirmar)
│   │   ├── dependencies.py
│   │   ├── error_handlers.py
│   │   └── __init__.py
│   ├── models/
│   │   ├── base/
│   │   │   ├── base.py
│   │   │   ├── mixins.py
│   │   │   └── validators.py
│   │   ├── core/
│   │   │   ├── companies.py
│   │   │   ├── contacts.py
│   │   │   ├── notes.py
│   │   │   ├── staff.py
│   │   │   └── __init__.py
│   │   ├── business/
│   │   │   └── (archivos de negocio)
│   │   ├── lookups/
│   │   │   └── lookups.py
│   │   └── __init__.py
│   ├── schemas/
│   │   ├── base.py
│   │   ├── core/
│   │   │   ├── company.py
│   │   │   ├── product.py
│   │   │   ├── address.py
│   │   │   ├── contact.py
│   │   │   ├── service.py
│   │   │   ├── staff.py
│   │   │   ├── note.py
│   │   │   └── __init__.py
│   │   ├── business/
│   │   │   ├── quote.py
│   │   │   ├── order.py
│   │   │   ├── delivery.py
│   │   │   ├── invoice.py
│   │   │   └── __init__.py
│   │   ├── lookups/
│   │   │   ├── lookup.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── repositories/
│   │   ├── base.py
│   │   ├── core/
│   │   │   ├── company_repository.py
│   │   │   ├── product_repository.py
│   │   │   ├── address_repository.py
│   │   │   ├── contact_repository.py
│   │   │   ├── service_repository.py
│   │   │   ├── staff_repository.py
│   │   │   ├── note_repository.py
│   │   │   └── __init__.py
│   │   ├── business/
│   │   │   ├── quote_repository.py
│   │   │   ├── order_repository.py
│   │   │   ├── delivery_repository.py
│   │   │   ├── invoice_repository.py
│   │   │   └── __init__.py
│   │   ├── lookups/
│   │   │   ├── country_repository.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── services/
│   │   ├── base.py
│   │   ├── core/
│   │   │   ├── company_service.py
│   │   │   ├── product_service.py
│   │   │   ├── address_service.py
│   │   │   ├── contact_service.py
│   │   │   ├── service_service.py
│   │   │   ├── staff_service.py
│   │   │   ├── note_service.py
│   │   │   └── __init__.py
│   │   ├── business/
│   │   │   ├── quote_service.py
│   │   │   ├── order_service.py
│   │   │   ├── delivery_service.py
│   │   │   ├── invoice_service.py
│   │   │   └── __init__.py
│   │   ├── lookups/
│   │   └── __init__.py
│   ├── database/
│   │   ├── engine.py
│   │   ├── session.py
│   │   ├── connection.py
│   │   └── __init__.py
│   ├── config/
│   │   ├── settings.py
│   │   ├── constants.py
│   │   └── __init__.py
│   ├── exceptions/
│   │   ├── base.py
│   │   ├── repository.py
│   │   ├── service.py
│   │   └── __init__.py
│   ├── utils/
│   │   ├── logger.py
│   │   └── __init__.py
│   └── __init__.py
├── migrations/
│   ├── versions/
│   └── env.py
├── tests/
│   ├── models/
│   └── test_company_type_enum.py
├── scripts/
│   └── seed_company_types.py
├── seeds/
│   ├── seed_data.py
│   └── seed_countries.py
├── main.py (FastAPI)
├── pyproject.toml
├── alembic.ini
├── .env.example
├── .gitignore
└── README.md
```

### Dependencias Actuales

```toml
[tool.poetry.dependencies]
python = "^3.13"
flet = "^0.28.3"                    # Ya presente (pero no usado)
sqlalchemy = "^2.0.44"
pydantic = "^2.12.3"
loguru = "^0.7.3"
alembic = "^1.17.0"
pendulum = "^3.1.0"
pydantic-settings = "^2.11.0"
aiosqlite = "^0.21.0"
email-validator = "^2.3.0"
greenlet = "^3.2.4"
openpyxl = "^3.1.5"
fastapi = "^0.115.0"
uvicorn = {extras = ["standard"], version = "^0.34.0"}
pymysql = "^1.1.0"
cryptography = "^44.0.0"
```

---

## 2. Nueva Estructura Propuesta

```
App-AKGroup/
├── src/
│   ├── shared/                    # NUEVO: Código compartido
│   │   ├── __init__.py
│   │   ├── schemas/               # Pydantic schemas compartidos
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── core/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── company.py
│   │   │   │   ├── product.py
│   │   │   │   ├── address.py
│   │   │   │   ├── contact.py
│   │   │   │   ├── service.py
│   │   │   │   ├── staff.py
│   │   │   │   └── note.py
│   │   │   ├── business/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── quote.py
│   │   │   │   ├── order.py
│   │   │   │   ├── delivery.py
│   │   │   │   └── invoice.py
│   │   │   └── lookups/
│   │   │       ├── __init__.py
│   │   │       └── lookup.py
│   │   ├── exceptions/            # Excepciones compartidas
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── repository.py
│   │   │   └── service.py
│   │   └── constants.py           # Constantes compartidas
│   │
│   ├── backend/                   # NUEVO: Backend FastAPI
│   │   ├── __init__.py
│   │   ├── main.py                # Entrada FastAPI
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── dependencies.py
│   │   │   ├── error_handlers.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── companies.py
│   │   │       ├── products.py
│   │   │       ├── addresses.py
│   │   │       ├── contacts.py
│   │   │       ├── services.py
│   │   │       ├── staff.py
│   │   │       ├── notes.py
│   │   │       ├── quotes.py
│   │   │       ├── orders.py
│   │   │       ├── deliveries.py
│   │   │       ├── invoices.py
│   │   │       └── lookups.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py
│   │   │   │   ├── mixins.py
│   │   │   │   └── validators.py
│   │   │   ├── core/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── companies.py
│   │   │   │   ├── contacts.py
│   │   │   │   ├── notes.py
│   │   │   │   └── staff.py
│   │   │   ├── business/
│   │   │   │   └── __init__.py
│   │   │   └── lookups/
│   │   │       ├── __init__.py
│   │   │       └── lookups.py
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── core/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── company_repository.py
│   │   │   │   ├── product_repository.py
│   │   │   │   ├── address_repository.py
│   │   │   │   ├── contact_repository.py
│   │   │   │   ├── service_repository.py
│   │   │   │   ├── staff_repository.py
│   │   │   │   └── note_repository.py
│   │   │   ├── business/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── quote_repository.py
│   │   │   │   ├── order_repository.py
│   │   │   │   ├── delivery_repository.py
│   │   │   │   └── invoice_repository.py
│   │   │   └── lookups/
│   │   │       ├── __init__.py
│   │   │       └── country_repository.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── core/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── company_service.py
│   │   │   │   ├── product_service.py
│   │   │   │   ├── address_service.py
│   │   │   │   ├── contact_service.py
│   │   │   │   ├── service_service.py
│   │   │   │   ├── staff_service.py
│   │   │   │   └── note_service.py
│   │   │   ├── business/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── quote_service.py
│   │   │   │   ├── order_service.py
│   │   │   │   ├── delivery_service.py
│   │   │   │   └── invoice_service.py
│   │   │   └── lookups/
│   │   │       └── __init__.py
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── engine.py
│   │   │   ├── session.py
│   │   │   └── connection.py
│   │   └── config/
│   │       ├── __init__.py
│   │       └── settings.py
│   │
│   └── frontend/                  # NUEVO: Frontend Flet
│       ├── __init__.py
│       ├── main.py                # Entrada Flet
│       ├── app.py                 # Clase principal App
│       ├── config/
│       │   ├── __init__.py
│       │   └── settings.py
│       ├── services/
│       │   ├── __init__.py
│       │   ├── base_api_client.py
│       │   ├── company_api.py
│       │   ├── product_api.py
│       │   └── auth_api.py (futuro)
│       ├── views/
│       │   ├── __init__.py
│       │   ├── base_view.py
│       │   ├── home_view.py
│       │   ├── companies/
│       │   │   ├── __init__.py
│       │   │   ├── companies_list_view.py
│       │   │   ├── company_detail_view.py
│       │   │   └── company_form_view.py
│       │   ├── products/
│       │   │   ├── __init__.py
│       │   │   ├── products_list_view.py
│       │   │   └── product_detail_view.py
│       │   └── settings/
│       │       ├── __init__.py
│       │       └── settings_view.py
│       ├── components/
│       │   ├── __init__.py
│       │   ├── navigation.py
│       │   ├── data_table.py
│       │   ├── form_fields.py
│       │   └── dialogs.py
│       ├── utils/
│       │   ├── __init__.py
│       │   ├── logger.py
│       │   ├── validators.py
│       │   └── formatters.py
│       └── assets/
│           └── (imágenes, iconos, etc.)
│
├── migrations/                    # Sin cambios
│   ├── versions/
│   └── env.py
│
├── tests/                         # Reorganizado
│   ├── __init__.py
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_repositories.py
│   │   ├── test_services.py
│   │   └── test_api.py
│   ├── frontend/
│   │   ├── __init__.py
│   │   └── test_components.py
│   └── shared/
│       ├── __init__.py
│       └── test_schemas.py
│
├── scripts/                       # Actualizado
│   ├── __init__.py
│   ├── dev_backend.py            # NUEVO: Ejecutar backend
│   ├── dev_frontend.py           # NUEVO: Ejecutar frontend
│   ├── dev_all.py                # NUEVO: Ejecutar ambos
│   ├── build_frontend.py         # NUEVO: Build frontend
│   └── seed_company_types.py
│
├── seeds/                         # Sin cambios
│   ├── seed_data.py
│   └── seed_countries.py
│
├── docs/                          # Actualizado
│   ├── ARCHITECTURE.md           # NUEVO
│   ├── BACKEND_API.md            # NUEVO
│   ├── FRONTEND_GUIDE.md         # NUEVO
│   └── MIGRATION_PLAN.md         # Este archivo
│
├── main.py                        # DEPRECATED: Mover a src/backend/main.py
├── pyproject.toml                 # Actualizar
├── alembic.ini                    # Sin cambios
├── .env.example                   # Actualizar
├── .gitignore                     # Actualizar
├── CLAUDE.md                      # Actualizar
└── README.md                      # Actualizar
```

---

## 3. Plan de Migración Paso a Paso

### Fase 1: Preparación (No Rompe Nada)

**1.1. Crear estructura de carpetas vacía**

```bash
mkdir -p src/shared/schemas/core
mkdir -p src/shared/schemas/business
mkdir -p src/shared/schemas/lookups
mkdir -p src/shared/exceptions
mkdir -p src/backend/api/v1
mkdir -p src/backend/models/base
mkdir -p src/backend/models/core
mkdir -p src/backend/models/business
mkdir -p src/backend/models/lookups
mkdir -p src/backend/repositories/core
mkdir -p src/backend/repositories/business
mkdir -p src/backend/repositories/lookups
mkdir -p src/backend/services/core
mkdir -p src/backend/services/business
mkdir -p src/backend/services/lookups
mkdir -p src/backend/database
mkdir -p src/backend/config
mkdir -p src/frontend/views/companies
mkdir -p src/frontend/views/products
mkdir -p src/frontend/views/settings
mkdir -p src/frontend/components
mkdir -p src/frontend/services
mkdir -p src/frontend/utils
mkdir -p src/frontend/assets
mkdir -p src/frontend/config
mkdir -p tests/backend
mkdir -p tests/frontend
mkdir -p tests/shared
mkdir -p scripts
mkdir -p docs
```

**1.2. Crear archivos __init__.py necesarios**

Todos los directorios Python deben tener `__init__.py`.

**1.3. Actualizar pyproject.toml**

Agregar dependencias necesarias:
- `httpx` para el cliente HTTP del frontend
- Configurar packages correctamente

### Fase 2: Mover Schemas a Shared (Alta Prioridad)

**2.1. Copiar schemas a shared/**

```
src/schemas/ -> src/shared/schemas/
```

**Importante**: COPIAR primero, no mover. Mantener originales hasta validar.

**2.2. Actualizar imports en shared/schemas/**

Cambiar todos los imports de:
```python
from src.schemas.base import ...
from src.config.constants import ...
from src.exceptions.base import ...
```

A:
```python
from src.shared.schemas.base import ...
from src.shared.constants import ...
from src.shared.exceptions.base import ...
```

**2.3. Mover excepciones a shared/**

```
src/exceptions/ -> src/shared/exceptions/
```

**2.4. Mover constantes a shared/**

```
src/config/constants.py -> src/shared/constants.py
```

### Fase 3: Mover Backend (Crítico - Hacerlo Cuidadosamente)

**3.1. Mover modelos**

```
src/models/ -> src/backend/models/
```

**3.2. Mover repositories**

```
src/repositories/ -> src/backend/repositories/
```

**3.3. Mover services**

```
src/services/ -> src/backend/services/
```

**3.4. Mover API**

```
src/api/ -> src/backend/api/
```

**3.5. Mover database**

```
src/database/ -> src/backend/database/
```

**3.6. Mover config**

```
src/config/ -> src/backend/config/
```

**3.7. Mover utils**

```
src/utils/ -> src/backend/utils/
```

**3.8. Mover main.py**

```
main.py -> src/backend/main.py
```

### Fase 4: Actualizar Todos los Imports del Backend

Esta es la parte más delicada. Cada archivo del backend debe actualizar sus imports.

**Patrones de reemplazo:**

| Antes | Después |
|-------|---------|
| `from src.schemas.` | `from src.shared.schemas.` |
| `from src.exceptions.` | `from src.shared.exceptions.` |
| `from src.config.constants` | `from src.shared.constants` |
| `from src.models.` | `from src.backend.models.` |
| `from src.repositories.` | `from src.backend.repositories.` |
| `from src.services.` | `from src.backend.services.` |
| `from src.api.` | `from src.backend.api.` |
| `from src.database.` | `from src.backend.database.` |
| `from src.config.settings` | `from src.backend.config.settings` |
| `from src.utils.` | `from src.backend.utils.` |

**Archivos críticos a actualizar:**

1. `src/backend/main.py` - Entry point
2. Todos los archivos en `src/backend/api/v1/*.py`
3. Todos los archivos en `src/backend/services/`
4. Todos los archivos en `src/backend/repositories/`
5. `src/backend/api/dependencies.py`
6. `src/backend/api/error_handlers.py`
7. `migrations/env.py` - Importante para Alembic

### Fase 5: Actualizar Configuración

**5.1. Actualizar alembic.ini**

Cambiar:
```ini
script_location = migrations
```

**5.2. Actualizar migrations/env.py**

Cambiar imports:
```python
from src.backend.models.base.base import Base
from src.backend.config.settings import settings
```

**5.3. Actualizar pyproject.toml**

```toml
[tool.poetry]
packages = [
    {include = "src"}
]

[tool.poetry.dependencies]
httpx = "^0.27.0"  # NUEVO para frontend
```

**5.4. Actualizar .env.example**

Agregar variables para frontend:
```env
# Backend API
API_HOST=127.0.0.1
API_PORT=8000

# Frontend
FRONTEND_API_URL=http://127.0.0.1:8000
```

### Fase 6: Crear Frontend Flet (Nuevo)

**6.1. Crear archivos base (ver sección 4)**

**6.2. Implementar cliente API**

**6.3. Implementar vistas básicas**

**6.4. Implementar componentes reutilizables**

### Fase 7: Testing

**7.1. Verificar backend**

```bash
cd src/backend
python main.py
```

**7.2. Verificar frontend**

```bash
cd src/frontend
python main.py
```

**7.3. Verificar tests**

```bash
pytest tests/backend/
pytest tests/frontend/
pytest tests/shared/
```

### Fase 8: Limpieza

**8.1. Eliminar archivos antiguos**

Después de validar que todo funciona:
```
rm -rf src/schemas/
rm -rf src/exceptions/
rm main.py (raíz)
```

**8.2. Limpiar __pycache__**

```bash
find . -type d -name "__pycache__" -exec rm -rf {} +
```

**8.3. Regenerar poetry.lock si es necesario**

```bash
poetry lock --no-update
```

---

## 4. Mapeo de Archivos Críticos

### Archivos a Mover

| Archivo Actual | Destino | Cambios Requeridos |
|----------------|---------|-------------------|
| `main.py` | `src/backend/main.py` | Actualizar todos los imports |
| `src/schemas/**/*.py` | `src/shared/schemas/**/*.py` | Actualizar imports internos |
| `src/exceptions/**/*.py` | `src/shared/exceptions/**/*.py` | Actualizar imports |
| `src/config/constants.py` | `src/shared/constants.py` | - |
| `src/models/**/*.py` | `src/backend/models/**/*.py` | Actualizar imports a shared |
| `src/repositories/**/*.py` | `src/backend/repositories/**/*.py` | Actualizar imports |
| `src/services/**/*.py` | `src/backend/services/**/*.py` | Actualizar imports |
| `src/api/**/*.py` | `src/backend/api/**/*.py` | Actualizar imports |
| `src/database/**/*.py` | `src/backend/database/**/*.py` | Actualizar imports |
| `src/config/settings.py` | `src/backend/config/settings.py` | Actualizar imports |
| `src/utils/**/*.py` | `src/backend/utils/**/*.py` | - |

### Archivos que NO se Mueven

- `migrations/` - Se mantiene en raíz
- `tests/` - Se reorganiza pero mantiene en raíz
- `scripts/` - Se mantiene en raíz
- `seeds/` - Se mantiene en raíz
- `pyproject.toml` - Se mantiene en raíz
- `alembic.ini` - Se mantiene en raíz
- `.env`, `.gitignore`, `README.md` - Se mantienen en raíz

---

## 5. Cambios en Configuración

### pyproject.toml - Cambios Requeridos

```toml
[tool.poetry]
name = "app-akgroup"
version = "0.1.0"
description = "Sistema de gestión empresarial AK Group - Monorepo FastAPI + Flet"
authors = ["Rafael Arenas López <ra.arenas.lopez@gmail.com>"]
readme = "README.md"
packages = [
    {include = "src"}
]

[tool.poetry.dependencies]
python = "^3.13"
# Backend
fastapi = "^0.115.0"
uvicorn = {extras = ["standard"], version = "^0.34.0"}
sqlalchemy = "^2.0.44"
alembic = "^1.17.0"
aiosqlite = "^0.21.0"
pymysql = "^1.1.0"
cryptography = "^44.0.0"
greenlet = "^3.2.4"
# Frontend
flet = "^0.28.3"
httpx = "^0.27.0"  # NUEVO
# Shared
pydantic = "^2.12.3"
pydantic-settings = "^2.11.0"
email-validator = "^2.3.0"
loguru = "^0.7.3"
pendulum = "^3.1.0"
openpyxl = "^3.1.5"

[tool.poetry.group.dev.dependencies]
pytest = "^8.0.0"
pytest-cov = "^4.1.0"
pytest-asyncio = "^0.24.0"  # NUEVO para tests async
black = "^24.0.0"
ruff = "^0.1.0"
mypy = "^1.8.0"

[tool.poetry.scripts]
backend = "scripts.dev_backend:main"
frontend = "scripts.dev_frontend:main"
dev = "scripts.dev_all:main"

[build-system]
requires = ["poetry-core>=2.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.black]
line-length = 88
target-version = ['py313']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.mypy_cache
  | \.venv
  | build
  | dist
)/
'''

[tool.ruff]
line-length = 88
target-version = "py313"

[tool.mypy]
python_version = "3.13"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

### .env.example - Actualización

```env
# ============================================================================
# BACKEND CONFIGURATION
# ============================================================================

# Environment
ENVIRONMENT=development

# Database
DATABASE_TYPE=sqlite
DATABASE_URL=sqlite:///./akgroup.db

# For MySQL/MariaDB (production)
# DATABASE_TYPE=mysql
# DATABASE_URL=mysql+pymysql://user:password@localhost:3306/akgroup

# API Configuration
API_HOST=127.0.0.1
API_PORT=8000
API_RELOAD=True

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://127.0.0.1:8000"]

# Security (futuro)
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOG_LEVEL=DEBUG
LOG_FILE=logs/app.log

# ============================================================================
# FRONTEND CONFIGURATION
# ============================================================================

# API Connection
FRONTEND_API_URL=http://127.0.0.1:8000
FRONTEND_API_TIMEOUT=30

# App Settings
APP_TITLE=AK Group - Sistema de Gestión
APP_WIDTH=1280
APP_HEIGHT=800

# UI Theme
UI_THEME=light  # light, dark, auto
PRIMARY_COLOR=#2196F3
```

### alembic.ini - Sin cambios importantes

Solo asegurarse que `script_location = migrations` esté correcto.

### migrations/env.py - Actualizar Imports

```python
# Cambiar:
from src.models.base.base import Base
from src.config.settings import settings

# A:
from src.backend.models.base.base import Base
from src.backend.config.settings import settings
```

---

## 6. Riesgos y Mitigaciones

### Riesgos Identificados

1. **Imports rotos** - Alto impacto
   - Mitigación: Script de búsqueda/reemplazo automatizado
   - Validación: Ejecutar `mypy` y `ruff` después de cada cambio

2. **Alembic no encuentra modelos** - Alto impacto
   - Mitigación: Actualizar `migrations/env.py` correctamente
   - Validación: Ejecutar `alembic check`

3. **Tests fallan** - Medio impacto
   - Mitigación: Actualizar imports en tests
   - Validación: Ejecutar `pytest` después de migración

4. **Circular imports** - Medio impacto
   - Mitigación: Revisar estructura de imports
   - Usar imports absolutos siempre

5. **Path de Python no configurado** - Bajo impacto
   - Mitigación: Asegurarse que raíz del proyecto esté en PYTHONPATH
   - Scripts deben manejar esto automáticamente

### Checklist de Validación

- [ ] Backend inicia sin errores
- [ ] Frontend inicia sin errores
- [ ] API responde a peticiones
- [ ] Frontend puede conectarse al backend
- [ ] Tests pasan
- [ ] MyPy no reporta errores
- [ ] Ruff no reporta errores
- [ ] Alembic puede generar migraciones
- [ ] Alembic puede aplicar migraciones
- [ ] Logs se generan correctamente

---

## 7. Timeline Estimado

| Fase | Tiempo Estimado | Descripción |
|------|----------------|-------------|
| Fase 1 | 30 min | Crear estructura de carpetas |
| Fase 2 | 1 hora | Mover y actualizar schemas |
| Fase 3 | 2 horas | Mover código del backend |
| Fase 4 | 3 horas | Actualizar todos los imports |
| Fase 5 | 1 hora | Actualizar configuración |
| Fase 6 | 4 horas | Crear frontend base |
| Fase 7 | 2 horas | Testing completo |
| Fase 8 | 30 min | Limpieza |
| **TOTAL** | **14 horas** | Estimado conservador |

---

## 8. Comandos Útiles

### Búsqueda y Reemplazo de Imports

```bash
# Buscar todos los archivos con imports antiguos
grep -r "from src.schemas" src/backend/

# Reemplazo automático (con precaución)
find src/backend -type f -name "*.py" -exec sed -i 's/from src\.schemas\./from src.shared.schemas./g' {} +
find src/backend -type f -name "*.py" -exec sed -i 's/from src\.exceptions\./from src.shared.exceptions./g' {} +
find src/backend -type f -name "*.py" -exec sed -i 's/from src\.config\.constants/from src.shared.constants/g' {} +
```

### Validación de Imports

```bash
# Verificar que no haya imports rotos
python -m py_compile src/backend/main.py

# Verificar con mypy
mypy src/backend/

# Verificar con ruff
ruff check src/backend/
```

### Testing

```bash
# Test completo
pytest -v

# Test con coverage
pytest --cov=src/backend --cov=src/frontend --cov=src/shared --cov-report=html

# Test específico
pytest tests/backend/test_services.py -v
```

---

## 9. Rollback Plan

Si algo sale mal durante la migración:

1. **Git**: Hacer commit antes de cada fase
2. **Plant**: Trabajar en `Plant`/monorepo-migration`
3. **Backup**: Guardar copia de `src/` original
4. **Rollback**: `git reset --hard` al commit anterior

---

## 10. Post-Migración

### Tareas Posteriores

1. Actualizar documentación completa
2. Actualizar CLAUDE.md con nueva estructura
3. Crear scripts de desarrollo
4. Configurar CI/CD si existe
5. Actualizar README.md
6. Entrenar equipo en nueva estructura

### Mejoras Futuras

1. Autenticación JWT en backend
2. State management en frontend (Provider pattern)
3. Caché en frontend
4. Offline mode en frontend
5. Tests e2e
6. Docker para deployment
7. GitHub Actions para CI/CD

---

## Conclusión

Esta migración es necesaria para:
- Separar responsabilidades claramente
- Permitir desarrollo independiente de frontend/backend
- Reutilizar schemas Pydantic
- Facilitar escalabilidad futura
- Mejorar mantenibilidad

**Siguiente paso**: Revisar este plan y dar aprobación para comenzar implementación.
