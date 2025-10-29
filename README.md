# App-AKGroup

**Sistema de Gestión Empresarial AK Group** - Una aplicación empresarial completa construida con FastAPI, SQLAlchemy y arquitectura limpia.

## Descripción

App-AKGroup es un sistema de gestión empresarial integral diseñado para AK Group, que proporciona una API REST robusta para gestionar empresas, productos, cotizaciones, pedidos, entregas y facturación. El sistema sigue principios de arquitectura limpia con separación de responsabilidades y patrones de diseño SOLID.

## Características Principales

- **Gestión de Empresas**: CRUD completo de empresas, sucursales y RUTs
- **Gestión de Productos**: Productos tipo ARTICLE y NOMENCLATURE con componentes
- **BOM (Bill of Materials)**: Gestión de componentes y cálculo automático de costos
- **Gestión de Cotizaciones**: Creación y seguimiento de cotizaciones con artículos y nomenclaturas
- **Gestión de Pedidos**: Procesamiento de pedidos con múltiples cotizaciones
- **Entregas**: Gestión de entregas parciales y completas
- **Facturación**: Gestión de facturas con integración SII
- **Auditoría**: Tracking automático de creación y actualización de registros
- **Soft Delete**: Eliminación lógica de registros con posibilidad de recuperación
- **Búsqueda Avanzada**: Endpoints de búsqueda por múltiples criterios

## Tecnologías

### Backend & API
- **Python**: >=3.13.0,<4.0
- **FastAPI**: 0.115.0+ - Framework web moderno y rápido
- **Uvicorn**: 0.34.0+ - Servidor ASGI de alto rendimiento
- **Pydantic**: 2.12.3+ - Validación de datos y configuración

### Base de Datos
- **SQLAlchemy**: 2.0.44+ - ORM potente y flexible
- **Alembic**: 1.17.0+ - Migraciones de base de datos
- **aiosqlite**: 0.21.0+ - SQLite asíncrono (desarrollo)
- **PyMySQL**: 1.1.0+ - MySQL/MariaDB connector (producción)

### Utilidades
- **Loguru**: 0.7.3+ - Logging simple y potente
- **Pendulum**: 3.1.0+ - Manejo de fechas y tiempos con zonas horarias
- **openpyxl**: 3.1.5+ - Exportación/importación de Excel
- **email-validator**: 2.3.0+ - Validación de correos electrónicos
- **cryptography**: 44.0.0+ - Encriptación y seguridad

### Herramientas de Desarrollo
- **Poetry**: 2.1.3+ - Gestión de dependencias y empaquetado
- **Black**: 24.0.0+ - Formateador de código (88 caracteres)
- **Ruff**: 0.1.0+ - Linter moderno y rápido
- **MyPy**: 1.8.0+ - Type checking estático
- **Pytest**: 8.0.0+ - Framework de testing
- **pytest-cov**: 4.1.0+ - Cobertura de código

## Requisitos

- Python >=3.13.0,<4.0
- Poetry 2.1.3+
- MySQL/MariaDB (producción) o SQLite (desarrollo)

## Instalación

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd App-AKGroup
```

### 2. Instalar Poetry (si no está instalado)

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 3. Instalar dependencias

```bash
poetry install
```

### 4. Configurar variables de entorno

Copiar el archivo de ejemplo y configurar según tu entorno:

```bash
cp .env.example .env
```

Editar `.env` con tus configuraciones:

```env
# Entorno
ENVIRONMENT=development

# Base de datos
DATABASE_TYPE=sqlite  # o mysql
DATABASE_URL=sqlite:///./akgroup.db

# Para MySQL:
# DATABASE_URL=mysql+pymysql://user:password@localhost:3306/akgroup

# API
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]

# Logging
LOG_LEVEL=INFO
```

### 5. Crear/Migrar base de datos

```bash
# Crear tablas automáticamente (desarrollo)
poetry run python main.py

# O usar migraciones (recomendado para producción)
poetry run alembic upgrade head
```

### 6. (Opcional) Poblar datos iniciales

```bash
poetry run python seeds/seed_data.py
```

## Uso

### Ejecutar el servidor de desarrollo

```bash
poetry run python main.py
```

La API estará disponible en: `http://localhost:8000`

### Documentación interactiva

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Health Check

```bash
curl http://localhost:8000/health
```

## Desarrollo

### Activar entorno virtual

```bash
poetry shell
```

### Agregar dependencias

```bash
# Dependencia de producción
poetry add <package-name>

# Dependencia de desarrollo
poetry add --group dev <package-name>
```

### Formatear código

```bash
# Formatear con Black (88 caracteres)
black .

# Verificar sin modificar
black --check .
```

### Linting

```bash
# Ejecutar Ruff
ruff check .

# Auto-fix
ruff check --fix .
```

### Type Checking

```bash
mypy .
```

### Ejecutar todos los checks de calidad

```bash
black . && ruff check --fix . && mypy .
```

### Testing

```bash
# Ejecutar todos los tests
pytest

# Con cobertura
pytest --cov=. --cov-report=html

# Ver reporte de cobertura
# Abrir htmlcov/index.html en navegador

# Test específico
pytest tests/test_specific.py

# Función específica
pytest tests/test_specific.py::test_function_name
```

### Migraciones de Base de Datos

```bash
# Crear nueva migración automática
alembic revision --autogenerate -m "descripción de cambios"

# Aplicar migraciones
alembic upgrade head

# Revertir una migración
alembic downgrade -1

# Ver historial
alembic history

# Ver estado actual
alembic current
```

## Arquitectura

### Estructura del Proyecto

```
App-AKGroup/
├── src/                        # Código fuente principal
│   ├── api/                    # Endpoints FastAPI
│   │   ├── v1/                 # API versión 1
│   │   │   ├── companies.py    # Endpoints de empresas
│   │   │   ├── products.py     # Endpoints de productos
│   │   │   ├── quotes.py       # Endpoints de cotizaciones
│   │   │   ├── orders.py       # Endpoints de pedidos
│   │   │   ├── deliveries.py   # Endpoints de entregas
│   │   │   └── invoices.py     # Endpoints de facturas
│   │   ├── dependencies.py     # Inyección de dependencias
│   │   └── error_handlers.py   # Manejadores de errores
│   ├── models/                 # Modelos SQLAlchemy
│   │   ├── base/               # Base y mixins
│   │   ├── core/               # Modelos core (empresas, productos, etc.)
│   │   ├── business/           # Modelos de negocio (quotes, orders, etc.)
│   │   └── lookups/            # Tablas de referencia
│   ├── repositories/           # Capa de acceso a datos
│   │   └── core/               # Repositorios por módulo
│   ├── schemas/                # Schemas Pydantic
│   │   └── core/               # Schemas por módulo
│   ├── services/               # Lógica de negocio
│   │   └── core/               # Servicios por módulo
│   ├── database/               # Configuración de BD
│   │   ├── engine.py           # Engine de SQLAlchemy
│   │   └── session.py          # Session management
│   ├── config/                 # Configuración
│   │   ├── settings.py         # Settings con pydantic-settings
│   │   └── constants.py        # Constantes de la aplicación
│   ├── exceptions/             # Excepciones personalizadas
│   └── utils/                  # Utilidades compartidas
├── migrations/                 # Migraciones Alembic
├── tests/                      # Tests unitarios e integración
├── seeds/                      # Scripts para datos iniciales
├── scripts/                    # Scripts de utilidad
├── docs/                       # Documentación adicional
├── logs/                       # Archivos de log
├── main.py                     # Punto de entrada FastAPI
├── pyproject.toml              # Configuración Poetry
├── alembic.ini                 # Configuración Alembic
├── CLAUDE.md                   # Guía para Claude Code
└── README.md                   # Este archivo
```

### Patrones de Diseño

- **Repository Pattern**: Abstracción de acceso a datos
- **Service Layer**: Lógica de negocio separada
- **Dependency Injection**: Inyección de dependencias con FastAPI
- **Factory Pattern**: Creación de objetos complejos
- **Unit of Work**: Gestión de transacciones (via SQLAlchemy Session)

### Principios SOLID

El código sigue estrictamente los principios SOLID:
- **Single Responsibility**: Cada clase/función tiene una única responsabilidad
- **Open/Closed**: Abierto para extensión, cerrado para modificación
- **Liskov Substitution**: Los subtipos son sustituibles por sus tipos base
- **Interface Segregation**: Interfaces específicas mejor que una general
- **Dependency Inversion**: Depender de abstracciones, no de implementaciones concretas

## API Endpoints

### Empresas (`/api/v1/companies`)
- `POST /companies` - Crear empresa
- `GET /companies` - Listar empresas
- `GET /companies/{id}` - Obtener empresa por ID
- `PUT /companies/{id}` - Actualizar empresa
- `DELETE /companies/{id}` - Eliminar empresa (soft delete)
- `GET /companies/search` - Búsqueda avanzada

### Productos (`/api/v1/products`)
- `POST /products` - Crear producto
- `GET /products` - Listar productos
- `GET /products/{id}` - Obtener producto por ID
- `PUT /products/{id}` - Actualizar producto
- `DELETE /products/{id}` - Eliminar producto
- `GET /products/{id}/bom` - Obtener Bill of Materials

### Cotizaciones (`/api/v1/quotes`)
- `POST /quotes` - Crear cotización
- `GET /quotes` - Listar cotizaciones
- `GET /quotes/{id}` - Obtener cotización
- `PUT /quotes/{id}` - Actualizar cotización
- `POST /quotes/{id}/items` - Agregar items a cotización
- `GET /quotes/{id}/total` - Calcular total de cotización

### Pedidos (`/api/v1/orders`)
- `POST /orders` - Crear pedido
- `GET /orders` - Listar pedidos
- `GET /orders/{id}` - Obtener pedido
- `PUT /orders/{id}/status` - Actualizar estado

### Entregas (`/api/v1/deliveries`)
- `POST /deliveries` - Crear entrega
- `GET /deliveries` - Listar entregas
- `GET /deliveries/{id}` - Obtener entrega

### Facturas (`/api/v1/invoices`)
- `POST /invoices` - Crear factura
- `GET /invoices` - Listar facturas
- `GET /invoices/{id}` - Obtener factura
- `POST /invoices/{id}/export-sii` - Exportar a SII

### Lookups (`/api/v1/lookups`)
- `GET /company-types` - Tipos de empresa
- `GET /units` - Unidades de medida
- `GET /countries` - Países
- `GET /currencies` - Monedas

Ver documentación completa en `/docs` cuando el servidor esté corriendo.

## Estándares de Código

### Convenciones de Nombres
- **Funciones/Variables**: `snake_case`
- **Clases**: `PascalCase`
- **Constantes**: `UPPER_SNAKE_CASE`
- **Módulos**: `lowercase.py`
- **Privados**: `_prefijo`

### Type Hints
- Obligatorio en todas las funciones públicas
- Usar tipos de `typing` para colecciones
- Usar `Optional[T]` para valores que pueden ser None

### Docstrings
- Obligatorio en funciones/clases públicas
- Formato Google/NumPy style
- Incluir: Args, Returns, Raises, Example

### Importaciones
1. Standard library
2. Third-party packages
3. Local imports

Cada grupo separado por línea en blanco.

## Logging

El proyecto usa **Loguru** para logging estructurado:

```python
from src.utils.logger import logger

# Info: Flujo normal
logger.info("Procesando pedido {order_id}", order_id=123)

# Success: Operaciones exitosas
logger.success("Pedido {order_id} procesado", order_id=123)

# Warning: Problemas recuperables
logger.warning("Stock bajo para item {item_id}", item_id=456)

# Error: Errores irrecuperables
logger.error("Falló procesar pedido {order_id}", order_id=123)

# Exception: Log con traceback completo
logger.exception("Error inesperado procesando pedido")
```

Los logs se guardan en `logs/` con rotación automática.

## Contribuir

### Workflow de Desarrollo

1. Crear branch desde `main`
2. Implementar cambios siguiendo estándares
3. Ejecutar formatters y linters
4. Ejecutar type checker
5. Escribir/actualizar tests
6. Ejecutar suite de tests con cobertura
7. Crear migración si hay cambios en modelos
8. Commit con mensaje descriptivo
9. Crear Pull Request

### Commits

Seguir formato convencional:
```
tipo(alcance): descripción breve

Descripción más detallada si es necesario.

- Cambio 1
- Cambio 2
```

Tipos: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## Seguridad

- Variables sensibles en `.env` (nunca en el código)
- `.env` está en `.gitignore`
- Validación de datos con Pydantic
- SQL injection prevenido por SQLAlchemy ORM
- TODO: Implementar autenticación y autorización

## Licencia

Propietaria - AK Group

## Contacto

- **Autor**: Rafael Arenas López
- **Email**: ra.arenas.lopez@gmail.com
- **Empresa**: AK Group

## Documentación Adicional

- **CLAUDE.md**: Guía completa para desarrollo con Claude Code
- **/docs**: Documentación interactiva de la API (cuando servidor está corriendo)
- **Inline docstrings**: Documentación detallada en el código

## Estado del Proyecto

**Versión actual**: 1.0.0

**Estado**: En desarrollo activo

### Completado
- ✅ Arquitectura base con FastAPI
- ✅ Modelos de base de datos completos
- ✅ Sistema de migraciones
- ✅ Repositorios y servicios core
- ✅ API REST endpoints principales
- ✅ Gestión de empresas y productos
- ✅ Sistema de cotizaciones, pedidos y entregas
- ✅ Logging estructurado
- ✅ Manejo de errores personalizado

### En Progreso
- 🚧 Tests unitarios e integración
- 🚧 Autenticación y autorización
- 🚧 Integración completa con SII
- 🚧 Dashboard y reportes

### Planificado
- 📋 UI con Flet (desktop app)
- 📋 Notificaciones por email
- 📋 Exportación avanzada a Excel/PDF
- 📋 API de webhooks
- 📋 Documentación de usuario final
