# App-AKGroup - Sistema de Gestión Empresarial

**Arquitectura Monorepo**: FastAPI (Backend) + Flet (Frontend)

---

## 🎯 Descripción

Sistema de gestión empresarial para AK Group que permite administrar empresas, productos, órdenes, cotizaciones y más. Desarrollado con arquitectura monorepo que separa el backend API REST del frontend desktop.

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────┐
│         App-AKGroup Monorepo            │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────┐    ┌──────────┐         │
│  │ Frontend │◄──►│  Shared  │         │
│  │  (Flet)  │    │(Schemas) │         │
│  └─────┬────┘    └────┬─────┘         │
│        │              │               │
│        │ HTTP/REST    │               │
│        │              ▼               │
│        │      ┌──────────┐            │
│        └─────►│ Backend  │            │
│               │(FastAPI) │            │
│               └────┬─────┘            │
│                    │                  │
│                    ▼                  │
│               ┌──────────┐            │
│               │ Database │            │
│               └──────────┘            │
└─────────────────────────────────────────┘
```

---

## 🚀 Tech Stack

### Backend
- **FastAPI** 0.115.0 - Framework web moderno
- **SQLAlchemy** 2.0.44 - ORM
- **Alembic** 1.17.0 - Migraciones
- **Uvicorn** - ASGI server
- **Pydantic** 2.12.3 - Validación de datos

### Frontend
- **Flet** 0.28.3 - Framework desktop (Flutter)
- **httpx** 0.27.0 - Cliente HTTP
- **Pydantic** - Validación compartida

### Shared
- **Pydantic** - Schemas compartidos
- **Python** 3.13 - Type hints modernos

### DevTools
- **Poetry** 2.1.3+ - Gestión de dependencias
- **Plant**: Plantas y sucursales.
- **Ruff** - Linting
- **MyPy** - Type checking
- **Pytest** - Testing

---

## 📁 Estructura del Proyecto

```
App-AKGroup/
├── src/
│   ├── shared/              # Código compartido
│   │   ├── schemas/         # Pydantic schemas (DTOs)
│   │   ├── exceptions/      # Excepciones personalizadas
│   │   └── constants.py     # Constantes compartidas
│   │
│   ├── backend/             # API REST
│   │   ├── main.py          # Entry point FastAPI
│   │   ├── api/             # Endpoints
│   │   ├── models/          # SQLAlchemy models
│   │   ├── repositories/    # Data access layer
│   │   ├── services/        # Business logic
│   │   ├── database/        # DB configuration
│   │   ├── config/          # Settings
│   │   └── utils/           # Helpers
│   │
│   └── frontend/            # Desktop App
│       ├── main.py          # Entry point Flet
│       ├── config/          # Settings
│       ├── services/        # API clients
│       ├── views/           # UI views
│       ├── components/      # Reusable UI components
│       └── utils/           # Helpers
│
├── migrations/              # Alembic migrations
├── tests/                   # Tests
│   ├── backend/
│   ├── frontend/
│   └── shared/
├── scripts/                 # Development scripts
│   ├── dev_backend.py
│   ├── dev_frontend.py
│   └── dev_all.py
├── docs/                    # Documentation
│   ├── ARCHITECTURE.md
│   ├── MIGRATION_PLAN.md
│   └── RESUMEN_PREPARACION.md
├── seeds/                   # Database seeds
├── logs/                    # Application logs
├── pyproject.toml           # Poetry configuration
├── alembic.ini              # Alembic configuration
├── .env.example             # Environment variables template
└── README.md                # This file
```

---

## 🛠️ Instalación

### Requisitos

- Python 3.13+
- Poetry 2.1.3+
- SQLite (desarrollo) o MySQL/MariaDB (producción)

### Setup

```bash
# 1. Clonar repositorio
git clone <repo-url>
cd App-AKGroup

# 2. Instalar dependencias con Poetry
poetry install

# 3. Activar entorno virtual
poetry shell

# 4. Copiar y configurar variables de entorno
cp .env.example .env
# Editar .env con tu configuración

# 5. Ejecutar migraciones
alembic upgrade head

# 6. (Opcional) Cargar datos de prueba
python seeds/seed_data.py
```

---

## 🚀 Uso

### Desarrollo

#### Ejecutar Backend Solo

```bash
# Opción 1: Con Python
python scripts/dev_backend.py

# Opción 2: Con Poetry
poetry run backend

# El backend estará disponible en:
# - API: http://127.0.0.1:8000
# - Docs: http://127.0.0.1:8000/docs
# - ReDoc: http://127.0.0.1:8000/redoc
```

#### Ejecutar Frontend Solo

```bash
# Opción 1: Con Python
python scripts/dev_frontend.py

# Opción 2: Con Poetry
poetry run frontend

# Se abrirá la aplicación desktop
```

#### Ejecutar Backend + Frontend Simultáneamente

```bash
# Opción 1: Con Python
python scripts/dev_all.py

# Opción 2: Con Poetry
poetry run dev

# Inicia ambos servicios en procesos separados
# Ctrl+C para detener ambos
```

### Producción

#### Backend

```bash
# Con Uvicorn (producción)
uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --workers 4

# Con Gunicorn + Uvicorn workers
gunicorn src.backend.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

#### Frontend

```bash
# Build para distribución
flet build macos    # Para macOS
flet build windows  # Para Windows
flet build linux    # Para Linux

# Los ejecutables estarán en build/
```

---

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Tests con coverage
pytest --cov=src --cov-report=html

# Tests específicos
pytest tests/backend/ -v
pytest tests/frontend/ -v
pytest tests/shared/ -v

# Tests con markers
pytest -m unit
pytest -m integration
```

---

## 🎨 Code Quality

```bash
# Formatear código
black .

# Linting
ruff check .
ruff check --fix .

# Type checking
mypy src/backend/
mypy src/frontend/

# Ejecutar todo junto
black . && ruff check --fix . && mypy src/
```

---

## 📊 Base de Datos

### Migraciones

```bash
# Crear nueva migración
alembic revision --autogenerate -m "descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Revertir migración
alembic downgrade -1

# Ver historial
alembic history

# Ver estado actual
alembic current

# Verificar configuración
alembic check
```

### Seeds

```bash
# Cargar datos de países
python seeds/seed_countries.py

# Cargar datos de prueba completos
python seeds/seed_data.py
```

---

## 📖 API Documentation

### Endpoints Principales

#### Empresas

- `GET /api/v1/companies` - Listar empresas
- `GET /api/v1/companies/{id}` - Obtener empresa
- `POST /api/v1/companies` - Crear empresa
- `PUT /api/v1/companies/{id}` - Actualizar empresa
- `DELETE /api/v1/companies/{id}` - Eliminar empresa

#### Productos

- `GET /api/v1/products` - Listar productos
- `GET /api/v1/products/{id}` - Obtener producto
- `POST /api/v1/products` - Crear producto
- `PUT /api/v1/products/{id}` - Actualizar producto
- `DELETE /api/v1/products/{id}` - Eliminar producto

#### Otros

- Addresses, Contacts, Services, Staff, Notes
- Quotes, Orders, Deliveries, Invoices
- Lookups (Countries, Cities, etc.)

### Documentación Interactiva

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **OpenAPI JSON**: http://127.0.0.1:8000/openapi.json

---

## 🎯 Características

### Backend (FastAPI)

- ✅ API REST completa con documentación automática
- ✅ Validación de datos con Pydantic
- ✅ ORM con SQLAlchemy (SQLite/MySQL)
- ✅ Migraciones con Alembic
- ✅ Repository pattern para data access
- ✅ Service layer para business logic
- ✅ Manejo de errores centralizado
- ✅ Logging con Loguru
- ✅ CORS configurado
- ✅ Soft delete en modelos
- ✅ Timestamps automáticos
- ⏳ Autenticación JWT (pendiente)
- ⏳ Autorización RBAC (pendiente)

### Frontend (Flet)

- ✅ Aplicación desktop cross-platform
- ✅ Cliente HTTP con httpx
- ✅ Routing entre vistas
- ✅ Componentes reutilizables
- ✅ Vista de empresas con CRUD completo
- ✅ Búsqueda en tiempo real
- ✅ Diálogos de confirmación
- ✅ Snackbars para notificaciones
- ✅ Loading indicators
- ⏳ Vista de productos (pendiente)
- ⏳ Vista de órdenes (pendiente)
- ⏳ Cache local (pendiente)

### Shared

- ✅ Schemas Pydantic compartidos entre backend y frontend
- ✅ Excepciones personalizadas
- ✅ Constantes compartidas
- ✅ Validaciones consistentes

---

## 🔧 Configuración

### Variables de Entorno

Copiar `.env.example` a `.env` y configurar:

#### Backend

```env
# Environment
ENVIRONMENT=development

# Database
DATABASE_TYPE=sqlite
DATABASE_URL=sqlite:///./akgroup.db

# API
API_HOST=127.0.0.1
API_PORT=8000
API_RELOAD=True

# CORS
CORS_ORIGINS=["http://localhost:3000"]

# Logging
LOG_LEVEL=DEBUG
```

#### Frontend

```env
# API Connection
FRONTEND_API_URL=http://127.0.0.1:8000
FRONTEND_API_TIMEOUT=30

# App Settings
APP_TITLE=AK Group - Sistema de Gestión
APP_WIDTH=1280
APP_HEIGHT=800
UI_THEME=light
```

---

## 📚 Documentación Adicional

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Arquitectura completa del sistema
- **[MIGRATION_PLAN.md](docs/MIGRATION_PLAN.md)** - Plan de migración a monorepo
- **[RESUMEN_PREPARACION.md](docs/RESUMEN_PREPARACION.md)** - Resumen de preparación
- **[CLAUDE.md](CLAUDE.md)** - Guía para Claude Code

---

## 🤝 Contribución

### Workflow

```bash
# 1. Crear branch
git checkout -b feature/nueva-caracteristica

# 2. Hacer cambios y commit
git add .
git commit -m "Descripción del cambio"

# 3. Ejecutar quality checks
black . && ruff check --fix . && mypy src/

# 4. Ejecutar tests
pytest

# 5. Push y crear PR
git push origin feature/nueva-caracteristica
```

### Convenciones

- **Commits**: Mensajes descriptivos en español
- **Branches**: `feature/`, `bugfix/`, `hotfix/`
- **Code style**: Black (88 chars), Ruff, MyPy
- **Type hints**: Obligatorios en todas las funciones
- **Docstrings**: Google style con Args, Returns, Raises, Example

---

## 🐛 Troubleshooting

### Backend no inicia

```bash
# Verificar variables de entorno
cat .env

# Verificar base de datos
alembic current

# Verificar logs
tail -f logs/app.log
```

### Frontend no conecta

```bash
# Verificar que backend está corriendo
curl http://127.0.0.1:8000/health

# Verificar FRONTEND_API_URL en .env
cat .env | grep FRONTEND_API_URL

# Verificar logs
tail -f logs/frontend.log
```

### Migraciones fallan

```bash
# Verificar estado
alembic current

# Ver historial
alembic history

# Downgrade y upgrade
alembic downgrade -1
alembic upgrade head
```

---

## 📄 Licencia

Proprietary - AK Group

---

## 👥 Autores

- Rafael Arenas López - <ra.arenas.lopez@gmail.com>

---

## 🔗 Links

- **Backend API**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs
- **Repository**: [GitHub/GitLab URL]
- **Documentation**: [Docs URL]

---

## 📅 Roadmap

### v1.0.0 (Actual)
- ✅ Backend FastAPI completo
- ✅ Frontend Flet base
- ✅ CRUD de empresas
- ✅ CRUD de productos

### v1.1.0 (Próximo)
- ⏳ Autenticación JWT
- ⏳ Vista de productos en frontend
- ⏳ Vista de órdenes en frontend
- ⏳ Reportes básicos

### v2.0.0 (Futuro)
- ⏳ Autorización RBAC
- ⏳ Módulo de inventario
- ⏳ Módulo de facturación
- ⏳ Integración con servicios externos

---

## 📊 Estadísticas

- **Lines of Code**: ~15,000+
- **Test Coverage**: ~70%
- **API Endpoints**: 50+
- **Database Tables**: 20+

---

**Última actualización**: 2025-10-29
